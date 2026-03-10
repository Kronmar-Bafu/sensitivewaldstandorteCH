CONFIG = {
    "canton": "SO",
    # Custom: Bedingung Höhenstufe column
    "excel_file": "SO_nais_einheiten_unique_v2_mf.xlsx",
    "excel_sheet": "Sheet1",
    "excel_format": "nais1_nais2_hs_bedingung",
    "excel_bedingung_cols": ["Bedingung Höhenstufe"],
    "join_keys": ["stantrung", "stanrgert", "stanrnigt"],
    "shapefile": "SO/Waldstandorte_SO_NaiS_HS_2024-02-13.shp",
    "raster_dem": "SO/SO_dem10m.tif",
    "raster_slope": "SO/SO_slopeprz.tif",
    "raster_radiation": "SO/SO_globradyyw.tif",
    "raster_hs": "SO/SO_vegetationshoehenstufen1975.tif",
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
    "custom_hook": True,   # Bedingung Höhenstufe
    "output_cols": [
        "joinid", "stantrung", "stanrgert", "stanrnigt", "taheute", "storeg",
        "meanslopeprc", "slpprzrec", "rad", "radiation", "hs1975",
        "nais", "nais1", "nais2", "mo", "ue", "hs", "tahs", "tahsue", "geometry",
    ],
    "treeapp_cols": [
        "stantrung", "stanrgert", "stanrnigt", "nais", "nais1", "nais2",
        "mo", "ue", "tahs", "tahsue", "geometry",
    ],
}
