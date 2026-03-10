"""hooks/SG.py — custom hoehenstufen logic for St. Gallen.

Differences from standard flow:
- Taheute: gpd.overlay intersection (Tannenareale2025.gpkg, same as BE/JU).
- Storeg: sjoin + groupby min (Waldstandortregionen_2024_TI4ab_Final_GR.gpkg).
- Excel: pre-split format; columns ['DTWGEINHEI','Bedingung Hoehenstufe',
  'Bedingung Region','nais1','nais2','hs']; filtered to nais1 != '' and not null.
- Pre-loop excel+stok corrections: DTWGEINHEI '6(18)'→'6(8)' and '9(19)'→'9(15)'
  with corrected nais/hs values applied to both datasets.
- hs typo fix: 'so' → 'sa' in excel.
- Bedingung Höhenstufe loops (before main loop, on rows WITH this condition):
    'sa':    hs1975>=9  → tahs='subalpin'
    'hm':    hs1975==8  → tahs='hochmontan'
    'om hm': hs1975==8  → tahs='hochmontan'; hs1975<=6 → tahs='obermontan'
  All set nais1/nais2/hs/ue/tahsue alongside tahs.
- Bedingung Region loops (before main loop, on rows WITH this condition):
    '2a': storeg=='2a' → set nais1/nais2/hs/ue (no tahs)
    '1':  storeg=='1'  → set nais1/nais2/hs/ue (no tahs)
- Main loop: only rows where both Bedingung cols are null.
  1-key join on DTWGEINHEI; same tahs logic as GR/JU.
- Post-loop fills: tahsue for ue==1; nais = nais1+'('+nais2+')' or nais1.
- Post-loop corrections (hs-based and DTWGEINHEI-based, for remaining empty tahs).
- "Korrekturen Juli2025": applied in-memory (not via re-read).
- fid + area; filter area > 0; filter nais != ''.
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
    kt = cfg["canton"]  # "SG"
    _, hs_dict_abk, _, hsmod_dict_kurz = get_dicts(cfg["dict_variant"])

    # --- read excel ---
    excel_path = os.path.join(codespace, cfg["excel_file"])
    naiseinheitenunique = pd.read_excel(
        excel_path, sheet_name=cfg["excel_sheet"], dtype="str", engine="openpyxl")
    naiseinheitenunique = naiseinheitenunique[
        ["DTWGEINHEI", "Bedingung Hoehenstufe", "Bedingung Region", "nais1", "nais2", "hs"]]
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

    stok_gdf.loc[stok_gdf["DTWGEINHEI"].isnull(), "DTWGEINHEI"] = ""
    for col in ["DTWGEINHEI", "nais1", "nais2", "hs"]:
        naiseinheitenunique.loc[naiseinheitenunique[col].isnull(), col] = ""

    # --- pre-loop corrections (excel + stok_gdf) ---
    # DTWGEINHEI '6(18)' → '6(8)' with corrected nais/hs
    for df in [naiseinheitenunique, stok_gdf]:
        df.loc[df["DTWGEINHEI"] == "6(18)", "nais1"] = "6"
        df.loc[df["DTWGEINHEI"] == "6(18)", "nais2"] = "8d"
        df.loc[df["DTWGEINHEI"] == "6(18)", "hs"] = "sm(um)"
        df.loc[df["DTWGEINHEI"] == "6(18)", "tahs"] = "submontan"
        df.loc[df["DTWGEINHEI"] == "6(18)", "tahsue"] = "untermontan"
        df.loc[df["DTWGEINHEI"] == "6(18)", "ue"] = 1
        df.loc[df["DTWGEINHEI"] == "6(18)", "DTWGEINHEI"] = "6(8)"
    # nais column correction only relevant on stok_gdf
    stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "6(8)", "nais"] = "6(8d)"
    naiseinheitenunique.loc[naiseinheitenunique["DTWGEINHEI"] == "6(8)", "nais"] = "6(8d)"

    for df in [naiseinheitenunique, stok_gdf]:
        df.loc[df["DTWGEINHEI"] == "9(19)", "nais1"] = "9a"
        df.loc[df["DTWGEINHEI"] == "9(19)", "nais2"] = "15"
        df.loc[df["DTWGEINHEI"] == "9(19)", "hs"] = "sm"
        df.loc[df["DTWGEINHEI"] == "9(19)", "tahs"] = "submontan"
        df.loc[df["DTWGEINHEI"] == "9(19)", "DTWGEINHEI"] = "9(15)"
    stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "9(15)", "nais"] = "9a(15)"
    naiseinheitenunique.loc[naiseinheitenunique["DTWGEINHEI"] == "9(15)", "nais"] = "9a(15)"

    # hs typo fix in excel
    naiseinheitenunique.loc[naiseinheitenunique["hs"] == "so", "hs"] = "sa"

    # --- Bedingung Höhenstufe: 'sa', 'hm', 'om hm' ---
    bedingunghs = naiseinheitenunique[naiseinheitenunique["Bedingung Hoehenstufe"].notnull()]

    for _, row in bedingunghs[bedingunghs["Bedingung Hoehenstufe"] == "sa"].iterrows():
        kt_mask = (stok_gdf["DTWGEINHEI"] == row["DTWGEINHEI"]) & (stok_gdf["hs1975"] >= 9)
        stok_gdf.loc[kt_mask, "nais1"] = row["nais1"]
        stok_gdf.loc[kt_mask, "nais2"] = row["nais2"]
        stok_gdf.loc[kt_mask, "hs"] = row["hs"]
        stok_gdf.loc[kt_mask, "tahs"] = "subalpin"
        if row["nais2"] != "":
            stok_gdf.loc[kt_mask, "ue"] = 1
            stok_gdf.loc[kt_mask, "tahsue"] = "subalpin"

    for _, row in bedingunghs[bedingunghs["Bedingung Hoehenstufe"] == "hm"].iterrows():
        kt_mask = (stok_gdf["DTWGEINHEI"] == row["DTWGEINHEI"]) & (stok_gdf["hs1975"] == 8)
        stok_gdf.loc[kt_mask, "nais1"] = row["nais1"]
        stok_gdf.loc[kt_mask, "nais2"] = row["nais2"]
        stok_gdf.loc[kt_mask, "hs"] = row["hs"]
        stok_gdf.loc[kt_mask, "tahs"] = "hochmontan"
        if row["nais2"] != "":
            stok_gdf.loc[kt_mask, "ue"] = 1
            stok_gdf.loc[kt_mask, "tahsue"] = "hochmontan"

    for _, row in bedingunghs[bedingunghs["Bedingung Hoehenstufe"] == "om hm"].iterrows():
        m_hm = (stok_gdf["DTWGEINHEI"] == row["DTWGEINHEI"]) & (stok_gdf["hs1975"] == 8)
        m_om = (stok_gdf["DTWGEINHEI"] == row["DTWGEINHEI"]) & (stok_gdf["hs1975"] <= 6)
        for m, tahs_val in [(m_hm, "hochmontan"), (m_om, "obermontan")]:
            stok_gdf.loc[m, "nais1"] = row["nais1"]
            stok_gdf.loc[m, "nais2"] = row["nais2"]
            stok_gdf.loc[m, "hs"] = row["hs"]
            stok_gdf.loc[m, "tahs"] = tahs_val
            if row["nais2"] != "":
                stok_gdf.loc[m, "ue"] = 1
                stok_gdf.loc[m, "tahsue"] = tahs_val

    # --- Bedingung Region: '2a', '1' ---
    bedingungreg = naiseinheitenunique[naiseinheitenunique["Bedingung Region"].notnull()]

    for reg_val in ["2a", "1"]:
        for _, row in bedingungreg[bedingungreg["Bedingung Region"] == reg_val].iterrows():
            m = (stok_gdf["DTWGEINHEI"] == row["DTWGEINHEI"]) & (stok_gdf["storeg"] == reg_val)
            stok_gdf.loc[m, "nais1"] = row["nais1"]
            stok_gdf.loc[m, "nais2"] = row["nais2"]
            stok_gdf.loc[m, "hs"] = row["hs"]
            if row["nais2"] != "":
                stok_gdf.loc[m, "ue"] = 1

    # --- main loop: rows with both Bedingung cols null ---
    naiseinheitenunique = naiseinheitenunique[
        naiseinheitenunique["Bedingung Hoehenstufe"].isnull() &
        naiseinheitenunique["Bedingung Region"].isnull()
    ]

    for _, row in naiseinheitenunique.iterrows():
        kantonseinheit = row["DTWGEINHEI"]
        nais1 = row["nais1"]
        nais2 = row["nais2"]
        hs_val = row["hs"]
        hslist = _parse_hs_tokens(hs_val)

        mask = stok_gdf["DTWGEINHEI"] == kantonseinheit

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
    stok_gdf.loc[(stok_gdf["nais2"] != "") & (stok_gdf["ue"] == 1), "nais"] = (
        stok_gdf["nais1"] + "(" + stok_gdf["nais2"] + ")")
    stok_gdf.loc[(stok_gdf["nais2"] == "") & (stok_gdf["ue"] == 0), "nais"] = stok_gdf["nais1"]

    # --- post-loop corrections (hs-based) ---
    stok_gdf.loc[(stok_gdf["hs"] == "sa") & (stok_gdf["tahs"] == ""), "tahs"] = "subalpin"
    stok_gdf.loc[(stok_gdf["hs"] == "osa") & (stok_gdf["tahs"] == ""), "tahs"] = "obersubalpin"
    stok_gdf.loc[(stok_gdf["hs"] == "sa(om)") & (stok_gdf["tahs"] == ""), "tahs"] = "subalpin"
    stok_gdf.loc[(stok_gdf["hs"] == "sa(om)") & (stok_gdf["tahsue"] == ""), "tahsue"] = "obermontan"
    stok_gdf.loc[(stok_gdf["hs"] == "hm(sa)") & (stok_gdf["tahs"] == ""), "tahs"] = "hochmontan"
    stok_gdf.loc[(stok_gdf["hs"] == "hm(sa)") & (stok_gdf["tahsue"] == ""), "tahsue"] = "subalpin"
    stok_gdf.loc[(stok_gdf["hs"] == "sa osa") & (stok_gdf["tahs"] == "") & (stok_gdf["hs1975"] <= 9),
                 "tahs"] = "subalpin"
    stok_gdf.loc[(stok_gdf["hs"] == "sa osa") & (stok_gdf["tahs"] == "") & (stok_gdf["hs1975"] >= 10),
                 "tahs"] = "obersubalpin"

    # DTWGEINHEI-based corrections for null hs1975
    for dtwg, n1, n2, tahs_val in [
        ("53",       "53Ta",  "",     "hochmontan"),
        ("53(69L)",  "53Ta",  "69G",  "hochmontan"),
        ("60*(24C)", "60*Ta", "24*",  "hochmontan"),
    ]:
        m = ((stok_gdf["DTWGEINHEI"] == dtwg) & (stok_gdf["tahs"] == "") &
             (stok_gdf["hs1975"].isnull()))
        stok_gdf.loc[m, "nais1"] = n1
        if n2:
            stok_gdf.loc[m, "nais2"] = n2
        stok_gdf.loc[m, "tahs"] = tahs_val

    m60u = ((stok_gdf["DTWGEINHEI"] == "60*/u") & (stok_gdf["tahs"] == "") &
            (stok_gdf["hs1975"] == 9))
    stok_gdf.loc[m60u, "nais1"] = "24*"
    stok_gdf.loc[m60u, "tahs"] = "subalpin"

    # fill remaining empty tahs from hs1975
    for index, row in stok_gdf.iterrows():
        if row["tahs"] == "" and row["hs1975"] is not None and row["hs1975"] > 0:
            hsmod = hsmod_dict_kurz.get(int(row["hs1975"]))
            if hsmod:
                stok_gdf.loc[index, "tahs"] = hs_dict_abk[hsmod]
    stok_gdf.loc[(stok_gdf["ue"] == 1) & (stok_gdf["tahsue"] == ""), "tahsue"] = stok_gdf["tahs"]

    # --- fid + area; filter area > 0 ---
    stok_gdf["fid"] = stok_gdf.index
    stok_gdf["area"] = stok_gdf.geometry.area
    stok_gdf = stok_gdf[stok_gdf["area"] > 0]

    # --- "Korrekturen Juli2025" (applied in-memory) ---
    for dtwg, hs_v, tahs_v, tahsue_v in [
        ("18(27)",   "om(um)", "obermontan", "untermontan"),
        ("18w(27)",  "om(um)", "obermontan", "untermontan"),
        ("20E(27)",  "om(um)", "obermontan", "untermontan"),
        ("20E(27f)", "om(um)", "obermontan", "untermontan"),
    ]:
        stok_gdf.loc[stok_gdf["DTWGEINHEI"] == dtwg, "hs"] = hs_v
        stok_gdf.loc[stok_gdf["DTWGEINHEI"] == dtwg, "tahs"] = tahs_v
        stok_gdf.loc[stok_gdf["DTWGEINHEI"] == dtwg, "tahsue"] = tahsue_v

    stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "49(32C)", "nais"] = "49(32*)"
    stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "49(32C)", "nais2"] = "32*"
    stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "53(18v)", "nais"] = "53Ta(18v)"
    stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "53(18v)", "nais1"] = "53Ta"
    stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "53(69L)/46R", "nais"] = "53Ta(46M)"
    stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "53(69L)/46R", "nais1"] = "53Ta"

    for n1, n2 in [("60*Ta", "27*"), ("60*Ta", "AV"), ("69", "53Ta")]:
        m = (stok_gdf["nais1"] == n1) & (stok_gdf["nais2"] == n2)
        stok_gdf.loc[m, "tahs"] = "hochmontan"
        stok_gdf.loc[m, "tahsue"] = "hochmontan"

    stok_gdf = stok_gdf[stok_gdf["nais"] != ""]

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
