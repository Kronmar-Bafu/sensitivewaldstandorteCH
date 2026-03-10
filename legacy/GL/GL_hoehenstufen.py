import numpy as np
import pandas as pd
import joblib
import fiona
import geopandas as gpd
import os
import shapely
import xlrd
import openpyxl
import rasterstats
from rasterstats import zonal_stats
from osgeo import osr, gdal
#import gdal
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(2056) #LV95
gtiff_driver=gdal.GetDriverByName("GTiff")


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
hsmoddict={2:"collin",4:"submontan",5:"untermontan",6:"obermontan",8:"hochmontan",9:"subalpin",10:"obersubalpin"}
hsmoddictkurz={2:"co",4:"sm",5:"um",6:"om",8:"hm",9:"sa",10:"osa"}
hoehenstufenlist=["collin","submontan","untermontan","obermontan","hochmontan","subalpin","obersubalpin"]
hsdictzuzahlen={"co":2,"sm":4,"um":5,"om":6,"hm":8,"sa":9,"osa":10}
#read excel files
naiseinheitenunique=pd.read_excel(codespace+"/GL_nais_einheiten_unique_joined_mf_Version26112024.xlsx", dtype="str", engine='openpyxl')

#read the rasters
#reference tif raster
print("read reference raster")
referenceraster=myworkspace+"/GL/dem10m.tif"
referencetifraster=gdal.Open(referenceraster)
referencetifrasterband=referencetifraster.GetRasterBand(1)
referencerasterProjection=referencetifraster.GetProjection()
ncols=referencetifrasterband.XSize
nrows=referencetifrasterband.YSize
indatatype=referencetifrasterband.DataType
#indatatypeint=gdal.Open(myworkspace+"/regionen.tif").GetRasterBand(1).DataType
#dhmarr=convert_tif_to_array("D:/CCW20/GIS/dhm25.tif")
NODATA_value=-9999

sloperaster=myworkspace+"/GL/slope10mprz.tif"
radiationraster=myworkspace+"/GL/globradyw.tif"
hoehenstufenraster=myworkspace+"/GL/hs1975.tif"
#hsheute=gpd.read_file(myworkspace+"/GL/vegetationshoehenstufen19611990clipSGAIAR.shp")

#read shapefile
stok_gdf=gpd.read_file(myworkspace+"/GL/waldgesellschaften/esri_shapefile/pub_gl_waldgesellschaften/waldgesellschaften.shp")
taheute=gpd.read_file(myworkspace+"/Tannenareale.shp")
storeg=gpd.read_file(myworkspace+"/Waldstandortsregionen.shp")
len(stok_gdf)
stok_gdf.crs
stok_gdf.columns

#Tannenareale
taheute.crs
taheute.columns
#taheute.plot()
#taheute.rename(columns={"Code_Ta": "taheute"}, inplace=True)
#taheute.drop(columns=['Areal_de', 'Areal_fr', 'Areal_it', 'Areal_en','Shape_Leng','Shape_Area'], inplace=True)
##overlay spatial join
##stok_gdf=gpd.sjoin(stok_gdf,taheute, how='left', op="intersects")
#len(stok_gdf)
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
#stok_gdf.columns
#stok_gdf=stok_gdf[['DTWGEINHEI','taheute','geometry']]
#stok_gdf['joinid']=stok_gdf.index
stok_gdf['taheute']=1

#Standortregionen
#storeg.crs
#storeg.columns
##taheute.plot()
#storeg.rename(columns={"Subcode": "storeg"}, inplace=True)
#storeg.drop(columns=['Region_de', 'Region_fr', 'Region_it', 'Region_en', 'Code', 'Code_Bu', 'Code_Fi', 'Shape_Leng', 'Shape_Area'], inplace=True)
##overlay spatial join
#stok_gdfstoreg=gpd.sjoin(stok_gdf,storeg, how='left', op="intersects")
#len(stok_gdfstoreg)
#stok_gdfstoreggrouped=stok_gdfstoreg[["joinid","storeg"]].groupby(by=["joinid"]).min()
###stok_gdftagrouped["joinid"]=stok_gdftagrouped.index
#len(stok_gdfstoreggrouped)
#stok_gdfstoreggrouped.columns
##stok_gdf.columns
#stok_gdf=stok_gdf.merge(stok_gdfstoreggrouped, on='joinid', how='left')#left_on='joinid', right_on='joinid',
##len(stok_gdf)
##stok_gdf.to_file(projectspace+"/GIS/stok_gdf_attributed.shp")
#del storeg
#del stok_gdfstoreggrouped
#del stok_gdfstoreg
stok_gdf['storeg']=1 #'Nördliche Randalpen'

#attribute shapefile
#mean slope in percent
print('slope stats')
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

stok_gdf.loc[stok_gdf["meanslopeprc"].isnull() == True, "meanslopeprc"]=15
stok_gdf.columns
del zonstatslope

#radiation
print('radiation stats')
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
del zonstatrad

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
#stok_gdf.to_file(myworkspace+"/GL/stok_gdf_attributed.gpkg")
#del zonstaths

#stok_gdf=gpd.read_file(myworkspace+"/GL/stok_gdf_attributed.gpkg")
stok_gdf.columns
#uebersetzung von Kantonseinheit in NAIS
print('Uebersetzung')
len(naiseinheitenunique)
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['NaiS'].isnull() == False]
len(naiseinheitenunique)
stok_gdf['nais']=''
stok_gdf['nais1']=''
stok_gdf['nais2']=''
stok_gdf['mo']=0
stok_gdf['ue']=0
stok_gdf['hs']=''
stok_gdf['tahs']=''
stok_gdf['tahsue']=''
stok_gdf['kantonseinheit']=''
naiseinheitenunique.columns
for index, row in naiseinheitenunique.iterrows():
    kantonseinheit = row['Einheit GL']
    kantonseinheit1=row["wg_haupt"]
    kantonseinheit2 = row["wg_zusatz"]
    wg_name=row['wg_name']
    nais=row["NaiS"]
    #add nais, nais1, nais2, ue, mo
    hslist=row['hs'].replace('/',' ').replace('(',' ').replace(')','').strip().split()
    #hslist = row['hs'].strip().split()
    stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "nais"] = nais
    stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "hs"] =row['hs']
    stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "kantonseinheit"] = kantonseinheit
    if '(' in row['NaiS']:
        stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "nais1"] = row['NaiS'].replace('/',' ').replace('(',' ').replace(')','').strip().split()[0]
        stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "nais2"] = row['NaiS'].replace('/',' ').replace('(',' ').replace(')','').strip().split()[1]
        stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "ue"] = 1
    elif '/' in row['NaiS']:
        stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "nais1"] = row['NaiS'].replace('/',' ').replace('(',' ').replace(')','').strip().split()[0]
        stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "nais2"] = row['NaiS'].replace('/',' ').replace('(',' ').replace(')','').strip().split()[1]
        stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "mo"] = 1
    else:
        stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "nais1"] = row['NaiS'].replace('/', ' ').replace('(', ' ').replace(')', '').strip().split()[0]
    #special rules for altitudinal belts attribution
    if row['Bedingung Hangneigung'] in ['<60%', '>60%']:
        if row['Bedingung Hangneigung'] == '<60%' and len(hslist)==1:
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['meanslopeprc']<60)), "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['meanslopeprc'] < 60)), "tahsue"] = hoehenstufendictabkuerzungen[hslist[0]]
        elif row['Bedingung Hangneigung'] == '>60%' and len(hslist)==1:
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['meanslopeprc']>=60)), "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['meanslopeprc'] >= 60)), "tahsue"] = hoehenstufendictabkuerzungen[hslist[0]]
        elif row['Bedingung Hangneigung'] == '<60%' and len(hslist) > 1:
            if "(" in row['hs']:
                stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['meanslopeprc']<60)), "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
                stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['meanslopeprc']<60)), "tahsue"] = hoehenstufendictabkuerzungen[hslist[1]]
            else:
                stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['meanslopeprc'] >= 60)), "tahs"] = hoehenstufendictabkuerzungen[hslist[1]]
                stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['meanslopeprc'] >= 60)), "tahsue"] = hoehenstufendictabkuerzungen[hslist[1]]
                #for index2, row2 in stok_gdf[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)& (stok_gdf['meanslopeprc']<60))].iterrows():
                #    if row2['hs1975'] > 0:
                #        hsmod = hsmoddictkurz[int(row2['hs1975'])]
                #    else:
                #        hsmod = 'nan'
                #    if hsmod in row2['hs'].strip().split():
                #        stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[hsmod]
                #    else:
                #        test = hoehenstufendictabkuerzungen[
                #            row2['hs'].replace('(', ' ').replace(')', '').strip().split()[0]]
                #        if len(row2['hs'].replace('(', ' ').replace(')',
                #                                                    '').strip().split()) > 1 and test == 'collin':
                #            stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[
                #                row2['hs'].replace('(', ' ').replace(')', '').strip().split()[-1]]
                #        else:
                #            stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[
                #                row2['hs'].replace('(', ' ').replace(')', '').strip().split()[0]]
        elif row['Bedingung Hangneigung'] == '>60%' and len(hslist) > 1:
            if "(" in row['hs']:
                stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['meanslopeprc']>=60)), "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
                stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['meanslopeprc']>=60)), "tahsue"] = hoehenstufendictabkuerzungen[hslist[1]]
            else:
                stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['meanslopeprc'] >= 60)), "tahs"] = hoehenstufendictabkuerzungen[hslist[1]]
                stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['meanslopeprc'] >= 60)), "tahsue"] = hoehenstufendictabkuerzungen[hslist[1]]
                #for index2, row2 in stok_gdf[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)& (stok_gdf['meanslopeprc']<60))].iterrows():
                #    if row2['hs1975'] > 0:
                #        hsmod = hsmoddictkurz[int(row2['hs1975'])]
                #    else:
                #        hsmod = 'nan'
                #    if hsmod in row2['hs'].strip().split():
                #        stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[hsmod]
                #    else:
                #        test = hoehenstufendictabkuerzungen[
                #            row2['hs'].replace('(', ' ').replace(')', '').strip().split()[0]]
                #        if len(row2['hs'].replace('(', ' ').replace(')',
                #                                                    '').strip().split()) > 1 and test == 'collin':
                #            stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[
                #                row2['hs'].replace('(', ' ').replace(')', '').strip().split()[-1]]
                #        else:
                #            stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[
                #                row2['hs'].replace('(', ' ').replace(')', '').strip().split()[-1]]
    if row['Bedingung Höhenstufe'] in ['sm um','hm','om','om hm','sa']:
        if row['Bedingung Höhenstufe'] == 'sm um':
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'] == 2)), "tahs"] = 'submontan'
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975']==4)), "tahs"] = 'submontan'
            #stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975']==4)), "nais"] = nais
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'] == 5)), "tahs"] = 'untermontan'
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'] == 6)), "tahs"] = 'untermontan'
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'] == 8)), "tahs"] = 'untermontan'
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'] == 9)), "tahs"] = 'untermontan'
            #stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'] == 5)), "nais"] = nais
            #stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (~stok_gdf['hs1975'].isin([4,5]))), "tahs"] = 'untermontan'
            #stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (~stok_gdf['hs1975'].isin([4,5]))), "nais"] = nais
        elif row['Bedingung Höhenstufe'] == 'om hm':
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'] == 2)), "tahs"] = 'obermontan'
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'] == 4)), "tahs"] = 'obermontan'
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'] == 5)), "tahs"] = 'obermontan'
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975']==6)), "tahs"] = 'obermontan'
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'] == 8)), "tahs"] = 'hochmontan'
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'] == 9)), "tahs"] = 'hochmontan'
            #stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (~stok_gdf['hs1975'].isin([6,8]))), "tahs"] = 'hochmontan'
            #stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (~stok_gdf['hs1975'].isin([6,8]))), "nais"] = nais
        elif row['Bedingung Höhenstufe'] == 'hm':
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "tahs"] = 'hochmontan'
            #stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975']!=8)), "tahs"] = 'hochmontan'
            #stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975']!=8)), "nais"] = nais
        elif row['Bedingung Höhenstufe'] == 'om':
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "tahs"] = 'obermontan'
            #stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975']!=6)), "tahs"] = 'obermontan'
            #stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975']!=6)), "nais"] = nais
        elif row['Bedingung Höhenstufe'] == 'sa':
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "tahs"] = 'subalpin'
            #stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975']!=9)), "tahs"] = 'subalpin'
            #stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975']!=9)), "nais"] = nais
    if "(" in row['hs'] and len(hslist)>1:# and row['Bedingung Höhenstufe'] not in ['sm um', 'hm', 'om', 'om hm', 'sa'] and row['Bedingung Hangneigung'] not in ['<60%', '>60%']:
        stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
        stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "tahsue"] = hoehenstufendictabkuerzungen[hslist[1]]
    #else:
    elif "(" not in row['hs'] and row['Bedingung Höhenstufe'] not in ['sm um', 'hm', 'om', 'om hm', 'sa'] and row['Bedingung Hangneigung'] not in ['<60%', '>60%']:
        if len(hslist)==1:
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
            stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)), "tahsue"] = hoehenstufendictabkuerzungen[hslist[0]]
        else:
            hslistinzahlen=[]
            for item in hslist:
                hslistinzahlen.append(hsdictzuzahlen[item])
            for hszahl in hslistinzahlen:
                stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2)&(stok_gdf['hs1975']==hszahl)), "tahs"] = hoehenstufendictabkuerzungen[hsmoddictkurz[hszahl]]
                stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'] == hslistinzahlen[1])), "tahs"] =hoehenstufendictabkuerzungen[hsmoddictkurz[hszahl]]
                stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'].isin(hslistinzahlen)==False)), "tahs"] =hoehenstufendictabkuerzungen[hsmoddictkurz[hslistinzahlen[-1]]]
                stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'] == hszahl)), "tahsue"] = hoehenstufendictabkuerzungen[hsmoddictkurz[hszahl]]
                stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'] == hslistinzahlen[1])), "tahsue"] = hoehenstufendictabkuerzungen[hsmoddictkurz[hszahl]]
                stok_gdf.loc[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2) & (stok_gdf['hs1975'].isin(hslistinzahlen) == False)), "tahsue"] = hoehenstufendictabkuerzungen[hsmoddictkurz[hslistinzahlen[-1]]]
                #for index2, row2 in stok_gdf[((stok_gdf["wg_haupt"] == kantonseinheit1) & (stok_gdf["wg_zusatz"] == kantonseinheit2))].iterrows():
                #    if row2['hs1975']>0:
                #        hsmod=hsmoddictkurz[int(row2['hs1975'])]
                #    else:
                #        hsmod = 'nan'
                #    if hsmod in row2['hs'].strip().split():
                #        stok_gdf.loc[index2,'tahs']=hoehenstufendictabkuerzungen[hsmod]
                #    else:
                #        test=hoehenstufendictabkuerzungen[row2['hs'].replace('(',' ').replace(')','').strip().split()[0]]
                #        if len(row2['hs'].replace('(',' ').replace(')','').strip().split()) >1 and test == 'collin':
                #            stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[row2['hs'].replace('(',' ').replace(')','').strip().split()[-1]]
                #        else:
                #            stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[row2['hs'].replace('(',' ').replace(')','').strip().split()[-1]]

#fixe Uebergaenge
for index, row in stok_gdf.iterrows():
    if "(" in row['hs']:
        hslist = row['hs'].replace('/', ' ').replace('(', ' ').replace(')', '').replace('  ', ' ').strip().split()
        stok_gdf.loc[index, "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
        stok_gdf.loc[index, "tahsue"] = hoehenstufendictabkuerzungen[hslist[1]]

#Gebüschwald
stok_gdf.loc[((stok_gdf['nais']=='AV')&(stok_gdf['hs1975']==-1)), 'tahs'] = 'subalpin'

stok_gdf.columns
#stok_gdf=stok_gdf[['joinid', 'DTWGEINHEI', 'taheute', 'storeg', 'meanslopeprc','slpprzrec', 'rad', 'radiation', 'hs1975', 'nais', 'nais1', 'nais2','mo', 'ue', 'hs', 'tahs', 'tahsue','geometry']]

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
naisohnetahs=checknohs['nais'].unique().tolist()
naisohnetahsue=checknohsue['nais'].unique().tolist()
#stok_gdf.loc[(stok_gdf['nais']=='53'), 'tahs'] = 'subalpin'
#stok_gdf.loc[(stok_gdf['nais']=='53(67)'), 'tahs'] = 'subalpin'
#stok_gdf.loc[(stok_gdf['nais']=='53Ta(67)'), 'tahs'] = 'hochmontan'
#stok_gdf.loc[(stok_gdf['nais']=='60*'), 'tahs'] = 'subalpin'
#stok_gdf.loc[(stok_gdf['nais']=='60*(67)'), 'tahs'] = 'subalpin'
#stok_gdf.loc[(stok_gdf['nais']=='60*(53)'), 'tahs'] = 'subalpin'
#stok_gdf.loc[(stok_gdf['nais']=='60*(AV)'), 'tahs'] = 'subalpin'
#stok_gdf.loc[(stok_gdf['nais']=='69(60*)'), 'tahs'] = 'subalpin'
#stok_gdf.loc[(stok_gdf['nais']=='53'), 'tahsue'] = 'subalpin'
#stok_gdf.loc[(stok_gdf['nais']=='53(67)'), 'tahsue'] = 'subalpin'
#stok_gdf.loc[(stok_gdf['nais']=='53Ta(67)'), 'tahsue'] = 'hochmontan'
#stok_gdf.loc[(stok_gdf['nais']=='60*'), 'tahsue'] = 'subalpin'
#stok_gdf.loc[(stok_gdf['nais']=='60*(67)'), 'tahsue'] = 'subalpin'
#stok_gdf.loc[(stok_gdf['nais']=='60*(AV)'), 'tahsue'] = 'subalpin'
#stok_gdf.loc[(stok_gdf['nais']=='69(60*)'), 'tahsue'] = 'subalpin'
#stok_gdf.loc[(stok_gdf['nais']=='60*(53)'), 'tahsue'] = 'subalpin'
#test=stok_gdf[stok_gdf['nais']=='18M(48)']
#test=stok_gdf[stok_gdf['nais']=='60*(53)']
#test=stok_gdf[stok_gdf['nais']=='57V']
#test=stok_gdf[stok_gdf['nais']=='18M(48)']
#fill hoehenstufe for empty values
#for index, row in stok_gdf.iterrows():
#    if row["tahs"]=='' and row['hs1975']>0:
#        stok_gdf.loc[index, "tahs"] = hoehenstufendictabkuerzungen[hsmoddictkurz[int(row['hs1975'])]]
#fill nais1, nais2
#for index, row in stok_gdf.iterrows():
#    if '(' in row['nais']:
#        stok_gdf.loc[index, "nais1"] = row['nais'].replace('/',' ').replace('(',' ').replace(')','').strip().split()[0]
#        stok_gdf.loc[index, "nais2"] = row['nais'].replace('/', ' ').replace('(', ' ').replace(')', '').strip().split()[1]
#        stok_gdf.loc[index, "ue"] = 1
#    elif '/' in row['hs']:
#        stok_gdf.loc[index, "nais1"] = row['nais'].replace('/',' ').replace('(',' ').replace(')','').strip().split()[0]
#        stok_gdf.loc[index, "nais2"] = row['nais'].replace('/', ' ').replace('(', ' ').replace(')', '').strip().split()[1]
#        stok_gdf.loc[index, "mo"] = 1
#    else:
#        stok_gdf.loc[index, "nais1"] = row['nais'].replace('/', ' ').replace('(', ' ').replace(')', '').strip().split()[0]
#write output
stok_gdf.to_file(myworkspace+"/GL/stok_gdf_attributed.gpkg",layer='stok_gdf_attributed', driver="GPKG")
#stok_gdf=gpd.read_file(myworkspace+"/GL/stok_gdf_attributed.gpkg", layer='stok_gdf_attributed')
print("done")
#Export for tree-app
print('Export for Tree-App')
stok_gdf.columns
stok_gdf.loc[((stok_gdf['ue']==1)&(stok_gdf['tahsue']=='')&(stok_gdf['tahs']!='')),'tahsue']=stok_gdf['tahs']
treeapp=stok_gdf[['joinid','wg_haupt','wg_zusatz', 'wg_name','nais', 'nais1', 'nais2', 'mo', 'ue','tahs', 'tahsue','geometry']]

treeapp.to_file(myworkspace+"/GL/GL_treeapp.gpkg", layer='GL_treeapp', driver="GPKG")
treeapp.columns
print("done")

#test = stok_gdf[stok_gdf['nais']=='18M(48)']
#test = stok_gdf[stok_gdf['nais']=='60*(53)']
#test = stok_gdf[stok_gdf['nais']=='18M(12a)']
#test2 = naiseinheitenunique[naiseinheitenunique['NaiS']=='60*(53)']
#test=stok_gdf[((stok_gdf['ue']==1)&(stok_gdf['tahs']=='')&(stok_gdf['tahs']!=''))]

