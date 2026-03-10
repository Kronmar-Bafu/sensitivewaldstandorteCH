import xlrd
import openpyxl
import pandas as pd
import geopandas as gpd
import numpy as np
import joblib

# *************************************************************
#environment settings
myworkspace="D:/CCW24sensi"
codespace="C:/DATA/develops/sensitivewaldstandorteCH"
hoehenstufendict={"collin":"co","submontan":"sm","untermontan":"um","obermontan":"om","hochmontan":"hm","subalpin":"sa","obersubalpin":"osa"}
hoehenstufenlist=["collin","submontan","untermontan","obermontan","hochmontan","subalpin","obersubalpin"]

#read geodata SH
sh_gdf=gpd.read_file(myworkspace+"/SH/Waldstandortkarte_detailliert.shp")
len(sh_gdf)
sh_gdf.columns
sh_gdf=sh_gdf[['gm_id_fors', 'wg_nr',"geometry"]]

sh_unique=sh_gdf[["wg_nr"]].drop_duplicates()
len(sh_unique)
sh_unique=sh_unique.sort_values(by=["wg_nr"])

#sh_gdf.to_file(myworkspace+"/SH"+"/SH_standortstypen_hs.gpkg", layer="SH_standortstypen", driver="GPKG")
sh_unique.to_excel(codespace+"/SH_nais_einheiten_unique_v3.xlsx")