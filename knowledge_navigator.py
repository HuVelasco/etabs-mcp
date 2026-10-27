# FILE: knowledge_navigator.py
# PURPOSE: ETABS MCP Knowledge Navigator Tool - Access API docs and manuals
# STATUS: v2.0 Ultra-Simplified Tool - Single file implementation
# HISTORY: Created 2025-01-19 for knowledge base access

"""
ETABS MCP Knowledge Navigator Tool
===================================
Simple, powerful tool for accessing API documentation and software manuals
from the knowledge_base/global directory.

Follows v2.0 Ultra-Simplified Architecture principles:
- Single file implementation
- Honest error handling
- Clean, simple interface
- Real value for engineers
"""

import os
import json
from typing import Dict, Any, Optional, List

#=============================================#
#           KNOWLEDGE BASE PATH              #
#=============================================#

# Define knowledge base path relative to project root
KNOWLEDGE_BASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "knowledge_base", "global"
)

#=============================================#
#         KNOWLEDGE CATEGORIES               #
#=============================================#

KNOWLEDGE_CATEGORIES = {
    "api": {
        "path": "api",
        "description": "ETABS API documentation and references",
        "files": {
            "reference": "API-REFERENCE-COMPLETE.md",
            "errors": "API-ERROR-CODES.md",
            "hierarchy": "API-OBJECT-HIERARCHY.md",
            "units": "API-UNITS-GUIDE.md"
        }
    },
    "codes": {
        "path": "codes",
        "description": "Design codes and standards",
        "files": {
            "aisc360": "AISC-360-16-OVERVIEW.md",
            "aisc341": "AISC-341-16-SEISMIC.md"
        }
    },
    "manuals": {
        "path": "manuals",
        "description": "ETABS manuals and design guides",
        "files": {
            "steel_frame": "STEEL-FRAME-DESIGN-GUIDE.md",
            "composite_beam": "composite-beam-design-guide.md",
            "composite_column": "composite-column-design-guide.md",
            "menu_reference": "etabs-menu-reference-guide.md",
            "steel_design": "steel-design-guide.md"
        }
    }
}

#=============================================#
#          MAIN KNOWLEDGE NAVIGATOR          #
#=============================================#

def knowledge_navigator(
    action: str = "search",
    topic: str = None,
    category: str = None,
    query: str = None
) -> Dict[str, Any]:
    """
    Navigate and access ETABS knowledge base documentation.
    
    Args:
        action: "search", "get_api", "get_manual", "get_code", "list_topics"
        topic: Specific topic to retrieve (e.g., "reference", "errors", "steel_frame")
        category: Category to search in ("api", "codes", "manuals")
        query: Search query for finding specific information
        
    Returns:
        dict: Knowledge content or search results
        
    Examples:
        # Get API reference
        knowledge_navigator(action="get_api", topic="reference")
        
        # Search for specific API method
        knowledge_navigator(action="search", query="FrameObj.GetDesignOrientation")
        
        # Get steel design manual
        knowledge_navigator(action="get_manual", topic="steel_frame")
        
        # List available topics
        knowledge_navigator(action="list_topics")
    """
    
    try:
        # Route based on action
        if action == "list_topics":
            return _list_available_topics()
            
        elif action == "get_api":
            if not topic:
                return {"success": False, "error": "topic required for get_api action"}
            return _get_api_knowledge(topic)
            
        elif action == "get_manual":
            if not topic:
                return {"success": False, "error": "topic required for get_manual action"}
            return _get_manual_knowledge(topic)
            
        elif action == "get_code":
            if not topic:
                return {"success": False, "error": "topic required for get_code action"}
            return _get_code_knowledge(topic)
            
        elif action == "search":
            if not query:
                return {"success": False, "error": "query required for search action"}
            return _search_knowledge(query, category)
            
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "available_actions": ["search", "get_api", "get_manual", "get_code", "list_topics"]
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Knowledge navigation failed: {str(e)}"
        }

#=============================================#
#          TOPIC LISTING FUNCTIONS           #
#=============================================#

def _list_available_topics() -> Dict[str, Any]:
    """List all available knowledge topics organized by category."""
    try:
        available_topics = {}
        
        for cat_name, cat_info in KNOWLEDGE_CATEGORIES.items():
            available_topics[cat_name] = {
                "description": cat_info["description"],
                "topics": list(cat_info["files"].keys()),
                "file_count": len(cat_info["files"])
            }
        
        return {
            "success": True,
            "action": "list_topics",
            "categories": available_topics,
            "total_topics": sum(len(cat["files"]) for cat in KNOWLEDGE_CATEGORIES.values()),
            "usage_example": "Use knowledge_navigator(action='get_api', topic='reference') to access content"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Failed to list topics: {str(e)}"}

#=============================================#
#         KNOWLEDGE RETRIEVAL FUNCTIONS      #
#=============================================#

def _get_api_knowledge(topic: str) -> Dict[str, Any]:
    """Get API documentation for a specific topic."""
    try:
        if topic not in KNOWLEDGE_CATEGORIES["api"]["files"]:
            return {
                "success": False,
                "error": f"Unknown API topic: {topic}",
                "available_topics": list(KNOWLEDGE_CATEGORIES["api"]["files"].keys())
            }
        
        file_name = KNOWLEDGE_CATEGORIES["api"]["files"][topic]
        file_path = os.path.join(KNOWLEDGE_BASE_PATH, "api", file_name)
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"Knowledge file not found: {file_path}"
            }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract first 100 lines for preview
        lines = content.split('\n')
        preview = '\n'.join(lines[:100])
        
        return {
            "success": True,
            "action": "get_api",
            "topic": topic,
            "file": file_name,
            "content": content,
            "preview": preview,
            "line_count": len(lines),
            "char_count": len(content)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Failed to read API knowledge: {str(e)}"}

def _get_manual_knowledge(topic: str) -> Dict[str, Any]:
    """Get manual/guide documentation for a specific topic."""
    try:
        if topic not in KNOWLEDGE_CATEGORIES["manuals"]["files"]:
            return {
                "success": False,
                "error": f"Unknown manual topic: {topic}",
                "available_topics": list(KNOWLEDGE_CATEGORIES["manuals"]["files"].keys())
            }
        
        file_name = KNOWLEDGE_CATEGORIES["manuals"]["files"][topic]
        file_path = os.path.join(KNOWLEDGE_BASE_PATH, "manuals", file_name)
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"Manual file not found: {file_path}"
            }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract first 100 lines for preview
        lines = content.split('\n')
        preview = '\n'.join(lines[:100])
        
        return {
            "success": True,
            "action": "get_manual",
            "topic": topic,
            "file": file_name,
            "content": content,
            "preview": preview,
            "line_count": len(lines),
            "char_count": len(content)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Failed to read manual: {str(e)}"}

def _get_code_knowledge(topic: str) -> Dict[str, Any]:
    """Get design code documentation for a specific topic."""
    try:
        if topic not in KNOWLEDGE_CATEGORIES["codes"]["files"]:
            return {
                "success": False,
                "error": f"Unknown code topic: {topic}",
                "available_topics": list(KNOWLEDGE_CATEGORIES["codes"]["files"].keys())
            }
        
        file_name = KNOWLEDGE_CATEGORIES["codes"]["files"][topic]
        file_path = os.path.join(KNOWLEDGE_BASE_PATH, "codes", file_name)
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"Code file not found: {file_path}"
            }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract first 100 lines for preview
        lines = content.split('\n')
        preview = '\n'.join(lines[:100])
        
        return {
            "success": True,
            "action": "get_code",
            "topic": topic,
            "file": file_name,
            "content": content,
            "preview": preview,
            "line_count": len(lines),
            "char_count": len(content)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Failed to read code documentation: {str(e)}"}

#=============================================#
#           SEARCH FUNCTIONALITY             #
#=============================================#

def _search_knowledge(query: str, category: Optional[str] = None) -> Dict[str, Any]:
    """Search across knowledge base files for specific information."""
    try:
        search_results = []
        files_searched = 0
        
        # Determine which categories to search
        if category and category in KNOWLEDGE_CATEGORIES:
            categories_to_search = {category: KNOWLEDGE_CATEGORIES[category]}
        else:
            categories_to_search = KNOWLEDGE_CATEGORIES
        
        # Search through each category
        for cat_name, cat_info in categories_to_search.items():
            cat_path = os.path.join(KNOWLEDGE_BASE_PATH, cat_info["path"])
            
            for topic_name, file_name in cat_info["files"].items():
                file_path = os.path.join(cat_path, file_name)
                
                if not os.path.exists(file_path):
                    continue
                
                files_searched += 1
                
                # Read and search file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Find matching lines
                matches = []
                for i, line in enumerate(lines, 1):
                    if query.lower() in line.lower():
                        matches.append({
                            "line_number": i,
                            "line_content": line.strip(),
                            "context": _get_line_context(lines, i-1, 2)
                        })
                
                if matches:
                    search_results.append({
                        "category": cat_name,
                        "topic": topic_name,
                        "file": file_name,
                        "match_count": len(matches),
                        "matches": matches[:5]  # Limit to first 5 matches per file
                    })
        
        # Sort results by match count
        search_results.sort(key=lambda x: x["match_count"], reverse=True)
        
        return {
            "success": True,
            "action": "search",
            "query": query,
            "category_filter": category,
            "files_searched": files_searched,
            "total_results": len(search_results),
            "results": search_results[:10],  # Limit to top 10 files
            "usage_tip": "Use action='get_api' or 'get_manual' with the topic name to get full content"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Search failed: {str(e)}"}

def _get_line_context(lines: List[str], line_index: int, context_size: int = 2) -> str:
    """Get surrounding context for a matched line."""
    start = max(0, line_index - context_size)
    end = min(len(lines), line_index + context_size + 1)
    
    context_lines = []
    for i in range(start, end):
        prefix = ">>> " if i == line_index else "    "
        context_lines.append(f"{prefix}{lines[i].strip()}")
    
    return '\n'.join(context_lines)

#=============================================#
#          TESTING FUNCTIONS                 #
#=============================================#

def test_knowledge_navigator():
    """Test the knowledge navigator functionality."""
    print("="*60)
    print("TESTING KNOWLEDGE NAVIGATOR")
    print("="*60)
    
    tests = [
        ("List topics", knowledge_navigator(action="list_topics")),
        ("Get API reference", knowledge_navigator(action="get_api", topic="reference")),
        ("Search for FrameObj", knowledge_navigator(action="search", query="FrameObj.Count")),
        ("Get steel manual", knowledge_navigator(action="get_manual", topic="steel_frame")),
        ("Invalid action", knowledge_navigator(action="invalid")),
        ("Missing topic", knowledge_navigator(action="get_api"))
    ]
    
    for test_name, result in tests:
        status = "PASS" if result.get("success") else "FAIL"
        print(f"\n{status} - {test_name}")
        if not result.get("success"):
            print(f"  Error: {result.get('error')}")
        else:
            if result.get("action") == "list_topics":
                print(f"  Categories: {len(result.get('categories', {}))}")
            elif result.get("action") == "search":
                print(f"  Results: {result.get('total_results', 0)} matches")
            elif result.get("content"):
                print(f"  Content size: {result.get('char_count', 0)} chars")
    
    print("\n" + "="*60)
    print("KNOWLEDGE NAVIGATOR TESTING COMPLETE")
    print("="*60)

#=============================================#
#            MAIN EXECUTION                  #
#=============================================#

if __name__ == "__main__":
    # Run tests if executed directly
    test_knowledge_navigator()
    
    # Example usage
    print("\n" + "="*60)
    print("EXAMPLE USAGE:")
    print("="*60)
    
    # Example 1: List all topics
    result = knowledge_navigator(action="list_topics")
    if result["success"]:
        print("\nAvailable knowledge categories:")
        for cat, info in result["categories"].items():
            print(f"  - {cat}: {info['description']} ({info['file_count']} files)")
    
    # Example 2: Search for specific API
    result = knowledge_navigator(action="search", query="DesignOrientation")
    if result["success"]:
        print(f"\nSearch results for 'DesignOrientation': {result['total_results']} matches found")
    
    print("\nKnowledge Navigator ready for integration with server.py")