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
hsmoddict={2:"collin",3:"collin",4:"submontan",5:"untermontan",6:"obermontan",8:"hochmontan",9:"subalpin",10:"obersubalpin"}
hsmoddictkurz={2:"co",3:"co",4:"sm",5:"um",6:"om",8:"hm",9:"sa",10:"osa"}
hoehenstufenlist=["collin","submontan","untermontan","obermontan","hochmontan","subalpin","obersubalpin"]

#read excel files
naiseinheitenunique=pd.read_excel(codespace+"/NE_nais_einheiten_unique_mf.xlsx", sheet_name='export', dtype="str", engine='openpyxl')
naiseinheitenunique.columns
naiseinheitenunique.dtypes
len(naiseinheitenunique)
naiseinheitenunique.drop(columns=['tahs'], inplace=True)
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['nais']!='-']
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['hs']!='']
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['hs'].isnull()==False]
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['hs']!='nan']
#read the rasters
#reference tif raster
print("read reference raster")
referenceraster=myworkspace+"/NE/NE_dem10m.tif"
referencetifraster=gdal.Open(referenceraster)
referencetifrasterband=referencetifraster.GetRasterBand(1)
referencerasterProjection=referencetifraster.GetProjection()
ncols=referencetifrasterband.XSize
nrows=referencetifrasterband.YSize
indatatype=referencetifrasterband.DataType
#indatatypeint=gdal.Open(myworkspace+"/regionen.tif").GetRasterBand(1).DataType
#dhmarr=convert_tif_to_array("D:/CCW20/GIS/dhm25.tif")
NODATA_value=-9999

sloperaster=myworkspace+"/NE/NE_slope10mprz.tif"
radiationraster=myworkspace+"/NE/NE_globradyw.tif"
hoehenstufenraster=myworkspace+("/NE/NE"
                                "_hs1975.tif")


#read shapefile
stok_gdf=gpd.read_file(myworkspace+"/geops_treeapp/forest_types_ne/forest_types_ne.shp")
stok_gdf.dtypes
stok_gdf=stok_gdf.astype({'code_neuch': 'str', 'code_nais': 'str'})
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

#Standortregionen
storeg.crs
storeg.columns
#taheute.plot()
storeg.rename(columns={"Subcode": "storeg"}, inplace=True)
storeg.drop(columns=[ 'Region_fr', 'Region_it', 'Region_en', 'Code', 'Code_Bu', 'Code_Fi', 'Shape_Leng', 'Shape_Area'], inplace=True)
#overlay spatial join
stok_gdf.columns
stok_gdf.drop(columns=[ 'index_right'], inplace=True)
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

#radiation
stok_gdf["rad"]=0
#zonstatslope=zonal_stats(stok_gdf, referenceraster,stats="count min mean max median")
zonstatrad=zonal_stats(stok_gdf, radiationraster,stats="mean")
i=0
while i < len(stok_gdf):
    stok_gdf.loc[i,"rad"]=zonstatrad[i]["mean"]
    i+=1
przquant90=stok_gdf['rad'].quantile(q=0.9, interpolation='linear')
przquant10=stok_gdf['rad'].quantile(q=0.1, interpolation='linear')

stok_gdf["radiation"]=0
#stok_gdf.loc[stok_gdf["rad"]>=147.0,"radiation"]=1 #90% quantile
#stok_gdf.loc[stok_gdf["rad"]<=112.0,"radiation"]=-1 #10% quantile
stok_gdf.loc[stok_gdf["rad"]>=przquant90,"radiation"]=1 #90% quantile
stok_gdf.loc[stok_gdf["rad"]<=przquant10,"radiation"]=-1 #10% quantile
stok_gdf.columns
#del zonstatrad
winsound.Beep(frequency, duration)

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

stok_gdf.to_file(myworkspace+"/NE/stok_gdf_attributed_temp.gpkg")
#stok_gdf=gpd.read_file(myworkspace+"/NE/stok_gdf_attributed_temp.gpkg")
winsound.Beep(frequency, duration)


#uebersetzung von Kantonseinheit in NAIS
#stok_gdf=gpd.read_file(myworkspace+"/NE/stok_gdf_attributed_temp.gpkg")
#naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['NaiS'].isnull() == False]
stok_gdf.columns
len(naiseinheitenunique)
stok_gdf['nais']=''
stok_gdf['nais1']=''
stok_gdf['nais2']=''
stok_gdf['mo']=0
stok_gdf['ue']=0
stok_gdf['hs']=''
stok_gdf['tahs']=''
stok_gdf['tahsue']=''
#transform null values
stok_gdf.loc[stok_gdf['code_neuch'].isnull()==True,'code_neuch']=''
stok_gdf.loc[stok_gdf['associatio'].isnull()==True,'associatio']=''
stok_gdf.loc[stok_gdf['code_nais'].isnull()==True,'code_nais']=''
naiseinheitenunique.loc[naiseinheitenunique['code_neuch'].isnull()==True,'code_neuch']=''
#naiseinheitenunique.loc[naiseinheitenunique['associatio'].isnull()==True,'associatio']=''
naiseinheitenunique.loc[naiseinheitenunique['code_nais'].isnull()==True,'code_nais']=''

print('iterate for attributing nais and tahs')
for index, row in naiseinheitenunique.iterrows():
    kantonseinheit=row['code_neuch']
    code_nais=row["code_nais"]
    nais=row["nais"]
    hslist=row['hs'].replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()
    #Hoehenstufenzuweisung
    stok_gdf.loc[((stok_gdf["code_neuch"] == kantonseinheit) & (stok_gdf["code_nais"] == code_nais)), "nais"] = nais
    stok_gdf.loc[((stok_gdf["code_neuch"] == kantonseinheit) & (stok_gdf["code_nais"] == code_nais)), "hs"] = row['hs']
    #Uebersetzung NaiS
    if '(' in row['nais']:
        stok_gdf.loc[((stok_gdf["code_neuch"] == kantonseinheit) & (stok_gdf["code_nais"] == code_nais)), "nais1"] = nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[0]
        stok_gdf.loc[((stok_gdf["code_neuch"] == kantonseinheit) & (stok_gdf["code_nais"] == code_nais)), "nais2"] = nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[1]
        stok_gdf.loc[((stok_gdf["code_neuch"] == kantonseinheit) & (stok_gdf["code_nais"] == code_nais)), "ue"] = 1
    elif '/' in row['nais']:
        stok_gdf.loc[((stok_gdf["code_neuch"] == kantonseinheit) & (stok_gdf["code_nais"] == code_nais)), "nais1"] = nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[0]
        stok_gdf.loc[((stok_gdf["code_neuch"] == kantonseinheit) & (stok_gdf["code_nais"] == code_nais)), "nais2"] = nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[1]
        stok_gdf.loc[((stok_gdf["code_neuch"] == kantonseinheit) & (stok_gdf["code_nais"] == code_nais)), "mo"] = 1
        stok_gdf.loc[((stok_gdf["code_neuch"] == kantonseinheit) & (stok_gdf["code_nais"] == code_nais)), "ue"] = 1
    else:
        stok_gdf.loc[((stok_gdf["code_neuch"] == kantonseinheit) & (stok_gdf["code_nais"] == code_nais)), "nais1"] = nais.replace('/', ' ').replace('(', ' ').replace(')', '').replace('  ', ' ').strip().split()[0]
        stok_gdf.loc[((stok_gdf["code_neuch"] == kantonseinheit) & (stok_gdf["code_nais"] == code_nais)), "nais2"] = ''
#Hohenstufenzuweisung
for index, row in stok_gdf.iterrows():
    hslist = row['hs'].replace('/', ' ').replace('(', ' ').replace(')', '').replace('  ', ' ').strip().split()
    if len(hslist)==1:
        stok_gdf.loc[index, "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
    else:
        if "(" in row['hs']:
            stok_gdf.loc[index, "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
            stok_gdf.loc[index, "tahsue"] = hoehenstufendictabkuerzungen[hslist[1]]
        else:
            if row['hs1975']>0:
                hsmod=hsmoddictkurz[int(row['hs1975'])]
                if hsmod in hslist:
                    stok_gdf.loc[index,'tahs']=hoehenstufendictabkuerzungen[hsmod]
                    if row['ue']==1:
                        stok_gdf.loc[index, 'tahsue'] = hoehenstufendictabkuerzungen[hsmod]
                else:
                    stok_gdf.loc[index, 'tahs'] =hoehenstufendictabkuerzungen[hslist[-1]]
                    if row['ue']==1:
                        stok_gdf.loc[index, 'tahsue'] = hoehenstufendictabkuerzungen[hslist[-1]]
            else:
                stok_gdf.loc[index, 'tahs'] =hoehenstufendictabkuerzungen[hslist[-1]]
                stok_gdf.loc[index, 'tahsue'] = hoehenstufendictabkuerzungen[hslist[-1]]
winsound.Beep(frequency, duration)


stok_gdf.columns
#test=stok_gdf[((stok_gdf["code_neuch"] == '6') & (stok_gdf["code_nais"] == '25*'))]
stok_gdf=stok_gdf[['joinid', 'code_neuch', 'associatio','taheute', 'storeg', 'meanslopeprc','slpprzrec', 'rad', 'radiation', 'hs1975', 'nais', 'nais1', 'nais2','mo', 'ue', 'hs', 'tahs', 'tahsue','geometry']]

#check empty values
stok_gdf["tahs"].unique().tolist()
stok_gdf["tahsue"].unique().tolist()
checknohs=stok_gdf[stok_gdf["tahs"]==""][['code_neuch', 'associatio',"nais",'hs1975',"hs"]]
print('Diese EInheiten haben keine Uebersetzung: '+str(checknohs['code_neuch'].unique().tolist()))

##fill hoehenstufe for empty values
#for index, row in stok_gdf.iterrows():
#    if row["tahs"]=='' and row['hs1975']>0:
#        stok_gdf.loc[index, "tahs"] = hoehenstufendictabkuerzungen[hsmoddictkurz[int(row['hs1975'])]]


#Gebüschwald
#stok_gdf.loc[((stok_gdf['nais']=='AV')&(stok_gdf['hs1975']==-1)), 'tahs'] = 'subalpin'

#Waldflächen, die im Höhenstufenmodell 1975 oberhalb der subalpinen Stufe liegen sollen der subalpinen Stufe zugeordnet werden.
#stok_gdf.loc[((stok_gdf['tahs']=='')&(stok_gdf['hs1975']==-1)), 'tahs'] = 'subalpin'


##fill tahsue
#for index, row in stok_gdf.iterrows():
#    if '(' in row['nais'] and row['ue']==1 and row['tahsue']=='':
#        hslist = row['hs'].replace('/', ' ').replace('(', ' ').replace(')', '').strip().split()
#        if len(hslist)==1:
#            stok_gdf.loc[index, 'tahsue']=row['tahs']
#

#check empty values
#stok_gdf["tahs"].unique().tolist()
#stok_gdf["tahsue"].unique().tolist()
#checknohs=stok_gdf[stok_gdf["tahs"]==""]#[["wg_haupt","wg_zusatz","nais",'hs1975']]
#checknohsue=stok_gdf[((stok_gdf["tahsue"]=="")&(stok_gdf["ue"]==1))]
#stok_gdf.loc[((stok_gdf["tahsue"]=="")&(stok_gdf["ue"]==1)), 'tahsue']=stok_gdf['tahs']
#naisohnetahs=checknohs['nais'].unique().tolist()
#naisohnetahsue=checknohsue['nais'].unique().tolist()
#stok_gdf.loc[((stok_gdf['ue']==0)&(stok_gdf['nais1']=='')&(stok_gdf['nais']!='')),'nais1']=stok_gdf['nais']
#
##fill nais2
#checknais2=stok_gdf[((stok_gdf["nais2"]=="")&(stok_gdf["ue"]==1))]
#for index, row in stok_gdf.iterrows():
#    if row['nais2']=='' and row['ue']==1:
#        naislist=row['nais'].replace('(', ' ').replace(')', ' ').replace('/',' ').replace('  ',' ').strip().split()
#        stok_gdf.loc[index,'nais2']=naislist[1]
#
stok_gdf.loc[((stok_gdf['tahsue']!='')&(stok_gdf['ue']==1)), 'tahsue'] = ''
stok_gdf.loc[stok_gdf['ue']==0, 'tahsue'] = ''
stok_gdf['tahsue'].unique().tolist()
print("write output")
stok_gdf.columns
#stok_gdf['BedingungHangneigung'].unique().tolist()
#stok_gdf['BedingungRegion'].unique().tolist()
stok_gdf.to_file(myworkspace+"/NE/stok_gdf_attributed.gpkg")
#stok_gdf=gpd.read_file(myworkspace+"/NE/stok_gdf_attributed.gpkg")
print("done")




#Export for tree-app
print('Export for Tree-App')
stok_gdf.columns
#stok_gdf.loc[((stok_gdf['ue']==1)&(stok_gdf['tahsue']=='')&(stok_gdf['tahs']!='')),'tahsue']=stok_gdf['tahs']
treeapp=stok_gdf[['code_neuch', 'associatio', 'nais', 'nais1', 'nais2', 'mo', 'ue','tahs', 'tahsue','geometry']]
treeapp.to_file(myworkspace+"/NE/NE_treeapp.gpkg", layer='NE_treeapp', driver="GPKG")
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



