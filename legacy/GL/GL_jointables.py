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


#read data GL
glunique=pd.read_excel(codespace+"/GL_nais_einheiten_unique.xlsx")
glunique.columns
glunique=glunique[['wg_haupt', 'wg_zusatz', 'wg_name', 'nais_profi']]
#glunique["joinnais"]=''

glorig=pd.read_excel(codespace+"/K_Zusammenzug_Vergleichstabellen_je_Kanton_20200630.xlsx", sheet_name='GL', skiprows=3)
glorig.columns
glorig=glorig[['Einheit GL', 'Bedingung, falls mehrere Einheiten möglich','Einheit NaiS']]
glorig_unique=glorig[['Einheit GL']].drop_duplicates()
glorig_unique['Bedingung']=''
glorig_unique['Einheit NaiS']=''
for index, row in glorig_unique.iterrows():
    wgzusatz=row['Einheit GL']
    bedingung =glorig[glorig['Einheit GL']==wgzusatz]['Bedingung, falls mehrere Einheiten möglich'].unique().tolist()
    nais=glorig[glorig['Einheit GL']==wgzusatz]['Einheit NaiS'].unique().tolist()
    glorig_unique.loc[index, 'Bedingung']=str(bedingung).replace('[','').replace(']','').replace(',','').replace("'",'')
    glorig_unique.loc[index, 'Einheit NaiS'] = str(nais).replace('[','').replace(']','').replace(',','').replace("'",'')

#join tables
glmerge=glunique.merge(glorig_unique, how='left', left_on='wg_zusatz', right_on='Einheit GL')

#check missing
glmerge_misses=glmerge[glmerge['Einheit NaiS'].isnull()==True]
len(glmerge_misses)

for index, row in glmerge_misses.iterrows():
    wg = row['wg_zusatz']
    wgzusatz=row['wg_zusatz'].replace('(', ' ').replace(')','').replace('  ',' ').strip().split()[0]
    tmpsel=glorig_unique[glorig_unique['Einheit GL']==wgzusatz]
    glmerge.loc[glmerge['wg_zusatz']==wg,'Einheit NaiS']=str(tmpsel['Einheit NaiS'].unique().tolist()).replace('[','').replace(']','').replace(',','').replace("'",'')
    glmerge.loc[glmerge['wg_zusatz'] == wg, 'Bedingung'] = str(tmpsel['Bedingung'].unique().tolist()).replace('[','').replace(']', '').replace(',', '').replace("'", '')

#check missing
glmerge_misses=glmerge[glmerge['Einheit NaiS'].isnull()==True]
len(glmerge_misses)

glmerge.to_excel(codespace+"/"+"GL_nais_einheiten_unique_joined.xlsx", sheet_name="GL", index_label='index')










