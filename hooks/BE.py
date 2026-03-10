"""hooks/BE.py — custom hoehenstufen logic for Bern.

Differences from standard flow:
- joinid set before taheute overlay (overlay splits polygons).
- Taheute: gpd.overlay intersection (Tannenareale2025.gpkg, different columns).
- Storeg: sjoin with named gpkg layer; different drop columns.
- nais already in shapefile (column NAIS renamed to nais); nais1/nais2 derived
  by splitting nais on '('. Excel provides only hs + hsue per BE unit.
- Pre-loop corrections: map specific BE units to corrected nais values.
- Post-loop corrections: hs1975-based overrides for BE units 32, 60*, 66.
- Filter: area > 0.
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


def _join_storeg_be(stok_gdf, storeg_path, storeg_layer):
    """Sjoin BE-specific storeg file (gpkg with named layer) + groupby min."""
    storeg = gpd.read_file(storeg_path, layer=storeg_layer)
    storeg.rename(columns={"Subcode": "storeg"}, inplace=True)
    drop_cols = [c for c in ["id", "Region_de", "Region_fr", "Region_it", "Region_en",
                              "Code", "Code_Bu", "Code_Fi", "Flaeche"]
                 if c in storeg.columns]
    storeg.drop(columns=drop_cols, inplace=True)
    if "index_right" in stok_gdf.columns:
        stok_gdf = stok_gdf.drop(columns=["index_right"])
    joined = stok_gdf.sjoin(storeg, how="left", predicate="intersects")
    grouped = joined[["joinid", "storeg"]].groupby("joinid").min()
    stok_gdf = stok_gdf.merge(grouped, on="joinid", how="left")
    return stok_gdf


def _translate_nais_be(stok_gdf, naiseinheitenunique, hoehenstufendictabkuerzungen, hsmoddictkurz):
    """BE translation: hs + hsue from Excel joined on BE unit; nais already set."""
    stok_gdf["hs"] = ""
    stok_gdf["hsue"] = ""
    stok_gdf["tahs"] = ""
    stok_gdf["tahsue"] = ""

    stok_gdf.loc[stok_gdf["nais"].isnull(), "nais"] = ""
    stok_gdf.loc[stok_gdf["BE"].isnull(), "BE"] = ""
    naiseinheitenunique.loc[naiseinheitenunique["BE"].isnull(), "BE"] = ""
    naiseinheitenunique.loc[naiseinheitenunique["hsue"].isnull(), "hsue"] = ""

    for _, row in naiseinheitenunique.iterrows():
        kantonseinheit = row["BE"]
        hs = row["hs"]
        hsue = row["hsue"]
        hslist = parse_nais_tokens(hs)
        hsuelist = parse_nais_tokens(hsue)

        mask = stok_gdf["BE"] == kantonseinheit
        stok_gdf.loc[mask, "hs"] = hs
        stok_gdf.loc[mask, "hsue"] = hsue

        # tahs assignment
        if len(hslist) == 1:
            stok_gdf.loc[mask, "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
        else:
            for idx2, row2 in stok_gdf[mask].iterrows():
                hs1975 = row2["hs1975"]
                if hs1975 and int(hs1975) > 0 and int(hs1975) in hsmoddictkurz:
                    hsmod = hsmoddictkurz[int(hs1975)]
                else:
                    hsmod = "nan"
                hs_tokens = parse_nais_tokens(row2["hs"])
                if hsmod in hs_tokens:
                    stok_gdf.loc[idx2, "tahs"] = hoehenstufendictabkuerzungen[hsmod]
                elif hs_tokens:
                    stok_gdf.loc[idx2, "tahs"] = hoehenstufendictabkuerzungen[hs_tokens[-1]]

        # tahsue assignment
        if len(hsuelist) == 1:
            stok_gdf.loc[mask, "tahsue"] = hoehenstufendictabkuerzungen[hsuelist[0]]
        elif len(hsuelist) > 1:
            for idx2, row2 in stok_gdf[mask].iterrows():
                hs1975 = row2["hs1975"]
                if hs1975 and int(hs1975) > 0 and int(hs1975) in hsmoddictkurz:
                    hsmod = hsmoddictkurz[int(hs1975)]
                else:
                    hsmod = "nan"
                hsue_tokens = parse_nais_tokens(row2["hsue"])
                hs_tokens = parse_nais_tokens(row2["hs"])   # fallback uses hs, matching legacy
                if hsmod in hsue_tokens:
                    stok_gdf.loc[idx2, "tahsue"] = hoehenstufendictabkuerzungen[hsmod]
                elif hs_tokens:
                    stok_gdf.loc[idx2, "tahsue"] = hoehenstufendictabkuerzungen[hs_tokens[-1]]

    # fill tahsue for ue polygons without one
    stok_gdf.loc[
        (stok_gdf["nais2"] != "") & (stok_gdf["ue"] == 1) & (stok_gdf["tahsue"] == ""),
        "tahsue"
    ] = stok_gdf["tahs"]
    return stok_gdf


def run(cfg, workspace, codespace):
    kt = cfg["canton"]  # "BE"
    _, hs_dict_abk, _, hsmod_dict_kurz = get_dicts(cfg["dict_variant"])

    # --- read excel (BE sheet: BE, NaiS_LFI_JU, NaiS_LFI_M/A, hs, hsue, ...) ---
    excel_path = os.path.join(codespace, cfg["excel_file"])
    naiseinheitenunique = pd.read_excel(
        excel_path, sheet_name=cfg["excel_sheet"], dtype="str", engine="openpyxl")
    naiseinheitenunique = naiseinheitenunique[
        ["BE", "NaiS_LFI_JU", "NaiS_LFI_M/A", "hs", "hsue",
         "Bemerkungen bh", "Bemerkung Monika"]]
    naiseinheitenunique.loc[naiseinheitenunique["hsue"].isnull(), "hsue"] = ""

    # --- read shapefile (joinid before overlay) ---
    shp_path = os.path.join(workspace, cfg["shapefile"])
    stok_gdf = gpd.read_file(shp_path)
    stok_gdf["joinid"] = stok_gdf.index

    # --- Tannenareale: overlay intersection (splits polygons) ---
    taheute_path = os.path.join(workspace, cfg["taheute_file"])
    taheute = gpd.read_file(taheute_path)
    taheute.rename(columns={"Code_Ta": "taheute"}, inplace=True)
    drop_ta = [c for c in ["id", "Region_de", "Region_fr", "Region_it", "Region_en",
                            "Code", "Subcode", "Code_Bu", "Code_Fi", "Flaeche"]
               if c in taheute.columns]
    taheute.drop(columns=drop_ta, inplace=True)
    stok_gdf = gpd.overlay(stok_gdf, taheute, how="intersection")

    # --- Standortregionen ---
    storeg_path = os.path.join(workspace, cfg["storeg_file"])
    storeg_layer = cfg.get("storeg_layer")
    stok_gdf = _join_storeg_be(stok_gdf, storeg_path, storeg_layer)

    # --- raster stats ---
    stok_gdf = compute_slope_classification(
        stok_gdf, os.path.join(workspace, cfg["raster_slope"]))
    stok_gdf = compute_radiation_classification(
        stok_gdf, os.path.join(workspace, cfg["raster_radiation"]), method="quantile")
    stok_gdf = compute_hoehenstufen_1975(
        stok_gdf, os.path.join(workspace, cfg["raster_hs"]))

    # --- save intermediate ---
    stok_gdf.to_file(os.path.join(workspace, kt, "stok_gdf_attributed_temp.gpkg"))

    # --- rename NAIS → nais; init columns ---
    stok_gdf.rename(columns={"NAIS": "nais"}, inplace=True)
    stok_gdf["nais1"] = ""
    stok_gdf["nais2"] = ""
    stok_gdf["mo"] = 0
    stok_gdf["ue"] = 0

    # --- pre-loop corrections: map BE units to corrected nais ---
    stok_gdf.loc[stok_gdf["BE"] == "18w", "nais"] = "18w"
    stok_gdf.loc[stok_gdf["BE"] == "27a", "nais"] = "27a"
    stok_gdf.loc[stok_gdf["BE"] == "27f", "nais"] = "27f"
    stok_gdf.loc[stok_gdf["BE"] == "27w", "nais"] = "27a"
    stok_gdf.loc[stok_gdf["BE"] == "38",  "nais"] = "39"
    stok_gdf.loc[stok_gdf["BE"] == "39",  "nais"] = "39*"
    stok_gdf.loc[stok_gdf["BE"] == "49a(20)", "nais"] = "49(20)"
    stok_gdf.loc[stok_gdf["BE"] == "49a(50)", "nais"] = "49(50)"
    stok_gdf.loc[stok_gdf["BE"] == "54*",  "nais"] = "46M(70)"
    stok_gdf.loc[stok_gdf["BE"] == "55",   "nais"] = "51(57V)"
    stok_gdf.loc[stok_gdf["BE"] == "63G",  "nais"] = "67G"
    stok_gdf.loc[stok_gdf["BE"] == "7e",   "nais"] = "7e"
    stok_gdf.loc[stok_gdf["BE"] == "7f",   "nais"] = "7f"
    stok_gdf.loc[stok_gdf["BE"] == "7g",   "nais"] = "7g"
    stok_gdf.loc[stok_gdf["BE"] == "8f",   "nais"] = "8f"
    stok_gdf.loc[stok_gdf["BE"] == "8g",   "nais"] = "8g"
    stok_gdf.loc[(stok_gdf["BE"] == "Pio") & (stok_gdf["hs1975"] <= 6), "nais"] = "32*"
    stok_gdf.loc[(stok_gdf["BE"] == "Pio") & (stok_gdf["hs1975"] > 6),  "nais"] = "AV"

    # null-fill before splitting
    stok_gdf.loc[stok_gdf["nais"].isnull(), "nais"] = ""
    stok_gdf.loc[stok_gdf["BE"].isnull(), "BE"] = ""

    # derive nais1 / nais2 from nais by splitting on '('
    stok_gdf["nais1"] = stok_gdf["nais"].str.split("(").str[0].str.strip()
    stok_gdf["nais2"] = (stok_gdf["nais"].str.split("(").str[1]
                         .str.split(")").str[0].str.strip())
    stok_gdf.loc[stok_gdf["nais2"].isnull(), "nais2"] = ""
    stok_gdf.loc[stok_gdf["nais2"] != "", "ue"] = 1

    # --- translation loop (hs + hsue from Excel, join on BE) ---
    stok_gdf = _translate_nais_be(stok_gdf, naiseinheitenunique, hs_dict_abk, hsmod_dict_kurz)

    # --- post-loop corrections (hs1975-based) ---
    stok_gdf.loc[(stok_gdf["BE"] == "32") & (stok_gdf["hs1975"] <= 5), "hs"] = "sm um"
    stok_gdf.loc[(stok_gdf["BE"] == "32") & (stok_gdf["hs1975"] <= 5), "nais"] = "32C"
    stok_gdf.loc[(stok_gdf["BE"] == "32") & (stok_gdf["hs1975"] <= 5), "nais1"] = "32C"
    stok_gdf.loc[(stok_gdf["BE"] == "32") & (stok_gdf["hs1975"] <= 4), "tahs"] = "submontan"
    stok_gdf.loc[(stok_gdf["BE"] == "32") & (stok_gdf["hs1975"] == 5), "tahs"] = "untermontan"

    stok_gdf.loc[(stok_gdf["BE"] == "60*") & (stok_gdf["hs1975"] == 8), "hs"] = "hm"
    stok_gdf.loc[(stok_gdf["BE"] == "60*") & (stok_gdf["hs1975"] == 8), "nais"] = "60*Ta"
    stok_gdf.loc[(stok_gdf["BE"] == "60*") & (stok_gdf["hs1975"] == 8), "nais1"] = "60*Ta"
    stok_gdf.loc[(stok_gdf["BE"] == "60*") & (stok_gdf["hs1975"] == 8), "tahs"] = "hochmontan"

    stok_gdf.loc[stok_gdf["BE"] == "66", "hs"] = "sm um"
    stok_gdf.loc[stok_gdf["BE"] == "66", "nais"] = "66L"
    stok_gdf.loc[stok_gdf["BE"] == "66", "nais1"] = "66L"
    stok_gdf.loc[(stok_gdf["BE"] == "66") & (stok_gdf["hs1975"] <= 4), "tahs"] = "submontan"
    stok_gdf.loc[(stok_gdf["BE"] == "66") & (stok_gdf["hs1975"] >= 5), "tahs"] = "untermontan"

    # --- select output columns, add fid + area, filter area > 0 ---
    out_cols = [c for c in cfg["output_cols"] if c in stok_gdf.columns]
    stok_gdf = stok_gdf[out_cols]
    stok_gdf["fid"] = stok_gdf.index
    stok_gdf["area"] = stok_gdf.geometry.area
    stok_gdf = stok_gdf[stok_gdf["area"] > 0]

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
