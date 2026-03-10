import xlrd
import openpyxl
import pandas as pd
import geopandas as gpd
import numpy as np
import joblib

# *************************************************************
#environment settings
myworkspace='D:/CCW24sensi'
codespace='C:/DATA/develops/sensitivewaldstandorteCH'
hoehenstufendict={'collin':'co','submontan':'sm','untermontan':'um','obermontan':'om','hochmontan':'hm','subalpin':'sa','obersubalpin':'osa'}
hoehenstufenlist=['collin','submontan','untermontan','obermontan','hochmontan','subalpin','obersubalpin']
hoehenstufenlistshort=['co','sm','um','om','hm','sa','osa']


#read geodata LU
ju_gdf=gpd.read_file(myworkspace+'/JU/ENV_3_01_Phytosociologie_stations_forestieres/donnees.gpkg', layeer='env.env_03_01_phytosociologie_stations_forestieres')
len(ju_gdf)
ju_gdf.columns
ju_gdf=ju_gdf[['association','etiquette','nais1', 'naisue', 'hs1', 'hsue','geometry']]
#ju_gdf=ju_gdf[ju_gdf['hs1'].isna() == False]
print(ju_gdf['hs1'].unique().tolist())

ju_unique=ju_gdf[['association','etiquette','nais1', 'naisue']].drop_duplicates()
len(ju_unique)
ju_unique['tahs']=''
ju_unique['tauehs']=''

for index, row in ju_unique.iterrows():
    tahs_list=[]
    tahs_listshort = []
    tahsue_list = []
    tahsue_listshort = []
    nais1=row['nais1']
    nais2=row['naisue']
    #print(stotyp)
    tempsel=ju_gdf[(ju_gdf['nais1']==nais1)]
    tahs_list=tempsel['hs1'].unique().tolist()
    tempsel2 = ju_gdf[(ju_gdf['naisue'] == nais2)]
    tahsue_list = tempsel2['hsue'].unique().tolist()
    for item in tahs_list:
        if item not in tahs_listshort:
            tahs_listshort.append(item)
    for item in tahsue_list:
        if item not in tahsue_listshort:
            tahsue_listshort.append(item)
    ju_unique.loc[((ju_unique['nais1'] == nais1)), 'tahs'] = str(tahs_listshort).replace('[','').replace(']','').replace("'",'').replace(']','').replace('_','').replace('-','').replace('None','').replace(',','')
    ju_unique.loc[((ju_unique['naisue'] == nais2)), 'tauehs'] = str(tahsue_listshort).replace('[','').replace(']','').replace("'",'').replace(']','').replace('_','').replace('-','').replace('None','').replace(',','')

ju_unique.to_excel(codespace+'/JU_nais_einheiten_unique_v2.xlsx')