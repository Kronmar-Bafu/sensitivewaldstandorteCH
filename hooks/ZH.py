"""hooks/ZH.py — custom hoehenstufen logic for Zürich.

Differences from standard flow:
- Taheute: direct gpd.sjoin (no groupby); joinid set AFTER sjoin.
- Storeg: sjoin + groupby min (Waldstandortregionen_2024_TI4ab_Final_GR.gpkg).
- Radiation: quantile.
- Dict variant: extended.
- Excel: columns ['id','EK72','NAIS','Bedingung Höhenstufe','nais1','nais2','tahs'];
  filtered to nais1 != '-' and not null. 'tahs' column contains hs abbreviation strings
  (e.g. 'hm', 'sm(um)') used as hs. 'Bedingung Höhenstufe' loaded but not used —
  all rows processed unconditionally.
- Join: 2-key (EK72 + NAIS).
- Main loop: standard tahs logic (same as GR/JU/SG/SO/UR).
- Post-loop: tahsue fill; filter tahs != ''; fill tahs from hs1975; EK72 corrections
  (EK72=='61M'/NAIS=='61(67)' and EK72=='62M'/NAIS=='62(67)' →
   tahs='obermontan', tahsue='obermontan', nais='63', nais1='63', nais2='');
  nais construction (ue==1 overwrites nais again — legacy quirk).
- Area filter + null geometry filter.
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


def _parse_hs_tokens(hs_val):
    return hs_val.replace("/", " ").replace("(", " ").replace(")", "").replace("  ", " ").strip().split()


def run(cfg, workspace, codespace):
    kt = cfg["canton"]  # "ZH"
    _, hs_dict_abk, _, hsmod_dict_kurz = get_dicts(cfg["dict_variant"])

    # --- read excel ---
    excel_path = os.path.join(codespace, cfg["excel_file"])
    naiseinheitenunique = pd.read_excel(
        excel_path, sheet_name=cfg["excel_sheet"], dtype="str", engine="openpyxl")
    naiseinheitenunique = naiseinheitenunique[
        ["id", "EK72", "NAIS", "Bedingung Höhenstufe", "nais1", "nais2", "tahs"]]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["nais1"] != "-"]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["nais1"].notnull()]
    naiseinheitenunique.loc[naiseinheitenunique["nais2"].isnull(), "nais2"] = ""
    for col in ["EK72", "NAIS", "nais1", "nais2", "tahs"]:
        naiseinheitenunique.loc[naiseinheitenunique[col].isnull(), col] = ""

    # --- read shapefile ---
    shp_path = os.path.join(workspace, cfg["shapefile"])
    stok_gdf = gpd.read_file(shp_path)

    # --- taheute: direct sjoin (no groupby); joinid set after ---
    taheute_path = os.path.join(workspace, cfg["taheute_file"])
    taheute = gpd.read_file(taheute_path)
    taheute.rename(columns={"Code_Ta": "taheute"}, inplace=True)
    drop_ta = [c for c in ["id", "Region_de", "Region_fr", "Region_it", "Region_en",
                            "Code", "Subcode", "Code_Bu", "Code_Fi", "Flaeche"]
               if c in taheute.columns]
    taheute.drop(columns=drop_ta, inplace=True)
    stok_gdf = stok_gdf.sjoin(taheute, how="left", predicate="intersects")
    stok_gdf["joinid"] = stok_gdf.index

    # --- storeg: sjoin + groupby min ---
    storeg_path = os.path.join(workspace, cfg["storeg_file"])
    storeg_layer = cfg.get("storeg_layer")
    storeg = gpd.read_file(storeg_path, layer=storeg_layer) if storeg_layer else gpd.read_file(storeg_path)
    storeg.rename(columns={"Subcode": "storeg"}, inplace=True)
    drop_sr = [c for c in ["id", "Region_de", "Region_fr", "Region_it", "Region_en",
                            "Code", "Code_Bu", "Code_Fi", "Flaeche"]
               if c in storeg.columns]
    storeg.drop(columns=drop_sr, inplace=True)
    if "index_right" in stok_gdf.columns:
        stok_gdf = stok_gdf.drop(columns=["index_right"])
    joined_storeg = stok_gdf.sjoin(storeg, how="left", predicate="intersects")
    grouped = joined_storeg[["joinid", "storeg"]].groupby("joinid").min()
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

    for col in ["EK72", "NAIS"]:
        stok_gdf.loc[stok_gdf[col].isnull(), col] = ""

    # --- main translation loop (all rows; excel 'tahs' col used as hs string) ---
    for _, row in naiseinheitenunique.iterrows():
        ek72 = row["EK72"]
        nais_key = row["NAIS"]
        nais1 = row["nais1"]
        nais2 = row["nais2"]
        hs_val = row["tahs"]  # 'tahs' column contains hs abbreviations (e.g. 'hm', 'sm um')
        hslist = _parse_hs_tokens(hs_val)

        mask = (stok_gdf["EK72"] == ek72) & (stok_gdf["NAIS"] == nais_key)

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
    stok_gdf.loc[(stok_gdf["nais2"] != "") & (stok_gdf["ue"] == 1) & (stok_gdf["tahsue"] == ""),
                 "tahsue"] = stok_gdf["tahs"]

    # filter rows with no tahs (units without a translation)
    stok_gdf = stok_gdf[stok_gdf["tahs"] != ""]

    # fill tahs from hs1975 for remaining empty
    for index, row in stok_gdf.iterrows():
        if row["tahs"] == "" and row["hs1975"] is not None and row["hs1975"] > 0:
            hsmod = hsmod_dict_kurz.get(int(row["hs1975"]))
            if hsmod:
                stok_gdf.loc[index, "tahs"] = hs_dict_abk[hsmod]

    # --- EK72 corrections ---
    for ek72_val, nais_val in [("61M", "61(67)"), ("62M", "62(67)")]:
        m = (stok_gdf["EK72"] == ek72_val) & (stok_gdf["NAIS"] == nais_val)
        stok_gdf.loc[m, ["tahs", "tahsue"]] = ["obermontan", "obermontan"]
        stok_gdf.loc[m, ["nais", "nais1", "nais2"]] = ["63", "63", ""]

    # --- nais column construction (ue==1 overwrites nais set in EK72 corrections — legacy) ---
    stok_gdf.loc[(stok_gdf["nais2"] != "") & (stok_gdf["ue"] == 1), "nais"] = (
        stok_gdf["nais1"] + "(" + stok_gdf["nais2"] + ")")
    stok_gdf.loc[(stok_gdf["nais2"] == "") & (stok_gdf["ue"] == 0), "nais"] = stok_gdf["nais1"]

    # --- area filter + null geometry filter ---
    stok_gdf["area"] = stok_gdf.geometry.area
    stok_gdf = stok_gdf[stok_gdf["area"] > 0]
    stok_gdf = stok_gdf[stok_gdf["geometry"].notnull()]

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
