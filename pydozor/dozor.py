from __future__ import annotations

from os import environ
from typing import TYPE_CHECKING, Self
from pathlib import Path
from tempfile import mkdtemp
from pydantic import FilePath, NewPath, validate_call
from ._compat import ffi, Detector, Datacol, Local, DatacolPickle, Reflection
from .schemas import DozorConfig, DataSchema, DatacolSchema, ReflectionSchema

if TYPE_CHECKING:
    from numpy.typing import NDArray

__all__ = ("create_config_file", "Dozor")

dozor = ffi.dlopen(environ.get("LIB_DOZOR_PATH", "libdozor.so"))


@validate_call
def create_config_file(
    config: DozorConfig,
    *,
    path: NewPath | None = None,
) -> Path:
    """Create a new Dozor config file.

    Parameters
    ----------
    config : DozorConfig
        Dozor configuration to be written to disk.
    path : NewPath | None, optional
        Path to create Dozor config file at, if undefined a `dozor.dat` file
        will be created under a new temporary directory, by default None.

    Returns
    -------
    Path
        File path to created Dozor config file.
    """
    if path is None:
        path = Path(f"{mkdtemp()}/dozor.dat")

    with open(path, "w") as _file:
        _file.write(config.model_dump())
    return path


class Dozor:
    """Python Wrapper For Dozor"""

    @validate_call
    def __init__(self, config_file: FilePath) -> None:
        _data_input = Datacol()
        _detector = Detector()
        _local = Local()

        dozor.dozor_set_defaults_(_data_input)

        dozor.read_dozor_(
            _detector,
            _data_input,
            ffi.new("char[1024]", str(config_file).encode("utf-8")),
            ffi.new("char[1024]"),
            ffi.cast('char*', ffi.NULL),
        )

        _detector.ix = _detector.ix_unbinned * _detector.binning_factor
        _detector.iy = _detector.iy_unbinned * _detector.binning_factor

        self._pixel_count: int = _detector.ix * _detector.iy

        _psi_im = ffi.new(f"char[{self._pixel_count}]")
        _kl_im = ffi.new(f"char[{self._pixel_count}]")
        dozor.pre_dozor_(
            _detector,
            _data_input,
            _local,
            _psi_im,
            _kl_im,
            ffi.new("int*", 0),
        )

        self._data_input = Datacol.to_dict(_data_input)
        self._detector = Detector.to_dict(_detector)
        self._local = Local.to_dict(_local)
        self._psi_im: bytes = ffi.string(_psi_im, self._pixel_count)
        self._kl_im: bytes = ffi.string(_kl_im, self._pixel_count)

    def do_image(self: Self, image: NDArray) -> tuple[DatacolSchema, DataSchema]:
        """Call Dozor to process frame.

        Wrapper around Dozor `dozor_do_image` subroutine.

        Parameters
        ----------
        image : NDArray
            Frame to process.

        Returns
        -------
        tuple[DatacolSchema, DataSchema]
            Decoded output from `dozor_do_image`.
        """
        _datacol = Datacol()
        _data = DatacolPickle()
        dozor.dozor_do_image_(
            ffi.cast("short*", ffi.from_buffer(image)),
            Detector(**self._detector),
            Datacol(**self._data_input),
            _datacol,
            _data,
            Local(**self._local),
            ffi.new(f"char[{self._pixel_count}]", self._psi_im),
            ffi.new(f"char[{self._pixel_count}]", self._kl_im),
        )
        return (
            Datacol.to_dict(_datacol),
            DatacolPickle.to_dict(_data),
        )

    def get_spot_list(
        self: Self,
        image: NDArray,
        data: DataSchema,
        datacol: DatacolSchema,
    ) -> list[ReflectionSchema]:
        """Get spot X/Y coordinates.

        Wrapper around Dozor `dozor_get_spot_list` subroutine.

        Parameters
        ----------
        image : NDArray
            Frame to get spots coords for.
        data : DataSchema
            Output from `dozor_do_image`.
        datacol : DatacolSchema
            Datacol.

        Returns
        -------
        list[ReflectionSchema]
            Spots X/Y coordinates.
        """
        _spots_length = data["NofR"]
        _spots = ffi.new(f"struct Reflection[{_spots_length}]")
        dozor.dozor_get_spot_list_(
            Detector(**self._detector),
            Datacol(**datacol),
            DatacolPickle(**data),
            ffi.cast("short*", ffi.from_buffer(image)),
            _spots,
        )
        return [
            Reflection.to_dict(_item)
            for _item in ffi.unpack(_spots, _spots_length)
        ]
