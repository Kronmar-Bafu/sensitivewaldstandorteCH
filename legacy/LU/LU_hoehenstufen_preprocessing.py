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
lu_gdf=gpd.read_file(myworkspace+'/geops_treeapp/forest_types_lu/forest_types_lu.shp')
len(lu_gdf)
lu_gdf.columns
lu_gdf=lu_gdf[['PLOTTXT','STO1_TXT', 'STO2_TXT', 'NAIS1','NAIS2','HS','geometry']]
print(lu_gdf['HS'].unique().tolist())
lu_gdf['tahs']=''
lu_gdf.loc[(lu_gdf['HS']==100),'tahs']='osa'
lu_gdf.loc[(lu_gdf['HS']==90),'tahs']='sa'
lu_gdf.loc[(lu_gdf['HS']==83),'tahs']='hm'
lu_gdf.loc[(lu_gdf['HS']==82),'tahs']='hm'
lu_gdf.loc[(lu_gdf['HS']==81),'tahs']='hm'
lu_gdf.loc[(lu_gdf['HS']==80),'tahs']='hm'
lu_gdf.loc[(lu_gdf['HS']==60),'tahs']='om'
lu_gdf.loc[(lu_gdf['HS']==50),'tahs']='um'
lu_gdf.loc[(lu_gdf['HS']==40),'tahs']='sm'
lu_gdf.loc[(lu_gdf['HS']==20),'tahs']='co'
print(lu_gdf['tahs'].unique().tolist())

lu_unique=lu_gdf[['PLOTTXT','STO1_TXT', 'STO2_TXT', 'NAIS1','NAIS2']].drop_duplicates()
len(lu_unique)
lu_unique['tahs']=''
lu_unique['tahsue']=''


for index, row in lu_unique.iterrows():
    tahs_list=[]
    tahs_listshort = []
    tahsue_list = []
    tahsue_listshort = []
    nais1=row['NAIS1']
    nais2=row['NAIS2']
    #print(stotyp)
    tempsel=lu_gdf[(lu_gdf['NAIS1']==nais1)]
    tahs_list=tempsel['tahs'].unique().tolist()
    tempsel2 = lu_gdf[(lu_gdf['NAIS2'] == nais2)]
    tahsue_list = tempsel2['tahs'].unique().tolist()
    for item in tahs_list:
        if item not in tahs_listshort:
            tahs_listshort.append(item)
    for item in tahsue_list:
        if item not in tahsue_listshort:
            tahsue_listshort.append(item)
    lu_unique.loc[((lu_unique['NAIS1'] == nais1)), 'tahs'] = str(tahs_listshort).replace('[','').replace(']','').replace("'",'').replace(']','')
    lu_unique.loc[((lu_unique['NAIS2'] == nais2)), 'tahsue'] = str(tahsue_listshort).replace('[','').replace(']','').replace("'",'').replace(']','')


lu_unique.to_excel(codespace+'/LU_nais_einheiten_unique.xlsx')