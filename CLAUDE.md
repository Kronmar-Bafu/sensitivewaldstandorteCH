# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

Computes climate-sensitive forest site maps for all 26 Swiss cantons. The pipeline:
1. **hoehenstufen.py** — reads a canton's forest site shapefile + NaiS translation Excel, enriches with raster stats (slope, radiation, elevation class 1975), then writes `stok_gdf_attributed.gpkg`
2. **`{KT}_sensi_treeapp.py`** (still per-canton in `legacy/`) — uses the attributed shapefile to compute future site types and tree species recommendations under RCP4.5 and RCP8.5
3. **sensi_treeappCombiRCP45RCP85.py** — combines the two climate scenarios
4. **test_Projektionswege.py** — validates projection paths

## Running the Generic Scripts

```bash
# Step 1: assign elevation stages for a canton
python hoehenstufen.py AG --workspace D:/CCW24sensi --codespace .

# Step 3: combine RCP scenarios
python sensi_treeappCombiRCP45RCP85.py AG --projectspace D:/CCW24sensi

# Validation
python test_Projektionswege.py AG --projectspace D:/CCW24sensi
```

- `--workspace` defaults to `D:/CCW24sensi` (data directory)
- `--codespace` defaults to `.` (location of Excel reference files)
- Output per canton lands in `{workspace}/{KT}/`

## Architecture

### Shared Code
- **`sensiCHfunctions.py`** — all shared constants and utility functions: three variants of the Höhenstufen dicts (`standard`, `extended`, `grvs`), GDAL raster helpers, zonal stats wrappers, NaiS string parsing, and `assign_tahs()`
- **`config/{KT}.py`** — one CONFIG dict per canton (24 files); loaded via `config.load_config(canton_code)`
- **`hoehenstufen.py`**, **`sensi_treeappCombiRCP45RCP85.py`**, **`test_Projektionswege.py`** — generic scripts parameterised by config

### Canton Configs (`config/{KT}.py`)
Each CONFIG dict specifies:
- `excel_file`, `excel_sheet`, `excel_format` (`"nais_hs"` or `"nais1_nais2_hs"`)
- `join_keys` — columns used to join Excel → shapefile
- `shapefile`, `raster_dem/slope/radiation/hs` — paths relative to `--workspace`
- `taheute_method` / `storeg_method` (`"const1"`, `"sjoin"`, `"overlay"`, `"none"`, `"in_file"`)
- `radiation_method` (`"quantile"` or `"fixed"`)
- `dict_variant` (`"standard"`, `"extended"`, or `"grvs"`)
- `custom_hook: True/False`

### Custom Hooks (`hooks/{KT}.py`)
Cantons with non-standard logic set `custom_hook: True` in their config. `hoehenstufen.py` then delegates entirely to `hooks/{KT}.py`, which must expose a `run(cfg, workspace, codespace)` function. Cantons needing hooks: AI, BE, FR, GE, GL, GR, JU, SG, SO, UR, ZH.

### Dict Variants
| Variant | Cantons | Extra levels |
|---------|---------|-------------|
| `standard` | AG, AI, AR, GE, LU, NE, NW, OW, SH | — |
| `extended` | BE, BLBS, JU, SG, SO, SZ, TG, UR, VD, ZG, ZH | hyperinsubrisch (1), mediterran (0), umom (7) |
| `grvs` | GR, VS | collin mit Buche = "cob"; umom = "um/om" |

### Legacy Code
Original per-canton scripts are preserved in `legacy/{KT}/` (git tag `v1-original`). The `{KT}_sensi_treeapp.py` scripts (~3666 lines each) are **not yet refactored** and are only available there.

## Dependencies

`numpy`, `pandas`, `geopandas`, `gdal` (osgeo), `rasterstats`, `openpyxl`
