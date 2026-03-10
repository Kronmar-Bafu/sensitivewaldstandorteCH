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


#read geodata BL
bl_gdf=gpd.read_file(myworkspace+"/geops_treeapp/forest_types_bl/forest_types_bl.shp")
len(bl_gdf)
bl_gdf.columns
bl_gdf=bl_gdf[['id','nais_2022', 'hoehenstuf', 'hs', "geometry"]]
print(bl_gdf['hoehenstuf'].unique().tolist())
bl_gdf["tahs"]=''
bl_gdf.loc[(bl_gdf["hoehenstuf"]=='obersubalpin'),"tahs"]="osa"
bl_gdf.loc[(bl_gdf["hoehenstuf"]=='subalpin'),"tahs"]="sa"
bl_gdf.loc[(bl_gdf["hoehenstuf"]=='hochmontan'),"tahs"]="hm"
bl_gdf.loc[(bl_gdf["hoehenstuf"]=='obermontan'),"tahs"]="om"
bl_gdf.loc[(bl_gdf["hoehenstuf"]=='untermontan'),"tahs"]="um"
bl_gdf.loc[(bl_gdf["hoehenstuf"]=='submontan'),"tahs"]="sm"
bl_gdf.loc[(bl_gdf["hoehenstuf"]=='collin'),"tahs"]="co"
bl_gdf.loc[(bl_gdf["hoehenstuf"]=='obersubalpin'),"tahs"]="osa"
bl_gdf.loc[(bl_gdf["hoehenstuf"]=='subalpin'),"tahs"]="sa"
bl_gdf.loc[(bl_gdf["hoehenstuf"]=='hochmontan'),"tahs"]="hm"
bl_gdf.loc[(bl_gdf["hoehenstuf"]=='obermontan'),"tahs"]="om"
bl_gdf.loc[(bl_gdf["hoehenstuf"]=='untermontan'),"tahs"]="um"
bl_gdf.loc[(bl_gdf["hoehenstuf"]=='submontan'),"tahs"]="sm"
bl_gdf.loc[(bl_gdf["hoehenstuf"]=='collin'),"tahs"]="co"
print(bl_gdf['tahs'].unique().tolist())

bl_unique=bl_gdf[['nais_2022']].drop_duplicates()
len(bl_unique)
bl_unique["tahs"]=''


for index, row in bl_unique.iterrows():
    tahs_list=[]
    tahs_listshort = []
    stotyp=row["nais_2022"]
    #print(stotyp)
    tempsel=bl_gdf[(bl_gdf["nais_2022"]==stotyp)]
    tahs_list=tempsel["tahs"].unique().tolist()
    for item in tahs_list:
        if item not in tahs_listshort:
            tahs_listshort.append(item)
    bl_unique.loc[((bl_unique["nais_2022"] == stotyp)), "tahs"] = str(tahs_listshort).replace("[","").replace("]","").replace("'","").replace("]","")

bl_unique.to_excel(codespace+"/BL_nais_einheiten_unique.xlsx")