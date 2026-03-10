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
zh_gdf=gpd.read_file(myworkspace+'/geops_treeapp/forest_types_zh_merge.gpkg')
len(zh_gdf)
zh_gdf.columns
zh_gdf=zh_gdf[['EK72', 'NAIS', 'HSTUFE', 'geometry']]
#zh_gdf=zh_gdf[zh_gdf['hs1'].isna() == False]
print(zh_gdf['HSTUFE'].unique().tolist())

zh_unique=zh_gdf[['EK72', 'NAIS']].drop_duplicates()
len(zh_unique)
zh_unique['tahs']=''

for index, row in zh_unique.iterrows():
    tahs_list=[]
    tahs_listshort = []
    #tahsue_list = []
    #tahsue_listshort = []
    nais1=row['NAIS']
    #nais2=row['naisue']
    #print(stotyp)
    tempsel=zh_gdf[(zh_gdf['NAIS']==nais1)]
    tahs_list=tempsel['HSTUFE'].unique().tolist()
    #tempsel2 = zh_gdf[(zh_gdf['naisue'] == nais2)]
    #tahsue_list = tempsel2['hsue'].unique().tolist()
    for item in tahs_list:
        if item not in tahs_listshort:
            tahs_listshort.append(item)
    #for item in tahsue_list:
    #    if item not in tahsue_listshort:
    #        tahsue_listshort.append(item)
    zh_unique.loc[((zh_unique['NAIS'] == nais1)), 'tahs'] = str(tahs_listshort).replace('[','').replace(']','').replace("'",'').replace(']','').replace('_','').replace('-','').replace('None','').replace(',','')
    #zh_unique.loc[((zh_unique['naisue'] == nais2)), 'tauehs'] = str(tahsue_listshort).replace('[','').replace(']','').replace("'",'').replace(']','').replace('_','').replace('-','').replace('None','').replace(',','')

zh_unique.to_excel(codespace+'/ZH_nais_einheiten_unique.xlsx')