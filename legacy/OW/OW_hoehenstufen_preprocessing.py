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

#read geodata BE
ow_gdf=gpd.read_file("C:/DATA/projects/CCWOW/GIS/Modellergebnisse/ow_standortstypenjoined.gpkg")
len(ow_gdf)
ow_gdf.crs
ow_hs=gpd.read_file("C:/DATA/projects/CCWOW/GIS/ow_vegetationshoehenstufen19611990ensembleBereinigt4.shp")
ow_hs=ow_hs[['Id', 'gridcode', 'HS_de','geometry']]
len(ow_hs)
ow_hs.columns
ow_hs.crs
ow_hs=ow_hs.set_crs(crs="EPSG:2056")
ow_hs['tahs']=''
for item in hoehenstufenlist:
    ow_hs.loc[(ow_hs['HS_de']==item), 'tahs']=hoehenstufendict[item]
ow_hs.loc[(ow_hs['HS_de']=='hochmontan im Tannen-Hauptareal'), 'tahs']=hoehenstufendict['hochmontan']

#intersect
#ow_hs_gdf = ow_gdf.sjoin(ow_hs, how="left")
ow_hs_gdf = ow_gdf.overlay(ow_hs, how="intersection")
len(ow_hs_gdf)
ow_hs_gdf.columns
ow_hs_gdf['tahs']=''
for item in hoehenstufenlist:
    ow_hs_gdf.loc[(ow_hs_gdf['HS_de']==item), 'tahs']=hoehenstufendict[item]
joblib.dump(ow_hs_gdf,myworkspace+"/OW"+"/OW_standortstypen.sav")
ow_hs_gdf.to_file(myworkspace+"/OW"+"/OW_standortstypen_hs.gpkg", layer="OW_standortstypen", driver="GPKG")
#ow_hs_gdf=joblib.load(myworkspace+"/OW"+"/OW_standortstypen.sav")

ow_unique=ow_hs_gdf[["OW_Einheit","NaiS_LFI"]].drop_duplicates()
ow_unique["tahs"]=''
len(ow_unique)

for index, row in ow_unique.iterrows():
    tahs_list=[]
    tahs_listshort = []
    naistyp=row["NaiS_LFI"]
    tempsel=ow_hs_gdf[ow_hs_gdf["NaiS_LFI"]==naistyp]
    tahs_list=tempsel["tahs"].unique().tolist()
    for item in tahs_list:
        if item in hoehenstufenlistshort and item not in tahs_listshort:
            tahs_listshort.append(item)
    ow_unique.loc[index, "tahs"] = str(tahs_listshort).replace("[","").replace("]","").replace("'","").replace("]","")

ow_unique.to_excel(codespace+"/OW_nais_einheiten_unique.xlsx")

