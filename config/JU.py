CONFIG = {
    "canton": "JU",
    # Custom: overlay taheute, many corrections for association=='38'
    "excel_file": "JU_nais_einheiten_unique_v2_mf.xlsx",
    "excel_sheet": "Sheet1",
    "excel_format": "nais1_nais2_hs",
    "join_keys": ["association", "etiquette"],
    "shapefile": "JU/ENV_3_01_donnees_de_base_foret/donnees.gpkg",
    "raster_dem": "JU/JU_dem10m.tif",
    "raster_slope": "JU/JU_slopeprz.tif",
    "raster_radiation": "JU/JU_globradyyw.tif",
    "raster_hs": "JU/JU_vegetationshoehenstufen1975.tif",
    "taheute_file": "Tannenareale2025.gpkg",
    "taheute_method": "overlay",
    "storeg_file": "Waldstandortregionen_2024_TI4ab_Final_GR.gpkg",
    "storeg_layer": "waldstandortregionen_2024_ti4ab_final",
    "storeg_method": "sjoin",
    "radiation_method": "quantile",
    "dict_variant": "extended",
    "filter_col": None,
    "treeapp_col_start": 25,
    "treeapp_col_end": -2,
    "custom_hook": True,   # corrections for association=='38'
    "output_cols": [
        "joinid", "association", "etiquette", "taheute", "storeg",
        "meanslopeprc", "slpprzrec", "rad", "radiation", "hs1975",
        "nais", "nais1", "nais2", "mo", "ue", "hs", "tahs", "tahsue", "geometry",
    ],
    "treeapp_cols": [
        "association", "etiquette", "nais", "nais1", "nais2",
        "mo", "ue", "tahs", "tahsue", "geometry",
    ],
}
