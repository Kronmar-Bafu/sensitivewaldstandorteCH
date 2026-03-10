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


#read geodata ZG
zg_gdf=gpd.read_file(myworkspace+'/ZG/ZG_kartierung_merge.gpkg')
len(zg_gdf)
zg_gdf.columns
zg_gdf=zg_gdf[['NUMMER', 'Beschriftu','geometry']]
#zg_gdf=zg_gdf[zg_gdf['hs1'].isna() == False]



#merge Uebersetzungstabelle
uetab=pd.read_excel(codespace+"/"+"ZG_nais_einheiten_unique.xlsx", dtype="str", engine='openpyxl', sheet_name='export')
zg_merge=pd.merge(zg_gdf, uetab, left_on='NUMMER', right_on='Einheit ZG')
zg_merge.columns
zg_unique=zg_merge[['NUMMER', 'Beschriftu', 'Einheit ZG','Bedingung, falls mehrere Einheiten möglich', 'Einheit NaiS','Bemerkung Kanton Zug', 'Bemerkung2']].drop_duplicates()
len(zg_unique)
#zg_unique['tahs']=''

#for index, row in zg_unique.iterrows():
#    tahs_list=[]
#    tahs_listshort = []
#    #tahsue_list = []
#    #tahsue_listshort = []
#    nais1=row['Einheit NaiS']
#    #nais2=row['naisue']
#    #print(stotyp)
#    tempsel=zg_gdf[(zg_gdf['NAIS']==nais1)]
#    tahs_list=tempsel['HSTUFE'].unique().tolist()
#    #tempsel2 = zg_gdf[(zg_gdf['naisue'] == nais2)]
#    #tahsue_list = tempsel2['hsue'].unique().tolist()
#    for item in tahs_list:
#        if item not in tahs_listshort:
#            tahs_listshort.append(item)
#    #for item in tahsue_list:
#    #    if item not in tahsue_listshort:
#    #        tahsue_listshort.append(item)
#    zg_unique.loc[((zg_unique['NAIS'] == nais1)), 'tahs'] = str(tahs_listshort).replace('[','').replace(']','').replace("'",'').replace(']','').replace('_','').replace('-','').replace('None','').replace(',','')
#    #zg_unique.loc[((zg_unique['naisue'] == nais2)), 'tauehs'] = str(tahsue_listshort).replace('[','').replace(']','').replace("'",'').replace(']','').replace('_','').replace('-','').replace('None','').replace(',','')
zg_unique=zg_unique.sort_values(by='NUMMER')
zg_unique.to_excel(codespace+'/ZG_nais_einheiten_unique_v2.xlsx')