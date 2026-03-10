CONFIG = {
    "canton": "BE",
    # Excel columns: BE, NaiS_LFI_JU, NaiS_LFI_M/A, hs, hsue
    # Custom logic: overlay taheute, overlay storeg (different files),
    # many canton-specific corrections; custom_hook=True
    "excel_file": "BE_nais_einheiten_unique_bh_20241128_bh_mf_v2.xlsx",
    "excel_sheet": "BE",
    "excel_format": "be_custom",
    "join_keys": ["BE"],
    "shapefile": "BE/bafu_baumartenempf_sens_standorte_20240212/stao_staohk_arrond_20240212.shp",
    "raster_dem": "BE/BE_dem10m.tif",
    "raster_slope": "BE/BE_slopeprz.tif",
    "raster_radiation": "BE/BE_globradyyw.tif",
    "raster_hs": "BE/BE_vegetationshoehenstufen1975.tif",
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
    "custom_hook": True,   # many corrections, custom hs logic
    "output_cols": [
        "joinid", "BE", "taheute", "storeg",
        "meanslopeprc", "slpprzrec", "rad", "radiation", "hs1975",
        "nais", "nais1", "nais2", "mo", "ue", "hs", "tahs", "tahsue", "geometry",
    ],
    "treeapp_cols": [
        "BE", "nais", "nais1", "nais2",
        "mo", "ue", "tahs", "tahsue", "geometry",
    ],
}
