CONFIG = {
    "canton": "AR",
    "excel_file": "AR_nais_einheiten_unique_mf_mit_7f.xlsx",
    "excel_sheet": None,
    "excel_format": "nais1_nais2_hs",   # nais pre-split in excel
    "join_keys": ["DTWGEINHEI"],
    "shapefile": "AR/forest_types_ar.gpkg",
    "raster_dem": "AR/dem10m.tif",
    "raster_slope": "AR/slope10mprz.tif",
    "raster_radiation": "AR/globradyw.tif",
    "raster_hs": "AR/hs1975.tif",
    "taheute_file": "Tannenareale.shp",
    "taheute_method": "sjoin",
    "storeg_file": "Waldstandortsregionen.shp",
    "storeg_method": "sjoin",
    "radiation_method": "fixed",
    "dict_variant": "standard",   # hsmoddictkurz starts at 3 (no key 2)
    "hsmoddictkurz_override": {3: "co", 4: "sm", 5: "um", 6: "om",
                                8: "hm", 9: "sa", 10: "osa"},
    "filter_col": None,
    "treeapp_col_start": 26,
    "treeapp_col_end": -1,
    "custom_hook": False,
    "output_cols": [
        "joinid", "DTWGEINHEI", "taheute", "storeg",
        "meanslopeprc", "slpprzrec", "rad", "radiation", "hs1975",
        "nais", "nais1", "nais2", "mo", "ue", "hs", "tahs", "tahsue", "geometry",
    ],
    "treeapp_cols": [
        "DTWGEINHEI", "nais", "nais1", "nais2",
        "mo", "ue", "tahs", "tahsue", "geometry",
    ],
}
