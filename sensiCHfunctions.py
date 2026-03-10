import numpy as np
import pandas as pd
import geopandas as gpd
from osgeo import osr, gdal
from rasterstats import zonal_stats

# ---------------------------------------------------------------------------
# Hoehenstufen dicts — standard variant
# (used by AG, AI, AR, GE, LU, NE, NW, OW, SH)
# ---------------------------------------------------------------------------
HOEHENSTUFENDICT = {
    "collin": "co",
    "submontan": "sm",
    "untermontan": "um",
    "obermontan": "om",
    "hochmontan": "hm",
    "subalpin": "sa",
    "obersubalpin": "osa",
}
HOEHENSTUFENDICTABKUERZUNGEN = {
    "co": "collin",
    "sm": "submontan",
    "um": "untermontan",
    "om": "obermontan",
    "hm": "hochmontan",
    "sa": "subalpin",
    "osa": "obersubalpin",
}
HSMODDICT = {
    2: "collin",
    3: "collin",
    4: "submontan",
    5: "untermontan",
    6: "obermontan",
    8: "hochmontan",
    9: "subalpin",
    10: "obersubalpin",
}
HSMODDICTKURZ = {
    2: "co",
    3: "co",
    4: "sm",
    5: "um",
    6: "om",
    8: "hm",
    9: "sa",
    10: "osa",
}
HOEHENSTUFENLIST = [
    "collin", "submontan", "untermontan", "obermontan",
    "hochmontan", "subalpin", "obersubalpin",
]

# ---------------------------------------------------------------------------
# Hoehenstufen dicts — extended variant
# (adds hyperinsubrisch, mediterran, umom; raster codes 0, 1, 7)
# used by BE, BLBS, JU, SG, SO, SZ, TG, UR, VD, ZG, ZH
# ---------------------------------------------------------------------------
HOEHENSTUFENDICT_EXT = {
    "hyperinsubrisch": "hyp",
    "mediterran": "med",
    "collin mit Buche": "co",
    "collin": "co",
    "submontan": "sm",
    "untermontan": "um",
    "obermontan": "om",
    "unter- & obermontan": "umom",
    "unter-/obermontan": "umom",
    "hochmontan": "hm",
    "subalpin": "sa",
    "obersubalpin": "osa",
}
HOEHENSTUFENDICTABKUERZUNGEN_EXT = {
    "co": "collin",
    "sm": "submontan",
    "um": "untermontan",
    "om": "obermontan",
    "hm": "hochmontan",
    "sa": "subalpin",
    "osa": "obersubalpin",
}
HSMODDICT_EXT = {
    0: "mediterran",
    1: "hyperinsubrisch",
    2: "collin",
    3: "collin",
    4: "submontan",
    5: "untermontan",
    6: "obermontan",
    7: "unter- & obermontan",
    8: "hochmontan",
    9: "subalpin",
    10: "obersubalpin",
}
HSMODDICTKURZ_EXT = {
    0: "med",
    1: "hyp",
    2: "co",
    3: "co",
    4: "sm",
    5: "um",
    6: "om",
    7: "umom",
    8: "hm",
    9: "sa",
    10: "osa",
}

# ---------------------------------------------------------------------------
# Hoehenstufen dicts — GR/VS variant
# (collin mit Buche has its own abbreviation "cob"; umom is "um/om"; no
# "mediterran"; used by GR and VS)
# ---------------------------------------------------------------------------
HOEHENSTUFENDICT_GRVS = {
    "hyperinsubrisch": "hyp",
    "collin mit Buche": "cob",
    "collin": "co",
    "submontan": "sm",
    "untermontan": "um",
    "obermontan": "om",
    "unter-/obermontan": "um/om",
    "hochmontan": "hm",
    "subalpin": "sa",
    "obersubalpin": "osa",
}
HOEHENSTUFENDICTABKUERZUNGEN_GRVS = {
    "hyp": "hyperinsubrisch",
    "co": "collin",
    "cob": "collin mit Buche",
    "sm": "submontan",
    "um": "untermontan",
    "om": "obermontan",
    "um/om": "unter-/obermontan",
    "hm": "hochmontan",
    "sa": "subalpin",
    "osa": "obersubalpin",
}
HSMODDICT_GRVS = {
    1: "hyperinsubrisch",
    2: "collin",
    3: "collin",
    4: "submontan",
    5: "untermontan",
    6: "obermontan",
    7: "unter-/obermontan",
    8: "hochmontan",
    9: "subalpin",
    10: "obersubalpin",
}
HSMODDICTKURZ_GRVS = {
    1: "hyp",
    2: "co",
    3: "cob",
    4: "sm",
    5: "um",
    6: "om",
    7: "um/om",
    8: "hm",
    9: "sa",
    10: "osa",
}

# Map dict_variant string to (hoehenstufendict, hoehenstufendictabkuerzungen,
#                              hsmoddict, hsmoddictkurz)
DICT_VARIANTS = {
    "standard": (HOEHENSTUFENDICT, HOEHENSTUFENDICTABKUERZUNGEN,
                 HSMODDICT, HSMODDICTKURZ),
    "extended": (HOEHENSTUFENDICT_EXT, HOEHENSTUFENDICTABKUERZUNGEN_EXT,
                 HSMODDICT_EXT, HSMODDICTKURZ_EXT),
    "grvs":     (HOEHENSTUFENDICT_GRVS, HOEHENSTUFENDICTABKUERZUNGEN_GRVS,
                 HSMODDICT_GRVS, HSMODDICTKURZ_GRVS),
}


def get_dicts(dict_variant):
    """Return (hs_dict, hs_dict_abk, hsmod_dict, hsmod_dict_kurz) for variant."""
    return DICT_VARIANTS[dict_variant]


# ---------------------------------------------------------------------------
# GDAL helpers
# ---------------------------------------------------------------------------
def convert_tif_to_array(intifraster):
    inras = gdal.Open(intifraster)
    inband = inras.GetRasterBand(1)
    outarr = inband.ReadAsArray()
    return outarr


def convertarrtotif(arr, outfile, tifdatatype, referenceraster, nodatavalue):
    ds_in = gdal.Open(referenceraster)
    inband = ds_in.GetRasterBand(1)
    gtiff_driver = gdal.GetDriverByName("GTiff")
    ds_out = gtiff_driver.Create(outfile, inband.XSize, inband.YSize, 1, tifdatatype)
    ds_out.SetProjection(ds_in.GetProjection())
    ds_out.SetGeoTransform(ds_in.GetGeoTransform())
    outband = ds_out.GetRasterBand(1)
    outband.WriteArray(arr)
    outband.SetNoDataValue(nodatavalue)
    ds_out.FlushCache()
    del ds_in, ds_out, inband, outband


# ---------------------------------------------------------------------------
# Raster zonal statistics
# ---------------------------------------------------------------------------
def compute_slope_classification(gdf, sloperaster):
    """Add meanslopeprc and slpprzrec (1-4) to gdf. Returns modified gdf."""
    gdf = gdf.copy()
    gdf["meanslopeprc"] = 0.0
    zonstatslope = zonal_stats(gdf, sloperaster, stats="mean")
    for i in range(len(gdf)):
        val = zonstatslope[i]["mean"]
        gdf.loc[i, "meanslopeprc"] = val if val is not None else 0.0
    gdf["slpprzrec"] = 0
    gdf.loc[gdf["meanslopeprc"] >= 70.0, "slpprzrec"] = 4
    gdf.loc[(gdf["meanslopeprc"] >= 60.0) & (gdf["meanslopeprc"] < 70.0), "slpprzrec"] = 3
    gdf.loc[(gdf["meanslopeprc"] >= 20.0) & (gdf["meanslopeprc"] < 60.0), "slpprzrec"] = 2
    gdf.loc[gdf["meanslopeprc"] < 20.0, "slpprzrec"] = 1
    return gdf


def compute_radiation_classification(gdf, radiationraster, method="quantile"):
    """Add rad and radiation (-1/0/1) to gdf.

    method="quantile"  uses the canton-wide 10th/90th percentile (default)
    method="fixed"     uses fixed thresholds 112 / 147
    """
    gdf = gdf.copy()
    gdf["rad"] = 0.0
    zonstatrad = zonal_stats(gdf, radiationraster, stats="mean")
    for i in range(len(gdf)):
        val = zonstatrad[i]["mean"]
        gdf.loc[i, "rad"] = val if val is not None else 0.0
    gdf["radiation"] = 0
    if method == "quantile":
        przquant90 = gdf["rad"].quantile(q=0.9, interpolation="linear")
        przquant10 = gdf["rad"].quantile(q=0.1, interpolation="linear")
        gdf.loc[gdf["rad"] >= przquant90, "radiation"] = 1
        gdf.loc[gdf["rad"] <= przquant10, "radiation"] = -1
    else:  # fixed
        gdf.loc[gdf["rad"] >= 147.0, "radiation"] = 1
        gdf.loc[gdf["rad"] <= 112.0, "radiation"] = -1
    return gdf


def compute_hoehenstufen_1975(gdf, hoehenstufenraster):
    """Add hs1975 (majority raster class) to gdf. Returns modified gdf."""
    gdf = gdf.copy()
    gdf["hs1975"] = 0
    zonstaths = zonal_stats(gdf, hoehenstufenraster, stats="majority")
    for i in range(len(gdf)):
        val = zonstaths[i]["majority"]
        gdf.loc[i, "hs1975"] = val if val is not None else 0
    return gdf


# ---------------------------------------------------------------------------
# Standortregionen spatial join
# ---------------------------------------------------------------------------
def join_waldstandortregionen(gdf, storeg_path, layer=None):
    """Sjoin Waldstandortsregionen and return gdf with 'storeg' column.

    Uses minimum storeg per polygon (same as original canton scripts).
    gdf must have a 'joinid' column.
    """
    storeg = gpd.read_file(storeg_path, layer=layer) if layer else gpd.read_file(storeg_path)
    storeg.rename(columns={"Subcode": "storeg"}, inplace=True)
    drop_cols = [c for c in ['id', 'Region_de', 'Region_fr', 'Region_it', 'Region_en', 'Code',
                              'Code_Bu', 'Code_Fi', 'Shape_Leng', 'Shape_Area', 'Flaeche']
                 if c in storeg.columns]
    storeg.drop(columns=drop_cols, inplace=True)
    if "index_right" in gdf.columns:
        gdf = gdf.drop(columns=["index_right"])
    joined = gdf.sjoin(storeg, how="left", predicate="intersects")
    grouped = joined[["joinid", "storeg"]].groupby("joinid").min()
    gdf = gdf.merge(grouped, on="joinid", how="left")
    return gdf


def join_waldstandortregionen_overlay(gdf, storeg_path, layer=None):
    """Overlay-based Waldstandortsregionen join (used by VS and some cantons)."""
    storeg = gpd.read_file(storeg_path, layer=layer) if layer else gpd.read_file(storeg_path)
    storeg.rename(columns={"Subcode": "storeg"}, inplace=True)
    drop_cols = [c for c in ['id', 'Region_de', 'Region_fr', 'Region_it', 'Region_en', 'Code',
                              'Code_Bu', 'Code_Fi', 'Shape_Leng', 'Shape_Area', 'Flaeche']
                 if c in storeg.columns]
    storeg.drop(columns=drop_cols, inplace=True)
    overlaid = gpd.overlay(gdf, storeg[["storeg", "geometry"]], how="intersection")
    grouped = overlaid[["joinid", "storeg"]].groupby("joinid").min()
    gdf = gdf.merge(grouped, on="joinid", how="left")
    return gdf


# ---------------------------------------------------------------------------
# NaiS string parsing
# ---------------------------------------------------------------------------
def parse_nais_tokens(nais_str):
    """Split a NaiS string like '18M(48)' or '46/47' into a token list."""
    return (nais_str.replace("/", " ").replace("(", " ").replace(")", "")
            .replace("  ", " ").strip().split())


# ---------------------------------------------------------------------------
# tahs / tahsue assignment loop (standard, used by most cantons)
# ---------------------------------------------------------------------------
def assign_tahs(gdf, hoehenstufendictabkuerzungen, hsmoddictkurz):
    """Assign tahs and tahsue columns from hs string + hs1975 raster value.

    Modifies gdf in place and returns it.
    """
    for index, row in gdf.iterrows():
        hs = row["hs"]
        if not isinstance(hs, str) or hs == "":
            continue
        hslist = parse_nais_tokens(hs)
        if len(hslist) == 1:
            if hslist[0] in hoehenstufendictabkuerzungen:
                gdf.loc[index, "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
        elif len(hslist) > 1:
            if "(" in hs:
                gdf.loc[index, "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
                gdf.loc[index, "tahsue"] = hoehenstufendictabkuerzungen[hslist[1]]
            else:
                hs1975 = row["hs1975"]
                if hs1975 and int(hs1975) > 0 and int(hs1975) in hsmoddictkurz:
                    hsmod = hsmoddictkurz[int(hs1975)]
                    if hsmod in hslist:
                        gdf.loc[index, "tahs"] = hoehenstufendictabkuerzungen[hsmod]
                        if row["ue"] == 1:
                            gdf.loc[index, "tahsue"] = hoehenstufendictabkuerzungen[hsmod]
                    else:
                        gdf.loc[index, "tahs"] = hoehenstufendictabkuerzungen[hslist[-1]]
                        if row["ue"] == 1:
                            gdf.loc[index, "tahsue"] = hoehenstufendictabkuerzungen[hslist[-1]]
                else:
                    gdf.loc[index, "tahs"] = hoehenstufendictabkuerzungen[hslist[-1]]
                    gdf.loc[index, "tahsue"] = hoehenstufendictabkuerzungen[hslist[-1]]
    gdf.loc[(gdf["ue"] == 1) & (gdf["tahsue"] == ""), "tahsue"] = gdf["tahs"]
    gdf.loc[gdf["ue"] == 0, "tahsue"] = ""
    return gdf
