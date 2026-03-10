"""hooks/FR.py — custom hoehenstufen logic for Fribourg.

Differences from standard flow:
- Taheute: direct sjoin without groupby; joinid set after sjoin.
- Radiation: fixed thresholds (112 / 147).
- Translation loop: 2-key join (ASSOC_TOT_ + LEGENDE).
  Part 1 — condition-based: nais/hs only assigned to polygons matching
    'Bedingung Hangneigung' (<60% / >60%) or 'Bedingung Region'
    (Region 1, Region M/J, Region J/M); sets BedingungHangneigung /
    BedingungRegion tracking columns.
  Part 2 — unconditional (full mask): nais1/nais2/mo/ue from NaiS string.
    Note: the if('(') / if('/') else structure means nais2 set by the '('
    block is immediately overwritten by the else block; nais2 is repaired
    by a post-loop fill pass.
  Part 3 — unconditional: standard tahs/tahsue assignment.
- Post-loop: 5 manual ASSOC_TOT_+LEGENDE corrections; fill tahs from hs1975
  for empty values; AV+hs1975==-1 → subalpin; fill tahsue for ue==1;
  final tahsue fallback; fill nais1 for ue==0; fill nais2 for ue==1.
- Extra column: naisdetail (added to config output_cols).
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


def _translate_nais_fr(stok_gdf, naiseinheitenunique, hoehenstufendictabkuerzungen, hsmoddictkurz):
    """FR translation: condition-based (slope/region) + unconditional NaiS/tahs."""
    stok_gdf["naisdetail"] = ""
    stok_gdf["nais"] = ""
    stok_gdf["nais1"] = ""
    stok_gdf["nais2"] = ""
    stok_gdf["mo"] = 0
    stok_gdf["ue"] = 0
    stok_gdf["hs"] = ""
    stok_gdf["tahs"] = ""
    stok_gdf["tahsue"] = ""
    stok_gdf["BedingungHangneigung"] = ""
    stok_gdf["BedingungRegion"] = ""

    for _, row in naiseinheitenunique.iterrows():
        legende = row["LEGENDE"]
        kantonseinheit = row["ASSOC_TOT_"]
        naisdetail = row["NaiS Detail"]
        naisvereinfacht = row["NaiS vereinfacht"]
        hslist = parse_nais_tokens(row["hs"])

        full_mask = (stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)

        # --- Part 1: condition-based nais/hs assignment ---
        bhn = row["Bedingung Hangneigung"]
        breg = row["Bedingung Region"]

        if bhn == "<60%":
            cond = full_mask & (stok_gdf["meanslopeprc"] < 60)
            stok_gdf.loc[cond, "naisdetail"] = naisdetail
            stok_gdf.loc[cond, "nais"] = naisvereinfacht
            stok_gdf.loc[cond, "hs"] = row["hs"]
            stok_gdf.loc[cond, "BedingungHangneigung"] = bhn
        elif bhn == ">60%":
            cond = full_mask & (stok_gdf["meanslopeprc"] >= 60)
            stok_gdf.loc[cond, "naisdetail"] = naisdetail
            stok_gdf.loc[cond, "nais"] = naisvereinfacht
            stok_gdf.loc[cond, "hs"] = row["hs"]
            stok_gdf.loc[cond, "BedingungHangneigung"] = bhn
        elif breg == "Region 1":
            for sv in (1, "1"):
                cond = full_mask & (stok_gdf["storeg"] == sv)
                stok_gdf.loc[cond, "naisdetail"] = naisdetail
                stok_gdf.loc[cond, "nais"] = naisvereinfacht
                stok_gdf.loc[cond, "hs"] = row["hs"]
                stok_gdf.loc[cond, "BedingungRegion"] = breg
        elif breg in ("Region M, J", "Region J, M"):
            for sv in ("M", "J"):
                cond = full_mask & (stok_gdf["storeg"] == sv)
                stok_gdf.loc[cond, "naisdetail"] = naisdetail
                stok_gdf.loc[cond, "nais"] = naisvereinfacht
                stok_gdf.loc[cond, "hs"] = row["hs"]
                stok_gdf.loc[cond, "BedingungRegion"] = breg
        else:
            stok_gdf.loc[full_mask, "naisdetail"] = naisdetail
            stok_gdf.loc[full_mask, "nais"] = naisvereinfacht
            stok_gdf.loc[full_mask, "hs"] = row["hs"]

        # --- Part 2: unconditional nais1/nais2/mo/ue (always full mask) ---
        nais_tokens = parse_nais_tokens(naisvereinfacht)
        if "(" in naisvereinfacht:
            stok_gdf.loc[full_mask, "naisdetail"] = naisdetail
            stok_gdf.loc[full_mask, "nais"] = naisvereinfacht
            stok_gdf.loc[full_mask, "nais1"] = nais_tokens[0] if len(nais_tokens) > 0 else ""
            stok_gdf.loc[full_mask, "nais2"] = nais_tokens[1] if len(nais_tokens) > 1 else ""
            stok_gdf.loc[full_mask, "ue"] = 1
        # NOTE: the if/if/else structure means the else always runs when '/' is absent,
        # overwriting nais2 back to ''. nais2 is repaired by the post-loop fill pass.
        if "/" in naisvereinfacht:
            stok_gdf.loc[full_mask, "naisdetail"] = naisdetail
            stok_gdf.loc[full_mask, "nais"] = naisvereinfacht
            stok_gdf.loc[full_mask, "nais1"] = nais_tokens[0] if len(nais_tokens) > 0 else ""
            stok_gdf.loc[full_mask, "nais2"] = nais_tokens[1] if len(nais_tokens) > 1 else ""
            stok_gdf.loc[full_mask, "mo"] = 1
            stok_gdf.loc[full_mask, "ue"] = 1
        else:
            stok_gdf.loc[full_mask, "naisdetail"] = naisdetail
            stok_gdf.loc[full_mask, "nais"] = naisvereinfacht
            stok_gdf.loc[full_mask, "nais1"] = nais_tokens[0] if len(nais_tokens) > 0 else ""
            stok_gdf.loc[full_mask, "nais2"] = ""

        # --- Part 3: tahs/tahsue assignment (full mask) ---
        if len(hslist) == 1:
            stok_gdf.loc[full_mask, "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
        else:
            if "(" in row["hs"]:
                stok_gdf.loc[full_mask, "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
                stok_gdf.loc[full_mask, "tahsue"] = hoehenstufendictabkuerzungen[hslist[1]]
            else:
                for idx2, row2 in stok_gdf[full_mask].iterrows():
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

    return stok_gdf


def run(cfg, workspace, codespace):
    kt = cfg["canton"]  # "FR"
    _, hs_dict_abk, _, hsmod_dict_kurz = get_dicts(cfg["dict_variant"])

    # --- read excel ---
    excel_path = os.path.join(codespace, cfg["excel_file"])
    naiseinheitenunique = pd.read_excel(
        excel_path, sheet_name=cfg["excel_sheet"], dtype="str", engine="openpyxl")
    naiseinheitenunique = naiseinheitenunique.astype({
        "LEGENDE": str, "ASSOC_TOT_": str,
        "Bedingung Hangneigung": str, "Bedingung Region": str,
        "NaiS vereinfacht": str, "hs": str,
    })
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["NaiS vereinfacht"] != "-"]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["hs"] != ""]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["hs"].notnull()]
    naiseinheitenunique = naiseinheitenunique[naiseinheitenunique["hs"] != "nan"]

    # --- read shapefile ---
    shp_path = os.path.join(workspace, cfg["shapefile"])
    stok_gdf = gpd.read_file(shp_path)

    # --- Tannenareale: direct sjoin without groupby; joinid set after ---
    taheute_path = os.path.join(workspace, cfg["taheute_file"])
    taheute = gpd.read_file(taheute_path)
    taheute.rename(columns={"Code_Ta": "taheute"}, inplace=True)
    drop_ta = [c for c in ["Areal_de", "Areal_fr", "Areal_it", "Areal_en",
                            "Shape_Leng", "Shape_Area"]
               if c in taheute.columns]
    taheute.drop(columns=drop_ta, inplace=True)
    stok_gdf = gpd.sjoin(stok_gdf, taheute, how="left", predicate="intersects")
    stok_gdf["joinid"] = stok_gdf.index
    if "index_right" in stok_gdf.columns:
        stok_gdf.drop(columns=["index_right"], inplace=True)

    # --- Standortregionen (standard sjoin + groupby) ---
    storeg_path = os.path.join(workspace, cfg["storeg_file"])
    stok_gdf = join_waldstandortregionen(stok_gdf, storeg_path)
    if "index_right" in stok_gdf.columns:
        stok_gdf.drop(columns=["index_right"], inplace=True)

    # --- raster stats ---
    stok_gdf = compute_slope_classification(
        stok_gdf, os.path.join(workspace, cfg["raster_slope"]))
    if "index_right" in stok_gdf.columns:
        stok_gdf.drop(columns=["index_right"], inplace=True)
    stok_gdf = compute_radiation_classification(
        stok_gdf, os.path.join(workspace, cfg["raster_radiation"]), method="fixed")
    if "index_right" in stok_gdf.columns:
        stok_gdf.drop(columns=["index_right"], inplace=True)
    stok_gdf = compute_hoehenstufen_1975(
        stok_gdf, os.path.join(workspace, cfg["raster_hs"]))

    stok_gdf.to_file(os.path.join(workspace, kt, "stok_gdf_attributed_temp.gpkg"))

    # --- translation loop (condition-based + unconditional NaiS/tahs) ---
    stok_gdf = _translate_nais_fr(stok_gdf, naiseinheitenunique, hs_dict_abk, hsmod_dict_kurz)

    # --- select first output columns (drops BedingungX intermediates) ---
    out_cols = [c for c in cfg["output_cols"] if c in stok_gdf.columns]
    stok_gdf = stok_gdf[out_cols]

    # --- post-loop corrections (ASSOC_TOT_ + LEGENDE pairs) ---
    def _fix(mask, **kwargs):
        for col, val in kwargs.items():
            stok_gdf.loc[mask, col] = val

    _fix(
        (stok_gdf["ASSOC_TOT_"] == "18aP(17C)") & (stok_gdf["LEGENDE"] == "18a"),
        naisdetail="18(18w)", nais="18(18w)", nais1="18", nais2="18w",
        mo=0, ue=1, hs="om", tahs="obermontan", tahsue="obermontan",
    )
    _fix(
        (stok_gdf["ASSOC_TOT_"] == "12s(24*U)") & (stok_gdf["LEGENDE"] == "12s"),
        naisdetail="12S(24*)", nais="12S(24*)", nais1="12S", nais2="24*",
        mo=0, ue=1, hs="um(om)", tahs="untermontan", tahsue="obermontan",
    )
    _fix(
        (stok_gdf["ASSOC_TOT_"] == "17/13ho") & (stok_gdf["LEGENDE"] == "17"),
        naisdetail="18w(13h)", nais="18w(13h)", nais1="18w", nais2="13h",
        mo=1, ue=1, hs="om", tahs="obermontan", tahsue="obermontan",
    )
    _fix(
        (stok_gdf["ASSOC_TOT_"] == "17/22a") & (stok_gdf["LEGENDE"] == "17"),
        naisdetail="17/22", nais="17(22)", nais1="17", nais2="22",
        mo=0, ue=1, hs="sm um", tahs="untermontan", tahsue="untermontan",
    )
    _fix(
        (stok_gdf["ASSOC_TOT_"] == "17/18fP/18w") & (stok_gdf["LEGENDE"] == "17"),
        naisdetail="17/18M/18w", nais="18w(18M)", nais1="18w", nais2="18M",
        mo=0, ue=1, hs="om", tahs="obermontan", tahsue="obermontan",
    )

    # fill tahs from hs1975 for remaining empty values
    for index, row in stok_gdf.iterrows():
        if row["tahs"] == "" and row["hs1975"] > 0:
            stok_gdf.loc[index, "tahs"] = hs_dict_abk[hsmod_dict_kurz[int(row["hs1975"])]]

    # Gebüschwald: AV with hs1975 == -1 → subalpin
    stok_gdf.loc[(stok_gdf["nais"] == "AV") & (stok_gdf["hs1975"] == -1), "tahs"] = "subalpin"

    # fill tahsue: ue==1, '(' in nais, single-token hs
    for index, row in stok_gdf.iterrows():
        if "(" in row["nais"] and row["ue"] == 1 and row["tahsue"] == "":
            hs_tokens = parse_nais_tokens(row["hs"])
            if len(hs_tokens) == 1:
                stok_gdf.loc[index, "tahsue"] = row["tahs"]

    # final tahsue fallback for remaining ue==1 without tahsue
    stok_gdf.loc[(stok_gdf["tahsue"] == "") & (stok_gdf["ue"] == 1), "tahsue"] = stok_gdf["tahs"]

    # fill nais1 for non-ue polygons where nais1 is empty
    stok_gdf.loc[
        (stok_gdf["ue"] == 0) & (stok_gdf["nais1"] == "") & (stok_gdf["nais"] != ""),
        "nais1"
    ] = stok_gdf["nais"]

    # fill nais2 for ue==1 polygons where nais2 is still empty (repairs if/else overwrite)
    for index, row in stok_gdf.iterrows():
        if row["nais2"] == "" and row["ue"] == 1:
            naislist = parse_nais_tokens(row["nais"].replace(")", " "))
            if len(naislist) > 1:
                stok_gdf.loc[index, "nais2"] = naislist[1]

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
