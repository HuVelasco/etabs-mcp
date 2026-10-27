"""
ETABS CLR Direct Access - Simplified Architecture
Purpose: Single-file CLR access to ETABS like Blender MCP's bpy access
Author: Hugo Velasco (Hugo VelP)

This module provides direct CLR access to ETABS similar to how Blender MCP
provides direct access to bpy. No complex wrappers, no guessing - just direct .NET access.
"""

import clr
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add ETABS DLL to CLR
etabs_dll_path = Path("C:/Program Files/Computers and Structures/ETABS 18/ETABSv1.dll")
if etabs_dll_path.exists():
    clr.AddReference(str(etabs_dll_path))
else:
    print(f"ETABS DLL not found at: {etabs_dll_path}")

try:
    import System
    import ETABSv1
    CLR_AVAILABLE = True
except ImportError:
    CLR_AVAILABLE = False

# COM fallback for runtime connection
try:
    import comtypes.client
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False


class ETABSCLRAccess:
    """
    Direct CLR access to ETABS - simplified like Blender MCP.

    Provides:
    1. Direct access to ETABSv1 namespace
    2. Automatic enum translation
    3. Simple API execution
    4. No complex wrappers
    """

    def __init__(self):
        self.etabs_object = None
        self.sap_model = None
        self.connected = False

        # Load exact enums from our CLR extraction
        self.exact_enums = self._load_exact_enums()

    def connect(self) -> bool:
        """Connect to running ETABS instance."""
        if not COM_AVAILABLE:
            return False

        try:
            self.etabs_object = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
            self.sap_model = self.etabs_object.SapModel
            self.connected = True
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def execute_api(self, api_path: str, args: list = None) -> Dict[str, Any]:
        """
        Execute ETABS API with direct CLR access and automatic enum translation.

        Similar to Blender MCP's direct execution but with ETABS specifics.
        """
        if not self.connected:
            if not self.connect():
                return {"error": "Not connected to ETABS", "success": False}

        if args is None:
            args = []

        try:
            # Navigate to the API method (like bpy.ops.mesh.primitive_cube_add)
            api_parts = api_path.split('.')
            current_obj = self.sap_model

            for part in api_parts[:-1]:
                current_obj = getattr(current_obj, part)

            method_name = api_parts[-1]
            method = getattr(current_obj, method_name)

            # Execute the method
            if args:
                result = method(*args)
            else:
                result = method()

            # Build response with automatic enum translation
            response = {
                "success": True,
                "api_path": api_path,
                "result": result,
                "translated": self._translate_result(result, api_path)
            }

            return response

        except Exception as e:
            return {
                "success": False,
                "api_path": api_path,
                "error": str(e),
                "error_type": type(e).__name__
            }

    def _load_exact_enums(self) -> Dict[str, Dict[str, int]]:
        """Load exact enum values from CLR extraction."""
        try:
            kb_file = Path(__file__).parent.parent / "knowledge_base" / "etabs_exact_clr_signatures.json"
            if kb_file.exists():
                with open(kb_file, 'r') as f:
                    data = json.load(f)
                    return data.get('enums', {})
        except:
            pass
        return {}

    def _translate_result(self, result: Any, api_path: str) -> Any:
        """Automatic enum translation with zero guessing."""

        # Simple context mappings for common APIs
        api_enum_mappings = {
            'GetPresentUnits': 'eUnits',
            'GetDatabaseUnits': 'eUnits'
        }

        # Check if this API has a known enum return type
        if api_path in api_enum_mappings:
            enum_type = api_enum_mappings[api_path]

            if isinstance(result, (int, float)) and enum_type in self.exact_enums:
                int_val = int(result)
                enum_values = self.exact_enums[enum_type]

                for enum_name, enum_val in enum_values.items():
                    if enum_val == int_val:
                        return f"{result} ({enum_name})"

        # Handle list results (like GetNameList)
        elif isinstance(result, list) and len(result) >= 3:
            # Common pattern: [count, data, return_code]
            translated = result.copy()
            last_val = result[-1]

            if isinstance(last_val, (int, float)) and 'eReturnCode' in self.exact_enums:
                int_val = int(last_val)
                return_codes = self.exact_enums['eReturnCode']

                for enum_name, enum_val in return_codes.items():
                    if enum_val == int_val:
                        translated[-1] = f"{last_val} ({enum_name})"
                        return translated

        # No translation available - return original (safe)
        return result

    def get_enum_value(self, enum_type: str, value: int) -> Optional[str]:
        """Get exact enum name for a value."""
        if enum_type in self.exact_enums:
            enum_values = self.exact_enums[enum_type]
            for enum_name, enum_val in enum_values.items():
                if enum_val == value:
                    return enum_name
        return None

    def list_enums(self) -> Dict[str, int]:
        """List all available enums with their value counts."""
        return {enum_type: len(values) for enum_type, values in self.exact_enums.items()}

    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection and capability info."""
        return {
            "connected": self.connected,
            "clr_available": CLR_AVAILABLE,
            "com_available": COM_AVAILABLE,
            "exact_enums_loaded": len(self.exact_enums),
            "etabs_namespace_access": CLR_AVAILABLE
        }


# Global instance for server use
etabs_clr = ETABSCLRAccess()


def execute_etabs_api_simple(api_path: str, args: list = None) -> str:
    """
    Simple ETABS API execution with automatic enum translation.

    This is the simplified equivalent of Blender MCP's execution model.
    """
    result = etabs_clr.execute_api(api_path, args)
    return json.dumps(result, indent=2, default=str)


def get_etabs_info() -> str:
    """Get ETABS connection and capability information."""
    info = etabs_clr.get_connection_info()
    return json.dumps(info, indent=2)


if __name__ == "__main__":
    # Test the simplified architecture
    print("ETABS CLR Access Test")
    print("=" * 50)

    info = etabs_clr.get_connection_info()
    print(f"CLR Available: {info['clr_available']}")
    print(f"COM Available: {info['com_available']}")
    print(f"Exact Enums: {info['exact_enums_loaded']}")

    if etabs_clr.connect():
        print("\\nConnected to ETABS!")

        # Test simple API call
        result = execute_etabs_api_simple("GetPresentUnits")
        print(f"\\nGetPresentUnits result:")
        print(result)
    else:
        print("\\nNot connected to ETABS")