from __future__ import annotations

from os import environ
from os.path import (
    abspath as os_abspath,
    dirname as os_dirname,
    join as os_joinpath,
    realpath as os_realpath,
)
from pathlib import Path
from typing import TYPE_CHECKING, Self

from ._compat.dozor import Datacol, DatacolPickle, Detector, Local, ffi
from .schemas import DatacolSchema, DataSchema

if TYPE_CHECKING:
    from numpy import uint16
    from numpy.typing import NDArray

__all__ = ("Dozor",)

CUR_DIR = os_dirname(os_realpath(__file__))


_lib_dozor_path = "libdozor.so"
if "LIB_DOZOR_PATH" in environ:
    _lib_dozor_path = environ.get("LIB_DOZOR_PATH")
elif Path(os_joinpath(CUR_DIR, "../libdozor.so")).exists():
    _lib_dozor_path = str(os_abspath(os_joinpath(CUR_DIR, "../libdozor.so")))


class Dozor:
    """Python Wrapper For Dozor"""

    def __init__(self, config_file: Path) -> None:
        self._lib = ffi.dlopen(_lib_dozor_path)

        self._data_input = Datacol()
        self._lib.dozor_set_defaults_(self._data_input)

        self._detector = Detector()

        self._lib.read_dozor_(
            self._detector,
            self._data_input,
            ffi.new("char[1024]", str(config_file).encode("utf-8")),
            ffi.new("char[1024]"),
            ffi.cast("char*", ffi.NULL),
        )

        self._local = Local()
        self._detector.ix = self._detector.ix_unbinned * self._detector.binning_factor
        self._detector.iy = self._detector.iy_unbinned * self._detector.binning_factor
        self._pixel_count: int = self._detector.ix * self._detector.iy
        self._psi_im = ffi.new(f"char[{self._pixel_count}]")
        self._kl_im = ffi.new(f"char[{self._pixel_count}]")
        self._lib.pre_dozor_(
            self._detector,
            self._data_input,
            self._local,
            self._psi_im,
            self._kl_im,
            ffi.new("int*", 0),
        )

    @property
    def pixel_max(self: Self) -> int:
        """Pixel max.

        Returns
        -------
        int
            Value `pixel_max` from `_data_input`.
        """
        return self._data_input.pixel_max

    def do_image(
        self: Self,
        image: NDArray[uint16],
    ) -> tuple[DatacolSchema, DataSchema]:
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
        _data = DatacolPickle()
        _datacol = Datacol()
        self._lib.dozor_do_image_(
            ffi.cast("short*", ffi.from_buffer(image)),
            self._detector,
            self._data_input,
            _datacol,
            _data,
            self._local,
            self._psi_im,
            self._kl_im,
        )
        return (
            Datacol.to_dict(_datacol),
            DatacolPickle.to_dict(_data),
        )

    # def get_spot_list(
    #     self: Self,
    #     image: NDArray,
    #     data: DataSchema,
    #     datacol: DatacolSchema,
    # ) -> list[ReflectionSchema]:
    #     """Get spot X/Y coordinates.

    #     Wrapper around Dozor `dozor_get_spot_list` subroutine.

    #     Parameters
    #     ----------
    #     image : NDArray
    #         Frame to get spots coords for.
    #     data : DataSchema
    #         Output from `dozor_do_image`.
    #     datacol : DatacolSchema
    #         Datacol.

    #     Returns
    #     -------
    #     list[ReflectionSchema]
    #         Spots X/Y coordinates.
    #     """
    #     _spots_length = data["NofR"]
    #     _spots = ffi.new(f"struct Reflection[{_spots_length}]")
    #     ffi.dozor_get_spot_list_(
    #         self._detector,
    #         Datacol(**datacol),
    #         DatacolPickle(**data),
    #         ffi.cast("short*", ffi.from_buffer(image)),
    #         _spots,
    #     )
    #     return [
    #         Reflection.to_dict(_item) for _item in ffi.unpack(_spots, _spots_length)
    #     ]
