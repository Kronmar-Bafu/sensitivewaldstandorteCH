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
parameterdf=pd.read_excel('C:/DATA/develops/ccwvd/Anhang1_Parameter_Waldstandorte_VD_20240826.xlsx', dtype="str", engine='openpyxl')
parameterdf.columns
parameterdf=parameterdf[['VD Einheit', 'NaiS_LFI (muss ich noch prüfen später)', 'Ju CO','Ju SM', 'Ju UM', 'Ju OM', 'Ju HM', 'M CO', 'M/A SM', 'M/A UM', 'M/A OM', 'M/A HM', 'M/A SA']]
parameterdf=parameterdf.rename(columns={'NaiS_LFI (muss ich noch prüfen später)':'NaiS_LFI'})
vd_unique=parameterdf[['VD Einheit','NaiS_LFI']].drop_duplicates()
vd_unique["tahsJU"]=''
vd_unique["tahsMA"]=''
len(vd_unique)

#Jura
for index, row in vd_unique.iterrows():
    tahs_list=[]
    nais=row['NaiS_LFI']
    tempsel=parameterdf[parameterdf["NaiS_LFI"]==nais]
    co=False
    sm=False
    um=False
    om=False
    hm=False
    sa=False
    osa=False
    if 'x' in tempsel['Ju CO'].unique().tolist():
        co=True
    if 'y' in tempsel['Ju CO'].unique().tolist():
        co=True
    if 'o' in tempsel['Ju CO'].unique().tolist():
        co=True
    if co == True:
        tahs_list.append('co')
    if 'x' in tempsel['Ju SM'].unique().tolist():
        sm=True
    if 'y' in tempsel['Ju SM'].unique().tolist():
        sm=True
    if 'o' in tempsel['Ju SM'].unique().tolist():
        sm=True
    if sm == True:
        tahs_list.append('sm')
    if 'x' in tempsel['Ju UM'].unique().tolist():
        um=True
    if 'y' in tempsel['Ju UM'].unique().tolist():
        um=True
    if 'o' in tempsel['Ju UM'].unique().tolist():
        um=True
    if um == True:
        tahs_list.append('um')
    if 'x' in tempsel['Ju OM'].unique().tolist():
        om=True
    if 'y' in tempsel['Ju OM'].unique().tolist():
        om=True
    if 'o' in tempsel['Ju OM'].unique().tolist():
        om=True
    if om == True:
        tahs_list.append('om')
    if 'x' in tempsel['Ju HM'].unique().tolist():
        hm=True
    if 'y' in tempsel['Ju HM'].unique().tolist():
        hm=True
    if 'o' in tempsel['Ju HM'].unique().tolist():
        hm=True
    if hm == True:
        tahs_list.append('hm')
    #if 'x' in tempsel['Ju SA'].unique().tolist():
    #    sa=True
    #if 'y' in tempsel['Ju SA'].unique().tolist():
    #    sa=True
    #if 'o' in tempsel['Ju SA'].unique().tolist():
    #    sa=True
    #if sa == True:
    #    tahs_list.append('sa')
    vd_unique.loc[index, "tahsJU"] = str(tahs_list).replace("[","").replace("]","").replace("'","").replace("]","").replace(",","")


#Mittelland/Alpen
for index, row in vd_unique.iterrows():
    tahs_list=[]
    tahs_list = []
    nais=row['NaiS_LFI']
    tempsel=parameterdf[parameterdf["NaiS_LFI"]==nais]
    co=False
    sm=False
    um=False
    om=False
    hm=False
    sa=False
    if 'x' in tempsel['M CO'].unique().tolist():
        co=True
    if 'y' in tempsel['M CO'].unique().tolist():
        co=True
    if 'o' in tempsel['M CO'].unique().tolist():
        co=True
    if 'm' in tempsel['M CO'].unique().tolist():
        co=True
    if 'a' in tempsel['M CO'].unique().tolist():
        co=True
    if co == True:
        tahs_list.append('co')
    if 'x' in tempsel['M/A SM'].unique().tolist():
        sm=True
    if 'y' in tempsel['M/A SM'].unique().tolist():
        sm=True
    if 'o' in tempsel['M/A SM'].unique().tolist():
        sm=True
    if 'm' in tempsel['M/A SM'].unique().tolist():
        sm=True
    if 'a' in tempsel['M/A SM'].unique().tolist():
        sm=True
    if sm == True:
        tahs_list.append('sm')
    if 'x' in tempsel['M/A UM'].unique().tolist():
        um=True
    if 'y' in tempsel['M/A UM'].unique().tolist():
        um=True
    if 'o' in tempsel['M/A UM'].unique().tolist():
        um=True
    if 'm' in tempsel['M/A UM'].unique().tolist():
        um=True
    if 'a' in tempsel['M/A UM'].unique().tolist():
        um=True
    if um == True:
        tahs_list.append('um')
    if 'x' in tempsel['M/A OM'].unique().tolist():
        om=True
    if 'y' in tempsel['M/A OM'].unique().tolist():
        om=True
    if 'o' in tempsel['M/A OM'].unique().tolist():
        om=True
    if 'm' in tempsel['M/A OM'].unique().tolist():
        om=True
    if 'a' in tempsel['M/A OM'].unique().tolist():
        om=True
    if om == True:
        tahs_list.append('om')
    if 'x' in tempsel['M/A HM'].unique().tolist():
        hm=True
    if 'y' in tempsel['M/A HM'].unique().tolist():
        hm=True
    if 'o' in tempsel['M/A HM'].unique().tolist():
        hm=True
    if 'm' in tempsel['M/A HM'].unique().tolist():
        hm=True
    if 'a' in tempsel['M/A HM'].unique().tolist():
        hm=True
    if hm == True:
        tahs_list.append('hm')
    if 'x' in tempsel['M/A SA'].unique().tolist():
        sa=True
    if 'y' in tempsel['M/A SA'].unique().tolist():
        sa=True
    if 'o' in tempsel['M/A SA'].unique().tolist():
        sa=True
    if 'm' in tempsel['M/A SA'].unique().tolist():
        sa=True
    if 'a' in tempsel['M/A SA'].unique().tolist():
        sa=True
    if sa == True:
        tahs_list.append('hm')
    #if 'x' in tempsel['M/A OSA'].unique().tolist():
    #    osa=True
    #if 'y' in tempsel['M/A OSA'].unique().tolist():
    #    osa=True
    #if 'o' in tempsel['M/A OSA'].unique().tolist():
    #    osa=True
    #if osa == True:
    #    tahs_list.append('osa')
    vd_unique.loc[index, "tahsMA"] = str(tahs_list).replace("[","").replace("]","").replace("'","").replace("]","").replace(",","")

vd_unique.to_excel(codespace+"/VD_nais_einheiten_unique.xlsx")

