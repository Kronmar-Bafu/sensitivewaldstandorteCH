CONFIG = {
    "canton": "GR",
    # Custom: starts from pre-processed gpkg (rasters already applied);
    # regional conditional logic via 'Bedingung' column;
    # 43 lines of ASS_GR value corrections
    "excel_file": "GR_nais_einheiten_unique_v2_bh_mf.xlsx",
    "excel_sheet": "Sheet1",
    "excel_format": "nais_hs",
    "join_keys": ["ASS_GR", "NAISbg"],
    # GR starts from pre-processed file, not raw shapefile + rasters
    "shapefile": "GR/stok_gdf_attributed_temp4_fixed.gpkg",
    # Rasters are commented out in the legacy script (already in shapefile)
    "raster_dem": "GR/gr_dem10m.tif",
    "raster_slope": None,   # pre-processed
    "raster_radiation": None,   # pre-processed
    "raster_hs": "GR/gr_vegetationshoehenstufen.tif",
    "taheute_file": None,
    "taheute_method": "in_file",   # already in pre-processed file
    "storeg_file": None,
    "storeg_method": "in_file",    # already in pre-processed file
    "radiation_method": "in_file",
    "dict_variant": "grvs",   # collin mit Buche="cob", um/om
    "filter_col": None,
    "treeapp_col_start": 25,
    "treeapp_col_end": -2,
    "custom_hook": True,   # pre-processed input, regional Bedingung logic
    "output_cols": [
        "joinid", "ASS_GR", "NAISbg", "taheute", "storeg",
        "meanslopeprc", "slpprzrec", "rad", "radiation", "hs1975",
        "nais", "nais1", "nais2", "mo", "ue", "hs", "tahs", "tahsue", "geometry",
    ],
    "treeapp_cols": [
        "ASS_GR", "NAISbg", "nais", "nais1", "nais2",
        "mo", "ue", "tahs", "tahsue", "geometry",
    ],
}
