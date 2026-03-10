"""hooks/AI.py — custom hoehenstufen logic for Appenzell Innerrhoden.

Differences from standard flow:
- Shapefile has pre-existing nais/nais1 columns renamed to naisalt/nais1alt.
- Taheute: direct sjoin without groupby (joinid assigned after sjoin).
- Radiation: fixed thresholds (112 / 147).
- NaiS translation: 4-key join (WSTEinheit, nais1alt, naisue, naismosaic);
  tahs is pre-computed in the Excel; hs output = raw tahs string from Excel.
- Post-write corrections for specific WSTEinheit values + filter nais1 == ''.
"""

import os
import geopandas as gpd
import pandas as pd

from sensiCHfunctions import (
    get_dicts,
    compute_slope_classification,
    compute_radiation_classification,
    compute_hoehenstufen_1975,
    join_waldstandortregionen,
    parse_nais_tokens,
)


def _translate_nais_ai(stok_gdf, naiseinheitenunique, hoehenstufendictabkuerzungen, hsmoddictkurz):
    """4-key NaiS translation with pre-computed tahs from Excel (AI-specific)."""
    stok_gdf["nais"] = ""
    stok_gdf["nais1"] = ""
    stok_gdf["nais2"] = ""
    stok_gdf["mo"] = 0
    stok_gdf["ue"] = 0
    stok_gdf["hs"] = ""
    stok_gdf["tahs"] = ""
    stok_gdf["tahsue"] = ""

    for col in ["WSTEinheit", "nais1alt", "naisue", "naismosaic"]:
        stok_gdf.loc[stok_gdf[col].isnull(), col] = ""
        if col in naiseinheitenunique.columns:
            naiseinheitenunique.loc[naiseinheitenunique[col].isnull(), col] = ""

    for _, row in naiseinheitenunique.iterrows():
        kantonseinheit = row["WSTEinheit"]
        nais1alt_key = row["nais"]        # Excel 'nais' = shapefile nais1alt (join key)
        naisue = row["naisue"]
        naismosaic = row["naismosaic"]
        nais1 = row["nais1"]
        nais2 = row["nais2"]
        tahs_raw = row["tahs"]            # pre-computed elevation stage, e.g. "um", "hm(sa)"
        hslist = parse_nais_tokens(tahs_raw)

        mask = (
            (stok_gdf["WSTEinheit"] == kantonseinheit) &
            (stok_gdf["nais1alt"] == nais1alt_key) &
            (stok_gdf["naisue"] == naisue) &
            (stok_gdf["naismosaic"] == naismosaic)
        )

        stok_gdf.loc[mask, "nais1"] = nais1
        stok_gdf.loc[mask, "nais2"] = nais2
        stok_gdf.loc[mask, "hs"] = tahs_raw   # hs = raw tahs string from Excel

        if nais2 == "":
            stok_gdf.loc[mask, "nais"] = nais1
        else:
            stok_gdf.loc[mask, "nais"] = f"{nais1}({nais2})"
            stok_gdf.loc[mask, "ue"] = 1

        if len(hslist) == 1:
            stok_gdf.loc[mask, "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
            # override nais1 with first token of the join-key nais string
            nais_tokens = parse_nais_tokens(row["nais"])
            if nais_tokens:
                stok_gdf.loc[mask, "nais1"] = nais_tokens[0]
        else:
            if "(" in tahs_raw:
                stok_gdf.loc[mask, "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
                stok_gdf.loc[mask, "tahsue"] = hoehenstufendictabkuerzungen[hslist[1]]
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
                    else:
                        stok_gdf.loc[idx2, "tahs"] = hoehenstufendictabkuerzungen[hs_tokens[-1]]

    stok_gdf.loc[(stok_gdf["tahsue"] == "") & (stok_gdf["ue"] == 1), "tahsue"] = stok_gdf["tahs"]
    stok_gdf.loc[stok_gdf["ue"] == 0, "tahsue"] = ""
    return stok_gdf


def run(cfg, workspace, codespace):
    kt = cfg["canton"]  # "AI"
    _, hs_dict_abk, _, hsmod_dict_kurz = get_dicts(cfg["dict_variant"])
    if "hsmoddictkurz_override" in cfg:
        hsmod_dict_kurz = cfg["hsmoddictkurz_override"]

    # --- read excel ---
    excel_path = os.path.join(codespace, cfg["excel_file"])
    naiseinheitenunique = pd.read_excel(excel_path, dtype="str", engine="openpyxl")
    for col in ["nais2", "tahs", "WSTEinheit", "nais", "naisue", "naismosaic"]:
        if col in naiseinheitenunique.columns:
            naiseinheitenunique.loc[naiseinheitenunique[col].isnull(), col] = ""
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["tahs"] != ""]

    # --- read shapefile ---
    shp_path = os.path.join(workspace, cfg["shapefile"])
    stok_gdf = gpd.read_file(shp_path)
    stok_gdf.set_crs(epsg=2056, inplace=True, allow_override=True)
    stok_gdf.rename(columns={"nais": "naisalt", "nais1": "nais1alt"}, inplace=True)
    for col in ["WSTEinheit", "nais1alt", "naisue", "naismosaic"]:
        if col in stok_gdf.columns:
            stok_gdf.loc[stok_gdf[col].isnull(), col] = ""
            stok_gdf.loc[stok_gdf[col] == "None", col] = ""
    str_cols = {c: "str" for c in ["WSTEinheit", "nais1alt", "naisue", "naismosaic"]
                if c in stok_gdf.columns}
    stok_gdf = stok_gdf.astype(str_cols)

    # --- Tannenareale: direct sjoin without groupby (matches legacy) ---
    taheute_path = os.path.join(workspace, cfg["taheute_file"])
    taheute = gpd.read_file(taheute_path)
    taheute.rename(columns={"Code_Ta": "taheute"}, inplace=True)
    drop_ta = [c for c in ["Areal_de", "Areal_fr", "Areal_it", "Areal_en",
                            "Shape_Leng", "Shape_Area"]
               if c in taheute.columns]
    taheute.drop(columns=drop_ta, inplace=True)
    stok_gdf = gpd.sjoin(stok_gdf, taheute, how="left", predicate="intersects")
    if "index_right" in stok_gdf.columns:
        stok_gdf.drop(columns="index_right", inplace=True)
    stok_gdf["joinid"] = stok_gdf.index   # set after sjoin, as in legacy

    # --- Standortregionen (groupby sjoin via shared function) ---
    storeg_path = os.path.join(workspace, cfg["storeg_file"])
    stok_gdf = join_waldstandortregionen(stok_gdf, storeg_path)

    # --- raster stats ---
    stok_gdf = compute_slope_classification(
        stok_gdf, os.path.join(workspace, cfg["raster_slope"]))
    stok_gdf = compute_radiation_classification(
        stok_gdf, os.path.join(workspace, cfg["raster_radiation"]), method="fixed")
    stok_gdf = compute_hoehenstufen_1975(
        stok_gdf, os.path.join(workspace, cfg["raster_hs"]))

    # --- NaiS translation (AI-specific 4-key join with pre-computed tahs) ---
    stok_gdf = _translate_nais_ai(stok_gdf, naiseinheitenunique, hs_dict_abk, hsmod_dict_kurz)

    # --- select output columns ---
    out_cols = [c for c in cfg["output_cols"] if c in stok_gdf.columns]
    stok_gdf = stok_gdf[out_cols]

    out_path = os.path.join(workspace, kt, "stok_gdf_attributed.gpkg")
    stok_gdf.to_file(out_path)
    print(f"Wrote {out_path}")

    # --- post-write corrections ---
    stok_gdf = gpd.read_file(out_path)
    stok_gdf.loc[stok_gdf["WSTEinheit"] == "18MBl", "nais1"] = "18M"
    stok_gdf.loc[stok_gdf["WSTEinheit"] == "18MBl(20g)", "nais1"] = "18M"
    stok_gdf.loc[stok_gdf["WSTEinheit"] == "18MBl(20g)", "nais2"] = "20"
    stok_gdf.loc[stok_gdf["WSTEinheit"] == "46(57V)", "hs"] = "hm(sa)"
    stok_gdf.loc[stok_gdf["WSTEinheit"] == "46(57V)", "tahs"] = "hochmontan"
    stok_gdf.loc[stok_gdf["WSTEinheit"] == "46(57V)", "tahsue"] = "subalpin"
    stok_gdf.loc[stok_gdf["WSTEinheit"] == "26(12a)", "nais2"] = "12a"

    # filter polygons without nais1
    stok_gdf = stok_gdf[stok_gdf["nais1"] != ""]
    stok_gdf = stok_gdf[stok_gdf["nais1"].notnull()]
    stok_gdf.to_file(out_path)
    print(f"Updated {out_path} (post-write corrections + nais1 filter applied)")

    # --- treeapp export ---
    treeapp_cols = [c for c in cfg.get("treeapp_cols", []) if c in stok_gdf.columns]
    if treeapp_cols:
        treeapp = stok_gdf[treeapp_cols]
        tp_path = os.path.join(workspace, kt, f"{kt}_treeapp.gpkg")
        treeapp.to_file(tp_path, layer=f"{kt}_treeapp", driver="GPKG")
        print(f"Wrote {tp_path}")

    print("done")
