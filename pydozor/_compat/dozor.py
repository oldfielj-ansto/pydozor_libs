from typing import TYPE_CHECKING, Any, ClassVar, Self, overload

from cffi import FFI

__all__ = ("ffi", "Detector", "Datacol", "Local", "DatacolPickle", "Reflection")


ffi = FFI()
ffi.cdef(
    """
struct DETECTOR
{
    int ix, iy;
    int ix_unbinned, iy_unbinned;
    int binning_factor;
    float pixel;
};

struct DATACOL
{
    float wave;
    float dist;
    float monoch;
    float aconst;
    int Ispot;
    float texposure;
    int mrd;
    float hmax2;
    float hmin2;
    float delh2;
    float mgain;
    float backpol[51];
    float backpolP[51];
    float backerr[51];
    float IMstep;
    float xcen, ycen;
    float start_angl, phiwidth;
    int number_images,image_first;
    int graph, sprint, backg, rd, isum;
    int w, wg;
    int pr;
    int prAll;
    float vbin[50];
    int pixel_min, pixel_max;
    int Kxmin, Kxmax, Kymin, Kymax;
    int nbad;
    int Bxmin[50], Bxmax[50], Bymin[50], Bymax[50];
    int wedge;
    int pLim1[1101], pLim2[1101];
    float idealback0[50];
    float idealback[150];
    float RList[51051];
    float hklKoor[102000];
    float Ilimit[51];
    float vbins[51];
    float vbina[51];
    float Wil[2103];
    float beamstop_size;
    float beamstop_distance;
    int beamstop_vertical;
    float sigLev;
};

struct LOCAL
{
    float cos2tet2[51];
    float pol[765]; //51*15
    float absorb[51];
};

struct DATACOL_PICKLE
{
    float backpol2D[51];
    float Rfexp;
    float Iav;
    int NofR;
    float dlim;
    double SumTotal2D, SumBack2D;
    float Coef;
    int table_suc;
    double table_sc;
    double table_b;
    float table_resol;
    float table_corr;
    float table_rfact;
    float table_intsum;
    float table_est;
    float score2;
    float score3;
    float dlim09;
    int NofS;
};

struct Reflection
{
    float x;
    float y;
    float intensity;
};

void dozor_set_defaults_(struct DATACOL*);
void read_dozor_(struct DETECTOR*, struct DATACOL*, char[1024], char[1024], char*);
void pre_dozor_(struct DETECTOR*, struct DATACOL*, struct LOCAL*, char*, char*, int*);
void dozor_do_image_(short*, struct DETECTOR*, struct DATACOL*, struct DATACOL*, struct DATACOL_PICKLE*, struct LOCAL*, char*, char*);
void dozor_get_spot_list_(struct DETECTOR*, struct DATACOL*, struct DATACOL_PICKLE*, short*, struct Reflection*);
"""
)


class _CData:
    """CData Handler"""

    _cdecl: ClassVar[str | FFI.CType]
    _cdecl_size: ClassVar[int | None]

    if TYPE_CHECKING:

        @overload
        def __new__(cls: type[Self], **kwargs: Any) -> Self: ...  # noqa: E704

    def __new__(cls: type[Self], **kwargs: Any) -> FFI.CData:
        _cdata = ffi.new(cls._cdecl)
        for _key, _value in kwargs.items():
            setattr(_cdata, _key, _value)
        return _cdata

    def __init_subclass__(
        cls: type[Self],
        cdecl: str | FFI.CType,
        cdecl_size: int | None = None,
    ) -> None:
        if isinstance(cdecl, str):
            cdecl = cdecl.strip()
        cls._cdecl = cdecl
        cls._cdecl_size = cdecl_size

    @classmethod
    def to_dict(cls: type[Self], obj: FFI.CData) -> dict[str, Any]:
        """ """
        _obj_dict = {}
        for _key in dir(obj):
            _value = getattr(obj, _key, None)

            try:
                _c_type = ffi.typeof(_value)
                _obj_dict[_key] = ffi.unpack(_value, _c_type.length)
            except TypeError:
                _obj_dict[_key] = _value
        return _obj_dict


class Detector(_CData, cdecl="struct DETECTOR*"):
    """Detector (CData)"""

    ix: int
    iy: int
    ix_unbinned: int
    iy_unbinned: int
    binning_factor: int
    pixel: int

    def __new__(
        cls: type[Self],
        *,
        ix: int = 0,
        iy: int = 0,
        binning_factor: int = 1,
        pixel: float = 0.0,
        **kwargs: Any,
    ) -> Self:
        return super().__new__(
            cls,
            ix=ix,
            iy=iy,
            binning_factor=binning_factor,
            pixel=pixel,
            **kwargs,
        )


class Datacol(_CData, cdecl="struct DATACOL*"):
    """Datacol (CData)"""

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


class Local(_CData, cdecl="struct LOCAL*"):
    """Local (CData)"""

    cos2tet2: list[float]
    pol: list[float]
    absorb: list[float]


class DatacolPickle(_CData, cdecl="struct DATACOL_PICKLE*"):
    """Datacol Pickle (CData)"""

    backpol2D: list[float]
    Rfexp: float
    Iav: float
    NofR: int
    dlim: float
    SumTotal2D: float
    SumBack2D: float
    Coef: float
    table_suc: int
    table_sc: float
    table_b: float
    table_resol: float
    table_corr: float
    table_rfact: float
    table_intsum: float
    table_est: float
    score2: float
    score3: float
    dlim09: float
    NofS: int


class Reflection(_CData, cdecl="struct Reflection*"):
    """Reflection (CData)"""

    x: float
    y: float
    intensity: float
