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

vergleichstabelle=pd.read_excel(codespace+"/"+"SG_nais_einheiten_unique.xlsx", dtype="str", engine='openpyxl')
vergleichstabelle["hs"]=""
for index, row in vergleichstabelle.iterrows():
    vergleichstabelle.loc[index,"hs"]=str(vergleichstabelle.loc[index,"hs1"]).replace("nan","")+str(vergleichstabelle.loc[index,"hs2"]).replace("nan","")

#read geodata BE
ar_gdf=gpd.read_file(myworkspace+"/AR/forest_types_ar.gpkg")
len(ar_gdf)
ar_gdf.columns
ar_gdf=ar_gdf[["DTWGEINHEI","tkeyStok_NaisTypCode","tkeyNaisTypen_NaiSTypNam","geometry"]]
ar_gdf=ar_gdf.astype({"tkeyStok_NaisTypCode":int})

ar_unique=ar_gdf[["DTWGEINHEI","tkeyStok_NaisTypCode","tkeyNaisTypen_NaiSTypNam"]].drop_duplicates()
len(ar_unique)
ar_unique.dtypes

ar_gdf=ar_gdf.astype({"tkeyStok_NaisTypCode":int})
ar_unique["NaiS"]=''
ar_unique["hs"]=''


for index, row in ar_unique.iterrows():
    areinheit=row["DTWGEINHEI"]
    nais=vergleichstabelle[(vergleichstabelle["SG"]==areinheit)]["NaiS"].unique().tolist()
    hs=vergleichstabelle[(vergleichstabelle["SG"]==areinheit)]["hs"].unique().tolist()
    ar_unique.loc[((ar_unique["DTWGEINHEI"] == areinheit)), "NaiS"] = str(nais).replace("[","").replace("]","").replace("'","").replace("]","")
    ar_unique.loc[((ar_unique["DTWGEINHEI"] == areinheit)), "hs"] = str(hs).replace("[", "").replace("]","").replace("'", "").replace("]", "").replace(",","")

ar_unique.to_excel(codespace+"/AR_nais_einheiten_unique.xlsx")