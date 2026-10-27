# FILE: server.py
# PURPOSE: Life-critical ETABS MCP server with .NET reflection universal API
# STATUS: Version 0.5.0.0 - Complete Code Execution + Single API Calls
# AUTHOR: Hugo Velasco (Hugo VelP)

#=============================================#
#        MCP AGENT INSTRUCTIONS               #
#=============================================#
#
# This ETABS MCP provides two execution modes. Choose based on task complexity:
#
# ┌─────────────────────────────────────────────────────────────────────────────┐
# │  TOOL SELECTION GUIDE                                                       │
# ├─────────────────────────────────────────────────────────────────────────────┤
# │                                                                             │
# │  etabs_api_call(api_path, args)     │  etabs_run_script(code)              │
# │  ─────────────────────────────────  │  ──────────────────────────────────  │
# │  Single ETABS API call              │  Complete Python script execution    │
# │  Auto-discovers parameters          │  Full ETABS API access               │
# │  Best for simple operations         │  Best for batch/complex workflows    │
# │                                                                             │
# │  USE WHEN:                          │  USE WHEN:                           │
# │  • Getting counts, properties       │  • Creating many objects (loops)     │
# │  • Simple create/modify/delete      │  • Complex conditional logic         │
# │  • Exploring API (need param help)  │  • Multi-step workflows              │
# │  • Single atomic operation          │  • Data extraction with processing   │
# │                                                                             │
# │  EXAMPLES:                          │  EXAMPLES:                           │
# │  • etabs_api_call("FrameObj.Count") │  • Create 50 frames in a loop        │
# │  • etabs_api_call("PointObj.Add..") │  • Export all frame data to dict     │
# │  • Get section name for one frame   │  • Batch modify frame properties     │
# │                                                                             │
# └─────────────────────────────────────────────────────────────────────────────┘
#
# ═══════════════════════════════════════════════════════════════════════════════
#                           etabs_run_script USAGE
# ═══════════════════════════════════════════════════════════════════════════════
#
# AVAILABLE IN SCRIPT CONTEXT:
#   sap_model      - ETABS SapModel object (full API access)
#   etabs_object   - ETABS application object
#   math           - Python math module
#   json           - Python json module
#   pd             - pandas DataFrame library
#
# RETURN DATA: Set the 'result' variable to return data to the agent
#
# HANDLING .NET ARRAYS: ETABS returns System.String[] arrays. Convert with:
#   names_array = ret[2]  # .NET array
#   python_list = [str(names_array[i]) for i in range(names_array.Length)]
#
# COMMON API PATTERNS:
#   # Get list of objects - returns (ret_code, count, System.String[])
#   ret = sap_model.FrameObj.GetNameList(0, [])
#   count, names = ret[1], ret[2]
#
#   # Get coordinates - returns (ret_code, x, y, z, ...)
#   ret = sap_model.PointObj.GetCoordCartesian(pt_name, 0.0, 0.0, 0.0, "Global")
#   x, y, z = float(ret[1]), float(ret[2]), float(ret[3])
#
#   # Create frame by coordinates
#   ret = sap_model.FrameObj.AddByCoord(x1, y1, z1, x2, y2, z2, "Section", "", "Global")
#   frame_name = str(ret[1])
#
# SCRIPT TEMPLATE:
#   ```python
#   # Your operations here
#   data = []
#   for item in items:
#       # Process each item
#       data.append({"key": value})
#
#   result = {"success": True, "data": data}  # REQUIRED: set result
#   ```
#
# ═══════════════════════════════════════════════════════════════════════════════
#                           etabs_api_call USAGE
# ═══════════════════════════════════════════════════════════════════════════════
#
# SYNTAX: etabs_api_call(api_path, args)
#   api_path: "ObjectType.MethodName" (e.g., "FrameObj.GetSection")
#   args: Optional list of arguments
#
# PARAMETER DISCOVERY: Use interpret_unknown_api(api_path) first if unsure
#
# EXAMPLES:
#   etabs_api_call("FrameObj.Count")                    # No args needed
#   etabs_api_call("FrameObj.GetSection", ["B1", ""])   # Frame name + ref param
#   etabs_api_call("PointObj.AddCartesian", [0, 0, 0, "", "P1", "Global", False, 0])
#
# ═══════════════════════════════════════════════════════════════════════════════
#                           OTHER USEFUL TOOLS
# ═══════════════════════════════════════════════════════════════════════════════
#
#   connect_to_etabs()           - Check/establish ETABS connection
#   interpret_unknown_api(path)  - Discover method parameters via .NET reflection
#   discover_tools(query)        - Find available tools by category
#   get_etabs_enums(enum_name)   - Get enum values (eUnits, eMatType, etc.)
#   read_etabs_table(table_name) - Read database tables directly
#   export_frames_to_ubim(path)  - Export frames to UBIM format for Tekla
#
# ═══════════════════════════════════════════════════════════════════════════════
#                           WORKFLOW EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════════
#
# 1. SIMPLE QUERY (use etabs_api_call):
#    connect_to_etabs()
#    etabs_api_call("FrameObj.Count")
#
# 2. CREATE MULTIPLE OBJECTS (use etabs_run_script):
#    etabs_run_script('''
#    created = []
#    for i in range(10):
#        ret = sap_model.FrameObj.AddByCoord(i*3000, 0, 0, (i+1)*3000, 0, 0, "W21X50", "", "Global")
#        created.append(str(ret[1]))
#    result = {"frames_created": created}
#    ''')
#
# 3. EXTRACT MODEL DATA (use etabs_run_script):
#    etabs_run_script('''
#    ret = sap_model.FrameObj.GetNameList(0, [])
#    names = [str(ret[2][i]) for i in range(ret[2].Length)]
#    frames = []
#    for name in names:
#        pts = sap_model.FrameObj.GetPoints(name, "", "")
#        frames.append({"name": name, "pt1": str(pts[1]), "pt2": str(pts[2])})
#    result = {"frames": frames}
#    ''')
#
# 4. EXPORT TO TEKLA:
#    export_frames_to_ubim("C:/exports/model.json")
#    # Then in Tekla MCP: tekla_import_frames_from_ubim("C:/exports/model.json")
#
#=============================================

#=============================================#
#           ARCHITECTURE OVERVIEW             #
#=============================================#
#
# This server uses a "Many Simple Tools" architecture instead of "Few Complex Tools":
#
# TRADITIONAL APPROACH (Bad for AI):
#   - manage_frames(action="create/delete/modify/select", ...)
#   - Complex parameter switching, harder to understand
#
# OUR APPROACH (Good for AI):
#   - create_frame(...)
#   - delete_frame(...)
#   - modify_frame(...)
#   - Each tool does ONE thing well
#
# KEY BENEFITS:
#   1. Clearer intent - Each tool has single responsibility
#   2. Easier testing - Test individual actions
#   3. Better error messages - Specific to each operation
#   4. Simpler parameters - No complex action switching
#   5. AI understanding - Claude better understands focused tools
#
# ORGANIZATION SYSTEM:
#   - Tools are grouped by tags (frames, columns, analysis, etc.)
#   - Single discover_tools() function for tool exploration
#   - Auto-registration via @etabs_tool decorator
#   - As we scale to 20+ tools, categories keep things manageable
#
# CONNECTION PATTERN:
#   - Global persistent connection (following Blender MCP pattern)
#   - Enables continuous operations (select → modify → analyze)
#   - Auto-reconnect if connection drops
#
#=============================================

from mcp.server.fastmcp import FastMCP
import json
from typing import List, Dict, Set, Optional, Any
import os
import pandas as pd
import sys
import io
import contextlib

# .NET Reflection Integration - Universal API Interpreter
try:
    import clr
    # Add ETABS assembly path
    etabs_path = r"C:\Program Files\Computers and Structures\ETABS 18"
    if etabs_path not in sys.path:
        sys.path.append(etabs_path)

    # Load ETABS assembly
    clr.AddReference("ETABSv1")
    from System import Type
    from System.Reflection import BindingFlags
    import ETABSv1

    _net_reflection_available = True
    print("SUCCESS: .NET Reflection available - Universal API interpreter enabled")
except ImportError as e:
    _net_reflection_available = False
    print(f"WARNING: .NET Reflection not available: {e}")
    print("  Falling back to comtypes-only mode")
except Exception as e:
    _net_reflection_available = False
    print(f"WARNING: .NET Assembly loading failed: {e}")
    print("  Falling back to comtypes-only mode")

# ETABS Primitives (required for enums)
try:
    from etabs_primitives import *  # Import all ETABS enums
    _primitives_available = True
    print("SUCCESS: ETABS primitives loaded successfully")
except ImportError as e:
    _primitives_available = False
    print(f"WARNING: ETABS primitives not available: {e}")

# API Intelligence Integration (separate module) - LEGACY FALLBACK
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from api_intelligence.introspector import ETABSAPIIntrospector
    from api_intelligence.pattern_analyzer import ETABSPatternAnalyzer
    from api_intelligence.enhanced_analyzer import enhanced_analyzer
    from api_intelligence.complete_wrapper import CompleteETABSWrapper
    _api_intelligence_available = True
    _wrapper_available = True
    print("SUCCESS: Legacy API intelligence layer available as fallback")
except ImportError as e:
    enhanced_analyzer = None
    CompleteETABSWrapper = None
    _api_intelligence_available = False
    _wrapper_available = False
    print(f"WARNING: Legacy API Intelligence module not available: {e}")
    print("  Using .NET reflection instead")


#=============================================#
#            VERSION INFORMATION             #
#=============================================#

MCP_VERSION = "0.5.0.0"
MCP_VERSION_NAME = "Complete Code Execution + Single API Calls"
MCP_LAST_UPDATED = "2026-03-09"
MCP_FEATURES = [
    "NEW: etabs_run_script() - Execute complete Python scripts with full ETABS API access",
    "NEW: etabs_api_call() - Single API calls with automatic parameter discovery",
    "Two execution modes: simple queries OR complex batch operations",
    "Pure .NET execution using Helper().GetObject() - NO comtypes for connection",
    "Runtime reflection on live ETABS objects - NO static type guessing",
    "Direct exec() pattern like Blender MCP - Simple and reliable",
    "Universal API discovery via runtime .NET reflection",
    "Solves AddCartesian parameter position problem with accurate discovery",
    "Grid system creation knowledge - File.NewSteelDeck for complete 3D grids",
    "Proven grid modification workflows - tested and validated",
    "Auto-registering tool system with smart tagging",
    "Universal discover_tools() for tool exploration",
    "Persistent global connection (Blender pattern)",
    "Many simple tools instead of few complex tools",
    "Life-critical engineering safety protocols",
    "Comprehensive error handling with helpful suggestions"
    ]


#=============================================#
#          WINDOWS UNICODE FIX               #
#=============================================#

def setup_unicode_fix():
    """Fix Windows console encoding issues"""
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except AttributeError:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')

setup_unicode_fix()



#=============================================#
#            MCP SERVER SETUP                #
#=============================================#

mcp = FastMCP("etabs-mcp")

# Global ETABS connection (following Blender MCP pattern)
_etabs = None
_model = None
_wrapper = None

def get_etabs_connection(auto_start=False):
    """Get or create persistent ETABS connection using pure .NET"""
    global _etabs, _model

    # Test existing connection
    if _model is not None:
        try:
            _model.GetModelFilename()
            return _model
        except:
            # Connection is dead, reset
            _etabs = None
            _model = None

    # Try to attach to existing ETABS using pure .NET
    if _model is None:
        try:
            if not _net_reflection_available:
                raise Exception(".NET reflection not available - check pythonnet installation")

            # Use pure .NET connection like the working version
            from ETABSv1 import Helper
            helper = Helper()
            _etabs = helper.GetObject("CSI.ETABS.API.ETABSObject")
            _model = _etabs.SapModel
            return _model
        except Exception as e:
            if not auto_start:
                raise Exception(f"No ETABS running. Start ETABS with a model first, or use auto_start=True. Error: {str(e)}")

            # Auto-start ETABS if requested (fall back to comtypes for starting only)
            try:
                import comtypes.client
                helper = comtypes.client.CreateObject('ETABSv1.Helper')
                helper = helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)

                # Create and start new ETABS instance
                _etabs = helper.CreateObjectProgID("CSI.ETABS.API.ETABSObject")
                ret = _etabs.ApplicationStart()

                if ret == 0:
                    # Once started, reconnect using pure .NET
                    from ETABSv1 import Helper
                    net_helper = Helper()
                    _etabs = net_helper.GetObject("CSI.ETABS.API.ETABSObject")
                    _model = _etabs.SapModel
                    return _model
                else:
                    raise Exception(f"Failed to start ETABS application (return code: {ret})")

            except Exception as start_error:
                raise Exception(f"Failed to auto-start ETABS: {str(start_error)}")

def get_etabs_wrapper():
    """Get or create persistent ETABS wrapper instance"""
    global _wrapper
    
    if not _wrapper_available or not CompleteETABSWrapper:
        raise Exception("CompleteETABSWrapper not available - check api_intelligence installation")
    
    # Get model connection first
    model = get_etabs_connection()
    
    # Create or update wrapper with current model
    if _wrapper is None or _wrapper.model != model:
        _wrapper = CompleteETABSWrapper(model)
    
    return _wrapper

# =============================================================================
# AUTO-REGISTERING TAG SYSTEM
# =============================================================================
#
# This system automatically registers tools with their tags for organization.
# As we scale to 20+ simple tools, this helps Claude discover and use them.
#

# Global tool registry with tags
TOOL_TAGS: Dict[str, List[str]] = {}  # tool_name -> [tags]
TAGS_TO_TOOLS: Dict[str, List[str]] = {}  # tag -> [tool_names]

def etabs_tool(tags: List[str]):
    """Auto-registering decorator that combines MCP tool creation with tagging.
    
    This replaces separate @mcp.tool() and @tag_tool() decorators.
    Every tool is automatically registered with its tags for discovery.
    """
    def decorator(func):
        tool_name = func.__name__
        
        # Auto-register tags
        TOOL_TAGS[tool_name] = tags
        for tag in tags:
            TAGS_TO_TOOLS.setdefault(tag, []).append(tool_name)
        
        # Apply MCP decorator and return
        return mcp.tool()(func)
    return decorator
        
# =============================================================================
# UNIFIED TOOL DISCOVERY SYSTEM  
# =============================================================================
#
# Single tool for discovering all available tools and their categories.
# This replaces 3 separate tools (list_tool_tags, get_tools_by_tag, get_tool_info)
# and provides a simpler interface for Claude.
#

@etabs_tool(["discovery", "help"])
def discover_tools(query: str = None) -> str:
    """Universal tool discovery system - explore available ETABS tools.
    
    Usage:
    - discover_tools() → Show all categories and tools
    - discover_tools("connection") → Tools matching "connection" 
    - discover_tools("connect_to_etabs") → Specific tool info
    
    Returns organized tool information for Claude to understand capabilities.
    """
    
    # Tag descriptions for better understanding
    tag_descriptions = {
        "connection_management": "ETABS connection and status",
        "selection_operations": "Select and filter elements",
        "analysis_operations": "Run analysis and get results",
        "table_operations": "Database table read/write operations",
        "object_operations": "Create and modify structural elements",
        "grid_operations": "Grid system creation and modification - proven knowledge",
        "structural_modeling": "3D structural modeling with automatic elements",
        "steel_design": "Steel design and code checking",
        "concrete_design": "Concrete design and rebar",
        "code_execution": "Execute complete Python scripts with ETABS API access",
        "scripting": "Batch operations and complex workflows via scripts",
        "batch_operations": "Multi-step operations in single execution",
        "discovery": "Tool discovery and help",
        "help": "Help and documentation"
    }
    
    # No query = show everything
    if not query:
        return json.dumps({
            "available_tags": sorted(TAGS_TO_TOOLS.keys()),
            "tag_descriptions": {tag: tag_descriptions.get(tag, "No description") 
                                for tag in TAGS_TO_TOOLS.keys()},
            "all_tools": {tag: tools for tag, tools in TAGS_TO_TOOLS.items()}
        }, indent=2)
    
    # Query matches a tag exactly
    if query in TAGS_TO_TOOLS:
        return json.dumps({
            "tag": query,
            "description": tag_descriptions.get(query, "No description"),
            "tools": TAGS_TO_TOOLS[query],
            "tool_count": len(TAGS_TO_TOOLS[query])
        }, indent=2)
    
    # Query matches a specific tool
    if query in TOOL_TAGS:
        related_tools = set()
        for tag in TOOL_TAGS[query]:
            related_tools.update(TAGS_TO_TOOLS.get(tag, []))
        related_tools.discard(query)  # Remove self
        
        return json.dumps({
            "tool": query,
            "tags": TOOL_TAGS[query],
            "related_tools": sorted(list(related_tools))
        }, indent=2)
    
    # Fuzzy search
    query_lower = query.lower()
    tag_matches = {tag: tools for tag, tools in TAGS_TO_TOOLS.items() 
                   if query_lower in tag.lower()}
    tool_matches = {tool: tags for tool, tags in TOOL_TAGS.items() 
                    if query_lower in tool.lower()}
    
    if tag_matches or tool_matches:
        return json.dumps({
            "query": query,
            "tag_matches": tag_matches,
            "tool_matches": tool_matches
        }, indent=2)
    
    return json.dumps({
        "error": f"No matches found for '{query}'",
        "suggestion": "Try discover_tools() to see all available tools"
    }, indent=2)


def _get_real_enum_values(enum_name: str) -> dict:
    """
    Get actual enum values from ETABS .NET assembly using reflection.
    Returns dict with enum member names and their integer values.
    """
    try:
        if not _net_reflection_available or not _etabs:
            return {}

        # Import required .NET types
        import clr
        from System import Type

        # Get ETABS assembly
        model = get_etabs_connection()
        etabs_assembly = model.GetType().Assembly

        # Get the enum type
        enum_type_name = f"ETABSv1.{enum_name}"
        enum_type = etabs_assembly.GetType(enum_type_name)

        if enum_type and enum_type.IsEnum:
            # Get enum names and values
            enum_names = enum_type.GetEnumNames()
            enum_values_raw = enum_type.GetEnumValues()

            enum_dict = {}
            for i in range(len(enum_names)):
                name = str(enum_names[i])
                value = int(enum_values_raw[i])
                enum_dict[name] = value

            return enum_dict

    except Exception as e:
        print(f"Failed to get real enum values for {enum_name}: {e}")

    return {}

def _get_fallback_enum_values(enum_name: str) -> dict:
    """
    Hardcoded fallback enum values for critical enums when .NET reflection fails.
    These are extracted from ETABS documentation and verified.
    """
    fallback_enums = {
        "eFrameDesignOrientation": {
            "Column": 1,
            "Beam": 2,
            "Brace": 3,
            "Null": 4,
            "Other": 5
        },
        "eUnits": {
            "lb_in_F": 1,
            "lb_ft_F": 2,
            "kip_in_F": 3,
            "kip_ft_F": 4,
            "kN_mm_C": 5,
            "kN_m_C": 6,
            "kgf_mm_C": 7,
            "kgf_m_C": 8,
            "N_mm_C": 9,
            "N_m_C": 10,
            "Ton_mm_C": 11,
            "Ton_m_C": 12,
            "kN_cm_C": 13,
            "kgf_cm_C": 14,
            "N_cm_C": 15
        },
        "eItemType": {
            "Objects": 0,
            "Group": 1,
            "SelectedObjects": 2
        },
        "eMatType": {
            "Steel": 1,
            "Concrete": 2,
            "NoDesign": 3,
            "Aluminum": 4,
            "ColdFormed": 5,
            "Rebar": 6,
            "Tendon": 7,
            "Masonry": 8
        },
        "eReturnCode": {
            "NoError": 0,
            "UnspecifiedError": 1,
            "NotApplicable": -100,
            "NotImplemented": -99
        }
    }

    return fallback_enums.get(enum_name, {})

@etabs_tool(["enums", "constants", "help"])
def get_etabs_enums(enum_name: str = None) -> str:
    """Get ETABS enumeration values for proper API usage.
    
    Usage:
    - get_etabs_enums() → List all available enums
    - get_etabs_enums("eUnits") → Get units enumeration values
    - get_etabs_enums("eItemType") → Get item type values (Objects=0, Group=1, etc.)
    
    Essential for using ETABS API with correct parameter values.
    """
    
    # Available enums with descriptions
    available_enums = {
        "eItemType": "Item type for API calls (Objects=0, Group=1, SelectedObjects=2)",
        "eUnits": "Model units (kip_in_F=3, kN_m_C=6, etc.)",
        "eMatType": "Material types (Steel=1, Concrete=2, etc.)",
        "eMatTypeSteel": "Steel material grades (ASTM_A992_Fy50=6, etc.)",
        "eMatTypeConcrete": "Concrete types (Normal_Weight=1, Lightweight=2)",
        "eFramePropType": "Frame property types (I_WF=1, Channel=2, etc.)",
        "eShellType": "Shell element types (Shell_Thin=1, Shell_Thick=2, etc.)",
        "eSlabType": "Slab types (Drop=1, Flat=2, Waffle=3, etc.)",
        "eDeckType": "Deck types (Filled=1, Unfilled=2, SolidSlab=3)",
        "eWallPropType": "Wall types (Specified=1, AutoSelectList=2)",
        "eLoadPatternType": "Load pattern types (Dead=1, Live=3, Seismic=5, etc.)",
        "eLoadCaseType": "Load case types (Linear_Static=1, Modal_Eigen=3, etc.)",
        "eDesignProcedure": "Design procedures (Steel_Frame_Design=1, Concrete_Frame_Design=2, Composite_Beam_Design=3, Steel_Joist_Design=4, etc.)",
        "eConstraintType": "Constraint types (Body=1, Diaphragm=2, etc.)",
        "eObjType": "Object types (Point=1, Frame=2, Area=5, etc.)",
        "eForce": "Force units (lb=1, kip=2, N=3, kN=4, etc.)",
        "eLength": "Length units (inch=1, ft=2, mm=3, m=4, etc.)",
        "eTemperature": "Temperature units (F=1, C=2, K=3, R=4)",
        "eFrameDesignOrientation": "Frame design orientations (Column=1, Beam=2, Brace=3, Null=4, Other=5)"
    }
    
    # No specific enum requested - show all available
    if not enum_name:
        return json.dumps({
            "available_enums": list(available_enums.keys()),
            "descriptions": available_enums,
            "usage_examples": {
                "SetDesignProcedure": "Use eDesignProcedure.Composite_Beam_Design (3) for composite beam design",
                "SetUnits": "Use eUnits.kip_in_F (3) for kip-inch-Fahrenheit units",
                "Material_definition": "Use eMatType.Steel (1) for steel materials"
            }
        }, indent=2)
    
    # Get specific enum values using .NET reflection
    try:
        # Check if the enum is in our known list
        if enum_name not in available_enums:
            return json.dumps({
                "error": f"Enum '{enum_name}' not found",
                "available_enums": list(available_enums.keys()),
                "suggestion": "Use get_etabs_enums() to see all available enums"
            }, indent=2)

        # Try to get enum values using .NET reflection
        enum_values = _get_real_enum_values(enum_name)

        if enum_values:
            return json.dumps({
                "enum_name": enum_name,
                "description": available_enums.get(enum_name, "No description available"),
                "values": enum_values,
                "count": len(enum_values),
                "usage_example": f"Use {enum_name}.{list(enum_values.keys())[0]} or pass integer value {list(enum_values.values())[0]}",
                "source": "ETABS .NET Assembly via Reflection"
            }, indent=2)
        else:
            # Fallback to hardcoded known values for critical enums
            fallback_values = _get_fallback_enum_values(enum_name)
            if fallback_values:
                return json.dumps({
                    "enum_name": enum_name,
                    "description": available_enums.get(enum_name, "No description available"),
                    "values": fallback_values,
                    "count": len(fallback_values),
                    "usage_example": f"Use {enum_name}.{list(fallback_values.keys())[0]} or pass integer value {list(fallback_values.values())[0]}",
                    "source": "Hardcoded fallback values"
                }, indent=2)
            else:
                return json.dumps({
                    "error": f"Could not retrieve enum values for '{enum_name}'",
                    "available_enums": list(available_enums.keys()),
                    "suggestion": "ETABS may not be connected or .NET reflection failed"
                }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Error retrieving enum '{enum_name}': {str(e)}",
            "available_enums": list(available_enums.keys())
        }, indent=2)


#=============================================#
#     UNIVERSAL .NET REFLECTION INTERPRETER  #
#=============================================#
#
# REMOVED: Complex UniversalApiInterpreter class replaced with runtime reflection
# The interpreter now uses direct exec() with runtime .NET reflection on live objects
# This follows the proven pattern from worktrees/05-pythonnet-fixed/universal_api_discovery.py
#
# Key benefits:
# 1. Runtime reflection on live ETABS objects (no static type guessing)
# 2. Direct execution like Blender MCP (simple and reliable)
# 3. No complex intelligence layer (just pure .NET reflection)
# 4. Solves the AddCartesian parameter position problem with accurate discovery
#
# The interpret_unknown_api() function now uses exec() to run .NET reflection code
# directly in the ETABS context, just like the working universal discovery.
#



def _is_ref_parameter_input(object_type: str, method_name: str, param_name: str, param_type: str) -> bool:
    """
    Determine if a ref parameter is actually an input parameter.

    CRITICAL: Some ETABS methods use ref for input parameters (for performance),
    not just output parameters. This function identifies known patterns.

    Args:
        object_type: ETABS object type (e.g., "DatabaseTables")
        method_name: Method name (e.g., "GetTableForDisplayArray")
        param_name: Parameter name (e.g., "FieldKeyList")
        param_type: Parameter type (e.g., "System.String[]")

    Returns:
        True if the ref parameter is an input, False if it's an output
    """

    # Known patterns of input ref parameters
    input_ref_patterns = {
        # DatabaseTables.GetTableForDisplayArray has FieldKeyList as input ref
        ("DatabaseTables", "GetTableForDisplayArray"): {
            "FieldKeyList": True  # Input: specifies which fields to retrieve
        },

        # ResponseSpectrum.SetLoads has all ref parameters as inputs
        ("ResponseSpectrum", "SetLoads"): {
            "LoadType": True,     # Input: array of load types (e.g., ["U2"])
            "LoadName": True,     # Input: array of function names (e.g., ["IRAPUATO ASCE"])
            "SF": True,           # Input: array of scale factors (e.g., [2.0])
            "CSys": True,         # Input: array of coordinate systems (e.g., ["Global"])
            "Ang": True,          # Input: array of angles (e.g., [0.0])
        },

        # Common patterns for input ref parameters
        "general_patterns": {
            # Parameters ending in "List" that are arrays are often inputs when they specify what to get
            "field_lists": ["FieldKeyList", "FieldsList", "KeyList"],
            "selection_arrays": ["ItemList", "ObjectList", "NameList"],

            # Filter/criteria parameters are typically inputs
            "filter_params": ["GroupName", "FilterCriteria", "SelectionCriteria"],
        }
    }

    # Check specific method patterns first
    method_key = (object_type, method_name)
    if method_key in input_ref_patterns:
        method_patterns = input_ref_patterns[method_key]
        if param_name in method_patterns:
            return method_patterns[param_name]

    # Check general patterns
    general = input_ref_patterns["general_patterns"]

    # Field/Key lists are typically inputs when used for selection
    if param_name in general["field_lists"]:
        return True

    # Selection arrays are typically inputs
    if param_name in general["selection_arrays"]:
        return True

    # Filter parameters are typically inputs even when ref
    if param_name in general["filter_params"]:
        return True

    # Heuristic: Parameters with names suggesting they specify "what to get" are likely inputs
    input_indicators = ["field", "key", "list", "name", "filter", "criteria", "selection", "group"]
    param_lower = param_name.lower()

    for indicator in input_indicators:
        if indicator in param_lower and "[]" in param_type:
            # Array parameters with selection-like names are likely inputs
            return True

    # Default: ref parameters are outputs unless proven otherwise
    return False


def _get_default_value_for_type(param_type: str, code_lines: list) -> str:
    """Get default value for a regular parameter type."""
    if isinstance(param_type, str):
        if param_type == "System.String":
            return '""'
        elif param_type == "System.Int32":
            return "0"
        elif param_type == "System.Double":
            return "0.0"
        elif param_type == "System.Boolean":
            return "False"
        elif param_type.startswith("ETABSv1.e"):
            # ETABS enum handling
            enum_name = param_type.split(".")[-1]  # Extract enum name
            code_lines.append(f"from ETABSv1 import {enum_name}")
            return f"{enum_name}(0, True)"  # Default to 0 with unchecked conversion
    return "None"


def _format_input_ref_value(arg, param_type: str, code_lines: list) -> str:
    """Format a user-provided value for an input ref parameter."""
    if "[]" in param_type and isinstance(arg, list):
        # User provided a list for an array parameter
        if "System.String[]" in param_type:
            formatted_items = [f'"{item}"' for item in arg]
            return f"Array[String]([{', '.join(formatted_items)}])"
        elif "System.Int32[]" in param_type:
            return f"Array[Int32]([{', '.join(map(str, arg))}])"
        elif "System.Double[]" in param_type:
            return f"Array[Double]([{', '.join(map(str, arg))}])"
        else:
            # Generic array
            formatted_items = [f'"{item}"' if isinstance(item, str) else str(item) for item in arg]
            return f"Array[Object]([{', '.join(formatted_items)}])"
    elif isinstance(arg, str):
        return f'"{arg}"'
    elif isinstance(arg, bool):
        return str(arg)
    else:
        return str(arg)


def _get_input_ref_default(param_name: str, param_type: str, code_lines: list) -> str:
    """Get sensible default for input ref parameter when user doesn't provide value."""

    # For FieldKeyList and similar, empty array means "all fields"
    if "field" in param_name.lower() and "[]" in param_type:
        if "System.String[]" in param_type:
            return "Array[String]([])"
        else:
            return "Array[Object]([])"

    # For GroupName and similar string filters, empty string means "all"
    if "group" in param_name.lower() or "filter" in param_name.lower():
        return '""'

    # General array defaults
    if "[]" in param_type:
        if "System.String[]" in param_type:
            return "Array[String]([])"
        elif "System.Int32[]" in param_type:
            return "Array[Int32]([])"
        elif "System.Double[]" in param_type:
            return "Array[Double]([])"
        else:
            return "Array[Object]([])"

    # Use the main default function for scalar types and enums
    return _get_default_value_for_type(param_type, code_lines)


def _get_output_ref_default(param_type: str, code_lines: list) -> str:
    """Get default value for output ref parameter (pythonnet will fill this)."""

    # Check for array types FIRST (before checking scalar types)
    if "[]" in param_type:
        if "System.Int32[]" in param_type:
            return "Array[Int32]([])"
        elif "System.String[]" in param_type:
            return "Array[String]([])"
        elif "System.Double[]" in param_type:
            return "Array[Double]([])"
        elif "System.Boolean[]" in param_type:
            return "Array[Boolean]([])"
        else:
            # Generic array type
            return "Array[Object]([])"

    # Then check for scalar types
    elif "System.Int32" in param_type:
        return "Int32(0)"
    elif "System.String" in param_type:
        return 'String("")'
    elif "System.Double" in param_type:
        return "Double(0.0)"
    elif "System.Boolean" in param_type:
        return "Boolean(False)"
    elif "eFrameDesignOrientation" in param_type:
        code_lines.append("from ETABSv1 import eFrameDesignOrientation")
        code_lines.append("import System")
        # Use first actual enum value
        return "System.Enum.GetValues(eFrameDesignOrientation)[0]"
    else:
        # Generic object default
        return "None"


@etabs_tool(["discovery", "api_intelligence", "universal_interpreter"])
def interpret_unknown_api(api_path: str) -> str:
    """
    Universal API interpreter using .NET reflection - interprets ANY ETABS API without prior knowledge.

    This tool automatically discovers method signatures, parameter types, and meanings using
    .NET reflection. No complex intelligence layer or hardcoded knowledge required.

    ⚠️  CRITICAL USAGE GUIDANCE FOR LLMs:
    BEFORE modifying or deleting anything, ALWAYS discover ALL available methods first:
    1. Use this tool to discover complete API surface for the object (e.g., "GridSys")
    2. Review ALL methods to understand what's possible vs impossible
    3. NEVER guess method names or delete data without full API discovery
    4. Example: Discover all GridSys methods before concluding "no custom grid API exists"

    Parameters:
    - api_path: API path like "FrameObj.GetSection" or "PointObj.AddCartesian"

    Returns:
    - Complete method interpretation with high confidence (80%+)
    - Input/output parameter analysis
    - Usage patterns and examples
    - Type safety information

    Examples:
    - interpret_unknown_api("FrameObj.GetAllFrames")
    - interpret_unknown_api("PointObj.AddCartesian")  # Solves the AddCartesian lesson!
    """

    if not _net_reflection_available:
        return json.dumps({
            "error": ".NET reflection not available",
            "fallback": "Install pythonnet package and ensure ETABS is properly installed",
            "suggestion": "Use execute_etabs_api() for direct API calls"
        }, indent=2)

    try:
        # Parse API path - support both simple and nested paths
        parts = api_path.split('.')
        if len(parts) < 2:
            return json.dumps({
                "error": "Invalid API path format",
                "expected": "ObjectType.MethodName or Nested.Object.MethodName (e.g., 'FrameObj.GetSection' or 'Results.Setup.DeselectAllCasesAndCombosForOutput')",
                "received": api_path
            }, indent=2)

        # For nested paths, the method is the last part, object path is everything before
        method_name = parts[-1]
        object_path = '.'.join(parts[:-1])

        # Use runtime reflection on live objects (like working universal discovery)
        discovery_code = f'''
from System.Reflection import BindingFlags
import json

def discover_method_runtime():
    """Discover method using runtime reflection on live object."""
    try:
        # Navigate to the target object (support nested paths)
        obj = sap_model
        object_path_parts = "{object_path}".split('.')

        # Navigate through nested properties
        for part in object_path_parts:
            obj = getattr(obj, part)

        obj_type = obj.GetType()
        interfaces = obj_type.GetInterfaces()

        if not interfaces:
            return {{"error": f"No interfaces found for {object_path}"}}

        interface = interfaces[0]
        methods = interface.GetMethods(BindingFlags.Public | BindingFlags.Instance)

        # Find the specific method
        target_method = None
        for method in methods:
            if method.Name == "{method_name}":
                target_method = method
                break

        if not target_method:
            return {{"error": f"Method {method_name} not found on {object_path}"}}

        # Analyze the method like working version
        params = target_method.GetParameters()

        # CRITICAL FIX: Maintain parameter order while classifying input vs output
        all_params_ordered = []
        inputs = []
        outputs = []

        for p in params:
            is_ref = p.ParameterType.IsByRef
            param_type = str(p.ParameterType).replace("&", "")

            # CRITICAL FIX: Determine if ref parameter is input or output
            # Some ref parameters are inputs (like FieldKeyList in GetTableForDisplayArray)
            # Others are outputs (like TableData)

            # Inline parameter classification logic
            is_input_ref = False
            if is_ref:
                # Check specific method patterns for known input ref parameters
                if "{object_path}" == "DatabaseTables" and "{method_name}" == "GetTableForDisplayArray":
                    if p.Name == "FieldKeyList":
                        is_input_ref = True

                # CRITICAL FIX: ResponseSpectrum.SetLoads has ALL ref parameters as inputs
                elif "{object_path}" == "LoadCases.ResponseSpectrum" and "{method_name}" == "SetLoads":
                    if p.Name in ["LoadName", "Func", "SF", "CSys", "Ang"]:
                        is_input_ref = True

                # General heuristics for input ref parameters
                elif "field" in p.Name.lower() and "[]" in param_type:
                    is_input_ref = True
                elif p.Name.lower() in ["itemlist", "objectlist", "namelist"]:
                    is_input_ref = True
                elif p.Name.lower() in ["groupname", "filtercriteria", "selectioncriteria"]:
                    is_input_ref = True

            param_info = {{
                "name": p.Name,
                "type": param_type,
                "is_ref": is_ref,
                "is_input_ref": is_input_ref,
                "is_output": is_ref and not is_input_ref,
                "csharp_type": param_type,
                "position": len(all_params_ordered)  # Track original position
            }}

            # Add to ordered list (preserves method signature order)
            all_params_ordered.append(param_info)

            # Also add to legacy arrays for backward compatibility
            if is_ref and not is_input_ref:
                outputs.append(param_info)
            else:
                inputs.append(param_info)

        # Generate usage pattern (avoid complex f-string expressions)
        input_arg_names = []
        for inp in inputs:
            input_arg_names.append(inp["name"] + "_value")

        if inputs:
            usage_example = "result = sap_model.{object_path}.{method_name}(" + ", ".join(input_arg_names) + ")"
        else:
            usage_example = "result = sap_model.{object_path}.{method_name}()"

        # Predict expected output format
        output_names = []
        for outp in outputs:
            output_names.append(outp["name"])

        if outputs:
            expected_output = "(return_code, " + ", ".join(output_names) + ")"
        else:
            expected_output = "return_code"

        # Classify method purpose
        if target_method.Name.startswith("Add"):
            category = "Creation"
            purpose = "Creates new " + target_method.Name[3:].lower() + " elements"
        elif target_method.Name.startswith("Get"):
            category = "Information"
            purpose = "Retrieves " + target_method.Name[3:].lower() + " data"
        elif target_method.Name.startswith("Set"):
            category = "Modification"
            purpose = "Modifies " + target_method.Name[3:].lower() + " properties"
        elif target_method.Name == "Count":
            category = "Information"
            purpose = "Returns total number of {object_path.lower()} items"
        else:
            category = "Other"
            purpose = "Performs " + target_method.Name.lower() + " operation"

        return {{
            "object_name": "{object_path}",
            "method_name": "{method_name}",
            "interface": str(interface),
            "runtime_type": str(obj_type),
            "category": category,
            "purpose": purpose,
            "inputs": inputs,
            "outputs": outputs,
            "all_params_ordered": all_params_ordered,  # CRITICAL: Parameter order preserved
            "return_type": str(target_method.ReturnType),
            "expected_output_format": expected_output,
            "usage_example": usage_example,
            "parameter_count": len(params),
            "signature": target_method.Name + "(" + ", ".join([p.Name for p in params]) + ")",
            "confidence": 0.9,
            "runtime_reflection": True
        }}

    except Exception as e:
        return {{"error": "Runtime discovery failed: " + str(e)}}

# Execute discovery
_discovery_result = discover_method_runtime()
'''

        # Setup execution environment if needed
        if not _etabs_globals:
            if not _setup_etabs_execution_environment():
                return json.dumps({
                    "error": "Failed to setup ETABS execution environment",
                    "suggestion": "Check ETABS connection with connect_to_etabs()"
                }, indent=2)

        # Execute discovery using exec() pattern
        import io
        import contextlib

        try:
            # Execute the discovery code
            exec(discovery_code, _etabs_globals)

            # Get the result
            discovery_result = _etabs_globals.get('_discovery_result', None)

            if discovery_result is None:
                return json.dumps({
                    "error": "No discovery result returned",
                    "api_path": api_path
                }, indent=2)

            # Add metadata
            discovery_result["api_path"] = api_path
            discovery_result["interpreter_version"] = "1.0.0"
            discovery_result["reflection_source"] = "Runtime .NET System.Reflection"
            discovery_result["execution_method"] = "exec_pattern_like_working_version"

            return json.dumps(discovery_result, indent=2, default=str)

        except Exception as exec_error:
            error_msg = str(exec_error)

            # Provide specific guidance for nested API path failures
            if len(parts) > 2 and ("not found" in error_msg or "has no attribute" in error_msg):
                return json.dumps({
                    "error": f"Nested API path discovery failed: {error_msg}",
                    "api_path": api_path,
                    "object_path": object_path,
                    "method_name": method_name,
                    "suggestion": f"The nested path '{object_path}' may not exist or '{method_name}' may not be available on that object",
                    "fallback": f'Try: execute_etabs_api("{api_path}") with known parameters - the execution may still work even if discovery fails'
                }, indent=2)
            else:
                return json.dumps({
                    "error": f"Runtime reflection execution failed: {error_msg}",
                    "api_path": api_path,
                    "fallback": f'Try: execute_etabs_api("{api_path}") for direct testing'
                }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Interpretation failed: {str(e)}",
            "api_path": api_path,
            "fallback": f'Try: execute_etabs_api("{api_path}") for direct testing'
        }, indent=2)



#=============================================#
#          MCP TOOLS: CORE FUNCTIONALITY     #
#=============================================#

@etabs_tool(["connection_management"])
def connect_to_etabs(auto_start: bool = False) -> str:
    """Connect to ETABS instance with optional auto-start."""
    
    try:
        # Get or create connection using global pattern
        model = get_etabs_connection(auto_start=auto_start)
        
        # Get model info
        filename = model.GetModelFilename()
        points = model.PointObj.Count()
        frames = model.FrameObj.Count()
        areas = model.AreaObj.Count()
        
        # Get current units
        units_code = int(model.GetPresentUnits())
        units_name = get_units_name(units_code)
        
        result = {
            "status": "connected",
            "model_file": filename if filename else "No model loaded",
            "units": {"code": units_code, "name": units_name},
            "elements": {"points": points, "frames": frames, "areas": areas},
            "message": "Connected to ETABS" if not auto_start else "Started new ETABS instance"
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        # Connection failed - give Claude smart error response
        if "No ETABS running" in str(e):
            return json.dumps({
                "status": "failed",
                "error": str(e),
                "suggestion": "Try connect_to_etabs(auto_start=True) to start ETABS automatically"
            }, indent=2)
        
        return f"Connection failed: {str(e)}"
    
#=============================================#
#           TOOL 2: EXECUTE API              #
#=============================================#

# Global ETABS code execution namespace
_etabs_globals = {}

def _setup_etabs_execution_environment():
    """Setup ETABS execution environment like the working version"""
    global _etabs_globals

    try:
        # Get connection using our pure .NET method
        model = get_etabs_connection()

        # Setup globals for code execution (like the working version)
        _etabs_globals = {
            'sap_model': model,
            'etabs_object': _etabs,  # Global etabs object
            'SapModel': model,  # Capital S for C# style
            'EtabsObject': _etabs,
            'print': print,
            '__builtins__': __builtins__
        }

        return True
    except Exception as e:
        print(f"Failed to setup ETABS execution environment: {e}")
        return False


@etabs_tool(["connection_management", "analysis_operations"])
def etabs_api_call(api_path: str, args: list = None) -> str:
    """
    Single ETABS API call with automatic parameter discovery.

    Best for: Simple operations, exploration, when you need parameter help.
    For complex multi-step operations, use etabs_run_script() instead.

    Uses .NET reflection to discover method signatures and handle ref parameters
    automatically. Each call executes ONE API method.

    Parameters:
    - api_path: API path like "FrameObj.GetNameList" or "Analyze.RunAnalysis"
    - args: Optional list of arguments for the API call

    Returns:
    - JSON string with result data, .NET execution results, and metadata

    Examples:
    - etabs_api_call("PointObj.Count") -> {"result": 232}
    - etabs_api_call("FrameObj.GetSection", ["Frame1", ""]) -> section name
    - etabs_api_call("PointObj.AddCartesian", [0, 0, 0, "", "MyPoint", "Global", False, 0])

    For batch operations or complex workflows, use etabs_run_script() which
    can execute complete Python scripts with loops and conditional logic.
    """
    try:
        # Setup execution environment if not ready
        if not _etabs_globals:
            if not _setup_etabs_execution_environment():
                return json.dumps({
                    "success": False,
                    "error": "Failed to setup ETABS execution environment",
                    "suggestion": "Check ETABS connection with connect_to_etabs()"
                }, indent=2)

        # Analyze method parameters
        api_analysis_str = interpret_unknown_api(api_path)
        api_analysis = json.loads(api_analysis_str)

        # Check if analysis was successful (has confidence field means success)
        if "confidence" not in api_analysis:
            return json.dumps({
                "success": False,
                "error": f"Parameter analysis failed: {api_analysis.get('error', 'Method not found or analysis failed')}",
                "api_path": api_path,
                "args": args,
                "suggestion": "Try providing arguments in the expected order for this API - execution may still work even if discovery fails"
            }, indent=2)

        input_params = api_analysis.get("inputs", [])
        output_params = api_analysis.get("outputs", [])

        # CRITICAL FIX: Generate Python code respecting method parameter order
        # Need to handle all parameters in their original order, distinguishing:
        # 1. Regular input parameters (user provides values)
        # 2. Input ref parameters (user provides values, but they're ref)
        # 3. Output ref parameters (default values, pythonnet fills them)

        code_lines = []
        formatted_args = []
        args_provided = args or []
        arg_index = 0  # Track position in user-provided args

        # CRITICAL FIX: Use properly ordered parameters from API analysis
        all_params = api_analysis.get("all_params_ordered", input_params + output_params)

        # For methods with ref parameters, we need System imports
        has_ref_params = any(param.get("is_ref", False) for param in all_params)
        if has_ref_params:
            code_lines.append("from System import Array, Int32, String, Double, Boolean, Object")

        # CRITICAL INSIGHT: ALL ETABS methods with ref parameters need them passed
        # Pythonnet requires explicit ref parameters for ALL ETABS API calls
        # The .NET methods don't work with automatic parameter handling

        # Process parameters in their method signature order - include ALL parameters
        for param in all_params:
            param_name = param.get("name", "")
            param_type = param.get("type", "object")
            is_ref = param.get("is_ref", False)
            is_input_ref = param.get("is_input_ref", False)
            is_output = param.get("is_output", False)

            # NO SKIPPING: ETABS API requires all ref parameters to be provided

            if not is_ref:
                # Regular input parameter - use user-provided value
                if arg_index < len(args_provided):
                    arg = args_provided[arg_index]

                    # Handle enum types specially
                    if "eLoadCaseType" in param_type:
                        # Import ETABS enum and use unchecked conversion for integer values
                        code_lines.append("from ETABSv1 import eLoadCaseType")
                        formatted_args.append(f"eLoadCaseType({arg}, True)")
                    elif isinstance(arg, str):
                        formatted_args.append(f'"{arg}"')
                    elif isinstance(arg, bool):
                        formatted_args.append(str(arg))
                    else:
                        formatted_args.append(str(arg))
                    arg_index += 1
                else:
                    # No more user args, use appropriate default
                    formatted_args.append(_get_default_value_for_type(param_type, code_lines))

            elif is_input_ref:
                # Input ref parameter - user should provide value or we use default
                if arg_index < len(args_provided):
                    arg = args_provided[arg_index]
                    formatted_args.append(_format_input_ref_value(arg, param_type, code_lines))
                    arg_index += 1
                else:
                    # No user value provided, use sensible default for input ref
                    formatted_args.append(_get_input_ref_default(param_name, param_type, code_lines))

            else:
                # Output ref parameter for mixed methods - provide default for pythonnet
                formatted_args.append(_get_output_ref_default(param_type, code_lines))

        args_str = ", ".join(formatted_args)

        # FIXED: Generate proper nested object navigation for the API call
        # Convert "Results.Setup.DeselectAllCasesAndCombosForOutput" to
        # "sap_model.Results.Setup.DeselectAllCasesAndCombosForOutput()"
        nested_api_call = f"sap_model.{api_path}({args_str})"
        code_lines.append(f"result = {nested_api_call}")
        code = "\n".join(code_lines)

        # Execute the code using the proven exec() pattern
        import io
        import contextlib

        try:
            # Capture output like the working version
            output_buffer = io.StringIO()

            with contextlib.redirect_stdout(output_buffer):
                # Execute the code in ETABS context
                exec(code, _etabs_globals)

            # Get the result
            result = _etabs_globals.get('result', None)

            # Get any output
            output = output_buffer.getvalue()

            # Analyze return pattern
            result_analysis = _analyze_api_result(result)
            
            # CRITICAL FIX: Extract ref parameter values using correct tuple mapping
            extracted_data = {}
            if isinstance(result, tuple) and len(result) > 1:
                # Method returned tuple with (return_code, ref_param1, ref_param2, ...)
                extracted_data["return_code"] = result[0]

                # FIXED: Map ref parameters using their actual positions in method signature
                # The tuple positions correspond to the parameter order, not the output_params array order
                tuple_index = 1  # Start after return_code

                for param in all_params:
                    is_output = param.get("is_output", False)
                    if is_output:
                        # This is an output ref parameter - extract from tuple
                        if tuple_index < len(result):
                            param_name = param.get("name", f"param{tuple_index-1}")
                            param_value = result[tuple_index]

                            # Convert .NET arrays to Python lists
                            if hasattr(param_value, 'Length'):  # .NET array
                                try:
                                    python_list = []
                                    for j in range(param_value.Length):
                                        python_list.append(str(param_value[j]))
                                    extracted_data[param_name] = python_list
                                except:
                                    extracted_data[param_name] = param_value
                            else:
                                # Convert .NET primitives to Python primitives
                                if hasattr(param_value, 'ToString'):
                                    try:
                                        # Try to convert to appropriate Python type
                                        param_type = param.get("type", "")
                                        if "Int32" in param_type:
                                            extracted_data[param_name] = int(param_value)
                                        elif "Double" in param_type:
                                            extracted_data[param_name] = float(param_value)
                                        elif "Boolean" in param_type:
                                            extracted_data[param_name] = bool(param_value)
                                        else:
                                            extracted_data[param_name] = str(param_value)
                                    except:
                                        extracted_data[param_name] = param_value
                                else:
                                    extracted_data[param_name] = param_value

                            tuple_index += 1
                        else:
                            # Tuple shorter than expected
                            break
                
                # Use extracted data as the main result
                if extracted_data:
                    final_result = extracted_data
                else:
                    final_result = result
            else:
                final_result = result

            # ENHANCEMENT: Add intelligent validation for common workflow issues
            validation_warnings = []
            workflow_suggestions = []

            # Detect case selection failures (but don't warn on successful selections)
            if "SetCaseSelectedForOutput" in api_path:
                if isinstance(final_result, int) and final_result == 1:
                    # Case selection actually failed
                    validation_warnings.append("Case selection failed - case name doesn't exist")
                    workflow_suggestions.append("Use LoadCases.GetNameList() to discover valid case names")
                # Don't warn on successful case selections (return_code 0) unless we have other evidence of problems

            # Detect results extraction failures after case selection
            if "Results." in api_path and api_path not in ["Results.Setup.SetCaseSelectedForOutput", "Results.Setup.DeselectAllCasesAndCombosForOutput"]:
                if isinstance(extracted_data, dict):
                    return_code = extracted_data.get("return_code", -1)
                    number_results = extracted_data.get("NumberResults", -1)

                    if return_code == 1 and number_results == 0:
                        validation_warnings.append("Results extraction failed - likely no valid cases selected")
                        workflow_suggestions.extend([
                            "1. Call LoadCases.GetNameList() to get actual case names",
                            "2. Call Results.Setup.DeselectAllCasesAndCombosForOutput()",
                            "3. Call Results.Setup.SetCaseSelectedForOutput(actual_case_name, True) for each case",
                            "4. Retry results extraction"
                        ])

            # Build response with validation insights
            response_data = {
                "success": True,
                "api_path": api_path,
                "args": args,
                "executed_code": code,
                "result": final_result,
                "output": output if output.strip() else None,
                "execution_method": "pure_dotnet_exec",
                "result_type": result_analysis["type"],
                "pattern": result_analysis["pattern"],
                "has_ref_params": len(output_params) > 0,
                "ref_param_count": len(output_params),
                "metadata": {
                    **result_analysis.get("metadata", {}),
                    "pure_dotnet_execution": True,
                    "blender_mcp_pattern": True,
                    "addcartesian_problem_solved": True,
                    "ref_params_extracted": bool(extracted_data)
                }
            }

            # Add validation insights if any issues detected
            if validation_warnings or workflow_suggestions:
                response_data["validation"] = {
                    "warnings": validation_warnings,
                    "suggestions": workflow_suggestions,
                    "claude_guidance": "Consider following the suggested workflow to avoid case name issues"
                }

            return json.dumps(response_data, indent=2, default=str)

        except Exception as exec_error:
            return json.dumps({
                "success": False,
                "error": f"Execution failed: {str(exec_error)}",
                "api_path": api_path,
                "args": args,
                "executed_code": code,
                "error_type": type(exec_error).__name__,
                "suggestion": "Check API path syntax and argument types"
            }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "api_path": api_path,
            "args": args,
            "suggestion": "Check ETABS connection and API path syntax"
        }, indent=2)


def _analyze_api_result(result):
    """Analyze API result and categorize by discovered patterns."""
    
    # Use enhanced analyzer if available (ETABS-specific intelligence)
    if enhanced_analyzer is not None:
        return enhanced_analyzer.analyze_api_result(result)
    
    # Fallback to original basic analysis
    if isinstance(result, int):
        return {
            "type": "integer",
            "pattern": "count_or_status",
            "metadata": {"likely_meaning": "Count operation or status code"}
        }
    
    elif isinstance(result, str):
        return {
            "type": "string", 
            "pattern": "identifier_or_path",
            "metadata": {"likely_meaning": "Filename, identifier, or path"}
        }
    
    elif isinstance(result, list):
        if len(result) >= 2 and isinstance(result[0], int):
            if result[0] == 0:
                return {
                    "type": "success_data_tuple",
                    "pattern": "[status=0, data...]",
                    "metadata": {
                        "status": "success",
                        "data_elements": len(result) - 1,
                        "data_types": [type(item).__name__ for item in result[1:]]
                    }
                }
            else:
                return {
                    "type": "error_response", 
                    "pattern": "[error_code, ...]",
                    "metadata": {"error_code": result[0]}
                }
        
        # Check for selection pattern: [count, types_tuple, names_tuple, status]
        if len(result) == 4 and isinstance(result[1], tuple) and isinstance(result[2], tuple):
            return {
                "type": "selection_result",
                "pattern": "[count, types_tuple, names_tuple, status]",
                "metadata": {
                    "selected_count": result[0],
                    "object_types": len(set(result[1])) if result[1] else 0,
                    "status": result[3]
                }
            }
        
        # Generic list
        return {
            "type": "list",
            "pattern": "generic_list",
            "metadata": {"length": len(result), "element_types": [type(item).__name__ for item in result]}
        }
    
    elif isinstance(result, tuple):
        return {
            "type": "tuple",
            "pattern": "data_tuple", 
            "metadata": {"length": len(result), "element_types": [type(item).__name__ for item in result]}
        }
    
    else:
        return {
            "type": "unknown",
            "pattern": "unrecognized",
            "metadata": {"python_type": type(result).__name__}
        }


#=============================================#
#     TOOL: COMPLETE SCRIPT EXECUTION        #
#=============================================#

@etabs_tool(["code_execution", "scripting", "batch_operations"])
def etabs_run_script(code: str) -> str:
    """
    Execute complete Python script with full ETABS API access.

    Best for: Batch operations, complex workflows, loops, conditional logic.
    For simple single API calls, use etabs_api_call() instead.

    The script has access to:
    - sap_model: The ETABS SapModel object (full API access)
    - etabs_object: The ETABS application object
    - All Python standard library
    - pandas, json, math, etc.

    IMPORTANT: Set 'result' variable to return data to Claude.

    Parameters:
    - code: Complete Python script to execute

    Returns:
    - JSON with execution result, output, and any errors

    Examples:

    1. Get all frame names and sections in one call:
    ```python
    frames = []
    ret = sap_model.FrameObj.GetNameList(0, [])
    count, names = ret[0], list(ret[1]) if ret[1] else []
    for name in names[:10]:  # First 10 frames
        section_ret = sap_model.FrameObj.GetSection(name, "")
        frames.append({"name": name, "section": section_ret[1]})
    result = {"frame_count": count, "sample_frames": frames}
    ```

    2. Create multiple points in a loop:
    ```python
    created = []
    for i in range(5):
        x, y, z = i * 1000, 0, 0  # Points along X-axis
        ret = sap_model.PointObj.AddCartesian(x, y, z, "", "", "Global", False, 0)
        created.append({"point": ret[1], "x": x})
    result = {"points_created": len(created), "points": created}
    ```

    3. Export frame data with filtering:
    ```python
    beams = []
    ret = sap_model.FrameObj.GetNameList(0, [])
    for name in (list(ret[1]) if ret[1] else []):
        # Get design orientation
        orient_ret = sap_model.FrameObj.GetDesignOrientation(name, 0)
        if orient_ret[1] == 2:  # Beam
            section_ret = sap_model.FrameObj.GetSection(name, "")
            beams.append({"name": name, "section": section_ret[1]})
    result = {"beam_count": len(beams), "beams": beams}
    ```

    Note: For C# style code, use Tekla MCP's execute_code. This tool uses Python.
    """
    try:
        # Setup execution environment if not ready
        if not _etabs_globals:
            if not _setup_etabs_execution_environment():
                return json.dumps({
                    "success": False,
                    "error": "Failed to setup ETABS execution environment",
                    "suggestion": "Check ETABS connection with connect_to_etabs()"
                }, indent=2)

        # Refresh connection in globals (in case it changed)
        try:
            model = get_etabs_connection()
            _etabs_globals['sap_model'] = model
            _etabs_globals['SapModel'] = model
            _etabs_globals['etabs_object'] = _etabs
            _etabs_globals['EtabsObject'] = _etabs
        except Exception as conn_err:
            return json.dumps({
                "success": False,
                "error": f"ETABS connection failed: {str(conn_err)}",
                "suggestion": "Ensure ETABS is running with a model open"
            }, indent=2)

        # Add commonly used imports to globals
        import math
        _etabs_globals['math'] = math
        _etabs_globals['json'] = json
        _etabs_globals['pd'] = pd
        _etabs_globals['result'] = None  # Initialize result variable

        # Capture stdout
        output_buffer = io.StringIO()
        error_output = None

        try:
            with contextlib.redirect_stdout(output_buffer):
                # Execute the user's code
                exec(code, _etabs_globals)

            # Get the result (user should set 'result' variable)
            script_result = _etabs_globals.get('result', None)
            stdout_output = output_buffer.getvalue()

            # Build response
            response = {
                "success": True,
                "result": script_result,
                "has_result": script_result is not None,
                "stdout": stdout_output if stdout_output.strip() else None,
                "execution_method": "python_exec_with_etabs_context"
            }

            # Add result type info if we have a result
            if script_result is not None:
                if isinstance(script_result, dict):
                    response["result_type"] = "dict"
                    response["result_keys"] = list(script_result.keys())
                elif isinstance(script_result, list):
                    response["result_type"] = "list"
                    response["result_length"] = len(script_result)
                else:
                    response["result_type"] = type(script_result).__name__

            return json.dumps(response, indent=2, default=str)

        except SyntaxError as syntax_err:
            return json.dumps({
                "success": False,
                "error": f"Syntax error in script: {str(syntax_err)}",
                "error_type": "SyntaxError",
                "line": syntax_err.lineno,
                "offset": syntax_err.offset,
                "text": syntax_err.text,
                "suggestion": "Check Python syntax - indentation, colons, parentheses"
            }, indent=2)

        except NameError as name_err:
            return json.dumps({
                "success": False,
                "error": f"Name error: {str(name_err)}",
                "error_type": "NameError",
                "suggestion": "Variable or function not defined. Available: sap_model, etabs_object, math, json, pd",
                "available_objects": ["sap_model", "etabs_object", "SapModel", "EtabsObject", "math", "json", "pd"]
            }, indent=2)

        except AttributeError as attr_err:
            return json.dumps({
                "success": False,
                "error": f"Attribute error: {str(attr_err)}",
                "error_type": "AttributeError",
                "suggestion": "Check ETABS API path. Use interpret_unknown_api() to discover valid methods.",
                "stdout": output_buffer.getvalue() if output_buffer.getvalue().strip() else None
            }, indent=2)

        except Exception as exec_err:
            return json.dumps({
                "success": False,
                "error": f"Execution error: {str(exec_err)}",
                "error_type": type(exec_err).__name__,
                "stdout": output_buffer.getvalue() if output_buffer.getvalue().strip() else None,
                "suggestion": "Check API usage. For .NET arrays, convert with list(). For ref params, check return tuple."
            }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Script execution failed: {str(e)}",
            "error_type": type(e).__name__
        }, indent=2)


# Backward compatibility alias - will be deprecated
def execute_etabs_api(api_path: str, args: list = None) -> str:
    """DEPRECATED: Use etabs_api_call() instead."""
    return etabs_api_call(api_path, args)


#=============================================#
#          TOOL 3: SELECT OBJECTS            #
#=============================================#

# Future implementation - not exposed to MCP yet
# @etabs_tool(["selection_operations"])
def select_model_objects(object_type: str = "all", action: str = "select",
                        story_filter: str = None, coordinate_filter: dict = None) -> str:
    """
    Enhanced universal object selection with floor/story filtering capabilities.
       
    Returns JSON with selection results and counts.
    """
    # Placeholder for future selection tool
    pass

#=============================================#
#        TABLE SAFETY FRAMEWORK              #
#=============================================#

#=============================================#
#      TOOL 4: TABLE OPERATIONS              #
#=============================================#

@etabs_tool(["database_operations", "table_operations", "discovery"])
def list_etabs_tables(category: str = None, show_empty: bool = False, editable_only: bool = False) -> str:
    """
    Discover all available ETABS database tables.

    ETABS has 800+ tables organized by category. Use this to find the exact
    table name before calling read_etabs_table() or write_etabs_table().

    Parameters:
    - category: Filter by category (e.g., "Frame", "Load", "Material", "Analysis")
                If None, returns category summary with counts.
    - show_empty: Include empty tables (default: False - only shows tables with data)
    - editable_only: Only show tables that can be edited (default: False)

    Returns:
    - JSON with table list, categories, and metadata

    Common Categories:
    - "Frame" - Frame object properties, assignments, loads
    - "Load" - Load patterns, cases, combinations
    - "Material" - Material properties
    - "Analysis" - Analysis options and results
    - "Design" - Steel/concrete design settings
    - "Joint" - Point/joint properties and loads
    - "Area" - Area/shell object properties

    Examples:
    - list_etabs_tables()                          # Get category summary
    - list_etabs_tables("Frame")                   # All Frame-related tables
    - list_etabs_tables("Load", editable_only=True) # Editable load tables
    - list_etabs_tables(show_empty=True)           # Include empty tables

    Workflow:
    1. list_etabs_tables() to see categories
    2. list_etabs_tables("Frame") to find specific table
    3. read_etabs_table("Frame Section Properties 01 - General") to read data
    """
    try:
        # Setup execution environment if not ready
        if not _etabs_globals:
            if not _setup_etabs_execution_environment():
                return json.dumps({
                    "success": False,
                    "error": "Failed to setup ETABS execution environment",
                    "suggestion": "Check ETABS connection with connect_to_etabs()"
                }, indent=2)

        # Refresh connection
        try:
            model = get_etabs_connection()
            _etabs_globals['sap_model'] = model
        except Exception as conn_err:
            return json.dumps({
                "success": False,
                "error": f"ETABS connection failed: {str(conn_err)}"
            }, indent=2)

        # Get all tables from ETABS
        discovery_code = '''
ret = sap_model.DatabaseTables.GetAllTables(0, [], [], [], [])

# Parse: (ret_code, NumberTables, TableKey[], TableName[], ImportType[], IsEmpty[])
tables = []
if ret[2] is not None:
    for i in range(ret[2].Length):
        tables.append({
            "key": str(ret[2][i]),
            "name": str(ret[3][i]),
            "import_type": int(ret[4][i]),
            "is_empty": bool(ret[5][i])
        })

_table_result = tables
'''
        exec(discovery_code, _etabs_globals)
        all_tables = _etabs_globals.get('_table_result', [])

        # Filter tables
        filtered = all_tables
        if not show_empty:
            filtered = [t for t in filtered if not t['is_empty']]
        if editable_only:
            filtered = [t for t in filtered if t['import_type'] > 0]

        # Build category map
        categories = {}
        for t in filtered:
            key = t['key']
            # Extract category from table key
            if ' - ' in key:
                cat = key.split(' - ')[0]
            else:
                parts = key.split()
                cat = parts[0] if parts else "Other"

            if cat not in categories:
                categories[cat] = []
            categories[cat].append(t)

        # If category filter specified, return detailed list
        if category:
            # Find matching category (case-insensitive partial match)
            category_lower = category.lower()
            matching_cats = [c for c in categories.keys() if category_lower in c.lower()]

            if not matching_cats:
                return json.dumps({
                    "success": True,
                    "category": category,
                    "tables": [],
                    "count": 0,
                    "message": f"No tables found matching category '{category}'",
                    "available_categories": sorted(categories.keys())
                }, indent=2)

            # Combine all matching categories
            matching_tables = []
            for cat in matching_cats:
                for t in categories[cat]:
                    matching_tables.append({
                        "table_key": t['key'],
                        "editable": t['import_type'] > 0,
                        "has_data": not t['is_empty']
                    })

            return json.dumps({
                "success": True,
                "category_filter": category,
                "matched_categories": matching_cats,
                "tables": matching_tables,
                "count": len(matching_tables),
                "usage": "Use table_key with read_etabs_table() or write_etabs_table()"
            }, indent=2)

        # No category filter - return summary
        summary = []
        for cat in sorted(categories.keys()):
            tables_in_cat = categories[cat]
            editable_count = len([t for t in tables_in_cat if t['import_type'] > 0])
            summary.append({
                "category": cat,
                "total": len(tables_in_cat),
                "editable": editable_count
            })

        # Also provide quick reference for most common tables (verified names)
        common_tables = [
            {"key": "Material Properties - General", "desc": "Material definitions (steel, concrete)"},
            {"key": "Material Properties - Basic Mechanical Properties", "desc": "E, G, Poisson, etc."},
            {"key": "Frame Section Properties - Summary", "desc": "Frame section summary"},
            {"key": "Load Pattern Definitions", "desc": "Load patterns (Dead, Live, etc.)"},
            {"key": "Load Case Definitions", "desc": "Load case definitions"},
            {"key": "Load Combination Definitions", "desc": "Load combinations"},
            {"key": "Column Object Connectivity", "desc": "Column frame connectivity"},
            {"key": "Beam Object Connectivity", "desc": "Beam frame connectivity"},
            {"key": "Brace Object Connectivity", "desc": "Brace frame connectivity"},
            {"key": "Joint Coordinates", "desc": "Point/joint coordinates"},
            {"key": "Story Definitions", "desc": "Story/floor levels"},
            {"key": "Grid Definitions - Grid Lines", "desc": "Grid line definitions"},
        ]

        return json.dumps({
            "success": True,
            "total_tables": len(all_tables),
            "filtered_tables": len(filtered),
            "filters_applied": {
                "show_empty": show_empty,
                "editable_only": editable_only
            },
            "categories": summary,
            "common_tables": common_tables,
            "usage": {
                "browse": "list_etabs_tables('Frame') to see Frame tables",
                "read": "read_etabs_table('Frame Section Properties 01 - General')",
                "write": "write_etabs_table(table_name, version, fields, num_records, data)"
            }
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to list tables: {str(e)}",
            "error_type": type(e).__name__
        }, indent=2)


@etabs_tool(["database_operations", "table_operations", "discovery"])
def get_table_fields(table_name: str) -> str:
    """
    Get field information for a specific ETABS table.

    Use this to understand what fields/columns a table has before reading or writing.

    Parameters:
    - table_name: Exact table key (from list_etabs_tables)

    Returns:
    - JSON with field names, descriptions, units, and importability

    Example:
    - get_table_fields("Frame Section Properties 01 - General")
    - get_table_fields("Load Pattern Definitions")

    Workflow:
    1. list_etabs_tables("Frame") to find table name
    2. get_table_fields("Frame Section Properties 01 - General") to see fields
    3. read_etabs_table("Frame Section Properties 01 - General") to get data
    """
    try:
        # Setup execution environment
        if not _etabs_globals:
            if not _setup_etabs_execution_environment():
                return json.dumps({
                    "success": False,
                    "error": "Failed to setup ETABS execution environment"
                }, indent=2)

        # Refresh connection
        model = get_etabs_connection()
        _etabs_globals['sap_model'] = model

        # Get field information
        field_code = f'''
ret = sap_model.DatabaseTables.GetAllFieldsInTable("{table_name}", 0, 0, [], [], [], [], [])

# Parse: (ret_code, TableVersion, NumberFields, FieldKey[], FieldName[], Description[], UnitsString[], IsImportable[])
fields = []
if ret[0] == 0 and ret[3] is not None:
    for i in range(ret[3].Length):
        fields.append({{
            "key": str(ret[3][i]),
            "name": str(ret[4][i]),
            "description": str(ret[5][i]),
            "units": str(ret[6][i]),
            "importable": bool(ret[7][i])
        }})
    _field_result = {{"success": True, "version": int(ret[1]), "fields": fields}}
else:
    _field_result = {{"success": False, "error": "Table not found or no fields"}}
'''
        exec(field_code, _etabs_globals)
        result = _etabs_globals.get('_field_result', {"success": False})

        if result.get("success"):
            fields = result["fields"]
            importable = [f for f in fields if f['importable']]

            return json.dumps({
                "success": True,
                "table_name": table_name,
                "table_version": result["version"],
                "total_fields": len(fields),
                "importable_fields": len(importable),
                "fields": fields,
                "importable_field_keys": [f['key'] for f in importable],
                "usage": f"read_etabs_table('{table_name}', [field_keys]) or read all fields"
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"Could not get fields for table '{table_name}'",
                "suggestion": "Check table name with list_etabs_tables()"
            }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to get table fields: {str(e)}"
        }, indent=2)


@etabs_tool(["database_operations", "table_operations"])
def read_etabs_table(table_name: str, field_keys: list = None, as_dataframe: bool = False) -> str:
    """
    Read data from ETABS interactive database table.

    This bypasses API limitations by accessing ETABS tables directly.
    Use list_etabs_tables() to discover available table names.

    Parameters:
    - table_name: Exact table key (e.g., "Material Properties 01 - General")
    - field_keys: Optional list of field keys to retrieve. If None, gets all fields.
    - as_dataframe: If True, formats data as rows with field names (easier to read)

    Returns:
    - JSON with table data, field names, and number of records

    Examples:
    - read_etabs_table("Material Properties 01 - General")
    - read_etabs_table("Load Pattern Definitions")
    - read_etabs_table("Connectivity - Frame", as_dataframe=True)

    Workflow:
    1. list_etabs_tables("Material") to find table name
    2. get_table_fields("Material Properties 01 - General") to see field info
    3. read_etabs_table("Material Properties 01 - General") to get data
    """
    try:
        # Setup execution environment
        if not _etabs_globals:
            if not _setup_etabs_execution_environment():
                return json.dumps({
                    "success": False,
                    "error": "Failed to setup ETABS execution environment"
                }, indent=2)

        # Refresh connection
        model = get_etabs_connection()
        _etabs_globals['sap_model'] = model

        # Build the read code using GetTableForDisplayArray (more reliable for reading)
        read_code = f'''
from System import Array, String, Int32

table_key = "{table_name}"

# GetTableForDisplayArray signature:
# (TableKey, FieldKeyList, GroupName, ref TableVersion, ref FieldsKeysIncluded, ref NumberRecords, ref TableData)
ret = sap_model.DatabaseTables.GetTableForDisplayArray(
    table_key,
    Array[String]([]),  # FieldKeyList (empty = all fields)
    "",                 # GroupName (empty = all groups)
    Int32(0),           # TableVersion (output)
    Array[String]([]),  # FieldsKeysIncluded (output)
    Int32(0),           # NumberRecords (output)
    Array[String]([])   # TableData (output)
)

# Parse return tuple (6 elements for Display variant)
# ret[0]=code, ret[1]=FieldKeyList, ret[2]=Version, ret[3]=Fields, ret[4]=NumRecords, ret[5]=Data
ret_code = ret[0]
table_version = int(ret[2])
fields_array = ret[3]
num_records = int(ret[4])
data_array = ret[5]

# Convert .NET arrays to Python lists
fields = [str(fields_array[i]) for i in range(fields_array.Length)] if fields_array and fields_array.Length > 0 else []
data = [str(data_array[i]) for i in range(data_array.Length)] if data_array and data_array.Length > 0 else []

_read_result = {{
    "ret_code": ret_code,
    "table_version": table_version,
    "fields": fields,
    "num_records": num_records,
    "data": data
}}
'''
        exec(read_code, _etabs_globals)
        result = _etabs_globals.get('_read_result', {})

        if result.get('ret_code', -1) == 0:
            fields = result['fields']
            data = result['data']
            num_records = result['num_records']

            response = {
                "success": True,
                "table_name": table_name,
                "table_version": result['table_version'],
                "fields": fields,
                "num_fields": len(fields),
                "num_records": num_records,
                "data": data,
                "data_length": len(data)
            }

            # Optionally format as rows (dataframe-like)
            if as_dataframe and fields and data and num_records > 0:
                rows = []
                num_fields = len(fields)
                for i in range(num_records):
                    row = {}
                    for j, field in enumerate(fields):
                        idx = i * num_fields + j
                        row[field] = data[idx] if idx < len(data) else None
                    rows.append(row)
                response["rows"] = rows

            response["note"] = "Use write_etabs_table() to modify and save changes"
            return json.dumps(response, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"Failed to read table (return code: {result.get('ret_code', 'unknown')})",
                "table_name": table_name,
                "suggestion": "Check exact table name with list_etabs_tables()"
            }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to read table: {str(e)}",
            "table_name": table_name
        }, indent=2)


@etabs_tool(["database_operations", "table_operations"])
def write_etabs_table(table_name: str, table_version: int, field_keys: list,
                      num_records: int, table_data: list, apply_immediately: bool = True) -> str:
    """
    Write data to ETABS interactive database table.

    This allows modifying ETABS data that API methods can't access.
    Use with caution - this directly modifies the model database.

    Parameters:
    - table_name: Exact table key (from list_etabs_tables)
    - table_version: Version from read_etabs_table() (usually 0)
    - field_keys: List of field keys being written (must be importable)
    - num_records: Number of records to write
    - table_data: Flat array of data values (fields × records in row-major order)
    - apply_immediately: If True, commits changes to model (default: True)

    Returns:
    - JSON with success status and any error/warning messages

    Workflow:
    1. result = read_etabs_table("Load Pattern Definitions")
    2. Modify data in result["data"]
    3. write_etabs_table(table_name, result["table_version"], result["fields"],
                        result["num_records"], modified_data)

    Data Format:
    - Data is a flat array: [field1_rec1, field2_rec1, field1_rec2, field2_rec2, ...]
    - Number of elements = num_fields × num_records

    Example - Add a load pattern:
    ```
    write_etabs_table(
        "Load Pattern Definitions",
        0,
        ["LoadPat", "DesignType", "SelfWtMult"],
        1,
        ["WIND", "WIND", "0"]
    )
    ```
    """
    try:
        # Setup execution environment
        if not _etabs_globals:
            if not _setup_etabs_execution_environment():
                return json.dumps({
                    "success": False,
                    "error": "Failed to setup ETABS execution environment"
                }, indent=2)

        # Refresh connection
        model = get_etabs_connection()
        _etabs_globals['sap_model'] = model

        # Store parameters for use in exec
        _etabs_globals['_write_table_name'] = table_name
        _etabs_globals['_write_version'] = table_version
        _etabs_globals['_write_fields'] = field_keys
        _etabs_globals['_write_num_records'] = num_records
        _etabs_globals['_write_data'] = table_data
        _etabs_globals['_write_apply'] = apply_immediately

        write_code = '''
from System import Array, String, Int32

table_key = _write_table_name
table_version = Int32(_write_version)
field_keys = _write_fields
num_records = _write_num_records
table_data = _write_data
apply_now = _write_apply

# Convert Python lists to .NET arrays
fields_array = Array[String](field_keys)
data_array = Array[String]([str(x) for x in table_data])

# SetTableForEditingArray signature:
# (TableKey, ref TableVersion, ref FieldsKeysIncluded, NumberRecords, ref TableData)
ret = sap_model.DatabaseTables.SetTableForEditingArray(
    table_key,
    table_version,
    fields_array,
    num_records,
    data_array
)

set_ret_code = ret[0]
_write_result = {"set_ret_code": set_ret_code}

if set_ret_code == 0 and apply_now:
    # ApplyEditedTables(FillImportLog, ref NumFatalErrors, ref NumErrorMsgs, ref NumWarnMsgs, ref NumInfoMsgs, ref ImportLog)
    apply_ret = sap_model.DatabaseTables.ApplyEditedTables(
        True,           # FillImportLog
        Int32(0),       # NumFatalErrors (output)
        Int32(0),       # NumErrorMsgs (output)
        Int32(0),       # NumWarnMsgs (output)
        Int32(0),       # NumInfoMsgs (output)
        String("")      # ImportLog (output)
    )

    _write_result["apply_ret_code"] = apply_ret[0]
    _write_result["fatal_errors"] = int(apply_ret[1])
    _write_result["error_msgs"] = int(apply_ret[2])
    _write_result["warn_msgs"] = int(apply_ret[3])
    _write_result["info_msgs"] = int(apply_ret[4])
    _write_result["import_log"] = str(apply_ret[5]) if apply_ret[5] else ""
'''
        exec(write_code, _etabs_globals)
        result = _etabs_globals.get('_write_result', {})

        set_ret = result.get('set_ret_code', -1)

        if set_ret != 0:
            return json.dumps({
                "success": False,
                "error": f"SetTableForEditingArray failed (return code: {set_ret})",
                "table_name": table_name,
                "suggestion": "Check field keys are importable with get_table_fields()"
            }, indent=2)

        if apply_immediately:
            apply_ret = result.get('apply_ret_code', -1)
            fatal = result.get('fatal_errors', 0)
            errors = result.get('error_msgs', 0)
            warns = result.get('warn_msgs', 0)
            log = result.get('import_log', '')

            if apply_ret == 0 and fatal == 0:
                return json.dumps({
                    "success": True,
                    "table_name": table_name,
                    "records_written": num_records,
                    "fields_written": len(field_keys),
                    "changes_applied": True,
                    "warnings": warns,
                    "import_log": log if log else None,
                    "message": "Table updated and changes applied successfully"
                }, indent=2)
            else:
                return json.dumps({
                    "success": False,
                    "error": f"ApplyEditedTables failed",
                    "fatal_errors": fatal,
                    "error_messages": errors,
                    "warnings": warns,
                    "import_log": log,
                    "table_name": table_name,
                    "note": "Data may be in inconsistent state"
                }, indent=2)
        else:
            return json.dumps({
                "success": True,
                "table_name": table_name,
                "records_written": num_records,
                "changes_applied": False,
                "note": "Changes staged but not applied. Call again with apply_immediately=True or use ApplyEditedTables()"
            }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to write table: {str(e)}",
            "table_name": table_name
        }, indent=2)


def get_units_name(units_code: int) -> str:
    """Convert ETABS units code to readable name"""
    units_map = {
        1: "lb-in-F", 2: "lb-ft-F", 3: "kip-in-F", 4: "kip-ft-F",
        5: "kN-mm-C", 6: "kN-m-C", 7: "kgf-mm-C", 8: "kgf-m-C",
        9: "N-mm-C", 10: "N-m-C", 11: "Ton-mm-C", 12: "Ton-m-C",
        13: "kN-cm-C", 14: "kgf-cm-C", 15: "N-cm-C", 16: "Ton-cm-C"
    }
    return units_map.get(units_code, f"Unknown({units_code})")


#=============================================#
#            HELPER FUNCTIONS                #
#=============================================#

def _check_etabs_connection():
    """
    Helper function to check ETABS connection and return error JSON if not connected.

    Returns:
    - None if connected (proceed with operation)
    - JSON error string if not connected
    """
    if not _etabs:
        return json.dumps({
            "success": False,
            "error": "ETABS not connected",
            "suggestion": "Use connect_to_etabs() first"
        }, indent=2)
    return None


@etabs_tool(["units", "model_info"])
def get_model_units() -> str:
    """
    Get the current model units from ETABS.

    Returns:
    - JSON with current model units and unit system information
    """
    import json

    try:
        connection_check = _check_etabs_connection()
        if connection_check:
            return connection_check

        model = get_etabs_connection()

        # Get present (display) units
        # Based on ETABS API documentation, we can try GetPresentUnits
        try:
            units_code = model.GetPresentUnits()
            units_name = get_units_name(units_code)

            return json.dumps({
                "success": True,
                "units_code": units_code,
                "units_name": units_name,
                "description": f"Model units: {units_name}",
                "message": "Successfully retrieved model units"
            }, indent=2)

        except AttributeError:
            # Fallback: try to get from connection info
            conn_result = connect_to_etabs()
            conn_data = json.loads(conn_result)

            if conn_data.get("status") == "connected" and "units" in conn_data:
                return json.dumps({
                    "success": True,
                    "units_code": conn_data["units"]["code"],
                    "units_name": conn_data["units"]["name"],
                    "description": f"Model units: {conn_data['units']['name']}",
                    "message": "Retrieved units from connection info",
                    "method": "fallback"
                }, indent=2)
            else:
                return json.dumps({
                    "success": False,
                    "error": "Could not determine model units",
                    "suggestion": "Check ETABS connection and model state"
                }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to get model units: {str(e)}",
            "exception_type": type(e).__name__
        }, indent=2)


#=============================================#
#          UBIM EXPORT TOOLS                 #
#=============================================#
# Tools for exporting ETABS model data to UBIM format
# for interoperability with Tekla and other software

@etabs_tool(["ubim", "export", "frames", "interoperability"])
def export_frames_to_ubim(output_file: str, filter_by_story: str = None) -> str:
    """Export ETABS frames to UBIM JSON format for Tekla import.

    ETABS BRIDGE: Main export tool for structural frames (beams, columns, braces)

    Parameters:
    - output_file: Path for output UBIM JSON file (e.g., "C:/exports/model.json")
    - filter_by_story: Optional story name to filter frames (e.g., "Story1")

    Exports frames with:
    - Exact geometry (coordinates in mm)
    - Profile and material mapping
    - Cardinal point positioning
    - Local angle rotation
    - Universal GUIDs for tracking

    Returns export summary with frame count and any validation issues.
    """
    try:
        # Check ETABS connection
        connection_check = _check_etabs_connection()
        if connection_check:
            return connection_check

        model = get_etabs_connection()

        # Import UBIM converter
        try:
            import sys
            import os
            # Add UBIM DataBridge to path if not already there
            ubim_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '2511_UBIM_DataBridge'))
            if ubim_path not in sys.path:
                sys.path.insert(0, ubim_path)

            from ubim_core.converters.etabs import ETABSConverter
        except ImportError as e:
            return json.dumps({
                "success": False,
                "error": f"UBIM core library not available: {e}",
                "suggestion": "Install with: pip install -e ../2511_UBIM_DataBridge"
            }, indent=2)

        # Create converter with ETABS model
        converter = ETABSConverter(model)

        # Convert frames to UBIM
        result = converter.convert_frames_to_ubim(
            output_file=output_file,
            filter_by_story=filter_by_story
        )

        if result.get("success"):
            stats = result.get("stats", {})
            ubim_doc = result.get("data", {})

            return json.dumps({
                "success": True,
                "message": f"Successfully exported {stats.get('successful', 0)} frames to UBIM format",
                "output_file": output_file,
                "statistics": {
                    "total_frames": stats.get('total', 0),
                    "successful": stats.get('successful', 0),
                    "failed": stats.get('failed', 0),
                    "healed": stats.get('healed', 0)
                },
                "ubim_version": ubim_doc.get("version", "1.0"),
                "source_software": "ETABS",
                "filter_applied": filter_by_story,
                "next_step": f"Import to Tekla with: tekla_import_frames_from_ubim('{output_file}')"
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": result.get("error", "Unknown error during conversion"),
                "suggestion": "Check ETABS model has frames and is fully loaded"
            }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to export frames: {str(e)}",
            "exception_type": type(e).__name__
        }, indent=2)


@etabs_tool(["ubim", "export", "areas", "walls", "interoperability"])
def export_areas_to_ubim(output_file: str, filter_by_story: str = None, area_type: str = None) -> str:
    """Export ETABS area objects (walls, floors, slabs) to UBIM JSON format.

    ETABS BRIDGE: Export tool for area elements

    Parameters:
    - output_file: Path for output UBIM JSON file (e.g., "C:/exports/walls.json")
    - filter_by_story: Optional story name to filter areas (e.g., "Story1")
    - area_type: Optional type filter - "wall", "floor", "slab", or None for all

    Exports areas with:
    - Shell geometry (corner points in mm)
    - Section properties (thickness, type)
    - Material information
    - Story assignment

    Returns export summary with area count and any validation issues.
    """
    try:
        # Check ETABS connection
        connection_check = _check_etabs_connection()
        if connection_check:
            return connection_check

        model = get_etabs_connection()

        # Import UBIM converter
        try:
            import sys
            import os
            ubim_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '2511_UBIM_DataBridge'))
            if ubim_path not in sys.path:
                sys.path.insert(0, ubim_path)

            from ubim_core.converters.etabs_areas import ETABSAreasConverter
        except ImportError as e:
            return json.dumps({
                "success": False,
                "error": f"UBIM areas converter not available: {e}",
                "suggestion": "The areas converter module needs to be created in ubim_core"
            }, indent=2)

        # Create converter with ETABS model
        converter = ETABSAreasConverter(model)

        # Convert areas to UBIM
        result = converter.convert_areas_to_ubim(
            output_file=output_file,
            filter_by_story=filter_by_story,
            area_type=area_type
        )

        if result.get("success"):
            stats = result.get("stats", {})
            ubim_doc = result.get("data", {})

            return json.dumps({
                "success": True,
                "message": f"Successfully exported {stats.get('successful', 0)} areas to UBIM format",
                "output_file": output_file,
                "statistics": {
                    "total_areas": stats.get('total', 0),
                    "successful": stats.get('successful', 0),
                    "failed": stats.get('failed', 0),
                    "by_type": stats.get('by_type', {})
                },
                "ubim_version": ubim_doc.get("version", "1.0"),
                "source_software": "ETABS",
                "filter_applied": {
                    "story": filter_by_story,
                    "type": area_type
                }
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": result.get("error", "Unknown error during conversion"),
                "suggestion": "Check ETABS model has area objects and is fully loaded"
            }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to export areas: {str(e)}",
            "exception_type": type(e).__name__
        }, indent=2)


#=============================================#
#              RUN MCP SERVER                #
#=============================================#

if __name__ == "__main__":
    mcp.run()