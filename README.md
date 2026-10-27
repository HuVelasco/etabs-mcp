# ETABS MCP — AI Control Layer for CSI ETABS

> **Full structural analysis, seismic design, and code checking via AI — not just geometry.**  
> The deepest ETABS integration available: 806+ database tables, modal analysis, AISC 360-16, NTC-CDMX.

**Author:** Hugo Velasco · [dualitum.com](https://dualitum.com)  
**License:** MIT · Copyright © 2026 Hugo Velasco

---

## What This Is

ETABS MCP is a **Model Context Protocol server** that gives any MCP-compatible AI (Claude, GPT-4o, etc.) complete programmatic control over **CSI ETABS** — the industry-standard structural analysis and building design software.

This is not a geometry wrapper. It exposes the full ETABS analysis engine:

| Capability | What it means |
|---|---|
| **All 806+ database tables** | Read and write every table in ETABS via `DatabaseTables.GetTableForDisplayCSVString` |
| **Seismic/Modal analysis** | Run modal, response spectrum, and seismic analysis; read results |
| **Code design** | AISC 360-16 steel design, NTC-CDMX (Mexico seismic), ASCE 7 load combinations |
| **UBIM export** | Export frame geometry to UBIM format for downstream Tekla/Revit use |
| **API intelligence** | Self-learning API discovery; Claude learns the ETABS COM API in-session |

---

## Why It's Different

The only other ETABS MCP publicly available (FEA-MCP) handles geometry only — it can place a frame or read a node coordinate. It does not run analysis, check design codes, or access ETABS database tables.

```
FEA-MCP (competitor):   [ Geometry only ] ─── no analysis, no design codes
ETABS MCP (this):       [ Geometry ] → [ Analysis ] → [ Code Design ] → [ UBIM Export ]
```

This server treats ETABS as a full structural engineering engine, not just a model viewer.

---

## UBIM — Unified BIM Exchange Format

ETABS MCP is the **upstream node** of the UBIM pipeline — it exports the structural model in a format that Tekla and Revit can consume directly.

```
ETABS Structural Model
        │
  export_frames_to_ubim  ──►  frames.ubim.json
  export_areas_to_ubim   ──►  areas.ubim.json
        │
        ▼
  Tekla MCP  (tekla_import_ubim_with_sync)
  Revit MCP  (place family, level assignment)
```

The UBIM format carries section profiles, materials, load assignments, story levels, and connection metadata — only what each discipline needs, nothing more.

---

## Installation

### Prerequisites
- CSI ETABS 2022 or later (licensed)
- Python 3.10+
- Claude Desktop or any MCP-compatible client

### Setup

1. **Install dependencies**
   ```bash
   cd etabs-mcp-clean
   pip install -r requirements.txt
   ```

2. **Start ETABS** and open a model (the server connects via COM)

3. **Add to Claude Desktop** (`claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "etabs-clean": {
         "command": "python",
         "args": ["path/to/etabs-mcp-clean/server.py"]
       }
     }
   }
   ```

---

## Tools Reference

### Connection
| Tool | Description |
|---|---|
| `connect_to_etabs` | Connect to running ETABS instance via COM |
| `get_model_units` | Read active unit system |
| `get_etabs_enums` | Retrieve ETABS enumeration constants |

### Database Tables *(full 806+ table access)*
| Tool | Description |
|---|---|
| `list_etabs_tables` | List all available database tables |
| `get_table_fields` | Get field names and types for any table |
| `read_etabs_table` | Read any table as structured data |
| `write_etabs_table` | Write/modify any table |

### API Discovery
| Tool | Description |
|---|---|
| `discover_tools` | Auto-discover available ETABS API methods |
| `interpret_unknown_api` | Interpret and call undocumented API paths |
| `etabs_api_call` | Execute any ETABS API call by path |
| `etabs_run_script` | Run a multi-step Python script against the ETABS COM API |

### UBIM Bridge
| Tool | Description |
|---|---|
| `export_frames_to_ubim` | Export frame elements (beams, columns, braces) to UBIM format |
| `export_areas_to_ubim` | Export area elements (slabs, walls, ramps) to UBIM format |

---

## API Intelligence Layer

A key differentiator: the server maintains a **confidence-tracked API database** that records which ETABS COM API calls work, which fail, and what the correct signatures are. Claude uses this knowledge base to call the right methods the first time, avoiding trial-and-error.

```
Claude prompts ETABS call
        │
 API Intelligence Layer checks known-good signatures
        │
 etabs_api_call / etabs_run_script executes
        │
 Result + confidence score written back to database
        │
 Next call is smarter
```

---

## Use Cases

- **Parametric building design** — AI creates and iterates entire building models from a config spreadsheet
- **Seismic design loop** — AI runs modal analysis, checks drift, adjusts lateral frame sizes, loops until code-compliant
- **ETABS ↔ Tekla workflow** — export structural model to UBIM, import to Tekla for detailing in one session
- **Load combination generation** — ASCE 7 load combinations applied automatically
- **Section optimization** — AI iterates frame sections against AISC 360-16 design ratios

---

## Design Codes Supported

- **AISC 360-16** — LRFD steel frame design
- **NTC-CDMX 2020** — Mexico City seismic design code
- **ASCE 7** — Load combination generation
- Additional codes accessible via table API

---

## Architecture

```
Claude / AI Client
       │  MCP (stdio)
       ▼
  Python FastMCP Server  ←──── tools defined here
       │  pythonnet (CLR)
       ▼
  CSI ETABS COM API  ←── ETABS must be running
       │
  Full ETABS Engine (analysis, design, tables)
```

---

## Project Status

- ✅ Database table read/write (806+ tables) — production ready  
- ✅ API discovery and intelligence layer — production ready  
- ✅ UBIM export (frames + areas) — production ready  
- ✅ AISC 360-16 design code access — production ready  
- ✅ Parametric building generation — production ready  
- 🔄 Automated seismic design loop — in development  
- 🔄 NTC-CDMX full automation — planned  

---

## Contributing & Support

Issues and PRs welcome. For enterprise licensing, structural consulting workflows, or custom automation, contact [dualitum.com](https://dualitum.com).

---

*© 2026 Hugo Velasco. ETABS and CSI OAPI are trademarks of Computers and Structures, Inc. This project is not affiliated with or endorsed by CSI.*
