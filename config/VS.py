CONFIG = {
    "canton": "VS",
    # Special dict: collin mit Buche="cob", unter-/obermontan="um/om"
    # storeg_method="overlay" (not sjoin, unlike all other cantons)
    "excel_file": "VS_nais_einheiten_unique_mf.xlsx",
    "excel_sheet": "Sheet1",
    "excel_format": "nais1_nais2_hs",
    "join_keys": ["UNITE_NAIS", "UNITE_NA_1", "UNITE_NA_2"],
    "shapefile": "VS/STATIONS_20250430_fixed.gpkg",
    "raster_dem": "VS/VS_dem10m.tif",
    "raster_slope": "VS/VS_slopeprz.tif",
    "raster_radiation": "VS/VS_globradyyw.tif",
    "raster_hs": "VS/VS_vegetationshoehenstufen1975.tif",
    "taheute_file": "Tannenareale2025.gpkg",
    "taheute_method": "overlay",
    "storeg_file": "Waldstandortregionen_2024_TI4ab_Final_GR.gpkg",
    "storeg_layer": "waldstandortregionen_2024_ti4ab_final",
    "storeg_method": "overlay",   # VS uses overlay for storeg (unique!)
    "radiation_method": "quantile",
    "dict_variant": "grvs",   # collin mit Buche="cob", um/om
    "filter_col": None,
    "treeapp_col_start": 25,
    "treeapp_col_end": -1,
    "custom_hook": False,
    "output_cols": [
        "joinid", "UNITE_NAIS", "UNITE_NA_1", "UNITE_NA_2",
        "taheute", "storeg", "meanslopeprc", "slpprzrec", "rad", "radiation",
        "hs1975", "nais", "nais1", "nais2", "mo", "ue", "hs", "tahs", "tahsue",
        "geometry",
    ],
    "treeapp_cols": [
        "UNITE_NAIS", "UNITE_NA_1", "UNITE_NA_2", "nais", "nais1", "nais2",
        "mo", "ue", "tahs", "tahsue", "geometry",
    ],
}
