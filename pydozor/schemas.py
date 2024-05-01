from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Self

from pydantic import BaseModel, ConfigDict, Field, model_serializer
from typing_extensions import Literal, TypedDict

if TYPE_CHECKING:
    from pydantic.main import IncEx

__all__ = ("DozorConfig", "DataSchema", "DatacolSchema", "ReflectionSchema")


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


class DatacolSchema(TypedDict, total=True):
    """Dozor Datacol"""

    wave: float
    dist: float
    monoch: float
    aconst: float
    Ispot: int
    texposure: float
    mrd: int
    hmax2: float
    hmin2: float
    delh2: float
    mgain: float
    backpol: list[float]
    backpolP: list[float]
    backerr: list[float]
    IMstep: float
    xcen: float
    ycen: float
    start_angl: float
    phiwidth: float
    number_images: int
    image_first: int
    graph: int
    sprint: int
    backg: int
    rd: int
    isum: int
    w: int
    wg: int
    pr: int
    prAll: int
    vbin: list[float]
    pixel_min: int
    pixel_max: int
    Kxmin: int
    Kxmax: int
    Kymin: int
    Kymax: int
    nbad: int
    Bxmin: list[int]
    Bxmax: list[int]
    Bymin: list[int]
    Bymax: list[int]
    wedge: int
    pLim1: list[int]
    pLim2: list[int]
    idealback0: list[float]
    idealback: list[float]
    RList: list[float]
    hklKoor: list[float]
    Ilimit: list[float]
    vbins: list[float]
    vbina: list[float]
    Wil: list[float]
    beamstop_size: float
    beamstop_distance: float
    beamstop_vertical: int
    sigLev: float


class DataSchema(TypedDict, total=True):
    """Dozor Output"""

    coef: float
    iav: float
    nof_r: int
    nof_s: int
    rfexp: float
    sumback_2d: float
    sumtotal_2d: float
    backpol_2d: list[float]
    dlim: float
    dlim09: float
    score2: float
    score3: float
    table_b: float
    table_corr: float
    table_est: float
    table_intsum: float
    table_resol: float
    table_rfact: float
    table_sc: float
    table_suc: int


class ReflectionSchema(TypedDict, total=True):
    """Dozor Nice Reflection"""

    x: float
    y: float
    intensity: float
