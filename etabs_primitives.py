"""
ETABS Primitives - Core data structures and enums for ETABS MCP
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import IntEnum


# ==================== ETABS ENUMERATIONS ====================

class eItemType(IntEnum):
    """Item type enumeration for ETABS API calls."""
    Objects = 0
    Group = 1
    SelectedObjects = 2


class eUnits(IntEnum):
    """Units enumeration for ETABS models."""
    lb_in_F = 1
    lb_ft_F = 2
    kip_in_F = 3
    kip_ft_F = 4
    kN_mm_C = 5
    kN_m_C = 6
    kgf_mm_C = 7
    kgf_m_C = 8
    N_mm_C = 9
    N_m_C = 10
    Ton_mm_C = 11
    Ton_m_C = 12
    kN_cm_C = 13
    kgf_cm_C = 14
    N_cm_C = 15
    Ton_cm_C = 16


class eMatType(IntEnum):
    """Material type enumeration."""
    Steel = 1
    Concrete = 2
    NoDesign = 3
    Aluminum = 4
    ColdFormed = 5
    Rebar = 6
    Tendon = 7


class eMatTypeSteel(IntEnum):
    """Steel material type enumeration."""
    ASTM_A36 = 1
    ASTM_A53_GrB = 2
    ASTM_A500_GrB_Fy42 = 3
    ASTM_A500_GrB_Fy46 = 4
    ASTM_A572_Fy50 = 5
    ASTM_A992_Fy50 = 6
    Chinese_Q345 = 7
    Indian_Fe415 = 8


class eMatTypeConcrete(IntEnum):
    """Concrete material type enumeration."""
    Normal_Weight = 1
    Lightweight = 2


class eFramePropType(IntEnum):
    """Frame property type enumeration."""
    I_WF = 1  # I/Wide Flange
    Channel = 2
    Tee = 3
    Angle = 4
    DblAngle = 5
    Box_Tube = 6
    Pipe = 7
    Rectangular = 8
    Circle = 9
    General = 10


class eShellType(IntEnum):
    """Shell element type enumeration."""
    Shell_Thin = 1
    Shell_Thick = 2
    Plate_Thin = 3
    Plate_Thick = 4
    Membrane = 5


class eSlabType(IntEnum):
    """Slab type enumeration."""
    Drop = 1
    Flat = 2
    Waffle = 3
    Ribbed = 4
    Solid = 5


class eDeckType(IntEnum):
    """Deck type enumeration."""
    Filled = 1
    Unfilled = 2
    SolidSlab = 3


class eWallPropType(IntEnum):
    """Wall property type enumeration."""
    Specified = 1
    AutoSelectList = 2


class eAreaDesignOrientation(IntEnum):
    """Area design orientation enumeration."""
    Default = 1
    User_Defined = 2


class eFrameDesignOrientation(IntEnum):
    """Frame design orientation enumeration."""
    Default = 1
    User_Defined = 2


class eLoadPatternType(IntEnum):
    """Load pattern type enumeration."""
    Dead = 1
    SuperDead = 2
    Live = 3
    Reducible_Live = 4
    Seismic = 5
    Wind = 6
    Snow = 7
    Other = 8


class eLoadCaseType(IntEnum):
    """Load case type enumeration."""
    Linear_Static = 1
    Nonlinear_Static = 2
    Modal_Eigen = 3
    Modal_Ritz = 4
    Response_Spectrum = 5
    Linear_History = 6
    Nonlinear_History = 7
    Linear_Dynamic = 8
    Nonlinear_Dynamic = 9
    Moving_Load = 10
    Buckling = 11
    Steady_State = 12
    Power_Spectral_Density = 13
    Linear_Static_Multistep = 14


class eDesignActionType(IntEnum):
    """Design action type enumeration."""
    No_Check_No_Design = 0
    Check = 1
    Design = 2


class eConstraintType(IntEnum):
    """Constraint type enumeration."""
    Body = 1
    Diaphragm = 2
    Rod = 3
    Beam = 4
    Equal = 5
    Local = 6


class eConstraintAxis(IntEnum):
    """Constraint axis enumeration."""
    Auto = 1
    Local_1 = 2
    Local_2 = 3  
    Local_3 = 4


class eDiaphragmOption(IntEnum):
    """Diaphragm option enumeration."""
    Disconnect = 1
    Connect = 2


class eObjType(IntEnum):
    """Object type enumeration."""
    Point = 1
    Frame = 2
    Cable = 3
    Tendon = 4
    Area = 5
    Solid = 6
    Link = 7


class eItemTypeElm(IntEnum):
    """Element item type enumeration."""
    ObjectElm = 1
    Element = 2
    GroupElm = 3
    SelectionElm = 4


class eReturnCode(IntEnum):
    """Return code enumeration."""
    Success = 0
    Failure = 1


class eForce(IntEnum):
    """Force units enumeration."""
    lb = 1
    kip = 2
    N = 3
    kN = 4
    kgf = 5
    tonf = 6


class eLength(IntEnum):
    """Length units enumeration."""  
    inch = 1
    ft = 2
    mm = 3
    m = 4
    cm = 5


class eTemperature(IntEnum):
    """Temperature units enumeration."""
    F = 1  # Fahrenheit
    C = 2  # Celsius
    K = 3  # Kelvin
    R = 4  # Rankine


class eLinkPropType(IntEnum):
    """Link property type enumeration."""
    Linear = 1
    Damper = 2
    Gap = 3
    Hook = 4
    Plastic_Wen = 5
    Isolator1 = 6
    Isolator2 = 7
    T_C_Friction_Isolator = 8
    Rubber_Isolator = 9
    Friction_Pendulum = 10


class eCNameType(IntEnum):
    """Name type enumeration."""
    LoadCase = 1
    LoadCombo = 2


# ==================== DESIGN PROCEDURE TYPES ====================

class eDesignProcedure(IntEnum):
    """Design procedure type enumeration for SetDesignProcedure."""
    Program_Determined = 0
    Steel_Frame_Design = 1
    Concrete_Frame_Design = 2
    Composite_Beam_Design = 3
    Steel_Joist_Design = 4
    No_Design = 7
    Composite_Column_Design = 13


@dataclass
class ETABSResult:
    """Standard result wrapper for all ETABS operations."""
    success: bool
    operation: str
    data: Optional[Dict[str, Any]] = None
    assigned_name: Optional[str] = None
    errors: List[str] = None
    warnings: List[str] = None
    etabs_raw: Any = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.data is None:
            self.data = {}


@dataclass  
class ETABSPoint:
    """ETABS point object representation."""
    name: str
    x: float
    y: float  
    z: float
    coordinate_system: str = "Global"
    

@dataclass
class ETABSFrame:
    """ETABS frame object representation."""
    name: str
    i_point: str
    j_point: str
    section_property: str
    

@dataclass
class ETABSArea:
    """ETABS area object representation."""
    name: str
    points: List[str]
    area_property: str
