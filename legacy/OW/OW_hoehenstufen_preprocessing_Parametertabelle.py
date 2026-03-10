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

#read Parametertabelle OW
parameterdf=pd.read_excel('C:/DATA/develops/ccwow/OW-Parametertabelle_20240907.xlsx', dtype="str", engine='openpyxl')
parameterdf.columns
parameterdf=parameterdf[['Einheit Obwalden','NaiS_LFI','SM', 'UM', 'OM', 'HM', 'SA']]
ow_unique=parameterdf[['Einheit Obwalden','NaiS_LFI']].drop_duplicates()
ow_unique["tahs"]=''
len(ow_unique)

for index, row in ow_unique.iterrows():
    tahs_list=[]
    nais=row['NaiS_LFI']
    tempsel=parameterdf[parameterdf["NaiS_LFI"]==nais]
    sm=False
    um=False
    om=False
    hm=False
    sa=False
    if 'x' in tempsel['SM'].unique().tolist():
        sm=True
    if 'y' in tempsel['SM'].unique().tolist():
        sm=True
    if 'o' in tempsel['SM'].unique().tolist():
        sm=True
    if sm == True:
        tahs_list.append('sm')
    if 'x' in tempsel['UM'].unique().tolist():
        um=True
    if 'y' in tempsel['UM'].unique().tolist():
        um=True
    if 'o' in tempsel['UM'].unique().tolist():
        um=True
    if um == True:
        tahs_list.append('um')
    if 'x' in tempsel['OM'].unique().tolist():
        om=True
    if 'y' in tempsel['OM'].unique().tolist():
        om=True
    if 'o' in tempsel['OM'].unique().tolist():
        om=True
    if om == True:
        tahs_list.append('om')
    if 'x' in tempsel['HM'].unique().tolist():
        hm=True
    if 'y' in tempsel['HM'].unique().tolist():
        hm=True
    if 'o' in tempsel['HM'].unique().tolist():
        hm=True
    if hm == True:
        tahs_list.append('hm')
    if 'x' in tempsel['SA'].unique().tolist():
        sa=True
    if 'y' in tempsel['SA'].unique().tolist():
        sa=True
    if 'o' in tempsel['SA'].unique().tolist():
        sa=True
    if sa == True:
        tahs_list.append('sa')
    ow_unique.loc[index, "tahs"] = str(tahs_list).replace("[","").replace("]","").replace("'","").replace("]","").replace(",","")

ow_unique.to_excel(codespace+"/OW_nais_einheiten_unique.xlsx")

