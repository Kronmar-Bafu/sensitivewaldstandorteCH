CONFIG = {
    "canton": "UR",
    # Custom: Bedingung Region + Bedingung Höhenstufe columns
    "excel_file": "UR_nais_einheiten_unique_v2_mf.xlsx",
    "excel_sheet": "Sheet1",
    "excel_format": "nais1_nais2_hs_bedingung",
    "excel_bedingung_cols": ["Bedingung Region", "Bedingung Höhenstufe"],
    "join_keys": ["Kategorie_"],
    "shapefile": "UR/Waldstandortkarte_20250204.shp",
    "raster_dem": "UR/UR_dem10m.tif",
    "raster_slope": "UR/UR_slopeprz.tif",
    "raster_radiation": "UR/UR_globradyyw.tif",
    "raster_hs": "UR/UR_vegetationshoehenstufen1975.tif",
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
    "custom_hook": True,   # Bedingung Region / Bedingung Höhenstufe
    "output_cols": [
        "joinid", "Kategorie_", "taheute", "storeg",
        "meanslopeprc", "slpprzrec", "rad", "radiation", "hs1975",
        "nais", "nais1", "nais2", "mo", "ue", "hs", "tahs", "tahsue", "geometry",
    ],
    "treeapp_cols": [
        "Kategorie_", "nais", "nais1", "nais2",
        "mo", "ue", "tahs", "tahsue", "geometry",
    ],
}
