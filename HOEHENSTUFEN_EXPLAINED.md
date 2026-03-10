# What does hoehenstufen.py do?

## Overview

`hoehenstufen.py` is Step 1 of the climate-sensitive forest site pipeline. For a given
Swiss canton it takes the canton's **forest site map** (a polygon shapefile or GeoPackage)
and enriches each polygon with the information needed to assess climate sensitivity:

- Which **NaiS forest site type** (Waldstandorttyp) does each mapped polygon correspond to?
- In which **elevation belt** (Höhenstufe) does it currently lie?
- How **steep** is the terrain, and does it receive high or low **solar radiation**?
- Is it in a **silver-fir area** (Tannenareale), and in which **site region**
  (Waldstandortregion)?

The result is a single enriched GeoPackage (`stok_gdf_attributed.gpkg`) and a slimmed-down
export for the Tree-App (`{KT}_treeapp.gpkg`), both written to `{workspace}/{KT}/`.

---

## Why "Höhenstufen"?

Swiss forest ecology uses **elevation belts** (Höhenstufen) to describe where a forest
community naturally occurs. From low to high these are:

| Abbreviation | Full name      | Raster code |
|-------------|----------------|-------------|
| `co`        | collin         | 2 / 3       |
| `sm`        | submontan      | 4           |
| `um`        | untermontan    | 5           |
| `om`        | obermontan     | 6           |
| `hm`        | hochmontan     | 8           |
| `sa`        | subalpin       | 9           |
| `osa`       | obersubalpin   | 10          |

Some dict variants add `hyp` (hyperinsubrisch), `med` (mediterran), `umom`
(unter-/obermontan), and — for Graubünden/Valais — `cob` (collin mit Buche).

The **1975 raster** (`raster_hs`) encodes the historically mapped elevation belt for each
10 m cell. Zonal statistics (majority) on this raster give each forest polygon its
**`hs1975`** value, which is used later to disambiguate polygons that span two elevation
belts (e.g. a site type valid in both `sm` and `um`).

---

## Input data

| Source | What it contains |
|--------|-----------------|
| **Forest site shapefile** (`shapefile`) | The canton's mapped forest polygons, each labelled with a canton-specific site unit code (e.g. `Kategorie_`, `EK72`, `ASSOC_TOT_`, …) |
| **NaiS translation Excel** (`excel_file`) | A lookup table mapping canton unit codes → NaiS type codes (`nais1`, `nais2`) and their valid elevation belt(s) (`hs`) |
| **Slope raster** (`raster_slope`) | Mean slope in percent for each 10 m cell |
| **Radiation raster** (`raster_radiation`) | Mean annual global radiation (W/m²) per cell |
| **Elevation belt raster 1975** (`raster_hs`) | Historically mapped Höhenstufe per cell (integer codes 2–10) |
| **Tannenareale** (`taheute_file`) | Polygon layer of silver-fir areas; adds column `taheute` (1 = inside fir area) |
| **Waldstandortregionen** (`storeg_file`) | Polygon layer of site regions; adds column `storeg` (e.g. `1`, `2a`, `2b`, `2c`) |

---

## Processing steps

### 1. Read the NaiS translation Excel

The Excel maps each canton-specific forest site unit to a NaiS type. Two formats exist:

- **`nais_hs`** — one `nais` column (e.g. `"46(57V)"`) plus one `hs` column
  (e.g. `"hm"` or `"hm sa"`). The `nais` string encodes transitions: `(` signals a
  transition type (`ue`), `/` signals a mosaic (`mo`).
- **`nais1_nais2_hs`** — already split into `nais1`, `nais2`, and `hs`.

Rows without a valid NaiS assignment are dropped before the translation loop.

### 2. Read the forest site shapefile

Each polygon is assigned a `joinid` (= its row index). This ID is used throughout to
merge results back after spatial joins.

### 3. Join Tannenareale

Silver-fir areas are joined spatially to assign each polygon a `taheute` value:
- **`sjoin`** — a spatial join followed by groupby-min on `joinid`; each polygon gets the
  minimum `taheute` code of all overlapping fir-area polygons.
- **`overlay`** — a geometric intersection; polygons are split at fir-area boundaries.
- **`const1`** — a fixed value of 1 is assigned to all polygons (used where the whole
  canton lies within the fir area, or outside it and a constant is sufficient).

### 4. Join Waldstandortregionen

Site regions are joined with `sjoin` + groupby-min in the same way, adding the `storeg`
column. Some cantons use a constant (`const1`) or already have the column in the
shapefile (`in_file`).

### 5. Raster zonal statistics

For each polygon, three values are extracted from rasters:

- **`meanslopeprc`** — mean slope in percent; binned into `slpprzrec`
  (1 = flat <20%, 2 = moderate 20–60%, 3 = steep 60–70%, 4 = very steep ≥70%).
- **`rad`** — mean radiation; classified into `radiation`
  (+1 = sunny top 10%, −1 = shady bottom 10%, 0 = intermediate). Either by canton-wide
  quantile or fixed thresholds (112 / 147 W/m²).
- **`hs1975`** — majority elevation belt code from the 1975 raster.

An intermediate result (`stok_gdf_attributed_temp.gpkg`) is written at this point.

### 6. NaiS translation loop

The Excel rows are iterated. For each row, a mask selects all shapefile polygons that
match the join keys (e.g. canton unit code). The matched polygons receive:

- `nais1`, `nais2` — primary and secondary NaiS type codes
- `ue` = 1 if a transition exists (nais2 present)
- `mo` = 1 if it is a mosaic (`/` notation)
- `hs` — the elevation belt string from the Excel (e.g. `"hm"`, `"hm sa"`, `"hm(sa)"`)
- `tahs` — the **target elevation belt** in full words (e.g. `"hochmontan"`)
- `tahsue` — target elevation belt for the transition type (if applicable)

**Elevation belt disambiguation** — when `hs` contains multiple belts without parentheses
(e.g. `"hm sa"`), the 1975 raster value (`hs1975`) is used to pick the appropriate belt
for each polygon individually. If `hs1975` matches one of the listed belts, that belt is
assigned; otherwise the last belt in the list is used as a fallback.

When `hs` uses parentheses (e.g. `"hm(sa)"`), the primary belt goes to `tahs` and the
parenthesised belt to `tahsue` directly, without raster lookup.

### 7. Post-processing and output

- `nais` is constructed as `nais1` for simple types, or `nais1(nais2)` for transition types.
- An optional row filter (e.g. remove polygons with a sentinel value in a specific column)
  is applied.
- Output columns are selected per canton config and written to
  `{workspace}/{KT}/stok_gdf_attributed.gpkg`.
- A slimmed-down treeapp export (geometry + NaiS/Höhenstufen columns only) is written to
  `{workspace}/{KT}/{KT}_treeapp.gpkg`.

---

## Canton-specific variations

Most cantons follow the standard flow above. Eleven cantons have complex
canton-specific logic (pre-loop corrections, Bedingung columns, different join
structures, etc.) and delegate to a dedicated **hook file** (`hooks/{KT}.py`). The
hook file receives the same config dict and workspace paths and must produce the same
output files. Documented canton differences are in `hooks/HOOKS_DIFFERENCES.md`.

---

## Output columns (typical)

| Column | Description |
|--------|-------------|
| `joinid` | Original polygon index (survives spatial joins) |
| `taheute` | Silver-fir area code (1 = inside) |
| `storeg` | Site region code (e.g. `1`, `2a`) |
| `meanslopeprc` | Mean slope in percent |
| `slpprzrec` | Slope class (1–4) |
| `rad` | Mean radiation (W/m²) |
| `radiation` | Radiation class (−1, 0, +1) |
| `hs1975` | 1975 elevation belt raster code |
| `nais` | Full NaiS type string (e.g. `"46(57V)"`) |
| `nais1` | Primary NaiS type |
| `nais2` | Secondary NaiS type (transition) |
| `mo` | Mosaic flag (0/1) |
| `ue` | Transition flag (0/1) |
| `hs` | Elevation belt abbreviation string from Excel |
| `tahs` | Target elevation belt, full word (e.g. `"hochmontan"`) |
| `tahsue` | Target elevation belt for transition type |
| `geometry` | Polygon geometry (EPSG:2056, LV95) |
