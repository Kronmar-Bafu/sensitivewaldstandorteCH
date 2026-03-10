"""hooks/JU.py — custom hoehenstufen logic for Jura.

Differences from standard flow:
- Shapefile: gpkg with long layer name; sliced to ['association','etiquette',
  'joinid','geometry'] immediately after read.
- Taheute: gpd.overlay intersection (Tannenareale2025.gpkg, same drop_cols as BE).
- Storeg: sjoin + groupby min (Waldstandortregionen_2024_TI4ab_Final_GR.gpkg).
- Excel: pre-split format (nais1/nais2/hs); selects columns
  ['association','etiquette','BedingungHoehenstufe','nais1','nais2','hs'];
  filtered to nais1 != '' and not null.
- Pre-loop corrections: 8 blocks of hs1975-conditional overrides for
  association in {'38','38w'} × specific etiquette values.
- Main loop: only rows where BedingungHoehenstufe is null.
  Loop sets nais1/nais2/hs/ue/tahs/tahsue (no nais — constructed post-loop).
  tahs: single→direct; multi-hs with '('→tahs/tahsue; multi-hs without '('→
  per-polygon hs1975 lookup, fallback to last element.
- Post-loop fills:
    tahsue for ue==1 where empty.
    nais = nais1+'('+nais2+')' for ue==1; nais = nais1 for ue==0.
    nais1=='39' and tahs=='': → tahs='submontan'.
    nais1=='39*' and tahs=='': → tahs='untermontan'.
    Fill tahs from hs1975 for any remaining empty tahs.
    Fill tahsue for ue==1 where still empty.
- Adds fid and area columns; filters area > 0.
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

# Pre-loop corrections for association=='38' / '38w'
# Each entry: (association, etiquette, nais1_low, nais2_low, hs_low,
#                                      nais1_high, nais2_high, hs_high)
# "low"  → hs1975 <= 4;  "high" → hs1975 > 4
_CORRECTIONS_38 = [
    # (assoc,  etiquette,          nais1_lo, nais2_lo, hs_lo,   nais1_hi, nais2_hi, hs_hi)
    ("38",  "38",               "39",  "",   "co sm", "39*", "",   "um"),
    ("38",  "38 rocher",        "39",  "",   "co sm", "39*", "",   "um"),
    ("38",  "38(14a)",          "39",  "14", "sm",    "39*", "14", "um"),
    ("38",  "38(38w)",          "39",  "",   "co sm", "39*", "",   "um"),
    ("38",  "38-38w rocher",    "39",  "",   "co sm", "39*", "",   "um"),
    ("38w", "38w",              "39",  "",   "co sm", "39*", "",   "um"),
    ("38w", "38w(14w)",         "39",  "14", "sm",    "39*", "14", "um"),
    ("38w", "38w(14w-16w)",     "39",  "14", "sm",    "39*", "14", "um"),
]


def _parse_hs_tokens(hs_val):
    return hs_val.replace("/", " ").replace("(", " ").replace(")", "").replace("  ", " ").strip().split()


def run(cfg, workspace, codespace):
    kt = cfg["canton"]  # "JU"
    _, hs_dict_abk, _, hsmod_dict_kurz = get_dicts(cfg["dict_variant"])

    # --- read excel ---
    excel_path = os.path.join(codespace, cfg["excel_file"])
    naiseinheitenunique = pd.read_excel(
        excel_path, sheet_name=cfg["excel_sheet"], dtype="str", engine="openpyxl")
    naiseinheitenunique = naiseinheitenunique[
        ["association", "etiquette", "BedingungHoehenstufe", "nais1", "nais2", "hs"]]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["nais1"] != ""]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["nais1"].notnull()]
    naiseinheitenunique.loc[naiseinheitenunique["nais2"].isnull(), "nais2"] = ""

    # --- read shapefile ---
    shp_path = os.path.join(workspace, cfg["shapefile"])
    layer_name = "env.env_03_01_phytosociologie_stations_forestieres"
    try:
        stok_gdf = gpd.read_file(shp_path, layer=layer_name)
    except Exception:
        stok_gdf = gpd.read_file(shp_path)
    stok_gdf["joinid"] = stok_gdf.index
    stok_gdf = stok_gdf[["association", "etiquette", "joinid", "geometry"]]

    # --- taheute: overlay intersection ---
    taheute_path = os.path.join(workspace, cfg["taheute_file"])
    taheute = gpd.read_file(taheute_path)
    taheute.rename(columns={"Code_Ta": "taheute"}, inplace=True)
    drop_cols = [c for c in ["id", "Region_de", "Region_fr", "Region_it", "Region_en",
                              "Code", "Subcode", "Code_Bu", "Code_Fi", "Flaeche"]
                 if c in taheute.columns]
    taheute.drop(columns=drop_cols, inplace=True)
    stok_gdf = gpd.overlay(stok_gdf, taheute, how="intersection")

    # --- storeg: sjoin + groupby min ---
    storeg_path = os.path.join(workspace, cfg["storeg_file"])
    storeg_layer = cfg.get("storeg_layer")
    storeg = gpd.read_file(storeg_path, layer=storeg_layer) if storeg_layer else gpd.read_file(storeg_path)
    storeg.rename(columns={"Subcode": "storeg"}, inplace=True)
    drop_cols_s = [c for c in ["id", "Region_de", "Region_fr", "Region_it", "Region_en",
                                "Code", "Code_Bu", "Code_Fi", "Flaeche"]
                   if c in storeg.columns]
    storeg.drop(columns=drop_cols_s, inplace=True)
    if "index_right" in stok_gdf.columns:
        stok_gdf = stok_gdf.drop(columns=["index_right"])
    stok_gdf_storeg = stok_gdf.sjoin(storeg, how="left", predicate="intersects")
    grouped = stok_gdf_storeg[["joinid", "storeg"]].groupby("joinid").min()
    stok_gdf = stok_gdf.merge(grouped, on="joinid", how="left")

    # --- raster zonal stats ---
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

    for col in ["association", "etiquette"]:
        stok_gdf.loc[stok_gdf[col].isnull(), col] = ""
    for col in ["association", "etiquette", "nais1", "nais2", "hs"]:
        naiseinheitenunique.loc[naiseinheitenunique[col].isnull(), col] = ""

    # --- pre-loop corrections for association=='38'/'38w' ---
    for assoc, etiq, n1_lo, n2_lo, hs_lo, n1_hi, n2_hi, hs_hi in _CORRECTIONS_38:
        m_lo = ((stok_gdf["association"] == assoc) &
                (stok_gdf["etiquette"] == etiq) &
                (stok_gdf["hs1975"] <= 4))
        m_hi = ((stok_gdf["association"] == assoc) &
                (stok_gdf["etiquette"] == etiq) &
                (stok_gdf["hs1975"] > 4))
        stok_gdf.loc[m_lo, "nais1"] = n1_lo
        stok_gdf.loc[m_lo, "nais2"] = n2_lo
        stok_gdf.loc[m_lo, "hs"] = hs_lo
        stok_gdf.loc[m_hi, "nais1"] = n1_hi
        stok_gdf.loc[m_hi, "nais2"] = n2_hi
        stok_gdf.loc[m_hi, "hs"] = hs_hi

    # --- filter excel to rows without BedingungHoehenstufe ---
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["BedingungHoehenstufe"].isnull()]

    # --- main translation loop ---
    for _, row in naiseinheitenunique.iterrows():
        kantonseinheit = row["association"]
        etiquette = row["etiquette"]
        nais1 = row["nais1"]
        nais2 = row["nais2"]
        hs_val = row["hs"]
        hslist = _parse_hs_tokens(hs_val)

        mask = (stok_gdf["association"] == kantonseinheit) & (stok_gdf["etiquette"] == etiquette)

        stok_gdf.loc[mask, "nais1"] = nais1
        stok_gdf.loc[mask, "nais2"] = nais2
        stok_gdf.loc[mask, "hs"] = hs_val
        if nais2 != "":
            stok_gdf.loc[mask, "ue"] = 1

        if len(hslist) == 1:
            stok_gdf.loc[mask, "tahs"] = hs_dict_abk[hslist[0]]
        else:
            if "(" in hs_val:
                stok_gdf.loc[mask, "tahs"] = hs_dict_abk[hslist[0]]
                stok_gdf.loc[mask, "tahsue"] = hs_dict_abk[hslist[1]]
            else:
                fallback = hs_dict_abk[hslist[-1]]
                for idx2, row2 in stok_gdf[mask].iterrows():
                    hs1975_val = row2["hs1975"]
                    if hs1975_val is not None and hs1975_val > 0:
                        hsmod = hsmod_dict_kurz.get(int(hs1975_val))
                        if hsmod and hsmod in row2["hs"].strip().split():
                            stok_gdf.loc[idx2, "tahs"] = hs_dict_abk[hsmod]
                            continue
                    stok_gdf.loc[idx2, "tahs"] = fallback

    # --- post-loop fills ---
    # tahsue for ue==1 where empty
    stok_gdf.loc[(stok_gdf["nais2"] != "") & (stok_gdf["ue"] == 1) & (stok_gdf["tahsue"] == ""),
                 "tahsue"] = stok_gdf["tahs"]

    # construct nais column
    stok_gdf.loc[(stok_gdf["nais2"] != "") & (stok_gdf["ue"] == 1), "nais"] = (
        stok_gdf["nais1"] + "(" + stok_gdf["nais2"] + ")")
    stok_gdf.loc[(stok_gdf["nais2"] == "") & (stok_gdf["ue"] == 0), "nais"] = stok_gdf["nais1"]

    # fallback tahs for association=='38' corrections
    stok_gdf.loc[(stok_gdf["nais1"] == "39") & (stok_gdf["tahs"] == ""), "tahs"] = "submontan"
    stok_gdf.loc[(stok_gdf["nais1"] == "39*") & (stok_gdf["tahs"] == ""), "tahs"] = "untermontan"

    # fill tahs from hs1975 for any remaining empty
    for index, row in stok_gdf.iterrows():
        if row["tahs"] == "" and row["hs1975"] is not None and row["hs1975"] > 0:
            hsmod = hsmod_dict_kurz.get(int(row["hs1975"]))
            if hsmod:
                stok_gdf.loc[index, "tahs"] = hs_dict_abk[hsmod]

    # final tahsue fill
    stok_gdf.loc[(stok_gdf["ue"] == 1) & (stok_gdf["tahsue"] == ""), "tahsue"] = stok_gdf["tahs"]

    # --- add fid, area; filter area > 0 ---
    stok_gdf["fid"] = stok_gdf.index
    stok_gdf["area"] = stok_gdf.geometry.area
    stok_gdf = stok_gdf[stok_gdf["area"] > 0]

    # --- select output columns and write ---
    out_cols = [c for c in cfg["output_cols"] if c in stok_gdf.columns]
    stok_gdf = stok_gdf[out_cols]

    out_path = os.path.join(workspace, kt, "stok_gdf_attributed.gpkg")
    stok_gdf.to_file(out_path, layer="stok_gdf_attributed", driver="GPKG")
    print(f"Wrote {out_path}")

    # --- treeapp export ---
    treeapp_cols = [c for c in cfg.get("treeapp_cols", []) if c in stok_gdf.columns]
    if treeapp_cols:
        treeapp = stok_gdf[treeapp_cols]
        tp_path = os.path.join(workspace, kt, f"{kt}_treeapp.gpkg")
        treeapp.to_file(tp_path, layer=f"{kt}_treeapp", driver="GPKG")
        print(f"Wrote {tp_path}")

    print("done")
