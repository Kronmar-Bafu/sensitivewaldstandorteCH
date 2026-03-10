CONFIG = {
    "canton": "FR",
    # Very custom: slope-condition-based and region-based hs logic,
    # many post-processing corrections; custom_hook=True
    "excel_file": "FR_nais_einheiten_unique_mf_mit_7f.xlsx",
    "excel_sheet": "Sheet1_sortiert",
    "excel_format": "nais1_nais2_hs",
    "join_keys": ["ASSOC_TOT_", "LEGENDE"],
    "shapefile": "geops_treeapp/forest_types_fr/forest_types_fr.shp",
    "raster_dem": "FR/dem10m.tif",
    "raster_slope": "FR/slope10mprz.tif",
    "raster_radiation": "FR/globradyw.tif",
    "raster_hs": "FR/hs1975.tif",
    "taheute_file": "Tannenareale.shp",
    "taheute_method": "sjoin",
    "storeg_file": "Waldstandortsregionen.shp",
    "storeg_method": "sjoin",
    "radiation_method": "fixed",
    "dict_variant": "standard",
    "filter_col": None,
    "treeapp_col_start": 25,
    "treeapp_col_end": -2,
    "custom_hook": True,   # slope/region-based hs, many corrections
    "output_cols": [
        "joinid", "ASSOC_TOT_", "LEGENDE", "taheute", "storeg",
        "meanslopeprc", "slpprzrec", "rad", "radiation", "hs1975",
        "naisdetail", "nais", "nais1", "nais2", "mo", "ue", "hs", "tahs", "tahsue", "geometry",
    ],
    "treeapp_cols": [
        "ASSOC_TOT_", "LEGENDE", "nais", "nais1", "nais2",
        "mo", "ue", "tahs", "tahsue", "geometry",
    ],
}
