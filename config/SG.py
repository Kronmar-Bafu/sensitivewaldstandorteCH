CONFIG = {
    "canton": "SG",
    # Custom: excel has Bedingung Hoehenstufe + Bedingung Region columns
    # with conditional hs assignment logic
    "excel_file": "SG_nais_einheiten_unique_mf.xlsx",
    "excel_sheet": "Sheet1",
    "excel_format": "nais1_nais2_hs_bedingung",
    "excel_bedingung_cols": ["Bedingung Hoehenstufe", "Bedingung Region"],
    "join_keys": ["DTWGEINHEI"],
    "shapefile": "SG/forest_types_sg.shp",
    "raster_dem": "SG/SG_dem10m.tif",
    "raster_slope": "SG/SG_slopeprz.tif",
    "raster_radiation": "SG/SG_globradyyw.tif",
    "raster_hs": "SG/SG_vegetationshoehenstufen1975.tif",
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
    "custom_hook": True,   # Bedingung Hoehenstufe / Bedingung Region
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
