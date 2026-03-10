CONFIG = {
    "canton": "GE",
    # Custom: 3-key join, no storeg, taheute=1, simplified hs logic
    # (if 'co' in hs and hs1975==2: tahs='collin' else: tahs='submontan')
    "excel_file": "GE_VEGETATION_einheiten_unique_bh2025_mf_bh.xlsx",
    "excel_sheet": "Sheet1",
    "excel_format": "nais_hs",
    "join_keys": ["VEGETATION", "NO_TYPOLOG", "MOSAIQUE"],
    "shapefile": "GE/SIPV_VEGETATION_5000.shp",
    "raster_dem": "GE/GE_dem10m.tif",
    "raster_slope": "GE/GE_slopeprz.tif",
    "raster_radiation": "GE/GE_globradyyw.tif",
    "raster_hs": "GE/GE_vegetationshoehenstufen1975.tif",
    "taheute_file": None,
    "taheute_method": "const1",
    "storeg_file": None,
    "storeg_method": "none",
    "radiation_method": "quantile",
    "dict_variant": "standard",
    "filter_col": None,
    "treeapp_col_start": 25,
    "treeapp_col_end": -2,
    "custom_hook": True,   # 3-key join, simplified hs logic, no storeg
    "output_cols": [
        "joinid", "VEGETATION", "NO_TYPOLOG", "MOSAIQUE", "taheute",
        "meanslopeprc", "slpprzrec", "rad", "radiation", "hs1975",
        "nais", "nais1", "nais2", "mo", "ue", "hs", "tahs", "tahsue", "geometry",
    ],
    "treeapp_cols": [
        "VEGETATION", "NO_TYPOLOG", "MOSAIQUE", "nais", "nais1", "nais2",
        "mo", "ue", "tahs", "tahsue", "geometry",
    ],
}
