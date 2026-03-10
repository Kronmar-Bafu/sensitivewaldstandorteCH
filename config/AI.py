CONFIG = {
    "canton": "AI",
    # Excel columns: WSTEinheit, nais, nais2, tahs, naisue, naismosaic
    # tahs is already computed in the excel — custom hook handles the join
    "excel_file": "AI_nais_einheiten_unique_mf.xlsx",
    "excel_sheet": None,   # default sheet
    "excel_format": "tahs_precomputed",
    "join_keys": ["WSTEinheit", "nais1alt", "naisue", "naismosaic"],
    "shapefile": "AI/stok_ai_wst_20250409.shp",
    "raster_dem": "AI/ai_dem10m.tif",
    "raster_slope": "AI/ai_slopeprz.tif",
    "raster_radiation": "AI/ai_globradyyw.tif",
    "raster_hs": "AI/ai_vegetationshoehenstufen.tif",
    "taheute_file": "Tannenareale.shp",
    "taheute_method": "sjoin",
    "storeg_file": "Waldstandortsregionen.shp",
    "storeg_method": "sjoin",
    "radiation_method": "fixed",
    "dict_variant": "standard",   # hsmoddictkurz starts at 3 (no key 2)
    "hsmoddictkurz_override": {3: "co", 4: "sm", 5: "um", 6: "om",
                                8: "hm", 9: "sa", 10: "osa"},
    "filter_col": None,
    "treeapp_col_start": 25,
    "treeapp_col_end": -2,
    "custom_hook": True,   # excel already has tahs; 4-key join
    "output_cols": [
        "joinid", "WSTEinheit", "nais1alt", "naisue", "naismosaic",
        "taheute", "storeg", "meanslopeprc", "slpprzrec", "rad", "radiation",
        "hs1975", "nais", "nais1", "nais2", "mo", "ue", "hs", "tahs", "tahsue",
        "geometry",
    ],
    "treeapp_cols": [
        "WSTEinheit", "nais1alt", "nais", "nais1", "nais2",
        "mo", "ue", "tahs", "tahsue", "geometry",
    ],
}
