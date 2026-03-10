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
hoehenstufendict={"collin":"co","submontan":"sm","untermontan":"um","obermontan":"om","hochmontan":"hm","subalpin":"sa","obersubalpin":"osa"}
hoehenstufendictabkuerzungen={"co":"collin","sm":"submontan","um":"untermontan","om":"obermontan","hm":"hochmontan","sa":"subalpin","osa":"obersubalpin"}
hsmoddict={3:"collin",4:"submontan",5:"untermontan",6:"obermontan",8:"hochmontan",9:"subalpin",10:"obersubalpin"}
hsmoddictkurz={3:"co",4:"sm",5:"um",6:"om",8:"hm",9:"sa",10:"osa"}
hoehenstufenlist=["collin","submontan","untermontan","obermontan","hochmontan","subalpin","obersubalpin"]

#read excel files
naiseinheitenunique=pd.read_excel(codespace+"/FR_nais_einheiten_unique_mf_mit_7f.xlsx", sheet_name='Sheet1_sortiert', dtype="str", engine='openpyxl')
naiseinheitenunique.columns
naiseinheitenunique.dtypes
naiseinheitenunique=naiseinheitenunique.astype({'LEGENDE':str, 'ASSOC_TOT_':str,'Bedingung Hangneigung':str,'Bedingung Region':str,'NaiS vereinfacht':str, 'hs':str})
len(naiseinheitenunique)
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['NaiS vereinfacht']!='-']
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['hs']!='']
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['hs'].isnull()==False]
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['hs']!='nan']
#sheet1=pd.read_excel(codespace+"/FR_nais_einheiten_unique_mf.xlsx", sheet_name='Sheet1', dtype="str", engine='openpyxl')
#read the rasters
#reference tif raster
print("read reference raster")
referenceraster=myworkspace+"/FR/dem10m.tif"
referencetifraster=gdal.Open(referenceraster)
referencetifrasterband=referencetifraster.GetRasterBand(1)
referencerasterProjection=referencetifraster.GetProjection()
ncols=referencetifrasterband.XSize
nrows=referencetifrasterband.YSize
indatatype=referencetifrasterband.DataType
#indatatypeint=gdal.Open(myworkspace+"/regionen.tif").GetRasterBand(1).DataType
#dhmarr=convert_tif_to_array("D:/CCW20/GIS/dhm25.tif")
NODATA_value=-9999

sloperaster=myworkspace+"/FR/slope10mprz.tif"
radiationraster=myworkspace+"/FR/globradyw.tif"
hoehenstufenraster=myworkspace+"/FR/hs1975.tif"


#read shapefile
stok_gdf=gpd.read_file(myworkspace+"/geops_treeapp/forest_types_fr/forest_types_fr.shp")
taheute=gpd.read_file(myworkspace+"/Tannenareale.shp")
storeg=gpd.read_file(myworkspace+"/Waldstandortsregionen.shp")
#stok_gdf=gpd.read_file(projectspace+"/GIS/stok_gdf_attributed.shp")
len(stok_gdf)
stok_gdf.crs
taheute.crs
storeg.crs
#stok_gdf.set_crs(epsg=2056, inplace=True)
#stok_gdf.plot()
stok_gdf.columns
#stok_gdf.drop(columns=['index_right'], inplace=True)
#change column names (sg___ are the St Gallen units)
#stok_gdf.rename(columns={"DTWGEINHEI": "kanteinh", "naisueberg": "sgue", "naismosaic":"sgmosaic"}, inplace=True)
#stok_gdf["nais1"]=""
#stok_gdf["naisue"]=""
#stok_gdf["naismosaic"]=""
#stok_gdf["joinid"]=0
#stok_gdf["joinid"]=stok_gdf.index


#Tannenareale
taheute.crs
taheute.columns
#taheute.plot()
taheute.rename(columns={"Code_Ta": "taheute"}, inplace=True)
taheute.drop(columns=['Areal_de', 'Areal_fr', 'Areal_it', 'Areal_en','Shape_Leng','Shape_Area'], inplace=True)
#overlay spatial join
stok_gdf=gpd.sjoin(stok_gdf,taheute, how='left', op="intersects")
len(stok_gdf)
#stok_gdfta=gpd.sjoin_nearest(stok_gdf, taheute, how='left', max_distance=500, distance_col=None)#lsuffix='left', rsuffix='right'
#stok_gdfta=gpd.sjoin(stok_gdf,taheute, how='left', op="intersects")
#len(stok_gdfta)
#stok_gdf=stok_gdfta[["joinid","taheute"]].groupby(by=["joinid"]).min()
#stok_gdftagrouped=stok_gdfta[["joinid","taheute"]].groupby(by=["joinid"]).min()
#stok_gdftagrouped["joinid"]=stok_gdftagrouped.index
#len(stok_gdftagrouped)
#stok_gdftagrouped.columns
#stok_gdf.columns
#stok_gdf=stok_gdf.merge(stok_gdftagrouped, on='joinid', how='left')#left_on='joinid', right_on='joinid',
#len(stok_gdf)
#np.max(stok_gdftagrouped["taheute"])
#stok_gdf.to_file(projectspace+"/GIS/stok_gdf_attributed.shp")
#del taheute
#del stok_gdftagrouped
#del stok_gdfta
stok_gdf.columns
#stok_gdf=stok_gdf[['DTWGEINHEI','taheute','geometry']]
stok_gdf['joinid']=stok_gdf.index
if 'index_right' in stok_gdf.columns:
    stok_gdf.drop(columns=['index_right'], inplace=True)

#Standortregionen
storeg.crs
storeg.columns
#taheute.plot()
storeg.rename(columns={"Subcode": "storeg"}, inplace=True)
storeg.drop(columns=[ 'Region_fr', 'Region_it', 'Region_en', 'Code', 'Code_Bu', 'Code_Fi', 'Shape_Leng', 'Shape_Area'], inplace=True)
#overlay spatial join
stok_gdfstoreg=stok_gdf.sjoin(storeg, how='left', op="intersects")
len(stok_gdfstoreg)
stok_gdfstoreggrouped=stok_gdfstoreg[["joinid","storeg"]].groupby(by=["joinid"]).min()
##stok_gdftagrouped["joinid"]=stok_gdftagrouped.index
len(stok_gdfstoreggrouped)
stok_gdfstoreggrouped.columns
#stok_gdf.columns
stok_gdf=stok_gdf.merge(stok_gdfstoreggrouped, on='joinid', how='left')#left_on='joinid', right_on='joinid',
len(stok_gdf)
#stok_gdf.to_file(projectspace+"/GIS/stok_gdf_attributed.shp")
#del storeg
#del stok_gdfstoreggrouped
#del stok_gdfstoreg
if 'index_right' in stok_gdf.columns:
    stok_gdf.drop(columns=['index_right'], inplace=True)


#attribute shapefile
#mean slope in percent
stok_gdf["meanslopeprc"]=0
#zonstatslope=zonal_stats(stok_gdf, referenceraster,stats="count min mean max median")
zonstatslope=zonal_stats(stok_gdf, sloperaster,stats="mean")
i=0
while i < len(stok_gdf):
    stok_gdf.loc[i,"meanslopeprc"]=zonstatslope[i]["mean"]
    i+=1
stok_gdf["slpprzrec"]=0
stok_gdf.loc[stok_gdf["meanslopeprc"]>=70.0,"slpprzrec"]=4
stok_gdf.loc[((stok_gdf["meanslopeprc"]>=60.0)&(stok_gdf["meanslopeprc"]<70.0)),"slpprzrec"]=3
stok_gdf.loc[((stok_gdf["meanslopeprc"]>=20.0)&(stok_gdf["meanslopeprc"]<60.0)),"slpprzrec"]=2
stok_gdf.loc[stok_gdf["meanslopeprc"]<20.0,"slpprzrec"]=1
stok_gdf.columns
#del zonstatslope
winsound.Beep(frequency, duration)
if 'index_right' in stok_gdf.columns:
    stok_gdf.drop(columns=['index_right'], inplace=True)

#radiation
stok_gdf["rad"]=0
#zonstatslope=zonal_stats(stok_gdf, referenceraster,stats="count min mean max median")
zonstatrad=zonal_stats(stok_gdf, radiationraster,stats="mean")
i=0
while i < len(stok_gdf):
    stok_gdf.loc[i,"rad"]=zonstatrad[i]["mean"]
    i+=1
stok_gdf["radiation"]=0
stok_gdf.loc[stok_gdf["rad"]>=147.0,"radiation"]=1 #10% quantile
stok_gdf.loc[stok_gdf["rad"]<=112.0,"radiation"]=-1 #90% quantile
stok_gdf.columns
#del zonstatrad
winsound.Beep(frequency, duration)
if 'index_right' in stok_gdf.columns:
    stok_gdf.drop(columns=['index_right'], inplace=True)

#hoehenstufen heute
stok_gdf["hs1975"]=0
#zonstatslope=zonal_stats(stok_gdf, referenceraster,stats="count min mean max median")
zonstaths=zonal_stats(stok_gdf, hoehenstufenraster,stats="majority")
i=0
while i < len(stok_gdf):
    stok_gdf.loc[i,"hs1975"]=zonstaths[i]["majority"]
    i+=1
stok_gdf.columns
stok_gdf.dtypes
#stok_gdf=stok_gdf.astype({'hs1975': 'int'})#.dtypes
#stok_gdf.to_file(myworkspace+"/AR/stok_gdf_attributed.gpkg")
#del zonstaths
winsound.Beep(frequency, duration)

stok_gdf.to_file(myworkspace+"/FR/stok_gdf_attributed_temp.gpkg")
#stok_gdf=gpd.read_file(myworkspace+"/FR/stok_gdf_attributed_temp.gpkg")


#uebersetzung von Kantonseinheit in NAIS
#stok_gdf=gpd.read_file(myworkspace+"/FR/stok_gdf_attributed_temp.gpkg")
#naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['NaiS'].isnull() == False]
stok_gdf.columns
len(naiseinheitenunique)
stok_gdf['naisdetail']=''
stok_gdf['nais']=''
stok_gdf['nais1']=''
stok_gdf['nais2']=''
stok_gdf['mo']=0
stok_gdf['ue']=0
stok_gdf['hs']=''
stok_gdf['tahs']=''
stok_gdf['tahsue']=''
stok_gdf['BedingungHangneigung']=''
stok_gdf['BedingungRegion']=''
for index, row in naiseinheitenunique.iterrows():
    legende=row['LEGENDE']
    kantonseinheit=row["ASSOC_TOT_"]
    naisdetail=row["NaiS Detail"]
    naisvereinfacht=row["NaiS vereinfacht"]
    hslist=row['hs'].replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()
    #Bedingung Hangneigung
    if row['Bedingung Hangneigung']=='<60%':
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)&(stok_gdf["meanslopeprc"]<60)), "naisdetail"] = naisdetail
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)&(stok_gdf["meanslopeprc"]<60)), "nais"] = naisvereinfacht
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)&(stok_gdf["meanslopeprc"]<60)), "hs"] = row['hs']
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["meanslopeprc"]<60)), "BedingungHangneigung"] = row['Bedingung Hangneigung']
    elif row['Bedingung Hangneigung']=='>60%':
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)&(stok_gdf["meanslopeprc"]>=60)), "naisdetail"] = naisdetail
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)&(stok_gdf["meanslopeprc"]>=60)), "nais"] = naisvereinfacht
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)&(stok_gdf["meanslopeprc"]>=60)), "hs"] = row['hs']
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["meanslopeprc"] >= 60)), "BedingungHangneigung"] = row['Bedingung Hangneigung']
    # Bedingung Region
    elif row['Bedingung Region']=='Region 1':
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"]==1)), "naisdetail"] = naisdetail
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"]==1)), "nais"] = naisvereinfacht
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"]==1)), "hs"] = row['hs']
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"]==1)), "BedingungRegion"] = row['Bedingung Region']
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"] == '1')), "naisdetail"] = naisdetail
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"] == '1')), "nais"] = naisvereinfacht
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"] == '1')), "hs"] = row['hs']
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"] == '1')), "BedingungRegion"] = row['Bedingung Region']
    elif row['Bedingung Region']=='Region M, J':
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"]=='M')), "naisdetail"] = naisdetail
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"]=='M')), "nais"] = naisvereinfacht
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"]=='M')), "hs"] = row['hs']
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"]=='M')), "BedingungRegion"] = row['Bedingung Region']
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"] == 'J')), "naisdetail"] = naisdetail
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"] == 'J')), "nais"] = naisvereinfacht
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"] == 'J')), "hs"] = row['hs']
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"] == 'J')), "BedingungRegion"] = row['Bedingung Region']
    elif row['Bedingung Region']=='Region J, M':
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"]=='M')), "naisdetail"] = naisdetail
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"]=='M')), "nais"] = naisvereinfacht
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"]=='M')), "hs"] = row['hs']
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"]=='M')), "BedingungRegion"] = row['Bedingung Region']
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"] == 'J')), "naisdetail"] = naisdetail
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"] == 'J')), "nais"] = naisvereinfacht
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"] == 'J')), "hs"] = row['hs']
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende) & (stok_gdf["storeg"] == 'J')), "BedingungRegion"] = row['Bedingung Region']
    else:
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "naisdetail"] = naisdetail
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "nais"] = naisvereinfacht
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "hs"] = row['hs']

    #Uebersetzung NaiS
    if '(' in row['NaiS vereinfacht']:
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "naisdetail"] = naisdetail
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "nais"] = row['NaiS vereinfacht']
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "nais1"] = row['NaiS vereinfacht'].replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[0]
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "nais2"] = row['NaiS vereinfacht'].replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[1]
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "ue"] = 1
    if '/' in row['NaiS vereinfacht']:
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "naisdetail"] = naisdetail
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "nais"] = row['NaiS vereinfacht']
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "nais1"] = row['NaiS vereinfacht'].replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[0]
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "nais2"] = row['NaiS vereinfacht'].replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[1]
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "mo"] = 1
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "ue"] = 1
    else:
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "naisdetail"] = naisdetail
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "nais"] = row['NaiS vereinfacht']
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "nais1"] = row['NaiS vereinfacht'].replace('/', ' ').replace('(', ' ').replace(')', '').replace('  ', ' ').strip().split()[0]
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "nais2"] = ''
    #Hohenstufenzuweisung
    if len(hslist)==1:
        stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
        #stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "nais1"] = row['NaiS'].replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[0]
    else:
        if "(" in row['hs']:
            stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
            stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende)), "tahsue"] = hoehenstufendictabkuerzungen[hslist[1]]
        else:
            for index2, row2 in stok_gdf[((stok_gdf["ASSOC_TOT_"] == kantonseinheit) & (stok_gdf["LEGENDE"] == legende))].iterrows():
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
                            stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[row2['hs'].replace('(',' ').replace(')','').strip().split()[-1]]
winsound.Beep(frequency, duration)
stok_gdf.columns
stok_gdf=stok_gdf[['joinid', 'ASSOC_TOT_', 'LEGENDE','taheute', 'storeg', 'meanslopeprc','slpprzrec', 'rad', 'radiation', 'hs1975', 'naisdetail','nais', 'nais1', 'nais2','mo', 'ue', 'hs', 'tahs', 'tahsue','geometry']]

#check empty values
stok_gdf["tahs"].unique().tolist()
stok_gdf["tahsue"].unique().tolist()
checknohs=stok_gdf[stok_gdf["hs"]==""][["LEGENDE","ASSOC_TOT_","naisdetail","nais",'hs1975',"hs"]]
print('Diese EInheiten haben keine Uebersetzung: '+str(checknohs['ASSOC_TOT_'].unique().tolist()))
#korrigiere mit sheet1
fehlendeuebersetzungen=checknohs[["LEGENDE","ASSOC_TOT_"]].drop_duplicates()
fehlendeuebersetzungen2=fehlendeuebersetzungen.merge(naiseinheitenunique, how='left', on=["LEGENDE","ASSOC_TOT_"])
fehlendeuebersetzungen2.to_excel(myworkspace+'/FR/'+'fehlendeHoehenstufen.xlsx')

len(fehlendeuebersetzungen)
#for index, row in fehlendeuebersetzungen:
#    legende2=row['LEGENDE']
#    assoc2=row['ASSOC_TOT_']
#    extractsheet1=sheet1[((sheet1['LEGENDE']==legende2)&(sheet1['ASSOC_TOT_']==assoc2))]
#    naisdetail2=extractsheet1['NaiS Detail'][0]
#    naisvereinfacht2=extractsheet1['NaiS vereinfacht'][0]
#    hs1=extractsheet1['Höhenstufe nur eine Möglichkeit'][0]
#    hs2 = extractsheet1['Höhenstufe nur eine Möglichkeit'][0]
#    hs3 = extractsheet1['Höhenstufe nur eine Möglichkeit'][0]

#Korrekturen der fehlenden Übersetzungen
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '18aP(17C)') & (stok_gdf["LEGENDE"] == '18a')), "naisdetail"] = '18(18w)'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '18aP(17C)') & (stok_gdf["LEGENDE"] == '18a')), "nais"] = '18(18w)'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '18aP(17C)') & (stok_gdf["LEGENDE"] == '18a')), "nais1"] = '18'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '18aP(17C)') & (stok_gdf["LEGENDE"] == '18a')), "nais2"] = '18w'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '18aP(17C)') & (stok_gdf["LEGENDE"] == '18a')), "mo"] = 0
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '18aP(17C)') & (stok_gdf["LEGENDE"] == '18a')), "ue"] = 1
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '18aP(17C)') & (stok_gdf["LEGENDE"] == '18a')), "hs"] = 'om'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '18aP(17C)') & (stok_gdf["LEGENDE"] == '18a')), "tahs"] = 'obermontan'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '18aP(17C)') & (stok_gdf["LEGENDE"] == '18a')), "tahsue"] = 'obermontan'
#
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '12s(24*U)') & (stok_gdf["LEGENDE"] == '12s')), "naisdetail"] = '12S(24*)'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '12s(24*U)') & (stok_gdf["LEGENDE"] == '12s')), "nais"] = '12S(24*)'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '12s(24*U)') & (stok_gdf["LEGENDE"] == '12s')), "nais1"] = '12S'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '12s(24*U)') & (stok_gdf["LEGENDE"] == '12s')), "nais2"] = '24*'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '12s(24*U)') & (stok_gdf["LEGENDE"] == '12s')), "mo"] = 0
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '12s(24*U)') & (stok_gdf["LEGENDE"] == '12s')), "ue"] = 1
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '12s(24*U)') & (stok_gdf["LEGENDE"] == '12s')), "hs"] = 'um(om)'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '12s(24*U)') & (stok_gdf["LEGENDE"] == '12s')), "tahs"] = 'untermontan'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '12s(24*U)') & (stok_gdf["LEGENDE"] == '12s')), "tahsue"] = 'obermontan'
#
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/13ho') & (stok_gdf["LEGENDE"] == '17')), "naisdetail"] = '18w(13h)'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/13ho') & (stok_gdf["LEGENDE"] == '17')), "nais"] = '18w(13h)'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/13ho') & (stok_gdf["LEGENDE"] == '17')), "nais1"] = '18w'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/13ho') & (stok_gdf["LEGENDE"] == '17')), "nais2"] = '13h'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/13ho') & (stok_gdf["LEGENDE"] == '17')), "mo"] = 1
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/13ho') & (stok_gdf["LEGENDE"] == '17')), "ue"] = 1
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/13ho') & (stok_gdf["LEGENDE"] == '17')), "hs"] = 'om'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/13ho') & (stok_gdf["LEGENDE"] == '17')), "tahs"] = 'obermontan'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/13ho') & (stok_gdf["LEGENDE"] == '17')), "tahsue"] = 'obermontan'
#
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/22a') & (stok_gdf["LEGENDE"] == '17')), "naisdetail"] = '17/22'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/22a') & (stok_gdf["LEGENDE"] == '17')), "nais"] = '17(22)'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/22a') & (stok_gdf["LEGENDE"] == '17')), "nais1"] = '17'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/22a') & (stok_gdf["LEGENDE"] == '17')), "nais2"] = '22'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/22a') & (stok_gdf["LEGENDE"] == '17')), "mo"] = 0
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/22a') & (stok_gdf["LEGENDE"] == '17')), "ue"] = 1
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/22a') & (stok_gdf["LEGENDE"] == '17')), "hs"] = 'sm um'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/22a') & (stok_gdf["LEGENDE"] == '17')), "tahs"] = 'untermontan'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/22a') & (stok_gdf["LEGENDE"] == '17')), "tahsue"] = 'untermontan'
#
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/18fP/18w') & (stok_gdf["LEGENDE"] == '17')), "naisdetail"] = '17/18M/18w'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/18fP/18w') & (stok_gdf["LEGENDE"] == '17')), "nais"] = '18w(18M)'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/18fP/18w') & (stok_gdf["LEGENDE"] == '17')), "nais1"] = '18w'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/18fP/18w') & (stok_gdf["LEGENDE"] == '17')), "nais2"] = '18M'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/18fP/18w') & (stok_gdf["LEGENDE"] == '17')), "mo"] = 0
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/18fP/18w') & (stok_gdf["LEGENDE"] == '17')), "ue"] = 1
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/18fP/18w') & (stok_gdf["LEGENDE"] == '17')), "hs"] = 'om'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/18fP/18w') & (stok_gdf["LEGENDE"] == '17')), "tahs"] = 'obermontan'
stok_gdf.loc[((stok_gdf["ASSOC_TOT_"] == '17/18fP/18w') & (stok_gdf["LEGENDE"] == '17')), "tahsue"] = 'obermontan'

#fill hoehenstufe for empty values
for index, row in stok_gdf.iterrows():
    if row["tahs"]=='' and row['hs1975']>0:
        stok_gdf.loc[index, "tahs"] = hoehenstufendictabkuerzungen[hsmoddictkurz[int(row['hs1975'])]]

#Gebüschwald
stok_gdf.loc[((stok_gdf['nais']=='AV')&(stok_gdf['hs1975']==-1)), 'tahs'] = 'subalpin'

stok_gdf.columns
#stok_gdf=stok_gdf[['joinid', 'ASSOC_TOT_', 'taheute', 'storeg', 'meanslopeprc','slpprzrec', 'rad', 'radiation', 'hs1975', 'nais', 'nais1', 'nais2','mo', 'ue', 'hs', 'tahs', 'tahsue','geometry']]

#fill tahsue
for index, row in stok_gdf.iterrows():
    if '(' in row['nais'] and row['ue']==1 and row['tahsue']=='':
        hslist = row['hs'].replace('/', ' ').replace('(', ' ').replace(')', '').strip().split()
        if len(hslist)==1:
            stok_gdf.loc[index, 'tahsue']=row['tahs']


#check empty values
stok_gdf["tahs"].unique().tolist()
stok_gdf["tahsue"].unique().tolist()
checknohs=stok_gdf[stok_gdf["tahs"]==""]#[["wg_haupt","wg_zusatz","nais",'hs1975']]
checknohsue=stok_gdf[((stok_gdf["tahsue"]=="")&(stok_gdf["ue"]==1))]
stok_gdf.loc[((stok_gdf["tahsue"]=="")&(stok_gdf["ue"]==1)), 'tahsue']=stok_gdf['tahs']
naisohnetahs=checknohs['nais'].unique().tolist()
naisohnetahsue=checknohsue['nais'].unique().tolist()
stok_gdf.loc[((stok_gdf['ue']==0)&(stok_gdf['nais1']=='')&(stok_gdf['nais']!='')),'nais1']=stok_gdf['nais']

#fill nais2
checknais2=stok_gdf[((stok_gdf["nais2"]=="")&(stok_gdf["ue"]==1))]
for index, row in stok_gdf.iterrows():
    if row['nais2']=='' and row['ue']==1:
        naislist=row['nais'].replace('(', ' ').replace(')', ' ').replace('/',' ').replace('  ',' ').strip().split()
        stok_gdf.loc[index,'nais2']=naislist[1]


#Korrekturen
stok_gdf.columns
#test=stok_gdf[stok_gdf['nais']=='32V']
#stok_gdf.loc[stok_gdf['nais']=='18v(53)','nais2']='53Ta'
#stok_gdf.loc[stok_gdf['nais']=='18v(53)','nais']='18v(53Ta)'
#stok_gdf.loc[stok_gdf['nais']=='12w(12Fe)','nais2']='12aFe'
#stok_gdf.loc[stok_gdf['nais']=='12w(12Fe)','nais']='12w(12aFe)'
#stok_gdf.loc[stok_gdf['nais']=='22(12)','nais2']='12a'
#stok_gdf.loc[stok_gdf['nais']=='22(12)','nais']='22(12a)'
#stok_gdf.loc[stok_gdf['nais']=='26h(12)','nais2']='12a'
#stok_gdf.loc[stok_gdf['nais']=='26h(12)','nais']='26h(12a)'
#test=stok_gdf[stok_gdf['hs']=='um(om)']
#test=stok_gdf[stok_gdf['hs']=='hm(om)']
#test=stok_gdf[stok_gdf['hs']=='om(um)']
#test=stok_gdf[stok_gdf['hs']=='om(hm)']
#test=stok_gdf[stok_gdf['nais']=='27h(49)']

print("write output")
stok_gdf.columns
#stok_gdf['BedingungHangneigung'].unique().tolist()
#stok_gdf['BedingungRegion'].unique().tolist()
stok_gdf.to_file(myworkspace+"/FR/stok_gdf_attributed.gpkg")
#stok_gdf=gpd.read_file(myworkspace+"/FR/stok_gdf_attributed.gpkg")
print("done")




#Export for tree-app
print('Export for Tree-App')
stok_gdf.columns
#stok_gdf.loc[((stok_gdf['ue']==1)&(stok_gdf['tahsue']=='')&(stok_gdf['tahs']!='')),'tahsue']=stok_gdf['tahs']
treeapp=stok_gdf[['ASSOC_TOT_','nais', 'nais1', 'nais2', 'mo', 'ue','tahs', 'tahsue','geometry']]
treeapp.to_file(myworkspace+"/FR/FR_treeapp.gpkg", layer='FR_treeapp', driver="GPKG")
treeapp.columns
print("done")

#test = stok_gdf[stok_gdf['nais']=='18M(48)']
#test = stok_gdf[stok_gdf['nais']=='12a(18)']
#test = stok_gdf[stok_gdf['nais']=='46(8*)']
#test = stok_gdf[stok_gdf['nais']=='7a(10a)']
#test = stok_gdf[stok_gdf['nais']=='18v(18*)']
#test = stok_gdf[stok_gdf['nais']=='53Ta(18v)']
#test = stok_gdf[stok_gdf['nais1']=='']
#test = stok_gdf[((stok_gdf['nais2']=='')&(stok_gdf['ue']==1))]

#test2 = naiseinheitenunique[naiseinheitenunique['NaiS']=='60*(53)']
#test=stok_gdf[((stok_gdf['ue']==1)&(stok_gdf['tahsue']=='')&(stok_gdf['tahs']!=''))]



