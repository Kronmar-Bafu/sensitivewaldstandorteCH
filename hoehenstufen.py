"""Generic hoehenstufen.py — replaces 24 canton-specific copies.

Usage:
    python hoehenstufen.py AG --workspace D:/CCW24sensi --codespace C:/DATA/...

For cantons with custom_hook=True the script delegates to hooks/{KT}.py.
All other parameters are driven by config/{KT}.py.
"""

import argparse
import os
import sys
import importlib

import numpy as np
import pandas as pd
import geopandas as gpd

from sensiCHfunctions import (
    get_dicts,
    compute_slope_classification,
    compute_radiation_classification,
    compute_hoehenstufen_1975,
    join_waldstandortregionen,
    join_waldstandortregionen_overlay,
    assign_tahs,
    parse_nais_tokens,
)
from config import load_config


# ---------------------------------------------------------------------------
# Tannenareale helpers
# ---------------------------------------------------------------------------
def add_taheute(gdf, cfg, workspace):
    method = cfg["taheute_method"]
    if method == "const1":
        gdf["taheute"] = 1
        return gdf
    taheute_path = os.path.join(workspace, cfg["taheute_file"])
    taheute = gpd.read_file(taheute_path)
    taheute.rename(columns={"Code_Ta": "taheute"}, inplace=True)
    drop_cols = [c for c in ['Areal_de', 'Areal_fr', 'Areal_it', 'Areal_en',
                              'Shape_Leng', 'Shape_Area', 'id', 'Region_de',
                              'Region_fr', 'Region_it', 'Region_en', 'Code',
                              'Subcode', 'Code_Bu', 'Code_Fi', 'Flaeche']
                 if c in taheute.columns]
    taheute.drop(columns=drop_cols, inplace=True)
    if method == "sjoin":
        joined = gpd.sjoin(gdf, taheute, how="left", predicate="intersects")
        grouped = joined[["joinid", "taheute"]].groupby("joinid").min()
        gdf = gdf.merge(grouped, on="joinid", how="left")
    elif method == "overlay":
        gdf = gpd.overlay(gdf, taheute, how="intersection")
    return gdf


def add_storeg(gdf, cfg, workspace):
    method = cfg["storeg_method"]
    if method == "const1":
        gdf["storeg"] = 1
        return gdf
    if method == "none":
        gdf["storeg"] = None
        return gdf
    if method == "in_file":
        return gdf   # already in shapefile
    storeg_path = os.path.join(workspace, cfg["storeg_file"])
    layer = cfg.get("storeg_layer", None)
    if method == "sjoin":
        return join_waldstandortregionen(gdf, storeg_path, layer=layer)
    elif method == "overlay":
        return join_waldstandortregionen_overlay(gdf, storeg_path, layer=layer)


# ---------------------------------------------------------------------------
# NaiS translation for "nais_hs" format (AG / NE style)
# The excel has a single nais column + hs column; the loop translates both
# ---------------------------------------------------------------------------
def translate_nais_standard(stok_gdf, naiseinheitenunique, join_keys,
                             hoehenstufendictabkuerzungen, hsmoddictkurz):
    stok_gdf["nais"] = ""
    stok_gdf["nais1"] = ""
    stok_gdf["nais2"] = ""
    stok_gdf["mo"] = 0
    stok_gdf["ue"] = 0
    stok_gdf["hs"] = ""
    stok_gdf["tahs"] = ""
    stok_gdf["tahsue"] = ""

    # null-fill join key columns
    for k in join_keys:
        stok_gdf.loc[stok_gdf[k].isnull(), k] = ""
        naiseinheitenunique.loc[naiseinheitenunique[k].isnull(), k] = ""

    for _, row in naiseinheitenunique.iterrows():
        nais = row["nais"]
        hs_val = row["hs"]
        mask = pd.Series([True] * len(stok_gdf), index=stok_gdf.index)
        for k in join_keys:
            mask = mask & (stok_gdf[k] == row[k])

        stok_gdf.loc[mask, "nais"] = nais
        stok_gdf.loc[mask, "hs"] = hs_val

        naislist = parse_nais_tokens(nais)
        if "(" in nais:
            stok_gdf.loc[mask, "nais1"] = naislist[0] if len(naislist) > 0 else ""
            stok_gdf.loc[mask, "nais2"] = naislist[1] if len(naislist) > 1 else ""
            stok_gdf.loc[mask, "ue"] = 1
        elif "/" in nais:
            stok_gdf.loc[mask, "nais1"] = naislist[0] if len(naislist) > 0 else ""
            stok_gdf.loc[mask, "nais2"] = naislist[1] if len(naislist) > 1 else ""
            stok_gdf.loc[mask, "mo"] = 1
            stok_gdf.loc[mask, "ue"] = 1
        else:
            stok_gdf.loc[mask, "nais1"] = naislist[0] if len(naislist) > 0 else ""

    stok_gdf = assign_tahs(stok_gdf, hoehenstufendictabkuerzungen, hsmoddictkurz)
    return stok_gdf


# ---------------------------------------------------------------------------
# NaiS translation for "nais1_nais2_hs" format (pre-split in excel)
# ---------------------------------------------------------------------------
def translate_nais_presplit(stok_gdf, naiseinheitenunique, join_keys,
                             hoehenstufendictabkuerzungen, hsmoddictkurz):
    stok_gdf["nais"] = ""
    stok_gdf["nais1"] = ""
    stok_gdf["nais2"] = ""
    stok_gdf["mo"] = 0
    stok_gdf["ue"] = 0
    stok_gdf["hs"] = ""
    stok_gdf["tahs"] = ""
    stok_gdf["tahsue"] = ""

    for k in join_keys:
        stok_gdf.loc[stok_gdf[k].isnull(), k] = ""
        naiseinheitenunique.loc[naiseinheitenunique[k].isnull(), k] = ""

    for _, row in naiseinheitenunique.iterrows():
        nais1 = row.get("nais1", "")
        nais2 = row.get("nais2", "")
        hs_val = row.get("hs", "")
        # Use the combined nais column from Excel if present; otherwise construct
        # with parenthesis notation (not "/" — that would wrongly trigger mo=1).
        nais_from_excel = row.get("nais", None)
        if nais_from_excel is not None:
            nais = nais_from_excel
        else:
            nais = nais1 + "(" + nais2 + ")" if nais2 else nais1
        mask = pd.Series([True] * len(stok_gdf), index=stok_gdf.index)
        for k in join_keys:
            mask = mask & (stok_gdf[k] == row[k])

        stok_gdf.loc[mask, "nais"] = nais
        stok_gdf.loc[mask, "nais1"] = nais1
        stok_gdf.loc[mask, "nais2"] = nais2
        stok_gdf.loc[mask, "hs"] = hs_val
        if nais2:
            stok_gdf.loc[mask, "ue"] = 1
            # mo only when the Excel provides a combined nais string with "/"
            if nais_from_excel is not None and "/" in str(nais_from_excel):
                stok_gdf.loc[mask, "mo"] = 1

    stok_gdf = assign_tahs(stok_gdf, hoehenstufendictabkuerzungen, hsmoddictkurz)
    return stok_gdf


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(canton, workspace, codespace):
    cfg = load_config(canton)
    kt = canton

    if cfg.get("custom_hook"):
        hook_module_path = f"hooks.{kt}"
        try:
            hook = importlib.import_module(hook_module_path)
        except ModuleNotFoundError:
            print(f"WARNING: custom_hook=True for {kt} but no hooks/{kt}.py found. "
                  "Running standard logic anyway.")
            cfg = dict(cfg, custom_hook=False)
        else:
            hook.run(cfg, workspace, codespace)
            return

    # --- load dicts ---
    hs_dict, hs_dict_abk, hsmod_dict, hsmod_dict_kurz = get_dicts(cfg["dict_variant"])
    if "hsmoddictkurz_override" in cfg:
        hsmod_dict_kurz = cfg["hsmoddictkurz_override"]

    # --- read excel ---
    excel_path = os.path.join(codespace, cfg["excel_file"])
    sheet = cfg.get("excel_sheet", None)
    kwargs = {"dtype": "str", "engine": "openpyxl"}
    if sheet:
        kwargs["sheet_name"] = sheet
    naiseinheitenunique = pd.read_excel(excel_path, **kwargs)

    # column rename if needed
    nais_col = cfg.get("excel_nais_col")
    if nais_col and nais_col in naiseinheitenunique.columns:
        naiseinheitenunique.rename(columns={nais_col: "nais"}, inplace=True)

    # filter invalid rows
    fmt = cfg.get("excel_format", "nais_hs")
    if fmt == "nais_hs":
        naiseinheitenunique.loc[naiseinheitenunique["nais"].isnull(), "nais"] = ""
        naiseinheitenunique.loc[naiseinheitenunique["hs"].isnull(), "hs"] = ""
        naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["nais"] != ""]
        naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["hs"] != ""]
    elif fmt == "nais1_nais2_hs":
        naiseinheitenunique.loc[naiseinheitenunique["nais1"].isnull(), "nais1"] = ""
        naiseinheitenunique.loc[naiseinheitenunique["nais2"].isnull(), "nais2"] = ""
        naiseinheitenunique.loc[naiseinheitenunique["hs"].isnull(), "hs"] = ""
        naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["nais1"] != ""]
        naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["hs"] != ""]

    # --- read shapefile ---
    shp_path = os.path.join(workspace, cfg["shapefile"])
    stok_gdf = gpd.read_file(shp_path)
    stok_gdf["joinid"] = stok_gdf.index

    # --- Tannenareale ---
    stok_gdf = add_taheute(stok_gdf, cfg, workspace)

    # --- Standortregionen ---
    stok_gdf = add_storeg(stok_gdf, cfg, workspace)

    # --- raster zonal stats ---
    slope_path = cfg.get("raster_slope")
    if slope_path:
        stok_gdf = compute_slope_classification(
            stok_gdf, os.path.join(workspace, slope_path))

    radiation_path = cfg.get("raster_radiation")
    if radiation_path:
        stok_gdf = compute_radiation_classification(
            stok_gdf, os.path.join(workspace, radiation_path),
            method=cfg.get("radiation_method", "quantile"))

    hs_path = cfg.get("raster_hs")
    if hs_path:
        stok_gdf = compute_hoehenstufen_1975(
            stok_gdf, os.path.join(workspace, hs_path))

    stok_gdf.to_file(os.path.join(workspace, kt, "stok_gdf_attributed_temp.gpkg"))

    # --- NaiS translation ---
    join_keys = cfg["join_keys"]
    if fmt in ("nais_hs",):
        stok_gdf = translate_nais_standard(
            stok_gdf, naiseinheitenunique, join_keys, hs_dict_abk, hsmod_dict_kurz)
    else:
        stok_gdf = translate_nais_presplit(
            stok_gdf, naiseinheitenunique, join_keys, hs_dict_abk, hsmod_dict_kurz)

    # --- filter ---
    filter_col = cfg.get("filter_col")
    filter_val = cfg.get("filter_val", "99")
    if filter_col and filter_col in stok_gdf.columns:
        stok_gdf = stok_gdf[stok_gdf[filter_col] != filter_val]

    # --- select output columns ---
    out_cols = [c for c in cfg.get("output_cols", stok_gdf.columns.tolist())
                if c in stok_gdf.columns]
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compute hoehenstufen attributed shapefile for a canton.")
    parser.add_argument("canton", help="Canton code, e.g. AG")
    parser.add_argument("--workspace", default="D:/CCW24sensi",
                        help="Path to project data workspace")
    parser.add_argument("--codespace", default=".",
                        help="Path to code/excel workspace (default: current directory)")
    args = parser.parse_args()
    main(args.canton, args.workspace, args.codespace)
