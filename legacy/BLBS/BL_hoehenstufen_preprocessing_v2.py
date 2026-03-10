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
bl_gdf=gpd.read_file(myworkspace+"/BLBS/standortskarte_BLBS_spatialjoin.gpkg")
len(bl_gdf)
bl_gdf['area']=bl_gdf['geometry'].area
bl_gdf=bl_gdf[bl_gdf['area']>0]
bl_gdf.columns
bl_gdf=bl_gdf[['g1_txt','waldgesell','nais_2022', 'hoehenstuf', 'hs', "geometry"]]
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

bl_unique=bl_gdf[['g1_txt','waldgesell','nais_2022']].drop_duplicates()
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

bl_unique.to_excel(codespace+"/BL_nais_einheiten_unique_v2.xlsx")



#originaltebelle only
bl_gdf=gpd.read_file(myworkspace+"/BLBS/Standortskarte_fixed.gpkg")
len(bl_gdf)
bl_gdf['area']=bl_gdf['geometry'].area
bl_gdf=bl_gdf[bl_gdf['area']>0]
bl_gdf.columns

bl_unique=bl_gdf[['g1_txt','waldgesell']].drop_duplicates()
len(bl_unique)
bljoin=pd.read_excel(codespace+"/BL_nais_einheiten_unique_v2_mf.xlsx", engine='openpyxl')
bljoin.columns
bljoin=bljoin[['g1_txt', 'waldgesell','nais_2025','tahs_2025']]
len(bljoin)
bljoin=bljoin[bljoin['nais_2025'].isna() == False]
len(bljoin)
bl_unique2=pd.merge(bl_unique,bljoin, left_on=['g1_txt', 'waldgesell'], right_on=['g1_txt', 'waldgesell'], how='left')
len(bl_unique2)
bl_unique.to_excel(codespace+"/BL_nais_einheiten_unique_v3.xlsx")

#treeapp only
bl_gdf=gpd.read_file(myworkspace+"/geops_treeapp/forest_types_bl/forest_types_bl.shp")
len(bl_gdf)
bl_gdf['area']=bl_gdf['geometry'].area
bl_gdf=bl_gdf[bl_gdf['area']>0]
bl_gdf.columns

bl_unique=bl_gdf[['nais_2022', 'hoehenstuf']].drop_duplicates()
len(bl_unique)
bl_unique.to_excel(codespace+"/BL_nais_einheiten_unique_v4_treeapp.xlsx")