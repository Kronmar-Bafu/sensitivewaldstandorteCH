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
vs_gdf=gpd.read_file(myworkspace+"/VS/VS_20250505/STATIONS_20250430.shp")
len(vs_gdf)
vs_gdf.columns
vs_gdf['hs']=''
vs_gdf['HSTUFE'].unique().tolist()
vs_gdf.loc[vs_gdf['HSTUFE']==10,'hs']='osa'
vs_gdf.loc[vs_gdf['HSTUFE']==9,'hs']='sa'
vs_gdf.loc[vs_gdf['HSTUFE']==8,'hs']='hm'
vs_gdf.loc[vs_gdf['HSTUFE']==6,'hs']='om'
vs_gdf.loc[vs_gdf['HSTUFE']==5,'hs']='um'
vs_gdf.loc[vs_gdf['HSTUFE']==4,'hs']='sm'
vs_gdf.loc[vs_gdf['HSTUFE']==2,'hs']='co'
vs_gdf['hs'].unique().tolist()


vs_gdf=vs_gdf[['UNITE_NAIS', 'UNITE_NA_1','UNITE_NA_2','Bez_DE','hs','geometry']]

vs_unique=vs_gdf[['UNITE_NAIS', 'UNITE_NA_1','UNITE_NA_2','Bez_DE','hs']].drop_duplicates()
len(vs_unique)
vs_unique.sort_values(by=["UNITE_NAIS", "UNITE_NA_1", "UNITE_NA_2", 'hs'], inplace=True)

vs_unique.to_excel(codespace+"/VS_nais_einheiten_unique.xlsx")
