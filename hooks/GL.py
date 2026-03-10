"""hooks/GL.py — custom hoehenstufen logic for Glarus.

Differences from standard flow:
- taheute = 1, storeg = 1 (constants; no spatial joins needed).
- Radiation: fixed thresholds (>=147 → 1, <=112 → -1).
- Excel has a 'NaiS' column (uppercase) plus 'Bedingung Hangneigung' and
  'Bedingung Höhenstufe' columns that drive tahs assignment per polygon.
- tahs/tahsue assignment logic:
    1. Bedingung Hangneigung ('<60%' or '>60%'): apply tahs only to polygons
       matching the slope condition.
    2. Bedingung Höhenstufe ('sm um', 'hm', 'om', 'om hm', 'sa'): assign
       fixed tahs based on hs1975 raster value.
    3. If '(' in hs and len(hslist)>1: always set tahs=hslist[0],
       tahsue=hslist[1] (overrides Bedingung assignments).
    4. Else, if no Bedingung conditions: single hs → direct assignment;
       multi hs → pick from hs1975 raster, fall back to last.
- Post-loop "fixe Uebergaenge": for any polygon where '(' in its hs field,
  re-apply tahs=hslist[0], tahsue=hslist[1].
- Special case: nais=='AV' and hs1975==-1 → tahs='subalpin'.
- Fill tahsue for ue==1 polygons where tahsue still empty.
"""

import os
import geopandas as gpd
import pandas as pd

from sensiCHfunctions import (
    get_dicts,
    compute_slope_classification,
    compute_radiation_classification,
    compute_hoehenstufen_1975,
)

# Reverse dict: abbreviation → numeric raster code (GL-specific)
HSDICTZUZAHLEN = {"co": 2, "sm": 4, "um": 5, "om": 6, "hm": 8, "sa": 9, "osa": 10}


def _hslist_from_hs(hs_val):
    """Parse hs field into list of abbreviations."""
    return hs_val.replace("/", " ").replace("(", " ").replace(")", "").strip().split()


def run(cfg, workspace, codespace):
    kt = cfg["canton"]  # "GL"
    _, hs_dict_abk, _, hsmod_dict_kurz = get_dicts(cfg["dict_variant"])

    # --- read excel ---
    excel_path = os.path.join(codespace, cfg["excel_file"])
    naiseinheitenunique = pd.read_excel(excel_path, dtype="str", engine="openpyxl")
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["NaiS"].notnull()]

    # --- read shapefile ---
    shp_path = os.path.join(workspace, cfg["shapefile"])
    stok_gdf = gpd.read_file(shp_path)
    stok_gdf["joinid"] = stok_gdf.index

    # --- taheute and storeg (constants) ---
    stok_gdf["taheute"] = 1
    stok_gdf["storeg"] = 1

    # --- raster zonal stats ---
    stok_gdf = compute_slope_classification(
        stok_gdf, os.path.join(workspace, cfg["raster_slope"]))
    stok_gdf = compute_radiation_classification(
        stok_gdf, os.path.join(workspace, cfg["raster_radiation"]), method="fixed")
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
    stok_gdf["kantonseinheit"] = ""

    # null-fill join key columns
    for col in ["wg_haupt", "wg_zusatz"]:
        if col in stok_gdf.columns:
            stok_gdf.loc[stok_gdf[col].isnull(), col] = ""
        if col in naiseinheitenunique.columns:
            naiseinheitenunique.loc[naiseinheitenunique[col].isnull(), col] = ""

    # --- NaiS translation loop with Bedingung logic ---
    for _, row in naiseinheitenunique.iterrows():
        kantonseinheit1 = row["wg_haupt"]
        kantonseinheit2 = row["wg_zusatz"]
        nais = row["NaiS"]
        hs_val = row["hs"]
        bedingung_hang = row.get("Bedingung Hangneigung", "")
        bedingung_hs = row.get("Bedingung Höhenstufe", "")
        if pd.isnull(bedingung_hang):
            bedingung_hang = ""
        if pd.isnull(bedingung_hs):
            bedingung_hs = ""

        hslist = _hslist_from_hs(hs_val)

        mask = (
            (stok_gdf["wg_haupt"] == kantonseinheit1) &
            (stok_gdf["wg_zusatz"] == kantonseinheit2)
        )

        stok_gdf.loc[mask, "nais"] = nais
        stok_gdf.loc[mask, "hs"] = hs_val
        stok_gdf.loc[mask, "kantonseinheit"] = row.get("Einheit GL", "")

        # parse nais1/nais2/ue/mo
        nais_tokens = nais.replace("/", " ").replace("(", " ").replace(")", "").strip().split()
        if "(" in nais:
            stok_gdf.loc[mask, "nais1"] = nais_tokens[0] if len(nais_tokens) > 0 else ""
            stok_gdf.loc[mask, "nais2"] = nais_tokens[1] if len(nais_tokens) > 1 else ""
            stok_gdf.loc[mask, "ue"] = 1
        elif "/" in nais:
            stok_gdf.loc[mask, "nais1"] = nais_tokens[0] if len(nais_tokens) > 0 else ""
            stok_gdf.loc[mask, "nais2"] = nais_tokens[1] if len(nais_tokens) > 1 else ""
            stok_gdf.loc[mask, "mo"] = 1
        else:
            stok_gdf.loc[mask, "nais1"] = nais_tokens[0] if len(nais_tokens) > 0 else ""

        # --- Bedingung Hangneigung ---
        if bedingung_hang in ("<60%", ">60%"):
            if bedingung_hang == "<60%":
                slope_mask = mask & (stok_gdf["meanslopeprc"] < 60)
            else:
                slope_mask = mask & (stok_gdf["meanslopeprc"] >= 60)

            if len(hslist) == 1:
                stok_gdf.loc[slope_mask, "tahs"] = hs_dict_abk[hslist[0]]
                stok_gdf.loc[slope_mask, "tahsue"] = hs_dict_abk[hslist[0]]
            else:
                if "(" in hs_val:
                    stok_gdf.loc[slope_mask, "tahs"] = hs_dict_abk[hslist[0]]
                    stok_gdf.loc[slope_mask, "tahsue"] = hs_dict_abk[hslist[1]]
                else:
                    # legacy: set tahs/tahsue for opposite slope (>=60) side
                    opp_mask = mask & (stok_gdf["meanslopeprc"] >= 60)
                    stok_gdf.loc[opp_mask, "tahs"] = hs_dict_abk[hslist[1]]
                    stok_gdf.loc[opp_mask, "tahsue"] = hs_dict_abk[hslist[1]]

        # --- Bedingung Höhenstufe ---
        if bedingung_hs in ("sm um", "hm", "om", "om hm", "sa"):
            if bedingung_hs == "sm um":
                stok_gdf.loc[mask & stok_gdf["hs1975"].isin([2, 4]), "tahs"] = "submontan"
                stok_gdf.loc[mask & stok_gdf["hs1975"].isin([5, 6, 8, 9]), "tahs"] = "untermontan"
            elif bedingung_hs == "om hm":
                stok_gdf.loc[mask & stok_gdf["hs1975"].isin([2, 4, 5, 6]), "tahs"] = "obermontan"
                stok_gdf.loc[mask & stok_gdf["hs1975"].isin([8, 9]), "tahs"] = "hochmontan"
            elif bedingung_hs == "hm":
                stok_gdf.loc[mask, "tahs"] = "hochmontan"
            elif bedingung_hs == "om":
                stok_gdf.loc[mask, "tahs"] = "obermontan"
            elif bedingung_hs == "sa":
                stok_gdf.loc[mask, "tahs"] = "subalpin"

        # --- hs with '(' → fixed tahs/tahsue (overwrites Bedingung) ---
        if "(" in hs_val and len(hslist) > 1:
            stok_gdf.loc[mask, "tahs"] = hs_dict_abk[hslist[0]]
            stok_gdf.loc[mask, "tahsue"] = hs_dict_abk[hslist[1]]
        # --- no Bedingung, no '(': use hs1975 raster to pick from list ---
        elif ("(" not in hs_val and
              bedingung_hs not in ("sm um", "hm", "om", "om hm", "sa") and
              bedingung_hang not in ("<60%", ">60%")):
            if len(hslist) == 1:
                stok_gdf.loc[mask, "tahs"] = hs_dict_abk[hslist[0]]
                stok_gdf.loc[mask, "tahsue"] = hs_dict_abk[hslist[0]]
            else:
                hslist_zahlen = [HSDICTZUZAHLEN[h] for h in hslist if h in HSDICTZUZAHLEN]
                for hszahl in hslist_zahlen:
                    abk = hsmod_dict_kurz[hszahl]
                    stok_gdf.loc[mask & (stok_gdf["hs1975"] == hszahl), "tahs"] = hs_dict_abk[abk]
                    stok_gdf.loc[mask & (stok_gdf["hs1975"] == hszahl), "tahsue"] = hs_dict_abk[abk]
                # second element takes priority for its numeric code
                if len(hslist_zahlen) > 1:
                    abk2 = hsmod_dict_kurz[hslist_zahlen[1]]
                    stok_gdf.loc[mask & (stok_gdf["hs1975"] == hslist_zahlen[1]), "tahs"] = hs_dict_abk[abk2]
                    stok_gdf.loc[mask & (stok_gdf["hs1975"] == hslist_zahlen[1]), "tahsue"] = hs_dict_abk[abk2]
                # fallback: polygons not matching any listed hs code → last in list
                last_abk = hsmod_dict_kurz[hslist_zahlen[-1]]
                stok_gdf.loc[mask & (~stok_gdf["hs1975"].isin(hslist_zahlen)), "tahs"] = hs_dict_abk[last_abk]
                stok_gdf.loc[mask & (~stok_gdf["hs1975"].isin(hslist_zahlen)), "tahsue"] = hs_dict_abk[last_abk]

    # --- fixe Uebergaenge: re-apply tahs/tahsue for any polygon where '(' in hs ---
    for index, row in stok_gdf.iterrows():
        if "(" in row["hs"]:
            hslist = _hslist_from_hs(row["hs"])
            stok_gdf.loc[index, "tahs"] = hs_dict_abk[hslist[0]]
            stok_gdf.loc[index, "tahsue"] = hs_dict_abk[hslist[1]]

    # --- special case: Gebüschwald AV with hs1975==-1 ---
    stok_gdf.loc[(stok_gdf["nais"] == "AV") & (stok_gdf["hs1975"] == -1), "tahs"] = "subalpin"

    # --- fill tahsue where ue==1 and tahsue still empty ---
    for index, row in stok_gdf.iterrows():
        if "(" in row["nais"] and row["ue"] == 1 and row["tahsue"] == "":
            hslist = _hslist_from_hs(row["hs"])
            if len(hslist) == 1:
                stok_gdf.loc[index, "tahsue"] = row["tahs"]

    # final fill for treeapp export
    stok_gdf.loc[
        (stok_gdf["ue"] == 1) & (stok_gdf["tahsue"] == "") & (stok_gdf["tahs"] != ""),
        "tahsue"
    ] = stok_gdf["tahs"]

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
