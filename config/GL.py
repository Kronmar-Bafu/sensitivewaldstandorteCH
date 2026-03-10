CONFIG = {
    "canton": "GL",
    # Custom: Bedingung Hangneigung + Bedingung Höhenstufe columns,
    # taheute=1, storeg=1, very custom hs logic with hsdictzuzahlen
    "excel_file": "GL_nais_einheiten_unique_joined_mf_Version26112024.xlsx",
    "excel_sheet": None,
    "excel_format": "nais1_nais2_hs",
    "join_keys": ["wg_haupt", "wg_zusatz"],
    "shapefile": "GL/waldgesellschaften/waldgesellschaften_fixed/waldgesellschaften.shp",
    "raster_dem": "GL/dem10m.tif",
    "raster_slope": "GL/slope10mprz.tif",
    "raster_radiation": "GL/globradyw.tif",
    "raster_hs": "GL/hs1975.tif",
    "taheute_file": None,
    "taheute_method": "const1",
    "storeg_file": None,
    "storeg_method": "const1",
    "radiation_method": "fixed",
    "dict_variant": "standard",
    "filter_col": None,
    "treeapp_col_start": 26,
    "treeapp_col_end": -1,
    "custom_hook": True,   # Bedingung columns, reverse dict for hs
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
