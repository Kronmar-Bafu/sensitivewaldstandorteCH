import numpy as np
import pandas as pd
import joblib
import fiona
import geopandas as gpd
import os
import shapely
from osgeo import ogr
import xlrd
import openpyxl
from rasterstats import zonal_stats
import joblib
from osgeo import osr, gdal
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(2056) #LV95
gtiff_driver=gdal.GetDriverByName("GTiff")
import winsound
frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)

#functions
def convert_tif_to_array(intifraster):
    inras = gdal.Open(intifraster)
    inband = inras.GetRasterBand(1)
    outarr = inband.ReadAsArray()
    return outarr
def convertarrtotif(arr, outfile, tifdatatype, referenceraster, nodatavalue):
    ds_in=gdal.Open(referenceraster)
    inband=ds_in.GetRasterBand(1)
    gtiff_driver=gdal.GetDriverByName("GTiff")
    ds_out = gtiff_driver.Create(outfile, inband.XSize, inband.YSize, 1, tifdatatype)
    ds_out.SetProjection(ds_in.GetProjection())
    ds_out.SetGeoTransform(ds_in.GetGeoTransform())
    outband=ds_out.GetRasterBand(1)
    outband.WriteArray(arr)
    outband.SetNoDataValue(nodatavalue)
    ds_out.FlushCache()
    del ds_in
    del ds_out
    del inband
    del outband

#input workspaces
myworkspace="D:/CCW24sensi"
codespace="C:/DATA/develops/sensitivewaldstandorteCH"
hoehenstufendict={"hyperinsubrisch":"hyp","collin mit Buche":"cob","collin":"co","submontan":"sm","untermontan":"um","obermontan":"om","unter-/obermontan":"um/om","hochmontan":"hm","subalpin":"sa","obersubalpin":"osa"}
hoehenstufendictabkuerzungen={"hyp":"hyperinsubroisch","co":"collin","cob":"collin mit Buche","sm":"submontan","um":"untermontan","om":"obermontan","um/om":"unter-/obermontan","hm":"hochmontan","sa":"subalpin","osa":"obersubalpin"}
hsmoddict={1:"hyperinsubrisch",2:"collin",3:"collin",4:"submontan",5:"untermontan",6:"obermontan",7:"unter-/obermontan",8:"hochmontan",9:"subalpin",10:"obersubalpin"}
hsmoddictkurz={1:"hyp",2:"co",3:"cob",4:"sm",5:"um",6:"om",7:"um/om",8:"hm",9:"sa",10:"osa"}
hoehenstufenlist=["hyperinsubrisch","collin","collin mit Buche","submontan","untermontan","obermontan","unter-/obermontan","hochmontan","subalpin","obersubalpin"]


#read excel files
naiseinheitenunique=pd.read_excel(codespace+"/GR_nais_einheiten_unique_v2_bh_mf.xlsx", sheet_name='Sheet1', dtype="str", engine='openpyxl')
naiseinheitenunique.columns
naiseinheitenunique.dtypes
len(naiseinheitenunique)
naiseinheitenunique.loc[naiseinheitenunique['ASS_GR'].isnull()==True, 'ASS_GR']=''
naiseinheitenunique.loc[naiseinheitenunique['NAISbg'].isnull()==True, 'NAISbg']=''
naiseinheitenunique.loc[naiseinheitenunique['nais'].isnull()==True, 'nais']=''
naiseinheitenunique.loc[naiseinheitenunique['hs'].isnull()==True, 'hs']=''
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['ASS_GR']!='']
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['NAISbg']!='']
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['nais']!='']
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['hs']!='']
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['hs'].isnull()==False]
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['hs']!='nan']
naiseinheitenunique['nais1']=''
naiseinheitenunique['nais2']=''
for index, row in naiseinheitenunique.iterrows():
    assgr=row['ASS_GR']
    naisbg=row['NAISbg']
    nais=row['nais']
    if "(" in nais:
        naislist=nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()
        naiseinheitenunique.loc[((naiseinheitenunique['ASS_GR']==assgr)&(naiseinheitenunique['NAISbg']==naisbg)),'nais1']=naislist[0]
        naiseinheitenunique.loc[((naiseinheitenunique['ASS_GR'] == assgr) & (naiseinheitenunique['NAISbg'] == naisbg)), 'nais2'] = naislist[1]
    elif "/" in nais:
        naislist=nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()
        naiseinheitenunique.loc[((naiseinheitenunique['ASS_GR']==assgr)&(naiseinheitenunique['NAISbg']==naisbg)),'nais1']=naislist[0]
        naiseinheitenunique.loc[((naiseinheitenunique['ASS_GR'] == assgr) & (naiseinheitenunique['NAISbg'] == naisbg)), 'nais2'] = naislist[1]
    else:
        naiseinheitenunique.loc[((naiseinheitenunique['ASS_GR']==assgr)&(naiseinheitenunique['NAISbg']==naisbg)),'nais1']=nais

##read the rasters
##reference tif raster
#print("read reference raster")
#referenceraster=myworkspace+"/GR/GR_dem10m.tif"
#referencetifraster=gdal.Open(referenceraster)
#referencetifrasterband=referencetifraster.GetRasterBand(1)
#referencerasterProjection=referencetifraster.GetProjection()
#ncols=referencetifrasterband.XSize
#nrows=referencetifrasterband.YSize
#indatatype=referencetifrasterband.DataType
#NODATA_value=-9999
#sloperaster=myworkspace+"/GR/GR_slopeprz.tif"
#radiationraster=myworkspace+"/GR/GR_globradyyw.tif"
#hoehenstufenraster=myworkspace+("/GR/GR_vegetationshoehenstufen1975.tif")


#read shapefile
stok_gdf=gpd.read_file(myworkspace+"/GR/stok_gdf_attributed_temp4_fixed.gpkg", layer='stok_gdf_attributed_temp4_fixed')
winsound.Beep(frequency, duration)
stok_gdf.rename(columns={'ass_gr':'ASS_GR', 'naisbg':'NAISbg'}, inplace=True)
stok_gdf.rename(columns={'meanslopep':'meanslopeprc'}, inplace=True)
stok_gdf.loc[stok_gdf['ASS_GR']=='747D','ASS_GR']='47D'
stok_gdf.loc[stok_gdf['ASS_GR']=='358C','ASS_GR']='58C'
stok_gdf.loc[stok_gdf['ASS_GR']=='257C','ASS_GR']='57C'
stok_gdf.loc[stok_gdf['ASS_GR']=='259','ASS_GR']='59'
stok_gdf.loc[stok_gdf['ASS_GR']=='0AV','ASS_GR']='AV'
stok_gdf.loc[stok_gdf['ASS_GR']=='558L','ASS_GR']='58L'
stok_gdf.loc[stok_gdf['ASS_GR']=='957V','ASS_GR']='57V'
stok_gdf.loc[stok_gdf['ASS_GR']=='447M','ASS_GR']='47M'
stok_gdf.loc[stok_gdf['ASS_GR']=='147V','ASS_GR']='47V'
stok_gdf.loc[stok_gdf['ASS_GR']=='452','ASS_GR']='52'
stok_gdf.loc[stok_gdf['ASS_GR']=='160','ASS_GR']='60'
stok_gdf.loc[stok_gdf['ASS_GR']=='9AV','ASS_GR']='AV'
stok_gdf.loc[stok_gdf['ASS_GR']=='555*','ASS_GR']='55*'
stok_gdf.loc[stok_gdf['ASS_GR']=='959*','ASS_GR']='59*'
stok_gdf.loc[stok_gdf['ASS_GR']=='0AV','ASS_GR']='AV'
stok_gdf.loc[stok_gdf['ASS_GR']=='060A','ASS_GR']='60A'
stok_gdf.loc[stok_gdf['ASS_GR']=='247','ASS_GR']='47'
stok_gdf.loc[stok_gdf['ASS_GR']=='833V','ASS_GR']='33V'
stok_gdf.loc[stok_gdf['ASS_GR']=='134L','ASS_GR']='34L'
stok_gdf.loc[stok_gdf['ASS_GR']=='934A','ASS_GR']='34A'
stok_gdf.loc[stok_gdf['ASS_GR']=='842C','ASS_GR']='42C'
stok_gdf.loc[stok_gdf['ASS_GR']=='942Q','ASS_GR']='42Q'
stok_gdf.loc[stok_gdf['ASS_GR']=='034F','ASS_GR']='34F'
stok_gdf.loc[stok_gdf['ASS_GR']=='858V','ASS_GR']='58V'
stok_gdf.loc[stok_gdf['ASS_GR']=='540P','ASS_GR']='40P'
stok_gdf.loc[stok_gdf['ASS_GR']=='947H','ASS_GR']='47H'
stok_gdf.loc[stok_gdf['ASS_GR']=='159A','ASS_GR']='59A'
stok_gdf.loc[stok_gdf['ASS_GR']=='253*','ASS_GR']='53*'
stok_gdf.loc[stok_gdf['ASS_GR']=='132*','ASS_GR']='32*'
stok_gdf.loc[stok_gdf['ASS_GR']=='632V','ASS_GR']='32V'
stok_gdf.loc[stok_gdf['ASS_GR']=='524S','ASS_GR']='24S'
stok_gdf.loc[stok_gdf['ASS_GR']=='547*','ASS_GR']='47*'
stok_gdf.loc[stok_gdf['ASS_GR']=='157BL','ASS_GR']='57BL'
stok_gdf.loc[stok_gdf['ASS_GR']=='647BL','ASS_GR']='47BL'
stok_gdf.loc[stok_gdf['ASS_GR']=='258BL','ASS_GR']='58BL'

stok_gdf.to_file(myworkspace+"/GR/stok_gdf_attributed_temp4_fixed_corr.gpkg")

#uebersetzung von Kantonseinheit in NAIS
stok_gdf.columns
stok_gdf['nais']=''
stok_gdf['nais1']=''
stok_gdf['nais2']=''
stok_gdf['mo']=0
stok_gdf['ue']=0
stok_gdf['hs']=''
stok_gdf['tahs']=''
stok_gdf['tahsue']=''
#transform null values
stok_gdf.loc[stok_gdf['ASS_GR'].isnull()==True,'ASS_GR']=''
stok_gdf.loc[stok_gdf['NAISbg'].isnull()==True,'NAISbg']=''
stok_gdf.loc[stok_gdf['ASS_GR']=='<Null>','ASS_GR']=''
stok_gdf.loc[stok_gdf['NAISbg']=='<Null>','NAISbg']=''
naiseinheitenunique.loc[naiseinheitenunique['ASS_GR'].isnull()==True,'ASS_GR']=''
naiseinheitenunique.loc[naiseinheitenunique['NAISbg'].isnull()==True,'NAISbg']=''
naiseinheitenunique.loc[naiseinheitenunique['nais'].isnull()==True,'nais']=''
naiseinheitenunique.loc[naiseinheitenunique['hs'].isnull()==True,'hs']=''
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['nais']!='']
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['hs']!='']

#set nais1 and nais2
naiseinheitenunique['nais1']=''
naiseinheitenunique['nais2']=''
for index, row in naiseinheitenunique.iterrows():
    kantonseinheit = row['ASS_GR']
    NAISbg = row["NAISbg"]
    nais = row["nais"]
    if "(" in nais and len(nais.replace('(',' ').replace(')','').strip().split())>1:
        naiseinheitenunique.loc[((naiseinheitenunique["ASS_GR"] == kantonseinheit) & (naiseinheitenunique["NAISbg"] == NAISbg)), "nais1"] = nais.replace('(',' ').replace(')','').strip().split()[0]
        naiseinheitenunique.loc[((naiseinheitenunique["ASS_GR"] == kantonseinheit) & (naiseinheitenunique["NAISbg"] == NAISbg)), "nais2"] = nais.replace('(', ' ').replace(')', '').strip().split()[1]
        naiseinheitenunique.loc[((naiseinheitenunique["ASS_GR"] == kantonseinheit) & (naiseinheitenunique["NAISbg"] == NAISbg)), "ue"] = 1
        naiseinheitenunique.loc[((naiseinheitenunique["ASS_GR"] == kantonseinheit) & (naiseinheitenunique["NAISbg"] == NAISbg)), "mo"] = 0
    elif "/" in nais and len(nais.replace('(',' ').replace(')','').strip().split())>1:
        naiseinheitenunique.loc[((naiseinheitenunique["ASS_GR"] == kantonseinheit) & (naiseinheitenunique["NAISbg"] == NAISbg)), "nais1"] = nais.replace('/',' ').strip().split()[0]
        naiseinheitenunique.loc[((naiseinheitenunique["ASS_GR"] == kantonseinheit) & (naiseinheitenunique["NAISbg"] == NAISbg)), "nais2"] = nais.replace('/', ' ').strip().split()[1]
        naiseinheitenunique.loc[((naiseinheitenunique["ASS_GR"] == kantonseinheit) & (naiseinheitenunique["NAISbg"] == NAISbg)), "ue"] = 1
        naiseinheitenunique.loc[((naiseinheitenunique["ASS_GR"] == kantonseinheit) & (naiseinheitenunique["NAISbg"] == NAISbg)), "mo"] = 1
    else:
        naiseinheitenunique.loc[((naiseinheitenunique["ASS_GR"] == kantonseinheit) & (naiseinheitenunique["NAISbg"] == NAISbg)), "nais1"] = nais.replace('(', ' ').replace(')', '').strip().split()[0]
        naiseinheitenunique.loc[((naiseinheitenunique["ASS_GR"] == kantonseinheit) & (naiseinheitenunique["NAISbg"] == NAISbg)), "ue"] = 0
        naiseinheitenunique.loc[((naiseinheitenunique["ASS_GR"] == kantonseinheit) & (naiseinheitenunique["NAISbg"] == NAISbg)), "mo"] = 0


print('iterate for attributing nais and tahs')
len(naiseinheitenunique)
naiseinheitenunique['Bedingung'].unique().tolist()
naiseinheitenunique['ASS_GR'].unique().tolist()
stok_gdf['ASS_GR'].unique().tolist()
#check entries
print('comparison')
for item in stok_gdf['ASS_GR'].unique().tolist():
    if item not in naiseinheitenunique['ASS_GR'].unique().tolist():
        print(item)
print('correct NAISbg')
naiseinheitenunique['NAISbg'].unique().tolist()
stok_gdf['NAISbg'].unique().tolist()

for item in stok_gdf['NAISbg'].unique().tolist():
    if ' ' in item:
        stok_gdf.loc[stok_gdf['NAISbg']==item, 'NAISbg']=item.replace(' ','')
naiseinheitenunique.loc[naiseinheitenunique['Bedingung'].isnull()==True,'Bedingung']=''
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['Bedingung']=='']
for index, row in naiseinheitenunique.iterrows():
    kantonseinheit=row['ASS_GR']
    NAISbg=row["NAISbg"]
    nais = row["nais"]
    nais1 = row["nais1"]
    nais2 = row["nais2"]
    hs=row['hs']
    hslist=row['hs'].replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()
    bedingung=row['Bedingung']
    #Hoehenstufenzuweisung
    stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "nais"] = nais
    stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "nais1"] = nais1
    stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "nais2"] = nais2
    stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "hs"] = row['hs']
    #Uebergang
    if nais2 !='':
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "ue"] = 1
    #Hohenstufenzuweisung
    if len(hslist)==1:
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
    else:
        if "(" in row['hs']:
            stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
            stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "tahsue"] = hoehenstufendictabkuerzungen[hslist[1]]
        else:
            for index2, row2 in stok_gdf[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg))].iterrows():
                if row2['hs1975']>0:
                    hsmod=hsmoddictkurz[int(row2['hs1975'])]
                else:
                    hsmod = 'nan'
                if hsmod in row2['hs'].strip().split():
                    stok_gdf.loc[index2,'tahs']=hoehenstufendictabkuerzungen[hsmod]
                else:
                    if len(row2['hs'].replace('(',' ').replace(')','').strip().split()) >0:
                        test=hoehenstufendictabkuerzungen[row2['hs'].replace('(',' ').replace(')','').strip().split()[0]]
                        if len(row2['hs'].replace('(',' ').replace(')','').strip().split()) >1 and test == 'collin':
                            stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[row2['hs'].replace('(',' ').replace(')','').strip().split()[-1]]
                        else:
                            stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[row2['hs'].replace('(', ' ').replace(')', '').strip().split()[-1]]
    # Bedingungen
    if bedingung=='Region 1':
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)&(stok_gdf["storeg"] == '1')), "nais"] = nais
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"] == '1')), "nais1"] = nais1
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"] == '1')), "hs"] = hs
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"] == '1')&(stok_gdf["hs1975"] <= 4)), "tahs"] = 'submontan'
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"] == '1') & (stok_gdf["hs1975"] == 5)), "tahs"] = 'untermontan'
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"] == '1') & (stok_gdf["hs1975"] >= 6)), "tahs"] = 'obermontan'
    if bedingung=='Region 2a':
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)&(stok_gdf["storeg"] == '2a')), "nais"] = nais
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"] == '2a')), "nais1"] = nais1
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"] == '2a')), "hs"] = hs
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"] == '2a')&(stok_gdf["hs1975"] <= 2)), "tahs"] = 'collin'
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"] == '2a') & (stok_gdf["hs1975"] == 4)), "tahs"] = 'submontan'
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"] == '2a') & (stok_gdf["hs1975"] == 5)), "tahs"] = 'untermontan'
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"] == '2a') & (stok_gdf["hs1975"] == 6)), "tahs"] = 'obermontan'
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"] == '2a') & (stok_gdf["hs1975"] >= 8)), "tahs"] = 'hochmontan'
    if bedingung=='Region 2b 2c' and nais=='65':
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '65') & (stok_gdf["NAISbg"] == NAISbg)&(stok_gdf["storeg"].isin(['2c','2b']))), "nais"] = nais
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '65') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['2c','2b']))), "nais1"] = nais1
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '65') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['2c','2b']))), "hs"] = hs
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '65') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['2c','2b']))&(stok_gdf["hs1975"] < 8)), "tahs"] = 'collin'
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '65') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['2c','2b'])) & (stok_gdf["hs1975"] >= 8)), "tahs"] = 'hochmontan'
    if bedingung=='Region 2b 2c' and nais=='68':
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '68') & (stok_gdf["NAISbg"] == NAISbg)&(stok_gdf["storeg"].isin(['2c','2b']))), "nais"] = nais
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '68') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['2c','2b']))), "nais1"] = nais1
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '68') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['2c','2b']))), "hs"] = hs
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '68') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['2c','2b']))), "tahs"] = 'hochmontan'
    if bedingung=='Region 1 2a':
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)&(stok_gdf["storeg"].isin(['1','2a']))), "nais"] = nais
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a']))), "nais1"] = nais1
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a']))), "hs"] = hs
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a']))&(stok_gdf["hs1975"] <= 4)), "tahs"] = 'submontan'
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a']))& (stok_gdf["hs1975"] == 5)), "tahs"] = 'untermontan'
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a'])) & (stok_gdf["hs1975"] >= 6)), "tahs"] = 'obermontan'
    if bedingung=='Region 2c' and nais=='49*':
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '49*') & (stok_gdf["NAISbg"] == NAISbg)&(stok_gdf["storeg"].isin(['2c']))), "nais"] = nais
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '49*') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['2c']))), "nais1"] = nais1
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '49*') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['2c']))), "hs"] = hs
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '49*') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['2c']))&(stok_gdf["hs1975"] <= 8)), "tahs"] = 'hochmontan'
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '49*') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['2c'])) & (stok_gdf["hs1975"] > 8)), "tahs"] = 'subalpin'
    if bedingung=='Region 2c' and nais=='60*':
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '60*') & (stok_gdf["NAISbg"] == NAISbg)&(stok_gdf["storeg"].isin(['2c']))), "nais"] = nais
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '60*') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['2c']))), "nais1"] = nais1
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '60*') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['2c']))), "hs"] = hs
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '60*') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['2c']))&(stok_gdf["hs1975"] <= 8)), "tahs"] = 'hochmontan'
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '60*') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['2c'])) & (stok_gdf["hs1975"] > 8)), "tahs"] = 'subalpin'
    if bedingung=='Region 1, 2a, 2b und sa' and nais=='49*':
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '49*') & (stok_gdf["NAISbg"] == NAISbg)&(stok_gdf["storeg"].isin(['1','2a','2b']))), "nais"] = nais
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '49*') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a','2b']))), "nais1"] = nais1
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '49*') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a','2b']))), "hs"] = hs
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '49*') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a','2b']))), "tahs"] = 'subalpin'
    if bedingung=='Region 1, 2a, 2b und sa' and nais=='60*':
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '60*') & (stok_gdf["NAISbg"] == NAISbg)&(stok_gdf["storeg"].isin(['1','2a','2b']))), "nais"] = nais
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '60*') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a','2b']))), "nais1"] = nais1
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '60*') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a','2b']))), "hs"] = hs
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '60*') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a','2b']))), "tahs"] = 'subalpin'
        if bedingung=='Region 1, 2a, 2b und hm' and nais=='49*Ta':
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '49*Ta') & (stok_gdf["NAISbg"] == NAISbg)&(stok_gdf["storeg"].isin(['1','2a','2b']))), "nais"] = nais
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '49*Ta') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a','2b']))), "nais1"] = nais1
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '49*Ta') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a','2b']))), "hs"] = hs
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '49*Ta') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a','2b']))), "tahs"] = 'hochmontan'
    if bedingung=='Region 1, 2a, 2b und hm' and nais=='60*Ta':
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '60*Ta') & (stok_gdf["NAISbg"] == NAISbg)&(stok_gdf["storeg"].isin(['1','2a','2b']))), "nais"] = nais
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '60*Ta') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a','2b']))), "nais1"] = nais1
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '60*Ta') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a','2b']))), "hs"] = hs
        stok_gdf.loc[((stok_gdf["ASS_GR"] == '60*Ta') & (stok_gdf["NAISbg"] == NAISbg) & (stok_gdf["storeg"].isin(['1','2a','2b']))), "tahs"] = 'hochmontan'
winsound.Beep(frequency, duration)

#check Hohenstufenzuweisung
#stok_gdf.loc[((stok_gdf["ASS_GR"] == '47D') & (stok_gdf["NAISbg"] == '47DRe')), "hs"] = 'hm'
#stok_gdf.loc[((stok_gdf["ASS_GR"] == '47D') & (stok_gdf["NAISbg"] == '47D')), "hs"] = 'hm'
checknohs=stok_gdf[((stok_gdf["tahs"]==""))]
checknohs['hs'].unique().tolist()
fehlendeuebersetzungen=checknohs['ASS_GR'].unique().tolist()
check47=checknohs[checknohs['ASS_GR']=='47D']
check47['ASS_GR'].unique().tolist()
check47['NAISbg'].unique().tolist()
stok_gdf.loc[((stok_gdf["ue"] == 0)&(stok_gdf["nais1"] == '')) , "nais1"] = stok_gdf["nais"]
stok_gdf.loc[((stok_gdf["ue"] == 1)&(stok_gdf["tahsue"] == '')) , "tahsue"] = stok_gdf["tahs"]
stok_gdf.loc[((stok_gdf["mo"] == 1)&(stok_gdf["tahsue"] == '')) , "tahsue"] = stok_gdf["tahs"]
stok_gdf['tahsue'].unique().tolist()
stok_gdf['tahs'].unique().tolist()
print("write output")
stok_gdf.columns
stok_gdf=stok_gdf[['ASS_GR', 'NAISbg','joinid', 'taheute','storeg', 'meanslopeprc', 'slpprzrec', 'rad', 'radiation','hs1975', 'nais','nais1', 'nais2', 'hs', 'ue',  'mo', 'tahs', 'tahsue', 'geometry']]
stok_gdf.to_file(myworkspace+"/GR/stok_gdf_attributed.gpkg")
#stok_gdf=gpd.read_file(myworkspace+"/GR/stok_gdf_attributed.gpkg")
print("done")

stok_gdf.dtypes


#Export for tree-app
print('Export for Tree-App')
stok_gdf.columns
#stok_gdf.loc[((stok_gdf['ue']==1)&(NAISbg['tahsue']=='')&(stok_gdf['tahs']!='')),'tahsue']=stok_gdf['tahs']
treeapp=stok_gdf[['ASS_GR', 'NAISbg','nais', 'nais1', 'nais2', 'mo', 'ue','tahs', 'tahsue','geometry']]
treeapp.to_file(myworkspace+"/GR/GR_treeapp.gpkg", layer='GR_treeapp', driver="GPKG")
treeapp.columns
print("done")
winsound.Beep(frequency, duration)
