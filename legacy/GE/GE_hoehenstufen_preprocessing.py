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
hoehenstufenlistshort=["co","sm","um","om","hm","sa","osa"]


#read geodata GE (VEGETATION)
ge_gdf=gpd.read_file(myworkspace+"/GE/SIPV_VEGETATION_5000.shp")
len(ge_gdf)
ge_gdf.columns
ge_gdf=ge_gdf[['VEG_ID', 'VEGETATION', 'MOSAIQUE', 'NO_TYPOLOG','NOM_TYPOLO', 'geometry']]
ge_unique=ge_gdf[['VEG_ID', 'VEGETATION', 'MOSAIQUE', 'NO_TYPOLOG','NOM_TYPOLO']].drop_duplicates()
len(ge_unique)
ge_unique.to_excel(codespace+"/GE_VEGETATION_einheiten_unique.xlsx")

#read geodata GE (FORET)
ge_gdf=gpd.read_file(myworkspace+"/GE/FFP_PHYTO_FORET_1963.shp")
len(ge_gdf)
ge_gdf.columns
ge_unique2=ge_gdf[['TYPE']].drop_duplicates()
len(ge_unique)
ge_unique2.to_excel(codespace+"/GE_FORET_einheiten_unique.xlsx")
