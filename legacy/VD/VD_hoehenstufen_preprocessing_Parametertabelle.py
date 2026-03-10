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
parameterdf=pd.read_excel('C:/DATA/develops/ccwvd/Anhang1_Parameter_Waldstandorte_VD_20250314.xlsx', dtype="str", engine='openpyxl')
parameterdf.columns
parameterdf=parameterdf[['BE','NaiS_LFI_JU','NaiS_LFI_M/A','Ju SM', 'Ju UM', 'Ju OM', 'Ju HM', 'Ju SA','M/A SM', 'M/A UM', 'M/A OM', 'M/A HM', 'M/A SA', 'M/A OSA']]
be_unique=parameterdf[['BE','NaiS_LFI_JU','NaiS_LFI_M/A']].drop_duplicates()
be_unique["tahsJU"]=''
be_unique["tahsMA"]=''
len(be_unique)

#Jura
for index, row in be_unique.iterrows():
    tahs_list=[]
    nais=row['NaiS_LFI_JU']
    tempsel=parameterdf[parameterdf["NaiS_LFI_JU"]==nais]
    sm=False
    um=False
    om=False
    hm=False
    sa=False
    osa=False
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
    if 'x' in tempsel['Ju SA'].unique().tolist():
        sa=True
    if 'y' in tempsel['Ju SA'].unique().tolist():
        sa=True
    if 'o' in tempsel['Ju SA'].unique().tolist():
        sa=True

    if sa == True:
        tahs_list.append('sa')
    be_unique.loc[index, "tahsJU"] = str(tahs_list).replace("[","").replace("]","").replace("'","").replace("]","").replace(",","")


#Mittelland/Alpen
for index, row in be_unique.iterrows():
    tahs_list=[]
    tahs_list = []
    nais=row['NaiS_LFI_M/A']
    tempsel=parameterdf[parameterdf["NaiS_LFI_M/A"]==nais]
    sm=False
    um=False
    om=False
    hm=False
    sa=False
    if 'x' in tempsel['M/A SM'].unique().tolist():
        sm=True
    if 'y' in tempsel['M/A SM'].unique().tolist():
        sm=True
    if 'o' in tempsel['M/A SM'].unique().tolist():
        sm=True
    if sm == True:
        tahs_list.append('sm')
    if 'x' in tempsel['M/A UM'].unique().tolist():
        um=True
    if 'y' in tempsel['M/A UM'].unique().tolist():
        um=True
    if 'o' in tempsel['M/A UM'].unique().tolist():
        um=True
    if um == True:
        tahs_list.append('um')
    if 'x' in tempsel['M/A OM'].unique().tolist():
        om=True
    if 'y' in tempsel['M/A OM'].unique().tolist():
        om=True
    if 'o' in tempsel['M/A OM'].unique().tolist():
        om=True
    if om == True:
        tahs_list.append('om')
    if 'x' in tempsel['M/A HM'].unique().tolist():
        hm=True
    if 'y' in tempsel['M/A HM'].unique().tolist():
        hm=True
    if 'o' in tempsel['M/A HM'].unique().tolist():
        hm=True
    if hm == True:
        tahs_list.append('hm')
    if 'x' in tempsel['M/A SA'].unique().tolist():
        sa=True
    if 'y' in tempsel['M/A SA'].unique().tolist():
        sa=True
    if 'o' in tempsel['M/A SA'].unique().tolist():
        sa=True
    if 'x' in tempsel['M/A OSA'].unique().tolist():
        osa=True
    if 'y' in tempsel['M/A OSA'].unique().tolist():
        osa=True
    if 'o' in tempsel['M/A OSA'].unique().tolist():
        osa=True
    if osa == True:
        tahs_list.append('osa')
    be_unique.loc[index, "tahsMA"] = str(tahs_list).replace("[","").replace("]","").replace("'","").replace("]","").replace(",","")




be_unique.to_excel(codespace+"/VD_nais_einheiten_unique_v2.xlsx")

