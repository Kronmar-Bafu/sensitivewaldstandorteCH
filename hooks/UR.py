"""hooks/UR.py — custom hoehenstufen logic for Uri.

Differences from standard flow:
- Taheute: gpd.overlay intersection (Tannenareale2025.gpkg, same as BE/JU/SG/SO).
- Storeg: sjoin + groupby min (Waldstandortregionen_2024_TI4ab_Final_GR.gpkg).
- Excel: pre-split format; columns ['Kategorie_','Einheit_Na','Bedingung Region',
  'Bedingung Höhenstufe','nais1','nais2','hs']; filtered to nais1 != '' and not null.
  'Bedingung Höhenstufe' is loaded but not used in processing.
- Bedingung Region filter: excel filtered to 'Bedingung Region'=='' before main loop.
- Join: 2-key (Kategorie_ + Einheit_Na).
- Main loop: standard tahs logic (same as GR/JU/SG/SO).
- Post-loop Bedingung Region corrections (hardcoded, 6 unit groups):
    '55'/'55'  storeg==1      → nais1='51', nais2='46M', hs/tahs/tahsue='hm/hochmontan'
    '55'/'55'  storeg 2a-2c   → nais1='55',              hs/tahs='hm/hochmontan'
    '55C'/'55*' storeg==1     → nais1='46M',             hs/tahs='hm/hochmontan'
    '55C'/'55*' storeg 2a-2c  → nais1='55*',             hs/tahs='hm/hochmontan'
    '55C'/''   storeg==1      → nais1='46M',             hs/tahs='hm/hochmontan'
    '55C'/''   storeg 2a-2c   → nais1='55*',             hs/tahs='hm/hochmontan'
    '72'/'72'  storeg==1/2+   → nais1='72'/'59', hs='sa osa', tahs=hs1975-conditional
    '72L'/'72' storeg==1/2+   → same as '72'
  Note: storeg matched against both int 1 and str '1' (legacy quirk).
- Post-loop fills: tahsue for ue==1; nais construction; fill tahs from hs1975.
- fid + area; filter area > 0.
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
    kt = cfg["canton"]  # "UR"
    _, hs_dict_abk, _, hsmod_dict_kurz = get_dicts(cfg["dict_variant"])

    # --- read excel ---
    excel_path = os.path.join(codespace, cfg["excel_file"])
    naiseinheitenunique = pd.read_excel(
        excel_path, sheet_name=cfg["excel_sheet"], dtype="str", engine="openpyxl")
    naiseinheitenunique = naiseinheitenunique[
        ["Kategorie_", "Einheit_Na", "Bedingung Region", "Bedingung Höhenstufe", "nais1", "nais2", "hs"]]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["nais1"] != ""]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["nais1"].notnull()]
    naiseinheitenunique.loc[naiseinheitenunique["nais2"].isnull(), "nais2"] = ""

    # --- read shapefile ---
    shp_path = os.path.join(workspace, cfg["shapefile"])
    stok_gdf = gpd.read_file(shp_path)
    stok_gdf["joinid"] = stok_gdf.index

    # --- taheute: overlay intersection ---
    taheute_path = os.path.join(workspace, cfg["taheute_file"])
    taheute = gpd.read_file(taheute_path)
    taheute.rename(columns={"Code_Ta": "taheute"}, inplace=True)
    drop_ta = [c for c in ["id", "Region_de", "Region_fr", "Region_it", "Region_en",
                            "Code", "Subcode", "Code_Bu", "Code_Fi", "Flaeche"]
               if c in taheute.columns]
    taheute.drop(columns=drop_ta, inplace=True)
    stok_gdf = gpd.overlay(stok_gdf, taheute, how="intersection")

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

    for col in ["Kategorie_", "Einheit_Na"]:
        stok_gdf.loc[stok_gdf[col].isnull(), col] = ""
    for col in ["Kategorie_", "Einheit_Na", "nais1", "nais2", "hs"]:
        naiseinheitenunique.loc[naiseinheitenunique[col].isnull(), col] = ""

    # --- filter excel to Bedingung Region=='' ---
    naiseinheitenunique.loc[naiseinheitenunique["Bedingung Region"].isnull(), "Bedingung Region"] = ""
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["Bedingung Region"] == ""]

    # --- main translation loop (2-key join: Kategorie_ + Einheit_Na) ---
    for _, row in naiseinheitenunique.iterrows():
        kantonseinheit = row["Kategorie_"]
        einheit_na = row["Einheit_Na"]
        nais1 = row["nais1"]
        nais2 = row["nais2"]
        hs_val = row["hs"]
        hslist = _parse_hs_tokens(hs_val)

        mask = (stok_gdf["Kategorie_"] == kantonseinheit) & (stok_gdf["Einheit_Na"] == einheit_na)

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

    # --- post-loop Bedingung Region corrections (hardcoded) ---
    storeg_1 = [1, "1"]
    storeg_2abc = ["2a", "2b", "2c"]

    # '55'/'55': storeg==1 → 51(46M)/hm; storeg 2abc → 55/hm
    m55_1 = (stok_gdf["Kategorie_"] == "55") & (stok_gdf["Einheit_Na"] == "55") & stok_gdf["storeg"].isin(storeg_1)
    stok_gdf.loc[m55_1, ["nais1", "nais2", "hs", "tahs", "tahsue"]] = ["51", "46M", "hm", "hochmontan", "hochmontan"]
    m55_2 = (stok_gdf["Kategorie_"] == "55") & (stok_gdf["Einheit_Na"] == "55") & stok_gdf["storeg"].isin(storeg_2abc)
    stok_gdf.loc[m55_2, ["nais1", "hs", "tahs"]] = ["55", "hm", "hochmontan"]

    # '55C'/'55*': storeg==1 → 46M/hm; storeg 2abc → 55*/hm
    m55c_star_1 = (stok_gdf["Kategorie_"] == "55C") & (stok_gdf["Einheit_Na"] == "55*") & stok_gdf["storeg"].isin(storeg_1)
    stok_gdf.loc[m55c_star_1, ["nais1", "hs", "tahs"]] = ["46M", "hm", "hochmontan"]
    m55c_star_2 = (stok_gdf["Kategorie_"] == "55C") & (stok_gdf["Einheit_Na"] == "55*") & stok_gdf["storeg"].isin(storeg_2abc)
    stok_gdf.loc[m55c_star_2, ["nais1", "hs", "tahs"]] = ["55*", "hm", "hochmontan"]

    # '55C'/'': storeg==1 → 46M/hm; storeg 2abc → 55*/hm
    m55c_empty_1 = (stok_gdf["Kategorie_"] == "55C") & (stok_gdf["Einheit_Na"] == "") & stok_gdf["storeg"].isin(storeg_1)
    stok_gdf.loc[m55c_empty_1, ["nais1", "hs", "tahs"]] = ["46M", "hm", "hochmontan"]
    m55c_empty_2 = (stok_gdf["Kategorie_"] == "55C") & (stok_gdf["Einheit_Na"] == "") & stok_gdf["storeg"].isin(storeg_2abc)
    stok_gdf.loc[m55c_empty_2, ["nais1", "hs", "tahs"]] = ["55*", "hm", "hochmontan"]

    # '72'/'72' and '72L'/'72': nais1 by storeg, hs='sa osa', tahs by hs1975
    for kat in ["72", "72L"]:
        base = (stok_gdf["Kategorie_"] == kat) & (stok_gdf["Einheit_Na"] == "72")
        stok_gdf.loc[base & stok_gdf["storeg"].isin(storeg_1), "nais1"] = "72"
        stok_gdf.loc[base & stok_gdf["storeg"].isin(storeg_2abc), "nais1"] = "59"
        stok_gdf.loc[base, "hs"] = "sa osa"
        for storeg_vals in [storeg_1, storeg_2abc]:
            m = base & stok_gdf["storeg"].isin(storeg_vals)
            stok_gdf.loc[m & (stok_gdf["hs1975"] == 9),  "tahs"] = "subalpin"
            stok_gdf.loc[m & (stok_gdf["hs1975"] == 10), "tahs"] = "obersubalpin"
            stok_gdf.loc[m & (stok_gdf["hs1975"] < 9),   "tahs"] = "obersubalpin"
        # null hs1975 fallback (only noted for '72', apply to both)
        stok_gdf.loc[base & stok_gdf["hs1975"].isnull(), "tahs"] = "obersubalpin"

    # --- post-loop fills ---
    stok_gdf.loc[(stok_gdf["nais2"] != "") & (stok_gdf["ue"] == 1) & (stok_gdf["tahsue"] == ""),
                 "tahsue"] = stok_gdf["tahs"]
    stok_gdf.loc[(stok_gdf["nais2"] != "") & (stok_gdf["ue"] == 1), "nais"] = (
        stok_gdf["nais1"] + "(" + stok_gdf["nais2"] + ")")
    stok_gdf.loc[(stok_gdf["nais2"] == "") & (stok_gdf["ue"] == 0), "nais"] = stok_gdf["nais1"]

    # fill tahs from hs1975 for remaining empty
    for index, row in stok_gdf.iterrows():
        if row["tahs"] == "" and row["hs1975"] is not None and row["hs1975"] > 0:
            hsmod = hsmod_dict_kurz.get(int(row["hs1975"]))
            if hsmod:
                stok_gdf.loc[index, "tahs"] = hs_dict_abk[hsmod]

    # --- fid + area; filter area > 0 ---
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
