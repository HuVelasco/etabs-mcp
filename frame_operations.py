# FILE: frame_operations.py
# PURPOSE: Comprehensive Frame Objects CRUD Operations for ETABS MCP
# VERSION: 0.3.0.1 (Development - needs MCP testing)
# AUTHOR: Hugo Velasco (Hugo VelP)

#=============================================#
#        FRAME CRUD OPERATIONS v0.3.0.1      #
#=============================================#
#
# Comprehensive Frame Objects CRUD Operations
# Following "Many Simple Tools" Architecture
#
# CREATE: create_frame_by_coord(), create_frame_by_points()
# READ:   get_frame_info(), get_frame_list(), get_frame_properties()
# UPDATE: update_frame_section(), update_frame_releases()
# DELETE: delete_frame(), delete_frame_selection()
#
# Safety-Critical: All operations require visual verification in ETABS GUI
# Version: 0.3.0.1 (Development - needs MCP testing)
#
#=============================================#

import json
from typing import List, Dict, Optional, Tuple


class FrameOperations:
    """
    Frame Objects CRUD Operations Manager

    Provides comprehensive Create, Read, Update, Delete operations for frame objects.
    All operations follow safety-critical protocols requiring visual verification.
    """

    def __init__(self, model_connection):
        """
        Initialize Frame Operations with ETABS model connection.

        Args:
            model_connection: Active ETABS model connection object
        """
        self.model = model_connection

    #=============================================#
    #              CREATE OPERATIONS             #
    #=============================================#

    def create_frame_by_coord(self, xi: float, yi: float, zi: float,
                             xj: float, yj: float, zj: float,
                             section_name: str = "Default",
                             frame_name: str = "",
                             coordinate_system: str = "Global") -> dict:
        """Create frame element using coordinates.

        Parameters:
        - xi, yi, zi: I-end coordinates (start point)
        - xj, yj, zj: J-end coordinates (end point)
        - section_name: Frame section property name (default: "Default")
        - frame_name: Desired frame name (optional, ETABS auto-assigns if empty)
        - coordinate_system: Coordinate system name (default: "Global")

        Returns:
        - Dict with creation result, assigned name, and status

        Safety Note: MUST verify frame appears in ETABS 3D view after creation
        """
        try:
            # Use the documented FrameObj.AddByCoord signature
            # From complete_api_database.json: AddByCoord(xi, yi, zi, xj, yj, zj, ref Name, PropName, UserName, CSys)
            assigned_name = ""
            result = self.model.FrameObj.AddByCoord(
                xi, yi, zi, xj, yj, zj,
                assigned_name,  # ref string - ETABS assigns name
                section_name,   # PropName
                frame_name,     # UserName (desired name)
                coordinate_system  # CSys
            )

            # ETABS returns [assigned_name, status_code]
            if isinstance(result, (list, tuple)) and len(result) >= 2:
                assigned_name = result[0]
                status_code = result[1]

                if status_code == 0:
                    # Get frame info for verification
                    frame_count = self.model.FrameObj.Count()

                    return {
                        "success": True,
                        "operation": "create_frame_by_coord",
                        "assigned_name": assigned_name,
                        "coordinates": {
                            "i_end": {"x": xi, "y": yi, "z": zi},
                            "j_end": {"x": xj, "y": yj, "z": zj}
                        },
                        "section_property": section_name,
                        "coordinate_system": coordinate_system,
                        "total_frames": frame_count,
                        "status_code": status_code,
                        "verification_required": "CRITICAL: Verify frame visible in ETABS 3D view",
                        "next_steps": [
                            "Visual confirmation in ETABS GUI required",
                            "Check frame appears at specified coordinates",
                            "Verify section property assignment"
                        ]
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Frame creation failed with status code: {status_code}",
                        "coordinates": {
                            "i_end": {"x": xi, "y": yi, "z": zi},
                            "j_end": {"x": xj, "y": yj, "z": zj}
                        },
                        "section_property": section_name
                    }
            else:
                return {
                    "success": False,
                    "error": "Unexpected return format from FrameObj.AddByCoord",
                    "result": result
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Frame creation failed: {str(e)}",
                "error_type": type(e).__name__,
                "coordinates": {
                    "i_end": {"x": xi, "y": yi, "z": zi},
                    "j_end": {"x": xj, "y": yj, "z": zj}
                },
                "troubleshooting": [
                    "Verify ETABS connection is active",
                    "Check coordinate values are valid numbers",
                    "Ensure section property exists in model"
                ]
            }

    def create_frame_by_points(self, point1_name: str, point2_name: str,
                              section_name: str = "Default",
                              frame_name: str = "") -> dict:
        """Create frame element between existing point objects.

        Parameters:
        - point1_name: Name of I-end point object
        - point2_name: Name of J-end point object
        - section_name: Frame section property name (default: "Default")
        - frame_name: Desired frame name (optional, ETABS auto-assigns if empty)

        Returns:
        - Dict with creation result, assigned name, and status

        Safety Note: MUST verify frame appears in ETABS 3D view after creation
        """
        try:
            # Verify points exist first
            point_count = self.model.PointObj.Count()
            if point_count == 0:
                return {
                    "success": False,
                    "error": "No point objects exist in model",
                    "suggestion": "Create points first or use create_frame_by_coord"
                }

            # Use the documented FrameObj.AddByPoint signature
            # From complete_api_database.json: AddByPoint(Point1, Point2, ref Name, PropName, UserName)
            assigned_name = ""
            result = self.model.FrameObj.AddByPoint(
                point1_name,
                point2_name,
                assigned_name,  # ref string - ETABS assigns name
                section_name,   # PropName
                frame_name      # UserName (desired name)
            )

            # ETABS returns [assigned_name, status_code]
            if isinstance(result, (list, tuple)) and len(result) >= 2:
                assigned_name = result[0]
                status_code = result[1]

                if status_code == 0:
                    # Get frame info for verification
                    frame_count = self.model.FrameObj.Count()

                    return {
                        "success": True,
                        "operation": "create_frame_by_points",
                        "assigned_name": assigned_name,
                        "connection_points": {
                            "i_end": point1_name,
                            "j_end": point2_name
                        },
                        "section_property": section_name,
                        "total_frames": frame_count,
                        "status_code": status_code,
                        "verification_required": "CRITICAL: Verify frame visible in ETABS 3D view",
                        "next_steps": [
                            "Visual confirmation in ETABS GUI required",
                            "Check frame connects specified points",
                            "Verify section property assignment"
                        ]
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Frame creation failed with status code: {status_code}",
                        "connection_points": {
                            "i_end": point1_name,
                            "j_end": point2_name
                        },
                        "section_property": section_name,
                        "troubleshooting": [
                            "Verify both point names exist in model",
                            "Check point names are spelled correctly",
                            "Ensure points are not coincident"
                        ]
                    }
            else:
                return {
                    "success": False,
                    "error": "Unexpected return format from FrameObj.AddByPoint",
                    "result": result
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Frame creation failed: {str(e)}",
                "error_type": type(e).__name__,
                "connection_points": {
                    "i_end": point1_name,
                    "j_end": point2_name
                },
                "troubleshooting": [
                    "Verify ETABS connection is active",
                    "Check point names exist in model",
                    "Ensure section property exists"
                ]
            }

    #=============================================#
    #               READ OPERATIONS              #
    #=============================================#

    def get_frame_list(self, include_properties: bool = False) -> dict:
        """Get list of all frame objects in the model.

        Parameters:
        - include_properties: Include section properties for each frame (default: False)

        Returns:
        - Dict with frame list and optional property information
        """
        try:
            # Get frame count first
            frame_count = self.model.FrameObj.Count()

            if frame_count == 0:
                return {
                    "success": True,
                    "operation": "get_frame_list",
                    "frame_count": 0,
                    "frames": [],
                    "message": "No frames exist in model"
                }

            # Get frame names using GetNameList
            # From complete_api_database.json: GetNameList(ref NumberNames, ref MyName)
            result = self.model.FrameObj.GetNameList(0, [])

            if isinstance(result, (list, tuple)) and len(result) >= 3:
                number_names = result[0]
                frame_names = result[1]
                status_code = result[2]

                if status_code == 0 and number_names > 0:
                    frame_list = []

                    for frame_name in frame_names:
                        frame_info = {"name": frame_name}

                        if include_properties:
                            try:
                                # Get section property for each frame
                                section_result = self.model.FrameObj.GetSection(frame_name, "", "", 0)
                                if isinstance(section_result, (list, tuple)) and len(section_result) >= 3:
                                    section_status = section_result[0]
                                    if section_status == 0:
                                        frame_info["section_property"] = section_result[1]
                                        frame_info["auto_select_list"] = section_result[2]
                            except:
                                frame_info["section_property"] = "Unable to retrieve"

                        frame_list.append(frame_info)

                    return {
                        "success": True,
                        "operation": "get_frame_list",
                        "frame_count": number_names,
                        "frames": frame_list,
                        "includes_properties": include_properties
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get frame names, status code: {status_code}",
                        "frame_count": frame_count
                    }
            else:
                return {
                    "success": False,
                    "error": "Unexpected return format from FrameObj.GetNameList",
                    "result": result
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get frame list: {str(e)}",
                "error_type": type(e).__name__
            }

    def get_frame_properties(self, frame_name: str) -> dict:
        """Get comprehensive properties for a specific frame.

        Parameters:
        - frame_name: Name of the frame object

        Returns:
        - Dict with frame properties including section, releases, geometry
        """
        try:
            frame_properties = {
                "name": frame_name,
                "properties": {}
            }

            # Get section property
            try:
                section_result = self.model.FrameObj.GetSection(frame_name, "", "", 0)
                if isinstance(section_result, (list, tuple)) and len(section_result) >= 3:
                    if section_result[0] == 0:  # status_code == 0 (success)
                        frame_properties["properties"]["section"] = {
                            "property_name": section_result[1],
                            "auto_select_list": section_result[2]
                        }
                    else:
                        frame_properties["properties"]["section"] = {"error": f"Status code: {section_result[0]}"}
            except Exception as e:
                frame_properties["properties"]["section"] = {"error": str(e)}

            # Get releases
            try:
                releases_result = self.model.FrameObj.GetReleases(frame_name, [False]*6, [False]*6, 0.0, 0.0, 0)
                if isinstance(releases_result, (list, tuple)) and len(releases_result) >= 5:
                    if releases_result[0] == 0:  # status_code == 0 (success)
                        frame_properties["properties"]["releases"] = {
                            "i_end_releases": list(releases_result[1]),  # Convert to list for JSON
                            "j_end_releases": list(releases_result[2]),
                            "start_value": releases_result[3],
                            "end_value": releases_result[4]
                        }
                    else:
                        frame_properties["properties"]["releases"] = {"error": f"Status code: {releases_result[0]}"}
            except Exception as e:
                frame_properties["properties"]["releases"] = {"error": str(e)}

            # Additional frame information could be added here:
            # - Connectivity (point names)
            # - Loads
            # - Design parameters
            # - Material properties

            return {
                "success": True,
                "operation": "get_frame_properties",
                "frame": frame_properties,
                "verification_note": "Verify properties match ETABS GUI display"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get frame properties: {str(e)}",
                "error_type": type(e).__name__,
                "frame_name": frame_name
            }

    #=============================================#
    #              UPDATE OPERATIONS             #
    #=============================================#

    def update_frame_section(self, frame_name: str, section_property: str, item_type: int = 0) -> dict:
        """Update/change the section property of a frame.

        Parameters:
        - frame_name: Name of the frame object to modify
        - section_property: New section property name
        - item_type: Item type (default: 0 for Objects)

        Returns:
        - Dict with update result and verification requirements

        Safety Note: MUST verify section change in ETABS GUI after update
        """
        try:
            # Get current section for comparison
            current_section = "Unknown"
            try:
                section_result = self.model.FrameObj.GetSection(frame_name, "", "", item_type)
                if isinstance(section_result, (list, tuple)) and len(section_result) >= 2:
                    if section_result[0] == 0:
                        current_section = section_result[1]
            except:
                pass

            # Update section using SetSection
            # From complete_api_database.json: SetSection(Name, PropName, ItemType)
            result = self.model.FrameObj.SetSection(frame_name, section_property, item_type)

            if result == 0:  # Success
                # Verify the change
                verification_result = self.model.FrameObj.GetSection(frame_name, "", "", item_type)
                new_section = "Unable to verify"
                if isinstance(verification_result, (list, tuple)) and len(verification_result) >= 2:
                    if verification_result[0] == 0:
                        new_section = verification_result[1]

                return {
                    "success": True,
                    "operation": "update_frame_section",
                    "frame_name": frame_name,
                    "previous_section": current_section,
                    "new_section": new_section,
                    "requested_section": section_property,
                    "change_verified": new_section == section_property,
                    "verification_required": "CRITICAL: Verify section change in ETABS GUI",
                    "next_steps": [
                        "Visual confirmation in ETABS Properties panel",
                        "Check frame display updates with new section",
                        "Verify analysis results reflect new properties"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": f"Section update failed with status code: {result}",
                    "frame_name": frame_name,
                    "requested_section": section_property,
                    "current_section": current_section,
                    "troubleshooting": [
                        "Verify frame name exists in model",
                        "Check section property name is valid",
                        "Ensure section property is defined in model"
                    ]
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Frame section update failed: {str(e)}",
                "error_type": type(e).__name__,
                "frame_name": frame_name,
                "requested_section": section_property
            }

    def update_frame_releases(self, frame_name: str,
                             i_end_releases: list,
                             j_end_releases: list,
                             start_value: float = 0.0,
                             end_value: float = 0.0,
                             item_type: int = 0) -> dict:
        """Update frame end releases (moment and force releases).

        Parameters:
        - frame_name: Name of the frame object to modify
        - i_end_releases: List of 6 booleans [P, V2, V3, T, M2, M3] for I-end releases
        - j_end_releases: List of 6 booleans [P, V2, V3, T, M2, M3] for J-end releases
        - start_value: Start value for releases (default: 0.0)
        - end_value: End value for releases (default: 0.0)
        - item_type: Item type (default: 0 for Objects)

        Returns:
        - Dict with update result and verification requirements

        Safety Note: MUST verify releases in ETABS GUI - affects structural behavior
        """
        try:
            # Validate input lists
            if len(i_end_releases) != 6:
                return {
                    "success": False,
                    "error": "i_end_releases must have exactly 6 boolean values [P, V2, V3, T, M2, M3]",
                    "received_length": len(i_end_releases)
                }

            if len(j_end_releases) != 6:
                return {
                    "success": False,
                    "error": "j_end_releases must have exactly 6 boolean values [P, V2, V3, T, M2, M3]",
                    "received_length": len(j_end_releases)
                }

            # Get current releases for comparison
            current_releases = {"i_end": [False]*6, "j_end": [False]*6}
            try:
                releases_result = self.model.FrameObj.GetReleases(frame_name, [False]*6, [False]*6, 0.0, 0.0, item_type)
                if isinstance(releases_result, (list, tuple)) and len(releases_result) >= 3:
                    if releases_result[0] == 0:
                        current_releases["i_end"] = list(releases_result[1])
                        current_releases["j_end"] = list(releases_result[2])
            except:
                pass

            # Update releases using SetReleases
            # From complete_api_database.json: SetReleases(Name, ii, jj, StartValue, EndValue, ItemType)
            result = self.model.FrameObj.SetReleases(
                frame_name,
                i_end_releases,
                j_end_releases,
                start_value,
                end_value,
                item_type
            )

            if result == 0:  # Success
                # Verify the change
                verification_result = self.model.FrameObj.GetReleases(frame_name, [False]*6, [False]*6, 0.0, 0.0, item_type)
                new_releases = {"i_end": [False]*6, "j_end": [False]*6}
                if isinstance(verification_result, (list, tuple)) and len(verification_result) >= 3:
                    if verification_result[0] == 0:
                        new_releases["i_end"] = list(verification_result[1])
                        new_releases["j_end"] = list(verification_result[2])

                release_names = ["P", "V2", "V3", "T", "M2", "M3"]

                return {
                    "success": True,
                    "operation": "update_frame_releases",
                    "frame_name": frame_name,
                    "previous_releases": {
                        "i_end": dict(zip(release_names, current_releases["i_end"])),
                        "j_end": dict(zip(release_names, current_releases["j_end"]))
                    },
                    "new_releases": {
                        "i_end": dict(zip(release_names, new_releases["i_end"])),
                        "j_end": dict(zip(release_names, new_releases["j_end"]))
                    },
                    "start_value": start_value,
                    "end_value": end_value,
                    "verification_required": "CRITICAL: Verify releases in ETABS GUI - affects structural behavior",
                    "next_steps": [
                        "Visual confirmation in ETABS Frame Properties panel",
                        "Check frame releases display correctly in 3D view",
                        "Verify analysis results reflect new release conditions",
                        "SAFETY: Releases affect load transfer - review carefully"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": f"Releases update failed with status code: {result}",
                    "frame_name": frame_name,
                    "requested_releases": {
                        "i_end": dict(zip(["P", "V2", "V3", "T", "M2", "M3"], i_end_releases)),
                        "j_end": dict(zip(["P", "V2", "V3", "T", "M2", "M3"], j_end_releases))
                    },
                    "troubleshooting": [
                        "Verify frame name exists in model",
                        "Check release values are boolean (True/False)",
                        "Ensure start_value and end_value are numeric"
                    ]
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Frame releases update failed: {str(e)}",
                "error_type": type(e).__name__,
                "frame_name": frame_name
            }

    #=============================================#
    #              DELETE OPERATIONS             #
    #=============================================#

    def delete_frame(self, frame_name: str, item_type: int = 0) -> dict:
        """Delete a specific frame object from the model.

        Parameters:
        - frame_name: Name of the frame object to delete
        - item_type: Item type (default: 0 for Objects)

        Returns:
        - Dict with deletion result and verification requirements

        DANGER: Permanent operation - frame will be completely removed
        Safety Note: MUST verify frame disappears from ETABS GUI
        """
        try:
            # Get current frame count and verify frame exists
            initial_count = self.model.FrameObj.Count()

            # Check if frame exists by trying to get its properties
            frame_exists = False
            try:
                section_result = self.model.FrameObj.GetSection(frame_name, "", "", item_type)
                if isinstance(section_result, (list, tuple)) and len(section_result) >= 1:
                    frame_exists = section_result[0] == 0
            except:
                frame_exists = False

            if not frame_exists:
                return {
                    "success": False,
                    "error": f"Frame '{frame_name}' does not exist in model",
                    "total_frames": initial_count,
                    "suggestion": "Check frame name spelling or use get_frame_list() to see available frames"
                }

            # Delete frame using Delete method
            # From complete_api_database.json: Delete(Name, ItemType)
            result = self.model.FrameObj.Delete(frame_name, item_type)

            if result == 0:  # Success
                # Verify deletion
                final_count = self.model.FrameObj.Count()

                # Double-check frame is gone
                frame_still_exists = False
                try:
                    section_result = self.model.FrameObj.GetSection(frame_name, "", "", item_type)
                    if isinstance(section_result, (list, tuple)) and len(section_result) >= 1:
                        frame_still_exists = section_result[0] == 0
                except:
                    frame_still_exists = False

                return {
                    "success": True,
                    "operation": "delete_frame",
                    "deleted_frame": frame_name,
                    "initial_frame_count": initial_count,
                    "final_frame_count": final_count,
                    "frames_deleted": initial_count - final_count,
                    "deletion_verified": not frame_still_exists,
                    "verification_required": "CRITICAL: Verify frame disappeared from ETABS 3D view",
                    "safety_warning": "PERMANENT DELETION - Frame cannot be recovered without undo",
                    "next_steps": [
                        "Visual confirmation in ETABS GUI required",
                        "Check frame no longer appears in 3D view",
                        "Verify associated loads and assignments removed",
                        "Review model stability after frame removal"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": f"Frame deletion failed with status code: {result}",
                    "frame_name": frame_name,
                    "total_frames": initial_count,
                    "troubleshooting": [
                        "Verify frame name exists in model",
                        "Check frame is not part of locked group",
                        "Ensure frame is not referenced by other objects"
                    ]
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Frame deletion failed: {str(e)}",
                "error_type": type(e).__name__,
                "frame_name": frame_name,
                "safety_note": "Deletion operation did not complete"
            }

    def delete_frame_selection(self, confirm_mass_deletion: bool = False) -> dict:
        """Delete all currently selected frame objects.

        Parameters:
        - confirm_mass_deletion: Must be True to confirm deletion of multiple frames

        Returns:
        - Dict with deletion result for selected frames

        EXTREME DANGER: Can delete multiple frames at once
        Safety Note: MUST verify all selected frames disappear from ETABS GUI
        """
        try:
            # Get initial frame count
            initial_count = self.model.FrameObj.Count()

            if initial_count == 0:
                return {
                    "success": True,
                    "message": "No frames exist in model to delete",
                    "frame_count": 0
                }

            # Safety check for mass deletion
            if not confirm_mass_deletion:
                return {
                    "success": False,
                    "error": "Mass deletion not confirmed",
                    "safety_requirement": "Must set confirm_mass_deletion=True to delete selected frames",
                    "warning": "This operation can delete multiple frames permanently",
                    "initial_frame_count": initial_count,
                    "recommendation": "Use delete_frame() for single frame deletion"
                }

            # Delete selected frames using Delete with empty name and ItemType=2 (Selected Objects)
            # From ETABS API: ItemType=2 means "Selected Objects"
            result = self.model.FrameObj.Delete("", 2)  # Empty name with Selected Objects item type

            if result == 0:  # Success
                # Get final count
                final_count = self.model.FrameObj.Count()
                frames_deleted = initial_count - final_count

                return {
                    "success": True,
                    "operation": "delete_frame_selection",
                    "initial_frame_count": initial_count,
                    "final_frame_count": final_count,
                    "frames_deleted": frames_deleted,
                    "verification_required": "CRITICAL: Verify selected frames disappeared from ETABS 3D view",
                    "safety_warning": "PERMANENT MASS DELETION - Frames cannot be recovered without undo",
                    "next_steps": [
                        "Visual confirmation in ETABS GUI required",
                        "Check deleted frames no longer appear in 3D view",
                        "Verify model integrity after mass deletion",
                        "Review structural system after frame removal",
                        "SAFETY: Consider running analysis to verify stability"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": f"Selected frame deletion failed with status code: {result}",
                    "initial_frame_count": initial_count,
                    "troubleshooting": [
                        "Verify frames are actually selected in ETABS",
                        "Check selected frames are not part of locked groups",
                        "Ensure selected frames are not referenced by other objects"
                    ]
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Selected frame deletion failed: {str(e)}",
                "error_type": type(e).__name__,
                "safety_note": "Mass deletion operation did not complete"
            }


# =============================================================================
# HELPER FUNCTIONS FOR MCP TOOLS
# =============================================================================

def create_frame_operations(model_connection):
    """Create FrameOperations instance with model connection."""
    return FrameOperations(model_connection)


def json_response(operation_result: dict) -> str:
    """Convert operation result dictionary to JSON string."""
    return json.dumps(operation_result, indent=2)