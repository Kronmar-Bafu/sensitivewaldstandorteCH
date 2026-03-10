CONFIG = {
    "canton": "ZH",
    # Custom: 2 specific post-processing corrections (EK72=='61M', '62M'),
    # area filter, sjoin taheute
    "excel_file": "ZH_nais_einheiten_unique_mf_v2.xlsx",
    "excel_sheet": "Sheet1",
    "excel_format": "nais1_nais2_hs",
    "join_keys": ["EK72", "NAIS"],
    "shapefile": "ZH/forest_types_zh_merge_fixed.gpkg",
    "raster_dem": "ZH/zh_dem10m.tif",
    "raster_slope": "ZH/zh_slopeprz.tif",
    "raster_radiation": "ZH/zh_globradyyw.tif",
    "raster_hs": "ZH/zh_hs1975.tif",
    "taheute_file": "Tannenareale2025.gpkg",
    "taheute_method": "sjoin",
    "storeg_file": "Waldstandortregionen_2024_TI4ab_Final_GR.gpkg",
    "storeg_layer": "waldstandortregionen_2024_ti4ab_final",
    "storeg_method": "sjoin",
    "radiation_method": "quantile",
    "dict_variant": "extended",
    "filter_col": None,
    "treeapp_col_start": 25,
    "treeapp_col_end": -2,
    "custom_hook": True,   # EK72 corrections + area filter
    "output_cols": [
        "joinid", "EK72", "NAIS", "taheute", "storeg",
        "meanslopeprc", "slpprzrec", "rad", "radiation", "hs1975",
        "nais", "nais1", "nais2", "mo", "ue", "hs", "tahs", "tahsue", "geometry",
    ],
    "treeapp_cols": [
        "EK72", "NAIS", "nais", "nais1", "nais2",
        "mo", "ue", "tahs", "tahsue", "geometry",
    ],
}
