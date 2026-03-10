CONFIG = {
    "canton": "AG",
    "excel_file": "AG_nais_einheiten_unique_v2_mf_korr.xlsx",
    "excel_sheet": "Sheet1",
    "excel_nais_col": "NaiS vereinfacht",   # rename to "nais"
    "excel_format": "nais_hs",              # excel has nais + hs columns
    "join_keys": ["STAO_87", "STANDORT"],
    "shapefile": "AG/AGIS.aw_stao/aw_stao_20100920.gpkg",
    "raster_dem": "AG/ag_dem10m.tif",
    "raster_slope": "AG/ag_slopeprz.tif",
    "raster_radiation": "AG/ag_globradyyw.tif",
    "raster_hs": "AG/ag_hs1975.tif",
    "taheute_method": "const1",
    "storeg_file": "Waldstandortsregionen.shp",
    "storeg_method": "sjoin",
    "radiation_method": "quantile",
    "dict_variant": "standard",
    "filter_col": "STAO_87",
    "filter_val": "99",
    "treeapp_col_start": 27,
    "treeapp_col_end": -2,
    "custom_hook": False,
    "output_cols": [
        "joinid", "STAO_87", "STANDORT", "taheute", "storeg",
        "meanslopeprc", "slpprzrec", "rad", "radiation", "hs1975",
        "nais", "nais1", "nais2", "mo", "ue", "hs", "tahs", "tahsue", "geometry",
    ],
    "treeapp_cols": [
        "STAO_87", "STANDORT", "nais", "nais1", "nais2",
        "mo", "ue", "tahs", "tahsue", "geometry",
    ],
}
