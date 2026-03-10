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
jointab=pd.read_excel(codespace+'/joinhs.xlsx', engine='openpyxl')#dtype='str',

#read geodata VD
vd_gdf=gpd.read_file(myworkspace+"/VD/vdstandortstypenarrondiertV3joined_entw.gpkg")
len(vd_gdf)
vd_gdf.columns
vd_gdf.crs
#join hs table
vd_gdf=vd_gdf.merge(jointab, left_on='hs', right_on='hs', how='left')
vd_gdf.columns
vd_gdf=vd_gdf[vd_gdf['joinid']>0]
#create unique table
vd_unique=vd_gdf[["VD Einheit","NaiS_LFI"]].drop_duplicates()
vd_unique["tahs"]=''
len(vd_unique)

for index, row in vd_unique.iterrows():
    tahs_list=[]
    tahs_listshort = []
    naistyp=row["NaiS_LFI"]
    tempsel=vd_gdf[vd_gdf["NaiS_LFI"]==naistyp]
    tahs_list=tempsel["tahs"].unique().tolist()
    for item in tahs_list:
        if item in hoehenstufenlistshort and item not in tahs_listshort:
            tahs_listshort.append(item)
    vd_unique.loc[index, "tahs"] = str(tahs_listshort).replace("[","").replace("]","").replace("'","").replace("]","")

vd_unique.to_excel(codespace+"/VD_nais_einheiten_unique_v2.xlsx")

