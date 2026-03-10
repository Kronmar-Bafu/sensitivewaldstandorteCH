# Custom Hook Differences

Documents the canton-specific logic in each `hooks/{KT}.py` relative to the
standard flow in `hoehenstufen.py`.

---

## Standard flow (reference)

1. Read Excel → filter rows with empty `nais` or `hs`
2. Read shapefile → assign `joinid = index`
3. Taheute → `add_taheute()`: sjoin + groupby min (or `const1`)
4. Storeg → `add_storeg()`: sjoin + groupby min (or `const1`)
5. Raster stats: slope, radiation (quantile), hs1975
6. NaiS translation loop (1-key join on `join_keys`; `nais`/`hs` from Excel)
7. Filter on `filter_col` / `filter_val`
8. Select `output_cols`, write `stok_gdf_attributed.gpkg`
9. Export `{KT}_treeapp.gpkg`

---

## AI — Appenzell Innerrhoden ✓

| Aspect | Difference |
|--------|-----------|
| Shapefile columns | `nais` → `naisalt`, `nais1` → `nais1alt` on read |
| CRS | Force EPSG:2056 with `allow_override=True` |
| Taheute | Direct `gpd.sjoin` **without groupby**; `joinid` set **after** sjoin |
| Radiation | Fixed thresholds (112 / 147) |
| hsmoddictkurz | Override: starts at key 3 (no raster code 2) |
| Excel format | `tahs_precomputed`: has `WSTEinheit`, `nais` (join key), `nais1`, `nais2`, `tahs`, `naisue`, `naismosaic` |
| Join keys | 4-key: `WSTEinheit`, `nais1alt`, `naisue`, `naismosaic` |
| `hs` output | Set to raw `tahs` string from Excel (e.g. `"hm(sa)"`) |
| `tahs` output | Full word via `hoehenstufendictabkuerzungen[hslist[0]]` |
| nais1 override | For single-stage: `nais1` = first token of Excel `nais` key string |
| Post-write corrections | Reload gpkg; patch `WSTEinheit` in `{'18MBl', '18MBl(20g)', '46(57V)', '26(12a)'}` |
| Filter | Remove rows where `nais1 == ''` or null after corrections |

---

## BE — Bern ✓

| Aspect | Difference |
|--------|-----------|
| `joinid` | Set **before** taheute overlay (preserved through overlay) |
| Taheute | `gpd.overlay` intersection (splits polygons); file `Tannenareale2025.gpkg`; different drop cols (includes `id`, `Subcode`, `Flaeche`) |
| Storeg | File `Waldstandortregionen_2024_TI4ab_Final_GR.gpkg`, layer `waldstandortregionen_2024_ti4ab_final`; different drop cols (includes `id`, `Flaeche`, no `Shape_Leng/Area`) |
| Radiation | Quantile (same as standard) |
| Dict variant | `extended` |
| Excel format | `BE` sheet; columns `BE`, `NaiS_LFI_JU`, `NaiS_LFI_M/A`, `hs`, `hsue`, remarks |
| Join key | `BE` column |
| `nais` source | Already in shapefile (`NAIS` column, renamed); Excel only provides `hs` / `hsue` |
| `nais1`/`nais2` | Derived by splitting `nais` on `(` (not from Excel) |
| `ue` flag | Set where `nais2 != ''` |
| Translation loop | Assigns `hs`, `hsue`, `tahs`, `tahsue`; separate disambiguation for both using raster `hs1975` |
| `tahsue` fallback | Multi-token case uses `hs` tokens (not `hsue`) for fallback — matches legacy |
| Pre-loop corrections | 18 BE-unit → nais overrides (e.g. `27w`→`27a`, `38`→`39`, `54*`→`46M(70)`, `Pio` → hs1975-conditional) |
| Post-loop corrections | hs1975-conditional overrides for units `32`, `60*`, `66` |
| Output | Adds `fid` + `area` columns; filters `area > 0` |
| Intermediate save | Writes `stok_gdf_attributed_temp.gpkg` after raster stats |

---

## FR — Fribourg ✓

| Aspect | Difference |
|--------|-----------|
| Taheute | Direct `gpd.sjoin` without groupby; `joinid` set after sjoin |
| Radiation | Fixed thresholds (112 / 147) |
| Dict variant | `standard` |
| Excel | Sheet `Sheet1_sortiert`; filtered on `NaiS vereinfacht != '-'`, `hs != ''`, `hs != 'nan'`; columns cast to str |
| Join keys | 2-key: `ASSOC_TOT_` + `LEGENDE` |
| Extra columns | `naisdetail`, `BedingungHangneigung`, `BedingungRegion` (intermediates); `naisdetail` in output |
| Translation Part 1 | Condition-based: nais/hs assigned only to polygons matching `Bedingung Hangneigung` (`<60%`/`>60%`) or `Bedingung Region` (`Region 1`, `Region M, J`, `Region J, M`); Region 1 matched against both int `1` and str `'1'` |
| Translation Part 2 | Unconditional (full mask): nais1/nais2/mo/ue from NaiS string; `if('(') / if('/') else` structure — the `else` overwrites `nais2=''` for `(`-only nais; repaired by post-loop fill pass |
| Translation Part 3 | Unconditional: standard tahs/tahsue via hs1975 disambiguation |
| Post-loop corrections | 5 manual `ASSOC_TOT_+LEGENDE` patches: `18aP(17C)/18a`, `12s(24*U)/12s`, `17/13ho/17`, `17/22a/17`, `17/18fP/18w/17` |
| Post-loop fills | Fill `tahs` from hs1975 for empty; `AV+hs1975==-1 → subalpin`; fill `tahsue` for `ue==1`; final `tahsue` fallback; fill `nais1` for `ue==0`; fill `nais2` for `ue==1` (repairs the overwrite) |
| Config fix | Added `naisdetail` to `output_cols` in `config/FR.py` |

---

## GE — Geneva ✓

| Aspect | Difference |
|--------|-----------|
| Taheute | `taheute = 1` constant — no spatial join (Geneva outside Tannenareale) |
| Storeg | None — no join, no column |
| Radiation | Quantile method |
| Dict variant | `standard` |
| Join keys | 3-key: `VEGETATION` + `NO_TYPOLOG` + `MOSAIQUE` |
| `else` branch | Uses 2-key mask (`VEGETATION + NO_TYPOLOG` only, no MOSAIQUE) |
| tahs logic | Simplified per-polygon loop: `'co' in hs and hs1975==2` → `collin`; else → `submontan`. No raster disambiguation. |
| tahsue | `tahsue = tahs` for all `ue==1` and `mo==1` — no further logic |
| No post-loop corrections | — |

---

## GL — Glarus ✓

| Aspect | Difference |
|--------|-----------|
| Taheute | `taheute = 1` constant |
| Storeg | `storeg = 1` constant |
| Radiation | Fixed thresholds (112 / 147) |
| Dict variant | `standard` |
| Excel column | `NaiS` (uppercase) — not `nais`; filtered on `NaiS.notnull()` |
| Join keys | 2-key: `wg_haupt` + `wg_zusatz` |
| `Bedingung Hangneigung` | `'<60%'` or `'>60%'`: apply tahs/tahsue only to polygons matching slope condition. Single hs → direct. Multi-hs with `(` → tahs=hslist[0], tahsue=hslist[1] on slope-matched polygons. Multi-hs without `(` → always set hslist[1] on `slope>=60` polygons (both cases, legacy quirk). |
| `Bedingung Höhenstufe` | `'sm um'`, `'hm'`, `'om'`, `'om hm'`, `'sa'`: assign fixed tahs based on hs1975 raster. |
| `(` in hs override | After Bedingung blocks, if `(` in hs and len>1: overwrite tahs/tahsue for ALL mask polygons (hslist[0]/[1]). |
| No-condition multi-hs | Use hs1975 raster to pick tahs from list; fallback to last item for unmatched polygons. |
| "fixe Uebergaenge" | Post-loop: for any polygon where `(` in its `hs` field, re-apply tahs=hslist[0], tahsue=hslist[1]. |
| Special case | `nais=='AV'` and `hs1975==-1` → `tahs='subalpin'`. |
| tahsue fill | Fill `tahsue` for `ue==1` polygons where still empty. Final fill before treeapp export. |

---

## GR — Graubünden ✓

| Aspect | Difference |
|--------|-----------|
| Dict variant | `grvs` |
| Input | Pre-processed gpkg (`stok_gdf_attributed_temp4_fixed.gpkg`); no raster stats run |
| Column renames | `ass_gr`→`ASS_GR`, `naisbg`→`NAISbg`, `meanslopep`→`meanslopeprc` |
| ASS_GR corrections | 34 leading-digit artefact fixes (e.g. `747D`→`47D`, `0AV`→`AV`, `860`→`60`) |
| NAISbg whitespace | Remove spaces from NAISbg values in stok_gdf |
| Excel pre-pass | nais1/nais2/ue/mo pre-computed on excel rows before main loop |
| Bedingung filter | Excel filtered to `Bedingung==''`; regional Bedingung handling in legacy is dead code (unreachable) |
| tahs — single hs | Direct lookup |
| tahs — multi-hs with `(` | tahs=hslist[0], tahsue=hslist[1] |
| tahs — multi-hs without `(` | Per-polygon hs1975 lookup; fallback to last element in hslist |
| Post-loop fills | `nais1` for `ue==0`; `tahsue` for `ue==1` and `mo==1` |

---

## JU — Jura ✓

| Aspect | Difference |
|--------|-----------|
| Shapefile | gpkg with layer `env.env_03_01_phytosociologie_stations_forestieres`; sliced to `['association','etiquette','joinid','geometry']` immediately |
| Taheute | `gpd.overlay` intersection (Tannenareale2025.gpkg, same drop_cols as BE) |
| Storeg | sjoin + groupby min (Waldstandortregionen_2024_TI4ab_Final_GR.gpkg) — config file paths corrected |
| Dict variant | `extended` |
| Excel | `nais1_nais2_hs` pre-split; selects `['association','etiquette','BedingungHoehenstufe','nais1','nais2','hs']`; filtered to `nais1 != ''` |
| Pre-loop corrections | 8 blocks: `association` in `{'38','38w'}` × specific etiquette values; hs1975-conditional: `<=4` → nais1='39', `>4` → nais1='39*'; hs/nais2 set per block |
| BedingungHoehenstufe filter | Main loop only processes rows where column is null |
| Main loop | Sets nais1/nais2/hs/ue/tahs/tahsue; `nais` column NOT set in loop |
| tahs assignment | Same as GR: single→direct; multi with `(`→tahs/tahsue; multi without `(`→hs1975 per-polygon, fallback to last |
| Post-loop | tahsue fill; `nais = nais1+'('+nais2+')'` for ue==1; `nais1=='39'→submontan`; `nais1=='39*'→untermontan`; fill tahs from hs1975 for remaining empty; final tahsue fill |
| Output | Adds `fid` + `area`; filters `area > 0` |

---

## SG — St. Gallen ✓

| Aspect | Difference |
|--------|-----------|
| Taheute | `gpd.overlay` intersection (Tannenareale2025.gpkg); config file paths corrected |
| Storeg | sjoin + groupby min (Waldstandortregionen_2024_TI4ab_Final_GR.gpkg) |
| Dict variant | `extended` |
| Pre-loop corrections | DTWGEINHEI `'6(18)'`→`'6(8)'` and `'9(19)'`→`'9(15)'` with corrected nais/hs applied to both excel and stok_gdf; hs typo `'so'`→`'sa'` in excel |
| Bedingung Höhenstufe | Applied before main loop on matching rows: `'sa'`→hs1975>=9; `'hm'`→hs1975==8; `'om hm'`→hs1975==8(hm)/hs1975<=6(om); sets nais1/nais2/hs/ue/tahs/tahsue |
| Bedingung Region | Applied before main loop: `'2a'`→storeg=='2a'; `'1'`→storeg=='1'; sets nais1/nais2/hs/ue (no tahs) |
| Main loop | Only rows where both Bedingung cols are null; 1-key join on DTWGEINHEI; same tahs logic as GR/JU |
| Post-loop fills | tahsue for ue==1; nais column construction |
| Post-loop corrections | hs-based: sa/osa/sa(om)/hm(sa)/sa osa; DTWGEINHEI-based for null hs1975: 53→53Ta, 53(69L)→53Ta/69G, 60*(24C)→60*Ta/24*, 60*/u+hs1975==9→24* |
| Fill fallback | Fill tahs from hs1975 for remaining empty; final tahsue fill |
| "Korrekturen Juli2025" | Applied in-memory (no write/re-read): 4×`om(um)` hs patches; 3×nais/nais1 patches; 3×tahs/tahsue='hochmontan' for nais1/nais2 combos; filter nais!='' |
| Output | fid + area; filter area > 0 |

---

## SO — Solothurn ✓

| Aspect | Difference |
|--------|-----------|
| Taheute | `gpd.overlay` intersection (Tannenareale2025.gpkg); config file paths corrected |
| Storeg | sjoin + groupby min (Waldstandortregionen_2024_TI4ab_Final_GR.gpkg) |
| Dict variant | `extended` |
| Excel | Pre-split; columns `['stantrung','stanrgert','stanrnigt','Bedingung Höhenstufe','nais1','nais2','hs']`; `Bedingung Höhenstufe` loaded but not used — all rows processed unconditionally |
| Join | 3-key: stantrung + stanrgert + stanrnigt |
| tahs | Same logic as GR/JU/SG: single→direct; multi with `(`→tahs/tahsue; multi without `(`→hs1975 per-polygon, fallback to last |
| nais column | Constructed post-loop from nais1/nais2 |
| Post-loop | tahsue fill for ue==1; nais construction; fill tahs from hs1975 for empty |
| Output | fid + area; filter area > 0 |

---

## UR — Uri ✓

| Aspect | Difference |
|--------|-----------|
| Taheute | `gpd.overlay` intersection (Tannenareale2025.gpkg, same as BE/JU/SG/SO) |
| Storeg | sjoin + groupby min (Waldstandortregionen_2024_TI4ab_Final_GR.gpkg) |
| Dict variant | `extended` |
| Excel format | Pre-split; columns `['Kategorie_','Einheit_Na','Bedingung Region','Bedingung Höhenstufe','nais1','nais2','hs']`; filtered to `nais1 != ''` and not null. `'Bedingung Höhenstufe'` loaded but not used. |
| Bedingung Region filter | Excel filtered to `'Bedingung Region'==''` before main loop |
| Join | 2-key: `Kategorie_` + `Einheit_Na` |
| Main loop | Standard tahs logic (same as GR/JU/SG/SO) |
| Post-loop regional corrections | Hardcoded 6 unit groups using `storeg_1=[1,"1"]` (both int and str — legacy quirk) and `storeg_2abc=["2a","2b","2c"]`: `'55'/'55'` storeg==1→nais1='51',nais2='46M',hochmontan; storeg 2abc→nais1='55',hochmontan. `'55C'/'55*'` and `'55C'/''`: storeg==1→nais1='46M'; storeg 2abc→nais1='55*'. `'72'/'72'` and `'72L'/'72'`: nais1='72'/'59'; hs='sa osa'; tahs by hs1975 (==9→subalpin, else→obersubalpin); null hs1975→obersubalpin. |
| Post-loop fills | tahsue for ue==1; nais construction; fill tahs from hs1975 |
| Output | fid + area; filter area > 0 |
| Intermediate save | Writes `stok_gdf_attributed_temp.gpkg` after raster stats |

---

## ZH — Zürich ✓

| Aspect | Difference |
|--------|-----------|
| Taheute | Direct `gpd.sjoin` (no groupby); `joinid` set **after** sjoin |
| Storeg | sjoin + groupby min (Waldstandortregionen_2024_TI4ab_Final_GR.gpkg) |
| Radiation | Quantile |
| Dict variant | `extended` |
| Excel format | Columns `['id','EK72','NAIS','Bedingung Höhenstufe','nais1','nais2','tahs']`; filtered to `nais1 != '-'`; `'tahs'` column contains hs abbreviation strings; `'Bedingung Höhenstufe'` loaded but not used — all rows processed unconditionally |
| Join | 2-key: `EK72` + `NAIS` |
| Main loop | Standard tahs logic (same as GR/JU/SG/SO/UR) |
| Post-loop | tahsue fill; filter `tahs != ''`; fill tahs from hs1975; EK72 corrections (`EK72=='61M'`/`NAIS=='61(67)'` and `EK72=='62M'`/`NAIS=='62(67)'` → tahs='obermontan', tahsue='obermontan', nais='63', nais1='63', nais2=''); nais construction (ue==1 overwrites the corrected `nais='63'` back to `'63()'` — legacy quirk since ue is not reset) |
| Output | area filter (`area > 0`) + null geometry filter |
| Intermediate save | Writes `stok_gdf_attributed_temp.gpkg` after raster stats |
