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
naiseinheitenunique=pd.read_excel(codespace+"/LU_nais_einheiten_unique_mf_Juli 2025.xlsx", dtype="str", engine='openpyxl')
len(naiseinheitenunique)
naiseinheitenunique.dtypes
naiseinheitenunique["nais2"].unique().tolist()
naiseinheitenunique.loc[naiseinheitenunique['nais1'].isnull()==True, 'nais1']=''
naiseinheitenunique.loc[naiseinheitenunique['nais2'].isnull()==True, 'nais2']=''
naiseinheitenunique.loc[naiseinheitenunique['hs'].isnull()==True, 'hs']=''
naiseinheitenunique.loc[naiseinheitenunique['PLOTTXT'].isnull()==True, 'PLOTTXT']=''
naiseinheitenunique.loc[naiseinheitenunique['STO1_TXT'].isnull()==True, 'STO1_TXT']=''
naiseinheitenunique.loc[naiseinheitenunique['STO2_TXT'].isnull()==True, 'STO2_TXT']=''

#read the rasters
#reference tif raster
print("read reference raster")
referenceraster=myworkspace+"/LU/LU_dem10m.tif"
referencetifraster=gdal.Open(referenceraster)
referencetifrasterband=referencetifraster.GetRasterBand(1)
referencerasterProjection=referencetifraster.GetProjection()
ncols=referencetifrasterband.XSize
nrows=referencetifrasterband.YSize
indatatype=referencetifrasterband.DataType
#indatatypeint=gdal.Open(myworkspace+"/regionen.tif").GetRasterBand(1).DataType
#dhmarr=convert_tif_to_array("D:/CCW20/GIS/dhm25.tif")
NODATA_value=-9999

sloperaster=myworkspace+"/LU/LU_slopeprz.tif"
radiationraster=myworkspace+"/LU/LU_globradyyw.tif"
hoehenstufenraster=myworkspace+"/LU/LU_vegetationshoehenstufen1975.tif"
#hsheute=gpd.read_file(myworkspace+"/Ar/vegetationshoehenstufen19611990clipSGAIAR.shp")

#read shapefile
stok_gdf=gpd.read_file(myworkspace+'/geops_treeapp/forest_types_lu/forest_types_lu.shp')
taheute=gpd.read_file(myworkspace+"/Tannenareale.shp")
storeg=gpd.read_file(myworkspace+"/Waldstandortsregionen.shp")
#stok_gdf=gpd.read_file(projectspace+"/GIS/stok_gdf_attributed.shp")
stok_gdf.columns
stok_gdf.rename(columns={'NAIS1':'nais1alt'}, inplace=True)
stok_gdf.rename(columns={'NAIS2':'nais2alt'}, inplace=True)
stok_gdf.rename(columns={'HS':'hsalt'}, inplace=True)
stok_gdf.loc[stok_gdf['PLOTTXT'].isnull()==True, 'PLOTTXT']=''
stok_gdf.loc[stok_gdf['STO1_TXT'].isnull()==True, 'STO1_TXT']=''
stok_gdf.loc[stok_gdf['STO2_TXT'].isnull()==True, 'STO2_TXT']=''
stok_gdf.dtypes
stok_gdf=stok_gdf.astype({'PLOTTXT': 'str','STO1_TXT': 'str', 'STO2_TXT': 'str'})
len(stok_gdf)
stok_gdf.crs
taheute.crs
storeg.crs
stok_gdf.set_crs(epsg=2056, inplace=True)
#stok_gdf.plot()
stok_gdf.columns
#change column names (sg___ are the St Gallen units)
#stok_gdf.rename(columns={"WSTEinheit": "kanteinh", "naisueberg": "sgue", "naismosaic":"sgmosaic"}, inplace=True)
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
#stok_gdf=stok_gdf[['WSTEinheit', 'nais1', 'naisue','naismosaic', 'hs1', 'hsue', 'hsmosaic', 'geometry']]
stok_gdf['joinid']=stok_gdf.index

#Standortregionen
storeg.crs
storeg.columns
stok_gdf.columns
stok_gdf.drop(columns='index_right', inplace=True)
#taheute.plot()
storeg.rename(columns={"Subcode": "storeg"}, inplace=True)
storeg.drop(columns=['Region_de', 'Region_fr', 'Region_it', 'Region_en', 'Code', 'Code_Bu', 'Code_Fi', 'Shape_Leng', 'Shape_Area'], inplace=True)
#overlay spatial join
stok_gdfstoreg=gpd.sjoin(stok_gdf,storeg, how='left', op="intersects")
len(stok_gdfstoreg)
stok_gdfstoreggrouped=stok_gdfstoreg[["joinid","storeg"]].groupby(by=["joinid"]).min()
##stok_gdftagrouped["joinid"]=stok_gdftagrouped.index
len(stok_gdfstoreggrouped)
stok_gdfstoreggrouped.columns
#stok_gdf.columns
stok_gdf=stok_gdf.merge(stok_gdfstoreggrouped, on='joinid', how='left')#left_on='joinid', right_on='joinid',
len(stok_gdf)


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
stok_gdf.to_file(myworkspace+"/LU/stok_gdf_attributed_temp.gpkg")
#del zonstaths

#uebersetzung von Kantonseinheit in NAIS
#stok_gdf=gpd.read_file(myworkspace+"/LU/stok_gdf_attributed.gpkg")
#naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['NaiS'].isnull() == False]
len(naiseinheitenunique)

stok_gdf.columns
stok_gdf['nais']=''
stok_gdf['nais1']=''
stok_gdf['nais2']=''
stok_gdf['mo']=0
stok_gdf['ue']=0
stok_gdf['hs']=''
stok_gdf['tahs']=''
stok_gdf['tahsue']=''
naiseinheitenunique.columns
for index, row in naiseinheitenunique.iterrows():
    PLOTTXT=row["PLOTTXT"]
    STO1_TXT=row["STO1_TXT"]
    STO2_TXT=row["STO2_TXT"]
    hs =row['hs']
    nais1 = row["nais1"]
    nais2 = row["nais2"]
    hslist=row['hs'].replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()
    stok_gdf.loc[((stok_gdf["PLOTTXT"] == PLOTTXT)&(stok_gdf["STO1_TXT"] == STO1_TXT)&(stok_gdf["STO2_TXT"] == STO2_TXT)), "nais1"] = nais1
    stok_gdf.loc[((stok_gdf["PLOTTXT"] == PLOTTXT)&(stok_gdf["STO1_TXT"] == STO1_TXT)&(stok_gdf["STO2_TXT"] == STO2_TXT)), "nais2"] = nais2
    stok_gdf.loc[((stok_gdf["PLOTTXT"] == PLOTTXT)&(stok_gdf["STO1_TXT"] == STO1_TXT)&(stok_gdf["STO2_TXT"] == STO2_TXT)), "hs"] =row['hs']
    if row['nais2']=='':
        stok_gdf.loc[((stok_gdf["PLOTTXT"] == PLOTTXT)&(stok_gdf["STO1_TXT"] == STO1_TXT)&(stok_gdf["STO2_TXT"] == STO2_TXT)), "nais"] = row['nais1']
    else:
        stok_gdf.loc[((stok_gdf["PLOTTXT"] == PLOTTXT)&(stok_gdf["STO1_TXT"] == STO1_TXT)&(stok_gdf["STO2_TXT"] == STO2_TXT)), "nais"] = row['nais1'] + '(' + row['nais2']+')'
    if row['nais2']!='':
        stok_gdf.loc[((stok_gdf["PLOTTXT"] == PLOTTXT)&(stok_gdf["STO1_TXT"] == STO1_TXT)&(stok_gdf["STO2_TXT"] == STO2_TXT)), "ue"] = 1
    if len(hslist)==1:
        stok_gdf.loc[((stok_gdf["PLOTTXT"] == PLOTTXT)&(stok_gdf["STO1_TXT"] == STO1_TXT)&(stok_gdf["STO2_TXT"] == STO2_TXT)), "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
        stok_gdf.loc[((stok_gdf["PLOTTXT"] == PLOTTXT)&(stok_gdf["STO1_TXT"] == STO1_TXT)&(stok_gdf["STO2_TXT"] == STO2_TXT)), "nais"] = row['nais1']#.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[0]
    else:
        if "(" in row['hs']:
            stok_gdf.loc[((stok_gdf["PLOTTXT"] == PLOTTXT)&(stok_gdf["STO1_TXT"] == STO1_TXT)&(stok_gdf["STO2_TXT"] == STO2_TXT)), "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
            stok_gdf.loc[((stok_gdf["PLOTTXT"] == PLOTTXT)&(stok_gdf["STO1_TXT"] == STO1_TXT)&(stok_gdf["STO2_TXT"] == STO2_TXT)), "tahsue"] = hoehenstufendictabkuerzungen[hslist[1]]
        else:
            for index2, row2 in stok_gdf[((stok_gdf["PLOTTXT"] == PLOTTXT)&(stok_gdf["STO1_TXT"] == STO1_TXT)&(stok_gdf["STO2_TXT"] == STO2_TXT))].iterrows():
                if row2['hs1975']>0:
                    hsmod=hsmoddictkurz[int(row2['hs1975'])]
                else:
                    hsmod = 'nan'
                if hsmod in row2['hs'].strip().split():
                    stok_gdf.loc[index2,'tahs']=hoehenstufendictabkuerzungen[hsmod]
                else:
                    test=hoehenstufendictabkuerzungen[row2['hs'].replace('(',' ').replace(')','').strip().split()[0]]
                    if len(row2['hs'].replace('(',' ').replace(')','').strip().split()) >1 and test == 'collin':
                        stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[row2['hs'].replace('(',' ').replace(')','').strip().split()[-1]]
                    else:
                        stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[row2['hs'].replace('(',' ').replace(')','').strip().split()[-1]]
stok_gdf.loc[((stok_gdf['tahsue']=='')&(stok_gdf['ue']==1)), 'tahsue']=stok_gdf['tahs']
stok_gdf.columns


#check empty values
stok_gdf["tahs"].unique().tolist()
stok_gdf["tahsue"].unique().tolist()
checknohs=stok_gdf[stok_gdf["tahs"]==""][["PLOTTXT","nais",'hs1975']]
checknohs['PLOTTXT'].unique().tolist()
stok_gdf.loc[((stok_gdf['PLOTTXT']=='16/N/18')), 'nais1']='16'
stok_gdf.loc[((stok_gdf['PLOTTXT']=='16/N/18')), 'nais2']='18'
stok_gdf.loc[((stok_gdf['PLOTTXT']=='16/N/18')), 'nais']='16(18)'
stok_gdf.loc[((stok_gdf['PLOTTXT']=='16/N/18')), 'tahs']='untermontan'
stok_gdf.loc[((stok_gdf['PLOTTXT']=='16/N/18')), 'tahsue']='obermontan'
stok_gdf.loc[((stok_gdf['PLOTTXT']=='49')), 'nais1']='49'
stok_gdf.loc[((stok_gdf['PLOTTXT']=='49')), 'nais']='49'
stok_gdf.loc[((stok_gdf['PLOTTXT']=='49')), 'tahs']='obermontan'

#fill hoehenstufe for empty values
for index, row in stok_gdf.iterrows():
    if row["tahs"]=='' and row['hs1975']>0:
        stok_gdf.loc[index, "tahs"] = hoehenstufendictabkuerzungen[hsmoddictkurz[int(row['hs1975'])]]
stok_gdf.loc[((stok_gdf['ue']==1)&(stok_gdf['tahsue']=='')), 'tahsue']=stok_gdf['tahs']
#Gebüschwald
#stok_gdf.loc[((stok_gdf['nais']=='AV')&(stok_gdf['hs1975']==-1)), 'tahs'] = 'subalpin'

stok_gdf.columns
#stok_gdf=stok_gdf[['joinid', 'PLOTTXT', 'taheute', 'storeg', 'meanslopeprc','slpprzrec', 'rad', 'radiation', 'hs1975', 'nais', 'nais1', 'nais2','mo', 'ue', 'hs', 'tahs', 'tahsue','geometry']]

##fill tahsue
#for index, row in stok_gdf.iterrows():
#    if '(' in row['nais'] and row['ue']==1 and row['tahsue']=='':
#        hslist = row['hs'].replace('/', ' ').replace('(', ' ').replace(')', '').strip().split()
#        if len(hslist)==1:
#            stok_gdf.loc[index, 'tahsue']=row['tahs']

##check empty values
#stok_gdf["tahs"].unique().tolist()
#stok_gdf["tahsue"].unique().tolist()
#checknohs=stok_gdf[stok_gdf["tahs"]==""]#[["wg_haupt","wg_zusatz","nais",'hs1975']]
#checknohsue=stok_gdf[((stok_gdf["tahsue"]=="")&(stok_gdf["ue"]==1))]
#stok_gdf.loc[((stok_gdf["tahsue"]=="")&(stok_gdf["ue"]==1)), 'tahsue']=stok_gdf['tahs']
#naisohnetahs=checknohs['nais'].unique().tolist()
#naisohnetahsue=checknohsue['nais'].unique().tolist()
#stok_gdf.loc[((stok_gdf['ue']==0)&(stok_gdf['nais1']=='')&(stok_gdf['nais']!='')),'nais1']=stok_gdf['nais']

##Korrekturen
#stok_gdf.columns
##test=stok_gdf[stok_gdf['nais']=='32V']
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
stok_gdf=stok_gdf[['joinid', 'PLOTTXT', 'taheute', 'storeg', 'meanslopeprc','slpprzrec', 'rad', 'radiation', 'hs1975', 'nais', 'nais1', 'nais2','mo', 'ue', 'hs', 'tahs', 'tahsue','geometry']]
stok_gdf.to_file(myworkspace+"/LU/stok_gdf_attributed.gpkg")
#stok_gdf=gpd.read_file(myworkspace+"/LU/stok_gdf_attributed.gpkg")
print("done")


#Export for tree-app
print('Export for Tree-App')
stok_gdf.columns
#stok_gdf.loc[((stok_gdf['ue']==1)&(stok_gdf['tahsue']=='')&(stok_gdf['tahs']!='')),'tahsue']=stok_gdf['tahs']
treeapp=stok_gdf[['PLOTTXT','nais', 'nais1', 'nais2', 'mo', 'ue','tahs', 'tahsue','geometry']]
treeapp.to_file(myworkspace+"/LU/LU_treeapp.gpkg", layer='LU_treeapp', driver="GPKG")
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



