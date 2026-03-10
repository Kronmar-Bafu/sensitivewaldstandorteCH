"""hooks/GR.py — custom hoehenstufen logic for Graubünden.

Differences from standard flow:
- Input is a pre-processed gpkg (raster stats already applied); no raster
  zonal stats are run.
- Column renames on read: ass_gr→ASS_GR, naisbg→NAISbg, meanslopep→meanslopeprc.
- 43 ASS_GR value corrections (leading-digit artefacts from preprocessing).
- NAISbg whitespace fix: remove spaces from NAISbg values in stok_gdf.
- Excel pre-pass: nais1/nais2/ue/mo computed on the excel rows before the
  main translation loop.
- Excel filtered to Bedingung=='' before the main loop (rows with a Bedingung
  value are not processed — the regional Bedingung handling in the legacy
  script is dead code because of this filter).
- Main translation loop: assign nais/nais1/nais2/hs/ue/mo/tahs/tahsue.
  tahs assignment:
    single hs → direct lookup
    multi-hs with '(' → tahs=hslist[0], tahsue=hslist[1]
    multi-hs without '(' → per-polygon hs1975 raster lookup;
      if hs1975 matches a value in hslist → use that;
      otherwise → use last element in hslist (fallback).
- Post-loop: fill nais1 for ue==0; fill tahsue for ue==1 and mo==1.
- Dict variant: grvs.
"""

import os
import geopandas as gpd
import pandas as pd

from sensiCHfunctions import get_dicts

# 43 ASS_GR value corrections (leading-digit artefacts from preprocessing)
ASS_GR_CORRECTIONS = {
    "747D":  "47D",
    "358C":  "58C",
    "257C":  "57C",
    "259":   "59",
    "0AV":   "AV",
    "558L":  "58L",
    "957V":  "57V",
    "447M":  "47M",
    "147V":  "47V",
    "452":   "52",
    "160":   "60",
    "9AV":   "AV",
    "555*":  "55*",
    "959*":  "59*",
    "060A":  "60A",
    "247":   "47",
    "833V":  "33V",
    "134L":  "34L",
    "934A":  "34A",
    "842C":  "42C",
    "942Q":  "42Q",
    "034F":  "34F",
    "858V":  "58V",
    "540P":  "40P",
    "947H":  "47H",
    "159A":  "59A",
    "253*":  "53*",
    "132*":  "32*",
    "632V":  "32V",
    "524S":  "24S",
    "547*":  "47*",
    "157BL": "57BL",
    "647BL": "47BL",
    "258BL": "58BL",
}


def _parse_nais_tokens(nais):
    return nais.replace("/", " ").replace("(", " ").replace(")", "").replace("  ", " ").strip().split()


def run(cfg, workspace, codespace):
    kt = cfg["canton"]  # "GR"
    _, hs_dict_abk, _, hsmod_dict_kurz = get_dicts(cfg["dict_variant"])

    # --- read and filter excel ---
    excel_path = os.path.join(codespace, cfg["excel_file"])
    naiseinheitenunique = pd.read_excel(
        excel_path, sheet_name=cfg["excel_sheet"], dtype="str", engine="openpyxl")

    for col in ["ASS_GR", "NAISbg", "nais", "hs"]:
        naiseinheitenunique.loc[naiseinheitenunique[col].isnull(), col] = ""
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["ASS_GR"] != ""]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["NAISbg"] != ""]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["nais"] != ""]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["hs"] != ""]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["hs"] != "nan"]

    # --- excel pre-pass: compute nais1/nais2/ue/mo on excel rows ---
    naiseinheitenunique["nais1"] = ""
    naiseinheitenunique["nais2"] = ""
    naiseinheitenunique["ue"] = 0
    naiseinheitenunique["mo"] = 0
    for idx, row in naiseinheitenunique.iterrows():
        nais = row["nais"]
        tokens = _parse_nais_tokens(nais)
        if "(" in nais and len(tokens) > 1:
            naiseinheitenunique.loc[idx, "nais1"] = tokens[0]
            naiseinheitenunique.loc[idx, "nais2"] = tokens[1]
            naiseinheitenunique.loc[idx, "ue"] = 1
        elif "/" in nais and len(tokens) > 1:
            naiseinheitenunique.loc[idx, "nais1"] = tokens[0]
            naiseinheitenunique.loc[idx, "nais2"] = tokens[1]
            naiseinheitenunique.loc[idx, "ue"] = 1
            naiseinheitenunique.loc[idx, "mo"] = 1
        else:
            naiseinheitenunique.loc[idx, "nais1"] = tokens[0] if tokens else ""

    # --- filter to Bedingung=='' (rows with a condition are not processed) ---
    if "Bedingung" in naiseinheitenunique.columns:
        naiseinheitenunique.loc[naiseinheitenunique["Bedingung"].isnull(), "Bedingung"] = ""
        naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["Bedingung"] == ""]

    # --- read pre-processed shapefile ---
    shp_path = os.path.join(workspace, cfg["shapefile"])
    layer = os.path.splitext(os.path.basename(shp_path))[0]
    try:
        stok_gdf = gpd.read_file(shp_path, layer=layer)
    except Exception:
        stok_gdf = gpd.read_file(shp_path)

    # column renames
    rename_map = {}
    if "ass_gr" in stok_gdf.columns:
        rename_map["ass_gr"] = "ASS_GR"
    if "naisbg" in stok_gdf.columns:
        rename_map["naisbg"] = "NAISbg"
    if "meanslopep" in stok_gdf.columns:
        rename_map["meanslopep"] = "meanslopeprc"
    if rename_map:
        stok_gdf.rename(columns=rename_map, inplace=True)

    stok_gdf["joinid"] = stok_gdf.index

    # --- ASS_GR corrections ---
    for wrong, right in ASS_GR_CORRECTIONS.items():
        stok_gdf.loc[stok_gdf["ASS_GR"] == wrong, "ASS_GR"] = right

    # --- NAISbg whitespace fix ---
    for item in stok_gdf["NAISbg"].unique():
        if isinstance(item, str) and " " in item:
            stok_gdf.loc[stok_gdf["NAISbg"] == item, "NAISbg"] = item.replace(" ", "")

    # --- init translation columns ---
    stok_gdf["nais"] = ""
    stok_gdf["nais1"] = ""
    stok_gdf["nais2"] = ""
    stok_gdf["mo"] = 0
    stok_gdf["ue"] = 0
    stok_gdf["hs"] = ""
    stok_gdf["tahs"] = ""
    stok_gdf["tahsue"] = ""

    for col in ["ASS_GR", "NAISbg"]:
        stok_gdf.loc[stok_gdf[col].isnull(), col] = ""
        stok_gdf.loc[stok_gdf[col] == "<Null>", col] = ""

    # --- main translation loop (only Bedingung=='' rows) ---
    for _, row in naiseinheitenunique.iterrows():
        kantonseinheit = row["ASS_GR"]
        naisbg = row["NAISbg"]
        nais = row["nais"]
        nais1 = row["nais1"]
        nais2 = row["nais2"]
        ue = int(row["ue"]) if row["ue"] != "" else 0
        mo = int(row["mo"]) if row["mo"] != "" else 0
        hs_val = row["hs"]
        hslist = _parse_nais_tokens(hs_val)

        mask = (stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == naisbg)

        stok_gdf.loc[mask, "nais"] = nais
        stok_gdf.loc[mask, "nais1"] = nais1
        stok_gdf.loc[mask, "nais2"] = nais2
        stok_gdf.loc[mask, "hs"] = hs_val
        if nais2 != "":
            stok_gdf.loc[mask, "ue"] = 1
        if mo:
            stok_gdf.loc[mask, "mo"] = 1

        # tahs assignment
        if len(hslist) == 1:
            stok_gdf.loc[mask, "tahs"] = hs_dict_abk[hslist[0]]
        else:
            if "(" in hs_val:
                stok_gdf.loc[mask, "tahs"] = hs_dict_abk[hslist[0]]
                stok_gdf.loc[mask, "tahsue"] = hs_dict_abk[hslist[1]]
            else:
                # per-polygon hs1975 lookup; fallback to last element
                fallback_tahs = hs_dict_abk[hslist[-1]]
                for idx2, row2 in stok_gdf[mask].iterrows():
                    hs1975_val = row2["hs1975"]
                    if hs1975_val is not None and hs1975_val > 0:
                        hsmod = hsmod_dict_kurz.get(int(hs1975_val))
                        if hsmod and hsmod in hs_val.strip().split():
                            stok_gdf.loc[idx2, "tahs"] = hs_dict_abk[hsmod]
                            continue
                    stok_gdf.loc[idx2, "tahs"] = fallback_tahs

    # --- post-loop fills ---
    stok_gdf.loc[(stok_gdf["ue"] == 0) & (stok_gdf["nais1"] == ""), "nais1"] = stok_gdf["nais"]
    stok_gdf.loc[(stok_gdf["ue"] == 1) & (stok_gdf["tahsue"] == ""), "tahsue"] = stok_gdf["tahs"]
    stok_gdf.loc[(stok_gdf["mo"] == 1) & (stok_gdf["tahsue"] == ""), "tahsue"] = stok_gdf["tahs"]

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
