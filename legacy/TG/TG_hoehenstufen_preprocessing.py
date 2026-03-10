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
hoehenstufenlistshort=["co","sm","um","om","hm","sa","osa"]


#read geodata NE
tg_gdf=gpd.read_file(myworkspace+"/geops_treeapp/forest_types_tg/forest_types_tg.shp")
len(tg_gdf)
tg_gdf.columns
parameterdf=pd.read_excel(codespace+"/"+"CH_nais_einheiten_unique.xlsx", dtype="str", engine='openpyxl')
#tg_gdf=tg_gdf[['fid', 'TGneu', 'NaiS', 'geometry']]
#print(tg_gdf['hohenstufe'].unique().tolist())
#tg_gdf["tahs"]=''
#tg_gdf.loc[(tg_gdf['hohenstufe']==100),'tahs']='osa'
#tg_gdf.loc[(tg_gdf['hohenstufe']==90),'tahs']='sa'
#tg_gdf.loc[(tg_gdf['hohenstufe']==83),'tahs']='hm'
#tg_gdf.loc[(tg_gdf['hohenstufe']==82),'tahs']='hm'
#tg_gdf.loc[(tg_gdf['hohenstufe']==81),'tahs']='hm'
#tg_gdf.loc[(tg_gdf['hohenstufe']==80),'tahs']='hm'
#tg_gdf.loc[(tg_gdf['hohenstufe']==60),'tahs']='om'
#tg_gdf.loc[(tg_gdf['hohenstufe']==50),'tahs']='um'
#tg_gdf.loc[(tg_gdf['hohenstufe']==40),'tahs']='sm'
#tg_gdf.loc[(tg_gdf['hohenstufe']==20),'tahs']='co'
#print(tg_gdf['tahs'].unique().tolist())

tg_unique=tg_gdf[['TGneu', 'NaiS']].drop_duplicates()
len(tg_unique)
tg_unique["nais1"]=''
tg_unique["nais2"]=''
tg_unique["tahs"]=''
tg_unique["tahsue"]=''
for index, row in tg_unique.iterrows():
    stotyp=row['NaiS']
    if stotyp is not None:
        if "(" in stotyp:
            stoyplist=stotyp.replace('(', ' ').replace(')', '').strip().split()
            if len(stoyplist)>1:
                tg_unique.loc[index,'nais1']=stoyplist[0]
                tg_unique.loc[index, 'nais2'] = stoyplist[1]
            else:
                tg_unique.loc[index, 'nais1'] = stoyplist[0]
        elif "/" in stotyp:
            stoyplist = stotyp.replace('/', ' ')
            if len(stoyplist) > 1:
                tg_unique.loc[index, 'nais1'] = stoyplist[0]
                tg_unique.loc[index, 'nais2'] = stoyplist[1]
            else:
                tg_unique.loc[index, 'nais1'] = stoyplist[0]
        else:
            tg_unique.loc[index, 'nais1']=stotyp

for index, row in tg_unique.iterrows():
    tahs_list=[]
    tahs_listshort = []
    flistshort=[]
    tahsue_list = []
    tahsue_listshort = []
    flistueshort = []
    nais1=row["nais1"]
    nais2 = row["nais2"]
    #print(stotyp)
    tempsel=parameterdf[(parameterdf["naishaupt"]==nais1)]
    tahs_list=tempsel["hoehenstufe1"].unique().tolist()
    tempsel = parameterdf[(parameterdf["naisue"] == nais2)]
    tahsue_list = tempsel["hoehenstufe1"].unique().tolist()
    for item in tahs_list:
        for i in str(item).replace(',','').strip().split():
            if i not in tahs_listshort and str(item) != 'nan':
                tahs_listshort.append(item)
    for item in tahsue_list:
        for i in str(item).replace(',','').strip().split():
            if i not in tahsue_listshort and str(item) != 'nan':
                tahsue_listshort.append(item)
    flist=list(set(tahs_listshort))
    flist2 = list(set(tahsue_listshort))
    #for item in str(flist).strip().split():
    #    if item not in flistshort:
    #        flistshort.append(item)
    tg_unique.loc[((tg_unique["NaiS"] == nais1)), "tahs"] = str(flist).replace("[","").replace("]","").replace("'","").replace("]","").replace('nan','').replace(',','').replace('"','')
    tg_unique.loc[((tg_unique["NaiS"] == nais2)), "tahsue"] = str(flist2).replace("[", "").replace("]", "").replace("'","").replace("]", "").replace('nan', '').replace(',', '').replace('"', '')

tg_unique.to_excel(codespace+"/TG_nais_einheiten_unique.xlsx")