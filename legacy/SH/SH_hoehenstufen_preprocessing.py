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
sh_gdf=gpd.read_file(myworkspace+"/SH/SH_forest_types_intsct_Waldstandortkarte_detailliert.gpkg")
len(sh_gdf)
sh_gdf.columns
sh_gdf=sh_gdf[["wg_nr","waldgesell","nais","naisue","Tree-App_2","geometry"]]
print(sh_gdf['Tree-App_2'].unique().tolist())
sh_gdf["tahs"]=''
sh_gdf.loc[(sh_gdf["Tree-App_2"]=='obersubalpin'),"tahs"]="osa"
sh_gdf.loc[(sh_gdf["Tree-App_2"]=='subalpin'),"tahs"]="sa"
sh_gdf.loc[(sh_gdf["Tree-App_2"]=='hochmontan'),"tahs"]="hm"
sh_gdf.loc[(sh_gdf["Tree-App_2"]=='sub u. untermontan'),"tahs"]="sm um"
sh_gdf.loc[(sh_gdf["Tree-App_2"]=='obermontan'),"tahs"]="om"
sh_gdf.loc[(sh_gdf["Tree-App_2"]=='untermontan'),"tahs"]="um"
sh_gdf.loc[(sh_gdf["Tree-App_2"]=='submontan'),"tahs"]="sm"
sh_gdf.loc[(sh_gdf["Tree-App_2"]=='collin'),"tahs"]="co"
print(sh_gdf['tahs'].unique().tolist())

sh_unique=sh_gdf[["wg_nr",'waldgesell', 'nais', 'naisue']].drop_duplicates()
len(sh_unique)
sh_unique["tahs"]=''

for index, row in sh_unique.iterrows():
    tahs_list=[]
    tahs_listshort = []
    stotyp=row["nais"]
    #print(stotyp)
    tempsel=sh_gdf[sh_gdf["nais"]==stotyp]
    tahs_list=tempsel["tahs"].unique().tolist()
    for item in tahs_list:
        if item not in tahs_listshort:
            tahs_listshort.append(item)
    sh_unique.loc[((sh_unique["nais"] == stotyp)), "tahs"] = str(tahs_listshort).replace("[","").replace("]","").replace("'","").replace("]","")

#sh_gdf.to_file(myworkspace+"/SH"+"/SH_standortstypen_hs.gpkg", layer="SH_standortstypen", driver="GPKG")
sh_unique.to_excel(codespace+"/SH_nais_einheiten_unique_v2.xlsx")