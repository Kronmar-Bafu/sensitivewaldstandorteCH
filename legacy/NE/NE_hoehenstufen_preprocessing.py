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


#read geodata NE
ne_gdf=gpd.read_file(myworkspace+"/geops_treeapp/forest_types_ne/forest_types_ne.shp")
len(ne_gdf)
ne_gdf.columns
ne_gdf=ne_gdf[['code_neuch', 'code_nais','hohenstufe', "geometry"]]
print(ne_gdf['hohenstufe'].unique().tolist())
ne_gdf["tahs"]=''
ne_gdf.loc[(ne_gdf['hohenstufe']==100),'tahs']='osa'
ne_gdf.loc[(ne_gdf['hohenstufe']==90),'tahs']='sa'
ne_gdf.loc[(ne_gdf['hohenstufe']==83),'tahs']='hm'
ne_gdf.loc[(ne_gdf['hohenstufe']==82),'tahs']='hm'
ne_gdf.loc[(ne_gdf['hohenstufe']==81),'tahs']='hm'
ne_gdf.loc[(ne_gdf['hohenstufe']==80),'tahs']='hm'
ne_gdf.loc[(ne_gdf['hohenstufe']==60),'tahs']='om'
ne_gdf.loc[(ne_gdf['hohenstufe']==50),'tahs']='um'
ne_gdf.loc[(ne_gdf['hohenstufe']==40),'tahs']='sm'
ne_gdf.loc[(ne_gdf['hohenstufe']==20),'tahs']='co'
print(ne_gdf['tahs'].unique().tolist())

ne_unique=ne_gdf[['code_neuch', 'code_nais']].drop_duplicates()
len(ne_unique)
ne_unique["tahs"]=''

for index, row in ne_unique.iterrows():
    tahs_list=[]
    tahs_listshort = []
    stotyp=row["code_nais"]
    #print(stotyp)
    tempsel=ne_gdf[(ne_gdf["code_nais"]==stotyp)]
    tahs_list=tempsel["tahs"].unique().tolist()
    for item in tahs_list:
        if item not in tahs_listshort:
            tahs_listshort.append(item)
    ne_unique.loc[((ne_unique["code_nais"] == stotyp)), "tahs"] = str(tahs_listshort).replace("[","").replace("]","").replace("'","").replace("]","")

ne_unique.to_excel(codespace+"/NE_nais_einheiten_unique.xlsx")