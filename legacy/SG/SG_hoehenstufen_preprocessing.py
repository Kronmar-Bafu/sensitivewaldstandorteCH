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
sg_gdf=gpd.read_file(myworkspace+'/geops_treeapp/forest_types_sg/forest_types_sg.shp')
len(sg_gdf)
sg_gdf.columns
sg_gdf=sg_gdf[['DTWGEINHEI', 'ta', 'taue', 'tahs', 'tauehs','geometry']]
print(sg_gdf['tahs'].unique().tolist())

sg_unique=sg_gdf[['DTWGEINHEI', 'ta', 'taue']].drop_duplicates()
len(sg_unique)
sg_unique['tahs']=''
sg_unique['tauehs']=''


for index, row in sg_unique.iterrows():
    tahs_list=[]
    tahs_listshort = []
    tahsue_list = []
    tahsue_listshort = []
    nais1=row['ta']
    nais2=row['taue']
    #print(stotyp)
    tempsel=sg_gdf[(sg_gdf['ta']==nais1)]
    tahs_list=tempsel['tahs'].unique().tolist()
    tempsel2 = sg_gdf[(sg_gdf['taue'] == nais2)]
    tahsue_list = tempsel2['tauehs'].unique().tolist()
    for item in tahs_list:
        if item not in tahs_listshort:
            tahs_listshort.append(item)
    for item in tahsue_list:
        if item not in tahsue_listshort:
            tahsue_listshort.append(item)
    sg_unique.loc[((sg_unique['ta'] == nais1)), 'tahs'] = str(tahs_listshort).replace('[','').replace(']','').replace("'",'').replace(']','').replace('_','').replace('-','')
    sg_unique.loc[((sg_unique['taue'] == nais2)), 'tauehs'] = str(tahsue_listshort).replace('[','').replace(']','').replace("'",'').replace(']','').replace('_','').replace('-','')

sg_unique.to_excel(codespace+'/SG_nais_einheiten_unique.xlsx')