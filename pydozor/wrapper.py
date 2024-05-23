from __future__ import annotations

from pathlib import Path
from tempfile import mkdtemp
from typing import TYPE_CHECKING, Any, overload

from numpy import uint16, unsignedinteger
from pydantic import NewPath, validate_call

from .dozor import Dozor
from .schemas import DatacolSchema, DataSchema, DozorConfig

if TYPE_CHECKING:
    from numpy.typing import NDArray

__all__ = ("create_config_file", "call_dozor")


def _convert_to_uint16(
    array: NDArray[unsignedinteger[Any]],
    pixel_max: int,
) -> NDArray[uint16]:
    """Convert array to DType `uint16`.

    Parameters
    ----------
    array : NDArray[unsignedinteger[Any]]
        Array with any unsigned integer DType.
    pixel_max : int
        Max pixel value.

    Returns
    -------
    NDArray[uint16]
        Array with DType `uint16`.
    """
    if array.dtype < uint16:
        array = array.astype(uint16)
    elif array.dtype > uint16:
        # if count is over 65534 and below max_count, set to the max value for uint16
        array[(array > 65534) & (array <= pixel_max)] = 65534
        array[array > pixel_max] = 65535
        array = array.astype(uint16)
    return array


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


@overload
def call_dozor(  # noqa: E704
    mask: NDArray[unsignedinteger[Any]],
    frame: NDArray[unsignedinteger[Any]],
    config_file: Path,
) -> tuple[DatacolSchema, DataSchema]: ...


def call_dozor(
    mask: NDArray[unsignedinteger[Any]],
    frame: NDArray[unsignedinteger[Any]],
    config_file: Path,
) -> tuple[DatacolSchema, DataSchema]:
    """ """
    _dozor_wrapper = Dozor(config_file)

    _np_frame = _convert_to_uint16(frame.copy(), _dozor_wrapper.pixel_max)

    # _np_frame[_idx] = 65535
    _np_frame = _np_frame * mask

    return _dozor_wrapper.do_image(_np_frame)
