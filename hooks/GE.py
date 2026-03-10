"""hooks/GE.py — custom hoehenstufen logic for Geneva.

Differences from standard flow:
- taheute = 1 (constant, no spatial join; Geneva is outside the Tannenareale).
- No storeg join.
- Radiation: quantile method.
- 3-key join: VEGETATION + NO_TYPOLOG + MOSAIQUE.
  Exception: the 'else' branch (simple nais) only uses 2-key mask
  VEGETATION + NO_TYPOLOG — matches legacy behaviour.
- Simplified tahs: per-polygon loop — 'collin' if 'co' in hs and hs1975==2,
  else 'submontan'. No raster-based disambiguation.
- tahsue = tahs for all ue==1 and mo==1 polygons.
"""

import os
import geopandas as gpd
import pandas as pd

from sensiCHfunctions import (
    get_dicts,
    compute_slope_classification,
    compute_radiation_classification,
    compute_hoehenstufen_1975,
    parse_nais_tokens,
)


def run(cfg, workspace, codespace):
    kt = cfg["canton"]  # "GE"
    _, hs_dict_abk, _, _ = get_dicts(cfg["dict_variant"])

    # --- read excel ---
    excel_path = os.path.join(codespace, cfg["excel_file"])
    naiseinheitenunique = pd.read_excel(
        excel_path, sheet_name=cfg["excel_sheet"], dtype="str", engine="openpyxl")
    for col in ["nais", "hs", "VEGETATION", "NO_TYPOLOG", "MOSAIQUE"]:
        if col in naiseinheitenunique.columns:
            naiseinheitenunique.loc[naiseinheitenunique[col].isnull(), col] = ""
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["nais"] != ""]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["hs"] != ""]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["hs"].notnull()]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["hs"] != "nan"]

    # --- read shapefile ---
    shp_path = os.path.join(workspace, cfg["shapefile"])
    stok_gdf = gpd.read_file(shp_path)
    stok_gdf["joinid"] = stok_gdf.index

    # --- taheute = 1 (no spatial join) ---
    stok_gdf["taheute"] = 1

    # --- raster stats (no storeg) ---
    stok_gdf = compute_slope_classification(
        stok_gdf, os.path.join(workspace, cfg["raster_slope"]))
    stok_gdf = compute_radiation_classification(
        stok_gdf, os.path.join(workspace, cfg["raster_radiation"]), method="quantile")
    stok_gdf = compute_hoehenstufen_1975(
        stok_gdf, os.path.join(workspace, cfg["raster_hs"]))

    stok_gdf.to_file(os.path.join(workspace, kt, "stok_gdf_attributed_temp.gpkg"))

    # --- init translation columns ---
    stok_gdf["nais"] = ""
    stok_gdf["nais1"] = ""
    stok_gdf["nais2"] = ""
    stok_gdf["mo"] = 0
    stok_gdf["ue"] = 0
    stok_gdf["hs"] = ""
    stok_gdf["tahs"] = ""
    stok_gdf["tahsue"] = ""

    for col in ["VEGETATION", "MOSAIQUE", "NO_TYPOLOG"]:
        if col in stok_gdf.columns:
            stok_gdf.loc[stok_gdf[col].isnull(), col] = ""
    for col in ["MOSAIQUE", "VEGETATION", "NO_TYPOLOG"]:
        if col in naiseinheitenunique.columns:
            naiseinheitenunique.loc[naiseinheitenunique[col].isnull(), col] = ""

    # re-filter after null-fill
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["nais"] != ""]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["hs"] != ""]

    # --- NaiS translation loop (3-key join, simplified) ---
    for _, row in naiseinheitenunique.iterrows():
        kantonseinheit = row["VEGETATION"]
        NO_TYPOLOG = row["NO_TYPOLOG"]
        MOSAIQUE = row["MOSAIQUE"]
        nais = row["nais"]
        nais_tokens = parse_nais_tokens(nais)

        mask3 = (
            (stok_gdf["VEGETATION"] == kantonseinheit) &
            (stok_gdf["NO_TYPOLOG"] == NO_TYPOLOG) &
            (stok_gdf["MOSAIQUE"] == MOSAIQUE)
        )
        mask2 = (
            (stok_gdf["VEGETATION"] == kantonseinheit) &
            (stok_gdf["NO_TYPOLOG"] == NO_TYPOLOG)
        )

        stok_gdf.loc[mask3, "nais"] = nais
        stok_gdf.loc[mask3, "hs"] = row["hs"]

        if "(" in nais:
            stok_gdf.loc[mask3, "nais1"] = nais_tokens[0] if len(nais_tokens) > 0 else ""
            stok_gdf.loc[mask3, "nais2"] = nais_tokens[1] if len(nais_tokens) > 1 else ""
            stok_gdf.loc[mask3, "ue"] = 1
        elif "/" in nais:
            stok_gdf.loc[mask3, "nais1"] = nais_tokens[0] if len(nais_tokens) > 0 else ""
            stok_gdf.loc[mask3, "nais2"] = nais_tokens[1] if len(nais_tokens) > 1 else ""
            stok_gdf.loc[mask3, "mo"] = 1
            stok_gdf.loc[mask3, "ue"] = 1
        else:
            # 'else' uses 2-key mask (no MOSAIQUE) — matches legacy
            if nais != "":
                stok_gdf.loc[mask2, "nais1"] = nais_tokens[0] if len(nais_tokens) > 0 else ""
                stok_gdf.loc[mask2, "nais2"] = ""
            else:
                stok_gdf.loc[mask2, "nais1"] = ""

    # --- simplified tahs: collin if 'co' in hs and hs1975==2, else submontan ---
    for index, row in stok_gdf.iterrows():
        if "co" in row["hs"] and row["hs1975"] == 2:
            stok_gdf.loc[index, "tahs"] = hs_dict_abk["co"]   # "collin"
        else:
            stok_gdf.loc[index, "tahs"] = hs_dict_abk["sm"]   # "submontan"

    # tahsue = tahs for all ue==1 and mo==1
    stok_gdf.loc[stok_gdf["ue"] == 1, "tahsue"] = stok_gdf["tahs"]
    stok_gdf.loc[stok_gdf["mo"] == 1, "tahsue"] = stok_gdf["tahs"]

    # --- select output columns and write ---
    out_cols = [c for c in cfg["output_cols"] if c in stok_gdf.columns]
    stok_gdf = stok_gdf[out_cols]

    out_path = os.path.join(workspace, kt, "stok_gdf_attributed.gpkg")
    stok_gdf.to_file(out_path)
    print(f"Wrote {out_path}")

    # --- treeapp export ---
    treeapp_cols = [c for c in cfg.get("treeapp_cols", []) if c in stok_gdf.columns]
    if treeapp_cols:
        treeapp = stok_gdf[treeapp_cols]
        tp_path = os.path.join(workspace, kt, f"{kt}_treeapp.gpkg")
        treeapp.to_file(tp_path, layer=f"{kt}_treeapp", driver="GPKG")
        print(f"Wrote {tp_path}")

    print("done")
