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

#read geodata BE
fr_gdf=gpd.read_file(myworkspace+"/geops_treeapp/forest_types_fr/forest_types_fr.shp")
len(fr_gdf)
fr_gdf.columns
fr_gdf=fr_gdf[["LEGENDE","ASSOC_TOT_","NaiS","Taux_1","Taux_2","Taux_3","geometry"]]
fr_gdf["tahs1"]=''
fr_gdf["tahs2"]=''
fr_gdf["tahs3"]=''
fr_gdf.loc[(fr_gdf["Taux_1"]==100),"tahs1"]="osa"
fr_gdf.loc[(fr_gdf["Taux_1"]==90),"tahs1"]="sa"
fr_gdf.loc[(fr_gdf["Taux_1"]==81),"tahs1"]="hm"
fr_gdf.loc[(fr_gdf["Taux_1"]==80),"tahs1"]="hm"
fr_gdf.loc[(fr_gdf["Taux_1"]==60),"tahs1"]="om"
fr_gdf.loc[(fr_gdf["Taux_1"]==50),"tahs1"]="um"
fr_gdf.loc[(fr_gdf["Taux_1"]==40),"tahs1"]="sm"
fr_gdf.loc[(fr_gdf["Taux_1"]==20),"tahs1"]="co"
fr_gdf.loc[(fr_gdf["Taux_2"]==100),"tahs2"]="osa"
fr_gdf.loc[(fr_gdf["Taux_2"]==90),"tahs2"]="sa"
fr_gdf.loc[(fr_gdf["Taux_2"]==81),"tahs2"]="hm"
fr_gdf.loc[(fr_gdf["Taux_2"]==80),"tahs2"]="hm"
fr_gdf.loc[(fr_gdf["Taux_2"]==60),"tahs2"]="om"
fr_gdf.loc[(fr_gdf["Taux_2"]==50),"tahs2"]="um"
fr_gdf.loc[(fr_gdf["Taux_2"]==40),"tahs2"]="sm"
fr_gdf.loc[(fr_gdf["Taux_2"]==20),"tahs2"]="co"
fr_gdf.loc[(fr_gdf["Taux_3"]==100),"tahs3"]="osa"
fr_gdf.loc[(fr_gdf["Taux_3"]==90),"tahs3"]="sa"
fr_gdf.loc[(fr_gdf["Taux_3"]==81),"tahs3"]="hm"
fr_gdf.loc[(fr_gdf["Taux_3"]==80),"tahs3"]="hm"
fr_gdf.loc[(fr_gdf["Taux_3"]==60),"tahs3"]="om"
fr_gdf.loc[(fr_gdf["Taux_3"]==50),"tahs3"]="um"
fr_gdf.loc[(fr_gdf["Taux_3"]==40),"tahs3"]="sm"
fr_gdf.loc[(fr_gdf["Taux_3"]==20),"tahs3"]="co"


fr_unique=fr_gdf[["LEGENDE","ASSOC_TOT_","NaiS"]].drop_duplicates()
len(fr_unique)
fr_unique["tahs1"]=''
fr_unique["tahs2"]=''
fr_unique["tahs3"]=''


for index, row in fr_unique.iterrows():
    tahs1_list=[]
    tahs2_list=[]
    tahs3_list=[]
    tahs1_listshort = []
    tahs2_listshort = []
    tahs3_listshort = []
    stotyp=row["ASSOC_TOT_"]
    #print(stotyp)
    tempsel=fr_gdf[fr_gdf["ASSOC_TOT_"]==stotyp]
    tahs1_list=tempsel["tahs1"].unique().tolist()
    tahs2_list = tempsel["tahs2"].unique().tolist()
    tahs3_list = tempsel["tahs3"].unique().tolist()
    for item in tahs1_list:
        if item not in tahs1_listshort:
            tahs1_listshort.append(item)
    for item in tahs2_list:
        if item not in tahs2_listshort:
            tahs2_listshort.append(item)
    for item in tahs3_list:
        if item not in tahs3_listshort:
            tahs3_listshort.append(item)
    fr_unique.loc[((fr_unique["ASSOC_TOT_"] == stotyp)), "tahs1"] = str(tahs1_listshort).replace("[","").replace("]","").replace("'","").replace("]","")
    fr_unique.loc[((fr_unique["ASSOC_TOT_"] == stotyp)), "tahs2"] = str(tahs2_listshort).replace("[", "").replace("]","").replace("'", "").replace("]", "")
    fr_unique.loc[((fr_unique["ASSOC_TOT_"] == stotyp)), "tahs3"] = str(tahs3_listshort).replace("[", "").replace("]","").replace("'", "").replace("]", "")

fr_unique.to_excel(codespace+"/FR_nais_einheiten_unique.xlsx")