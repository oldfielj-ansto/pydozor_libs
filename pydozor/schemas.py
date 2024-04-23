from __future__ import annotations

from typing import Annotated, Any, Callable, Self, TYPE_CHECKING
from typing_extensions import Literal, TypedDict
from pydantic import BaseModel, ConfigDict, Field, model_serializer
from .types import Backpol2DType

if TYPE_CHECKING:
    from pydantic.main import IncEx

__all__ = ("DozorConfig", "DozorOutput", "DozorNiceReflection")


class DozorConfig(BaseModel):
    """Dozor Config"""

    spot_size: int = Field(title="Spot Size")
    spot_level: int = Field(title="Spot Level")
    ix_min: int = Field(title="IX-Min")
    ix_max: int = Field(title="IX-Max")
    iy_min: int = Field(title="IY-Min")
    iy_max: int = Field(title="IY-Max")
    detector: str = Field(title="Detector")
    nx: int = Field(title="NX")
    ny: int = Field(title="NY")
    pixel: float = Field(title="Pixel")
    fraction_polarization: float = Field(title="Fraction Polarization")
    pixel_min: int = Field(title="Pixel Min")
    pixel_max: int = Field(title="Pixel Max")
    exposure: float = Field(title="Exposure")
    detector_distance: float = Field(title="Detector Distance")
    wavelength: float = Field(title="X-ray Wavelength", alias="X-ray_wavelength")
    org_x: int = Field(title="Org-X", alias="orgx")
    org_y: int = Field(title="Org-Y", alias="orgy")
    oscillation_range: float = Field(title="Oscillation Range")
    image_step: float = Field(title="Image Step")
    starting_angle: float = Field(title="Starting Angle")

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @model_serializer(mode="wrap")
    def serialize_model(self, serializer: Callable[[Self], dict[str, Any]]) -> str:
        return "\n".join(
            [f"{_key} {_value}" for _key, _value in serializer(self).items()] + ["end"]
        )

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "python",
        include: IncEx = None,
        exclude: IncEx = None,
        context: dict[str, Any] | None = None,
        by_alias: bool = True,
        exclude_unset: bool = True,
        exclude_defaults: bool = True,
        exclude_none: bool = True,
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        serialize_as_any: bool = False,
    ) -> str:
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any,
        )


class DozorOutput(TypedDict, total=True):
    """Dozor Output"""

    coef: Annotated[
        float,
        Field(title="Coef", validation_alias="Coef"),
    ]
    iav: Annotated[
        float,
        Field(title="Iav", validation_alias="Iav"),
    ]
    nof_r: Annotated[
        int,
        Field(title="NofR", validation_alias="NofR"),
    ]
    nof_s: Annotated[
        int,
        Field(title="NofS", validation_alias="NofS"),
    ]
    rfexp: Annotated[
        float,
        Field(title="Rfexp", validation_alias="Rfexp"),
    ]
    sumback_2d: Annotated[
        float,
        Field(title="SumBack2D", validation_alias="SumBack2D"),
    ]
    sumtotal_2d: Annotated[
        float,
        Field(title="SumTotal2D", validation_alias="SumTotal2D"),
    ]
    backpol_2d: Annotated[
        Backpol2DType,
        Field(title="backpol2D", validation_alias="backpol2D"),
    ]
    dlim: Annotated[
        float,
        Field(title="dlim", validation_alias="dlim"),
    ]
    dlim09: Annotated[
        float,
        Field(title="dlim09", validation_alias="dlim09"),
    ]
    score2: Annotated[
        float,
        Field(title="score2", validation_alias="score2"),
    ]
    score3: Annotated[
        float,
        Field(title="score3", validation_alias="score3"),
    ]
    table_b: Annotated[
        float,
        Field(title="table_b", validation_alias="table_b"),
    ]
    table_corr: Annotated[
        float,
        Field(title="table_corr", validation_alias="table_corr"),
    ]
    table_est: Annotated[
        float,
        Field(title="table_est", validation_alias="table_est"),
    ]
    table_intsum: Annotated[
        float,
        Field(title="table_intsum", validation_alias="table_intsum"),
    ]
    table_resol: Annotated[
        float,
        Field(title="table_resol", validation_alias="table_resol"),
    ]
    table_rfact: Annotated[
        float,
        Field(title="table_rfact", validation_alias="table_rfact"),
    ]
    table_sc: Annotated[
        float,
        Field(title="table_sc", validation_alias="table_sc"),
    ]
    table_suc: Annotated[
        int,
        Field(title="table_suc", validation_alias="table_suc"),
    ]

    __pydantic_config__ = ConfigDict(populate_by_name=True)


class DozorNiceReflection(TypedDict, total=True):
    """Dozor Nice Reflection"""

    x: float
    y: float
    intensity: float

    __pydantic_config__ = ConfigDict(populate_by_name=True)
