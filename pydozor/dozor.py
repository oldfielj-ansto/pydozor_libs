from __future__ import annotations
from typing import Any, Self
from pathlib import Path
from tempfile import mkdtemp
from datetime import datetime, timezone
from pydantic import NewPath, validate_call
from ._compat import ffi
from .schemas import DozorConfig

__all__ = ("create_config_file", "Dozor")

dozor = ffi.dlopen('libdozor.so')


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


class Dozor():
    def __init__(self, config_file):
        self.data_input = ffi.new('struct DATACOL*')
        dozor.dozor_set_defaults_(self.data_input)

        self.detector = ffi.new('struct DETECTOR*')

        self.detector.binning_factor = 1
        
        self.detector.ix = 0
        self.detector.iy = 0
        self.detector.pixel =0.0  #0.075
        fname = ffi.new('char[1024]', config_file)
        templ = ffi.new('char[1024]')
        library = ffi.cast('char*', ffi.NULL) #ffi.new("char**", ffi.NULL)
        dozor.read_dozor_(self.detector, self.data_input, fname, templ, library)

        self.local = ffi.new('struct LOCAL*')
        self.detector.ix = self.detector.ix_unbinned * self.detector.binning_factor
        self.detector.iy = self.detector.iy_unbinned * self.detector.binning_factor
        detector_xy = self.detector.ix * self.detector.iy
        self.PSIim = ffi.new('char[%d]' % detector_xy)
        self.KLim = ffi.new('char[%d]' % detector_xy)
        debug = ffi.new('int*', 0)
        dozor.pre_dozor_(self.detector, self.data_input, self.local, self.PSIim, self.KLim, debug)

    def do_image(self: Self, img: Any) -> Any:
        _data = ffi.new("struct DATACOL_PICKLE*")
        _datacol = ffi.new("struct DATACOL*")
        _c_img = ffi.cast("short*", ffi.from_buffer(img))
        _started = datetime.now(timezone.utc)
        dozor.dozor_do_image_(
            _c_img,
            self.detector,
            self.data_input,
            _datacol,
            _data,
            self.local,
            self.PSIim,
            self.KLim,
        )
        _finished = datetime.now(timezone.utc)
        return _data

    def get_spot_list(self: Self, img: Any, data: Any, datacol: Any) -> Any:
        _spots = ffi.new(f"struct Reflection[{data.NofR}]")
        dozor.dozor_get_spot_list_(
            self.detector,
            datacol,
            data,
            ffi.cast("short*", ffi.from_buffer(img)),
            _spots,
        )
        return _spots
