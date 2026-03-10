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


#read geodata NW
nw_gdf=gpd.read_file(myworkspace+'/NW/Waldgesellschaften_Ellenberg_Klötzli_1972.shp')
len(nw_gdf)
nw_gdf.columns
#nw_gdf=nw_gdf[['DTWGEINHEI', 'ta', 'taue', 'tahs', 'tauehs','geometry']]
#print(nw_gdf['tahs'].unique().tolist())

nw_unique=nw_gdf[['Beschriftu', 'Art_1', 'Art_2', 'Art_Ueberg']].drop_duplicates()
len(nw_unique)
nw_unique['nais']=''
nw_unique['nais1']=''
nw_unique['nais']=''
nw_unique['hs']=''


#for index, row in nw_unique.iterrows():
#    tahs_list=[]
#    tahs_listshort = []
#    tahsue_list = []
#    tahsue_listshort = []
#    nais1=row['ta']
#    nais2=row['taue']
#    #print(stotyp)
#    tempsel=nw_gdf[(nw_gdf['ta']==nais1)]
#    tahs_list=tempsel['tahs'].unique().tolist()
#    tempsel2 = nw_gdf[(nw_gdf['taue'] == nais2)]
#    tahsue_list = tempsel2['tauehs'].unique().tolist()
#    for item in tahs_list:
#        if item not in tahs_listshort:
#            tahs_listshort.append(item)
#    for item in tahsue_list:
#        if item not in tahsue_listshort:
#            tahsue_listshort.append(item)
#    nw_unique.loc[((nw_unique['ta'] == nais1)), 'tahs'] = str(tahs_listshort).replace('[','').replace(']','').replace("'",'').replace(']','').replace('_','').replace('-','')
#    nw_unique.loc[((nw_unique['taue'] == nais2)), 'tauehs'] = str(tahsue_listshort).replace('[','').replace(']','').replace("'",'').replace(']','').replace('_','').replace('-','')

nw_unique.to_excel(codespace+'/NW_nais_einheiten_unique.xlsx')