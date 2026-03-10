CONFIG = {
    "canton": "OW",
    # Note: legacy script used absolute paths for DEM/slope from an older project.
    # Standard OW paths are used here; verify before running.
    "excel_file": "OW_nais_einheiten_unique_bh_20241128_mf.xlsx",
    "excel_sheet": None,
    "excel_format": "nais1_nais2_hs",
    "join_keys": ["wg_haupt", "wg_zusatz"],
    "shapefile": "OW/OW_standortstypen_hs.gpkg",
    "raster_dem": "OW/OW_dem10m.tif",
    "raster_slope": "OW/OW_slopeprz.tif",
    "raster_radiation": "OW/OW_globradyyw.tif",
    "raster_hs": "OW/OW_vegetationshoehenstufen1975.tif",
    "taheute_file": "Tannenareale.shp",
    "taheute_method": "const1",
    "storeg_file": "Waldstandortsregionen.shp",
    "storeg_method": "const1",
    "radiation_method": "quantile",
    "dict_variant": "standard",
    "filter_col": None,
    "treeapp_col_start": 25,
    "treeapp_col_end": -2,
    "custom_hook": False,
    "output_cols": [
        "joinid", "wg_haupt", "wg_zusatz", "taheute", "storeg",
        "meanslopeprc", "slpprzrec", "rad", "radiation", "hs1975",
        "nais", "nais1", "nais2", "mo", "ue", "hs", "tahs", "tahsue", "geometry",
    ],
    "treeapp_cols": [
        "wg_haupt", "wg_zusatz", "nais", "nais1", "nais2",
        "mo", "ue", "tahs", "tahsue", "geometry",
    ],
}
