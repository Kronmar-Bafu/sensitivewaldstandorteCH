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

#read geodata AI
ai_gdf=gpd.read_file(myworkspace+"/AI/stok_ai_wst_20250409.shp")
len(ar_gdf)
ai_gdf.columns
ai_gdf=ai_gdf[['WSTEinheit', 'nais1', 'naisue','naismosaic', 'hs1', 'hsue', 'hsmosaic', 'geometry']]

ai_unique=ar_gdf[['WSTEinheit', 'nais1', 'naisue','naismosaic', 'hs1', 'hsue', 'hsmosaic']].drop_duplicates()
len(ai_unique)
ai_unique.dtypes

ai_unique["NaiS"]=''
ai_unique["hs"]=''

ai_unique.to_excel(codespace+"/AI_nais_einheiten_unique.xlsx")


#read geodata AI
ai_gdf=gpd.read_file(myworkspace+"/AI/Waldstandortkarte AI_polygon.shp")
len(ai_gdf)
ai_gdf.columns
ai_unique=ai_gdf[['INFO']].drop_duplicates()
len(ai_unique)
ai_unique.dtypes


ai_unique.to_excel(codespace+"/AI_Waldstandortskarte_einheiten_unique.xlsx")