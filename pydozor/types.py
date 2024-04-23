from typing import TYPE_CHECKING

__all__ = ("Backpol2DType",)

if TYPE_CHECKING:
    Backpol2DType = tuple[float, ...]
else:
    Backpol2DType = tuple[(float,) * 51]
