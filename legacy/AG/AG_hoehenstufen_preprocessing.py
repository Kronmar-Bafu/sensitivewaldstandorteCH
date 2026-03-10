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
vergleichstabelle.columns
vergleichstabelle["hs1"]=""
for index, row in vergleichstabelle.iterrows():
    vergleichstabelle.loc[index,"hs1"]=str(vergleichstabelle.loc[index,"hs"]).replace("nan","")


#read geodata
ag_gdf=gpd.read_file(myworkspace+"/AG/AGIS.aw_stao/aw_stao_20100920.gpkg")
len(ag_gdf)
ag_gdf.columns

ag_df=pd.read_csv(myworkspace+"/AG/AG_NaiS_22_10_2019.txt", sep='\t')
ag_df.columns
ag_gdf= ag_gdf.merge(ag_df, left_on='STAO_87', right_on='Einheit_AG')
ag_gdf.columns
ag_gdf=ag_gdf[['STAO_87','STANDORT','Einheit_Nais', 'geometry']]

ag_unique=ag_gdf[['STAO_87', 'STANDORT','Einheit_Nais']].drop_duplicates()
len(ag_unique)
ag_unique.dtypes

ag_unique.to_excel(codespace+"/AG_nais_einheiten_unique_v2.xlsx")