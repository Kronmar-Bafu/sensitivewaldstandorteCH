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


#read geodata UR
ur_gdf=gpd.read_file(myworkspace+'/UR/Waldstandortkarte_20250204.shp')
len(ur_gdf)
ur_gdf.columns
#ur_gdf=ur_gdf[['NUMMER', 'Beschriftu','geometry']]
#ur_gdf=ur_gdf[ur_gdf['hs1'].isna() == False]



#merge Uebersetzungstabelle
#uetab=pd.read_excel(myworkspace+"/UR/Legende PSK_UR_export.xlsx", dtype="str", engine='openpyxl', sheet_name='PKS_UR')
#ur_merge=pd.merge(ur_gdf, uetab, left_on='NUMMER', right_on='Einheit ZG')
#ur_merge.columns
#ur_unique=ur_merge[['NUMMER', 'Beschriftu', 'Einheit ZG','Bedingung, falls mehrere Einheiten möglich', 'Einheit NaiS','Bemerkung Kanton Zug', 'Bemerkung2']].drop_duplicates()
#len(ur_unique)
#ur_unique['tahs']=''

#for index, row in ur_unique.iterrows():
#    tahs_list=[]
#    tahs_listshort = []
#    #tahsue_list = []
#    #tahsue_listshort = []
#    nais1=row['Einheit NaiS']
#    #nais2=row['naisue']
#    #print(stotyp)
#    tempsel=ur_gdf[(ur_gdf['NAIS']==nais1)]
#    tahs_list=tempsel['HSTUFE'].unique().tolist()
#    #tempsel2 = ur_gdf[(ur_gdf['naisue'] == nais2)]
#    #tahsue_list = tempsel2['hsue'].unique().tolist()
#    for item in tahs_list:
#        if item not in tahs_listshort:
#            tahs_listshort.append(item)
#    #for item in tahsue_list:
#    #    if item not in tahsue_listshort:
#    #        tahsue_listshort.append(item)
#    ur_unique.loc[((ur_unique['NAIS'] == nais1)), 'tahs'] = str(tahs_listshort).replace('[','').replace(']','').replace("'",'').replace(']','').replace('_','').replace('-','').replace('None','').replace(',','')
#    #ur_unique.loc[((ur_unique['naisue'] == nais2)), 'tauehs'] = str(tahsue_listshort).replace('[','').replace(']','').replace("'",'').replace(']','').replace('_','').replace('-','').replace('None','').replace(',','')

ur_unique=ur_gdf[['Kategorie_','Kategori_1', 'Kategori_2', 'Einheit_Na']].drop_duplicates()
len(ur_unique)
ur_unique=ur_unique.sort_values(by='Kategorie_')
ur_unique.to_excel(codespace+'/UR_nais_einheiten_unique_v2.xlsx')