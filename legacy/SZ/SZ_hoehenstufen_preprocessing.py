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
#read geodata SZ
sz_gdf=gpd.read_file("S:/backup_az/CCWSZ/GIS/Modellergebnisse/szstandortstypenjoined.gpkg")
#sz_gdf=joblib.load("S:/backup_az/CCWSZ/GIS/Modellergebnisse/sz_rcp45_baumartenempfehlungen.sav")
sz_gdf.columns
sz_gdf=sz_gdf[["SZ Einheit","NaiS_LFI","geometry"]]
joblib.dump(sz_gdf,myworkspace+"/SZ"+"/SZ_standortstypen.sav")
sz_gdf.to_file(myworkspace+"/SZ"+"/SZ_standortstypen.gpkg", layer="SZ_standortstypen", driver="GPKG")
len(sz_gdf)
sz_unique=sz_gdf[["SZ Einheit","NaiS_LFI"]].drop_duplicates()
sz_unique["tahs"]=''
len(sz_unique)
sz_hs=gpd.read_file("S:/backup_az/CCWSZ/GIS/Vegetationshoehenstufen_ABENIS_Feld_20220125e_LV95.shp")
len(sz_hs)
sz_hs.columns
sz_hs=sz_hs[['Id', 'HS_de','geometry']]
sz_hs['tahs']=''
for item in hoehenstufenlist:
    sz_hs.loc[(sz_hs['HS_de']==item), 'tahs']=hoehenstufendict[item]
sz_hs.loc[(sz_hs['HS_de']=='hochmontan im Tannen-Hauptareal'), 'tahs']=hoehenstufendict['hochmontan']
#overlay
sz_hs_gdf = sz_gdf.overlay(sz_hs, how="intersection")
sz_gdf.to_file(myworkspace+"/SZ"+"/SZ_standortstypen_hs.gpkg", layer="SZ_standortstypen_hs", driver="GPKG")

#aggregate hoehenstufen
for index, row in sz_unique.iterrows():
    tahs_listshort = []
    naistyp=row["NaiS_LFI"]
    tempsel=sz_hs_gdf[sz_hs_gdf["NaiS_LFI"]==naistyp]
    tahs_list=tempsel["tahs"].unique().tolist()
    for item in tahs_list:
        if item in hoehenstufenlistshort and item not in tahs_listshort:
            tahs_listshort.append(item)
    sz_unique.loc[((sz_unique["NaiS_LFI"] == naistyp)), "tahs"] = str(tahs_listshort).replace("[","").replace("]","").replace("'","").replace(",","")

sz_unique.to_excel(codespace+"/SZ_nais_einheiten_unique.xlsx")

