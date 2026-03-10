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

#read geodata SO
#so_gdf=gpd.read_file(myworkspace+"/geops_treeapp/forest_types_so/forest_types_so.shp")
so_gdf=gpd.read_file(myworkspace+"/SO/Waldstandorte_SO_NaiS_HS_2024-02-13.shp")
len(so_gdf)
so_gdf.columns
so_gdf=so_gdf[['stantrung','stanrgert', 'stanrnigt','stan_nais', 'grunnheit', 'legende','HS',"geometry"]]
print(so_gdf['HS'].unique().tolist())
#print(so_gdf['hsue_code'].unique().tolist())
so_gdf["tahs"]=''
so_gdf["tahsue"]=''
so_gdf.loc[(so_gdf["HS"]=='obersubalpin'),"tahs"]="osa"
so_gdf.loc[(so_gdf["HS"]=='subalpin'),"tahs"]="sa"
so_gdf.loc[(so_gdf["HS"]=='hochmontan'),"tahs"]="hm"
so_gdf.loc[(so_gdf["HS"]=='obermontan'),"tahs"]="om"
so_gdf.loc[(so_gdf["HS"]=='untermontan'),"tahs"]="um"
so_gdf.loc[(so_gdf["HS"]=='submontan'),"tahs"]="sm"
so_gdf.loc[(so_gdf["HS"]=='collin'),"tahs"]="co"
so_gdf.loc[(so_gdf["HS"]=='obersubalpin'),"tahs"]="osa"
so_gdf.loc[(so_gdf["HS"]=='subalpin'),"tahs"]="sa"
so_gdf.loc[(so_gdf["HS"]=='hochmontan'),"tahs"]="hm"
so_gdf.loc[(so_gdf["HS"]=='obermontan'),"tahs"]="om"
so_gdf.loc[(so_gdf["HS"]=='untermontan'),"tahs"]="um"
so_gdf.loc[(so_gdf["HS"]=='submontan'),"tahs"]="sm"
so_gdf.loc[(so_gdf["HS"]=='collin'),"tahs"]="co"
so_gdf.loc[(so_gdf["HS"]=='collin'),"tahs"]="co"
#so_gdf.loc[(so_gdf['hsue_code']==40),'tahsue']="sm"

so_unique=so_gdf[['stantrung','stanrgert', 'stanrnigt','stan_nais', 'grunnheit']].drop_duplicates()
len(so_unique)
so_unique["tahs"]=''
so_unique["tahsue"]=''

for index, row in so_unique.iterrows():
    tahs_list=[]
    tahs_listshort = []
    tahsue_list = []
    tahsue_listshort = []
    stotyp=row["stan_nais"]
    stotyp2 = row["grunnheit"]
    #print(stotyp)
    tempsel=so_gdf[((so_gdf["stan_nais"]==stotyp)&(so_gdf["grunnheit"]==stotyp2))]
    tahs_list=tempsel["tahs"].unique().tolist()
    tahsue_list = tempsel["tahsue"].unique().tolist()
    for item in tahs_list:
        if item not in tahs_listshort:
            tahs_listshort.append(item)
    for item in tahsue_list:
        if item not in tahsue_listshort:
            tahsue_listshort.append(item)
    so_unique.loc[((so_unique["stan_nais"] == stotyp)), "tahs"] = str(tahs_listshort).replace("[","").replace("]","").replace("'","").replace("]","")
    so_unique.loc[((so_unique["grunnheit"] == stotyp)), "tahsue"] = str(tahsue_listshort).replace("[", "").replace("]", "").replace("'", "").replace("]", "")

so_unique.to_excel(codespace+"/SO_nais_einheiten_unique_v2.xlsx")