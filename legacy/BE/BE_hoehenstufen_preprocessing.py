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
be_gdf=gpd.read_file("S:/backup_az/CCWBE/GIS/Modellergebnisse/be_rcp45_baumartenempfehlungen.shp")

be_gdf=be_gdf[["index","joinid","BE","nais","mo","ue","ta","taue","tahs", "tauehs","geometry"]]
joblib.dump(be_gdf,myworkspace+"/BE"+"/BE_standortstypen.sav")
be_gdf.to_file(myworkspace+"/BE"+"/BE_standortstypen.gpkg", layer="BE_standortstypen", driver="GPKG")
len(be_gdf)
be_unique=be_gdf[["BE","nais","mo","ue","ta","taue"]].drop_duplicates()
be_unique["tahs"]=''
be_unique["tauehs"]=''
len(be_unique)

for index, row in be_unique.iterrows():
    tahs_list=[]
    tauehslist=[]
    tahs_listshort = []
    tauehs_listshort = []
    naistyp=row["nais"]
    tempsel=be_gdf[be_gdf["nais"]==naistyp]
    tahs_list=tempsel["tahs"].unique().tolist()
    tauehs_list = tempsel["tauehs"].unique().tolist()
    for item in tahs_list:
        if item in hoehenstufendict:
            tahs_listshort.append(hoehenstufendict[item])
    for item in tauehs_list:
        if item in hoehenstufendict:
            tauehs_listshort.append(hoehenstufendict[item])
    be_unique.loc[((be_unique["nais"] == naistyp)), "tahs"] = str(tahs_listshort).replace("[","").replace("]","").replace("'","").replace("]","")
    be_unique.loc[((be_unique["nais"] == naistyp)), "tauehs"] = str(tauehs_listshort).replace("[", "").replace("'", "").replace("]","")

be_unique.to_excel(codespace+"/BE_nais_einheiten_unique.xlsx")

