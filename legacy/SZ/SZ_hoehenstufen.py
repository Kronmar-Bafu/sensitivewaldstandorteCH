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
from scipy.spatial.distance import sokalsneath

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
hoehenstufendict={"hyperinsubrisch":"hyp","mediterran":"med","collin mit Buche":"co","collin":"co","submontan":"sm","untermontan":"um","obermontan":"om","unter- & obermontan":"umom","unter-/obermontan":"umom","hochmontan":"hm","subalpin":"sa","obersubalpin":"osa"}
hoehenstufendictabkuerzungen={"co":"collin","sm":"submontan","um":"untermontan","om":"obermontan","hm":"hochmontan","sa":"subalpin","osa":"obersubalpin"}
hsmoddict={0:"mediterran",1:"hyperinsubrisch",2:"collin",3:"collin",4:"submontan",5:"untermontan",6:"obermontan",7:"unter- & obermontan",8:"hochmontan",9:"subalpin",10:"obersubalpin"}
hsmoddictkurz={0:"med",1:"hyp",2:"co", 3:"co",4:"sm",5:"um",6:"om",7:"umom",8:"hm",9:"sa",10:"osa"}
hoehenstufenlist=["collin","submontan","untermontan","obermontan","hochmontan","subalpin","obersubalpin"]

#read excel files
naiseinheitenunique=pd.read_excel(codespace+"/SZ_nais_einheiten_unique_bh_20241128_mf_bh_mfJuli 2025.xlsx", sheet_name='Sheet', dtype="str", engine='openpyxl')
naiseinheitenunique.columns
naiseinheitenunique.dtypes
len(naiseinheitenunique)
naiseinheitenunique=naiseinheitenunique[['SZ Einheit', 'NaiS_LFI','hs_ohne_co', 'hs_inkl_co','Bedingung_Hoehenstufe', 'nais', 'nais1', 'nais2','hs', 'Bemerkung Monika', 'Bemerkung BH']]
naiseinheitenunique.loc[naiseinheitenunique['Bedingung_Hoehenstufe'].isnull()==True, 'Bedingung_Hoehenstufe']=''
naiseinheitenunique.loc[naiseinheitenunique['nais2'].isnull()==True, 'nais2']=''
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['Bedingung_Hoehenstufe']=='']

#naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['hs']!='nan']
#read the rasters
#reference tif raster
print("read reference raster")
referenceraster=myworkspace+"/SZ/SZ_dem10m.tif"
referencetifraster=gdal.Open(referenceraster)
referencetifrasterband=referencetifraster.GetRasterBand(1)
referencerasterProjection=referencetifraster.GetProjection()
ncols=referencetifrasterband.XSize
nrows=referencetifrasterband.YSize
indatatype=referencetifrasterband.DataType
#indatatypeint=gdal.Open(myworkspace+"/regionen.tif").GetRasterBand(1).DataType
#dhmarr=convert_tif_to_array("D:/CCW20/GIS/dhm25.tif")
NODATA_value=-9999

sloperaster=myworkspace+"/SZ/SZ_slopeprz.tif"
radiationraster=myworkspace+"/SZ/SZ_globradyyw_lv95.tif"
hoehenstufenraster=myworkspace+"/SZ/SZ_vegetationshoehenstufen1975.tif"


#read shapefile
stok_gdf=gpd.read_file(myworkspace+'/SZ/SZ_standortstypen.gpkg', layer='SZ_standortstypen')
stok_gdf['joinid']=stok_gdf.index
taheute=gpd.read_file(myworkspace+"/Tannenareale2025.gpkg")
storeg=gpd.read_file(myworkspace+"/Waldstandortregionen_2024_TI4ab_Final_GR.gpkg", layer='waldstandortregionen_2024_ti4ab_final')
entwaesserungen=gpd.read_file(myworkspace+"/SZ/"+"Drainage_NGK.shp")
entwaesserungen=entwaesserungen[['drainage','geometry']]
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
taheute.drop(columns=['id', 'Region_de', 'Region_fr', 'Region_it', 'Region_en', 'Code','Subcode', 'Code_Bu', 'Code_Fi', 'Flaeche', ], inplace=True)
#overlay spatial join
#stok_gdf=gpd.sjoin(stok_gdf,taheute, how='left', op="intersects")
stok_gdf=gpd.overlay(stok_gdf,taheute, how='intersection')
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


#Standortregionen
storeg.crs
storeg.columns
#taheute.plot()
storeg.rename(columns={"Subcode": "storeg"}, inplace=True)
storeg.drop(columns=[ 'id', 'Region_de', 'Region_fr', 'Region_it', 'Region_en', 'Code','Code_Bu', 'Code_Fi', 'Flaeche'], inplace=True)
#overlay spatial join
stok_gdf.columns
if 'index_right' in stok_gdf.columns.tolist():
    stok_gdf.drop(columns=[ 'index_right'], inplace=True)
stok_gdfstoreg=stok_gdf.sjoin(storeg, how='left', op="intersects")
len(stok_gdfstoreg)
stok_gdfstoreggrouped=stok_gdfstoreg[["joinid","storeg"]].groupby(by=["joinid"]).min()
##stok_gdftagrouped["joinid"]=stok_gdftagrouped.index
len(stok_gdfstoreggrouped)
stok_gdfstoreggrouped.columns
stok_gdf=stok_gdf.merge(stok_gdfstoreggrouped, on='joinid', how='left')#left_on='joinid', right_on='joinid',
len(stok_gdf)


#attribute shapefile
#mean slope in percent
stok_gdf["meanslopeprc"]=0
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

winsound.Beep(frequency, duration)
stok_gdf.columns
stok_gdf.to_file(myworkspace+"/SZ/stok_gdf_attributed_temp.gpkg")
#stok_gdf=gpd.read_file(myworkspace+"/SZ/stok_gdf_attributed_temp.gpkg")
checknohs=stok_gdf[stok_gdf['hs1975'].isnull()==True]
stok_gdf.loc[stok_gdf['hs1975'].isnull()==True, 'hs1975']=-1
stok_gdf.loc[stok_gdf['rad'].isnull()==True, 'rad']=np.mean(stok_gdf['rad'])
stok_gdf.loc[stok_gdf['meanslopeprc'].isnull()==True, 'meanslopeprc']=np.mean(stok_gdf['meanslopeprc'])
stok_gdf.loc[stok_gdf["meanslopeprc"]>=70.0,"slpprzrec"]=4
stok_gdf.loc[((stok_gdf["meanslopeprc"]>=60.0)&(stok_gdf["meanslopeprc"]<70.0)),"slpprzrec"]=3
stok_gdf.loc[((stok_gdf["meanslopeprc"]>=20.0)&(stok_gdf["meanslopeprc"]<60.0)),"slpprzrec"]=2
stok_gdf.loc[stok_gdf["meanslopeprc"]<20.0,"slpprzrec"]=1
len(stok_gdf)
stok_gdf=stok_gdf[stok_gdf['SZ Einheit']!='']

#Entwaesserungen
#overlay
print('overlay Entwaesserungen')
stok_gdf=stok_gdf.overlay(entwaesserungen, how='union', keep_geom_type=True)
stok_gdf.columns
#wo 49 im Entwässerungspolygon modelliert wurde, daraus ein 49(50) bei HM oder ein 49(20) bei OM machen.
stok_gdf.loc[((stok_gdf['NaiS_LFI']=='49')&(stok_gdf['drainage']==1)&(stok_gdf['hs1975']==8)),'NaiS_LFI']='49(50)'
stok_gdf.loc[((stok_gdf['NaiS_LFI']=='49')&(stok_gdf['drainage']==1)&(stok_gdf['hs1975']==6)),'NaiS_LFI']='49(20)'
stok_gdf.loc[((stok_gdf['SZ Einheit']=='49')&(stok_gdf['drainage']==1)&(stok_gdf['hs1975']==8)),'SZ Einheit']='49(50)'
stok_gdf.loc[((stok_gdf['SZ Einheit']=='49')&(stok_gdf['drainage']==1)&(stok_gdf['hs1975']==6)),'SZ Einheit']='49(20)'
len(stok_gdf)
stok_gdf=stok_gdf[stok_gdf['SZ Einheit']!='']
stok_gdf=stok_gdf[stok_gdf['SZ Einheit'].isnull()==False]
stok_gdf.loc[stok_gdf['rad'].isnull()==True, 'rad']=np.mean(stok_gdf[stok_gdf['rad'].isnull()==False]['rad'])
stok_gdf.to_file(myworkspace+"/SZ/stok_gdf_attributed_temp_entw.gpkg")


#stok_gdf=gpd.read_file(myworkspace+"/SZ/stok_gdf_attributed_temp_entw.gpkg")
checkdrainage=stok_gdf[stok_gdf['drainage']==1]


#uebersetzung von Kantonseinheit in NAIS
#naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['NaiS'].isnull() == False]
stok_gdf.columns
len(naiseinheitenunique)
stok_gdf['nais']=''
stok_gdf['nais1']=''
stok_gdf['nais2']=''
stok_gdf['mo']=0
stok_gdf['ue']=0
stok_gdf['hs']=''
stok_gdf['hsue']=''
stok_gdf['tahs']=''
stok_gdf['tahsue']=''

#transform null values
stok_gdf.loc[stok_gdf['nais'].isnull()==True,'nais']=''
stok_gdf.loc[stok_gdf['SZ Einheit'].isnull()==True,'SZ Einheit']=''
naiseinheitenunique.loc[naiseinheitenunique['SZ Einheit'].isnull()==True,'SZ Einheit']=''
naiseinheitenunique.loc[naiseinheitenunique['hs'].isnull()==True,'hs']=''
naiseinheitenunique.loc[naiseinheitenunique['nais2'].isnull()==True,'nais2']=''

#create nais 1 and nais2
#stok_gdf['nais1'] = stok_gdf['nais'].str.split('(').str[0].str.strip()
#stok_gdf['nais2']= stok_gdf['nais'].str.split('(').str[1].str.split(')').str[0].str.strip()
#stok_gdf.loc[stok_gdf['nais2'].isnull()==True, 'nais2']= ''
#stok_gdf.loc[stok_gdf['nais2']!='', 'ue']= 1
#check= stok_gdf[stok_gdf['ue']==1]

print('iterate for attributing tahs and tahsue')
for index, row in naiseinheitenunique.iterrows():
    kantonseinheit=row['SZ Einheit']
    naislfi=row['NaiS_LFI']
    hs=row["hs"]
    hslist=row['hs'].replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()
    nais=row['nais']
    nais1=row['nais1']
    nais2=row['nais2']
    #Hoehenstufenzuweisung
    stok_gdf.loc[((stok_gdf["SZ Einheit"] == kantonseinheit)&(stok_gdf["NaiS_LFI"] == naislfi)), "hs"] = hs
    stok_gdf.loc[((stok_gdf["SZ Einheit"] == kantonseinheit)&(stok_gdf["NaiS_LFI"] == naislfi)), "nais"] = nais
    stok_gdf.loc[((stok_gdf["SZ Einheit"] == kantonseinheit) & (stok_gdf["NaiS_LFI"] == naislfi)), "nais1"] = nais1
    stok_gdf.loc[((stok_gdf["SZ Einheit"] == kantonseinheit) & (stok_gdf["NaiS_LFI"] == naislfi)), "nais2"] = nais2
    if nais2!='':
        stok_gdf.loc[((stok_gdf["SZ Einheit"] == kantonseinheit) & (stok_gdf["NaiS_LFI"] == naislfi)), "ue"] = 1
    #Hohenstufenzuweisung
    if len(hslist)==1:
        stok_gdf.loc[((stok_gdf["SZ Einheit"] == kantonseinheit)&(stok_gdf["NaiS_LFI"] == naislfi)), "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
    else:
        for index2, row2 in stok_gdf[((stok_gdf["SZ Einheit"] == kantonseinheit)&(stok_gdf["NaiS_LFI"] == naislfi))].iterrows():
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


#check=stok_gdf[stok_gdf['SZ Einheit']=='49F']
winsound.Beep(frequency, duration)

#correct multiple entries
#13
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '13')&(stok_gdf["hs1975"] <= 4)), "tahs"] = 'submontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '13')&(stok_gdf["hs1975"] == 5)), "tahs"] = 'untermontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '13')&(stok_gdf["hs1975"] >= 6)), "tahs"] = 'obermontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '13')&(stok_gdf["hs1975"].isnull()==True)), "tahs"] = 'obermontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '13')&(stok_gdf["tahs"] == 'obermontan')), "nais"] = '13h'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '13')&(stok_gdf["tahs"] == 'untermontan')), "nais"] = '13a'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '13')&(stok_gdf["tahs"] == 'submontan')), "nais"] = '13a'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '13')&(stok_gdf["tahs"] == 'obermontan')), "nais1"] = '13h'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '13')&(stok_gdf["tahs"] == 'untermontan')), "nais1"] = '13a'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '13')&(stok_gdf["tahs"] == 'submontan')), "nais1"] = '13a'
#53
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53')&(stok_gdf["hs1975"] <= 6)), "tahs"] = 'obermontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53')&(stok_gdf["hs1975"] == 8)), "tahs"] = 'hochmontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53')&(stok_gdf["hs1975"] >= 9)), "tahs"] = 'subalpin'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53')&(stok_gdf["tahs"] == 'obermontan')), "nais"] = '53Ta'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53')&(stok_gdf["tahs"] == 'hochmontan')), "nais"] = '53Ta'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53')&(stok_gdf["tahs"] == 'subalpin')), "nais"] = '53'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53')&(stok_gdf["tahs"] == 'obermontan')), "nais1"] = '53Ta'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53')&(stok_gdf["tahs"] == 'hochmontan')), "nais1"] = '53Ta'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53')&(stok_gdf["tahs"] == 'subalpin')), "nais1"] = '53'
#27h
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27h')&(stok_gdf["hs1975"] <= 6)), "tahs"] = 'obermontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27h')&(stok_gdf["hs1975"] >= 8)), "tahs"] = 'hochmontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27h')&(stok_gdf["hs1975"].isnull()==True)), "tahs"] = 'hochmontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27h')&(stok_gdf["tahs"] == 'obermontan')), "nais"] = '27h'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27h')&(stok_gdf["tahs"] == 'hochmontan')), "nais"] = '27*'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27h')&(stok_gdf["tahs"] == 'obermontan')), "nais1"] = '27h'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27h')&(stok_gdf["tahs"] == 'hochmontan')), "nais1"] = '27*'
#27w
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27w')&(stok_gdf["hs1975"] <= 6)), "tahs"] = 'obermontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27w')&(stok_gdf["hs1975"] >= 8)), "tahs"] = 'hochmontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27w')&(stok_gdf["tahs"] == 'obermontan')), "nais"] = '27h(26w)'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27w')&(stok_gdf["tahs"] == 'obermontan')), "nais1"] = '27h'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27w')&(stok_gdf["tahs"] == 'obermontan')), "nais2"] = '26w'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27w')&(stok_gdf["tahs"] == 'hochmontan')), "nais"] = '27*(60*Ta)'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27w')&(stok_gdf["tahs"] == 'hochmontan')), "nais1"] = '27h'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27w')&(stok_gdf["tahs"] == 'hochmontan')), "nais2"] = '60*Ta'
#32V
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["NaiS_LFI"] == '32C')&(stok_gdf["hs1975"] <= 4)), "tahs"] = 'submontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["NaiS_LFI"] == '32C')&(stok_gdf["hs1975"] >= 5)), "tahs"] = 'untermontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["NaiS_LFI"] == '32V')&(stok_gdf["hs1975"] <= 6)), "tahs"] = 'obermontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["NaiS_LFI"] == '32V')&(stok_gdf["hs1975"] >= 8)), "tahs"] = 'hochmontan'
#stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["NaiS_LFI"] == '32V')&(stok_gdf["hs1975"] >= 9)), "tahs"] = 'subalpin'
#stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["NaiS_LFI"] == '32V')&(stok_gdf["hs1975"].isnull()==True)), "tahs"] = 'subalpin'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["tahs"] == 'submontan')), "nais"] = '32C'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["tahs"] == 'submontan')), "nais1"] = '32C'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["tahs"] == 'untermontan')), "nais"] = '32C'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["tahs"] == 'untermontan')), "nais1"] = '32C'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["tahs"] == 'obermontan')), "nais"] = '32V'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["tahs"] == 'obermontan')), "nais1"] = '32V'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["tahs"] == 'hochmontan')), "nais"] = '32V'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["tahs"] == 'hochmontan')), "nais1"] = '32V'
#stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["tahs"] == 'subalpin')), "nais"] = '32V'
#stok_gdf.loc[((stok_gdf["SZ Einheit"] == '32V')&(stok_gdf["tahs"] == 'subalpin')), "nais1"] = '32V'
#53Bl
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53Bl')&(stok_gdf["hs1975"] <= 6)), "tahs"] = 'obermontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53Bl')&(stok_gdf["hs1975"] == 8)), "tahs"] = 'hochmontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53Bl')&(stok_gdf["hs1975"] >= 9)), "tahs"] = 'subalpin'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53Bl')&(stok_gdf["hs1975"].isnull()==True)), "tahs"] = 'subalpin'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53Bl')&(stok_gdf["tahs"] == 'obermontan')), "nais"] = '53Ta(48)'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53Bl')&(stok_gdf["tahs"] == 'obermontan')), "nais1"] = '53Ta'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53Bl')&(stok_gdf["tahs"] == 'obermontan')), "nais2"] = '48'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53Bl')&(stok_gdf["tahs"] == 'hochmontan')), "nais"] = '53Ta(48)'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53Bl')&(stok_gdf["tahs"] == 'hochmontan')), "nais1"] = '53Ta'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53Bl')&(stok_gdf["tahs"] == 'hochmontan')), "nais2"] = '48'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53Bl')&(stok_gdf["tahs"] == 'subalpin')), "nais"] = '53(57Bl)'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53Bl')&(stok_gdf["tahs"] == 'subalpin')), "nais1"] = '53'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53Bl')&(stok_gdf["tahs"] == 'subalpin')), "nais2"] = '57Bl'
#53w
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53w')&(stok_gdf["hs1975"] <= 8)), "tahs"] = 'hochmontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53w')&(stok_gdf["hs1975"] >= 9)), "tahs"] = 'subalpin'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53w')&(stok_gdf["tahs"] == 'hochmontan')), "nais"] = '53Ta(60*Ta)'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53w')&(stok_gdf["tahs"] == 'hochmontan')), "nais1"] = '53Ta'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53w')&(stok_gdf["tahs"] == 'hochmontan')), "nais2"] = '60*Ta'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53w')&(stok_gdf["tahs"] == 'subalpin')), "nais"] = '53(60*)'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53w')&(stok_gdf["tahs"] == 'subalpin')), "nais1"] = '53'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '53w')&(stok_gdf["tahs"] == 'subalpin')), "nais2"] = '60*'
#60*
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '60*')&(stok_gdf["hs1975"] <= 6)), "tahs"] = 'obermontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '60*')&(stok_gdf["hs1975"] == 8)), "tahs"] = 'hochmontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '60*')&(stok_gdf["hs1975"] >= 9)), "tahs"] = 'subalpin'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '60*')&(stok_gdf["tahs"] == 'obermontan')), "nais"] = '60*Ta'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '60*')&(stok_gdf["tahs"] == 'obermontan')), "nais1"] = '60*Ta'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '60*')&(stok_gdf["tahs"] == 'hochmontan')), "nais"] = '60*Ta'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '60*')&(stok_gdf["tahs"] == 'hochmontan')), "nais1"] = '60*Ta'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '60*')&(stok_gdf["tahs"] == 'subalpin')), "nais"] = '60*'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '60*')&(stok_gdf["tahs"] == 'subalpin')), "nais1"] = '60*'
#27
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27')&(stok_gdf["hs1975"] <= 4)), "tahs"] = 'submontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27')&(stok_gdf["hs1975"] >= 5)), "tahs"] = 'untermontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '27')&(stok_gdf["hs1975"].isnull()==True)), "tahs"] = 'untermontan'
stok_gdf.loc[(stok_gdf["SZ Einheit"] == '27'), "nais"] = '27f'
stok_gdf.loc[(stok_gdf["SZ Einheit"] == '27'), "nais1"] = '27f'
#49(20)
stok_gdf.loc[((stok_gdf["NaiS_LFI"] == '49(20)')), "tahs"] = 'obermontan'
stok_gdf.loc[((stok_gdf["NaiS_LFI"] == '49(20)')), "tahsue"] = 'obermontan'
stok_gdf.loc[((stok_gdf["NaiS_LFI"] == '49(20)')), "nais"] = '49(20)'
stok_gdf.loc[((stok_gdf["NaiS_LFI"] == '49(20)')), "nais1"] = '49'
stok_gdf.loc[((stok_gdf["NaiS_LFI"] == '49(20)')), "nais2"] = '20'
#49(50)
stok_gdf.loc[((stok_gdf["NaiS_LFI"] == '49(50)')), "tahs"] = 'hochmontan'
stok_gdf.loc[((stok_gdf["NaiS_LFI"] == '49(50)')), "tahsue"] = 'hochmontan'
stok_gdf.loc[((stok_gdf["NaiS_LFI"] == '49(50)')), "nais"] = '49(50)'
stok_gdf.loc[((stok_gdf["NaiS_LFI"] == '49(50)')), "nais1"] = '49'
stok_gdf.loc[((stok_gdf["NaiS_LFI"] == '49(50)')), "nais2"] = '50'
#73
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '73')&(stok_gdf["hs1975"] <= 8)), "tahs"] = 'hochmontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '73')&(stok_gdf["hs1975"] >= 9)), "tahs"] = 'subalpin'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '73')), "nais"] = '69'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '73')), "nais1"] = '69'

#30
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '30')&(stok_gdf["hs1975"] <= 4)), "tahs"] = 'submontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '30')&(stok_gdf["hs1975"] >= 5)), "tahs"] = 'untermontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '30')&(stok_gdf["hs1975"].isnull()==True)), "tahs"] = 'untermontan'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '30')), "nais1"] = '30'
stok_gdf.loc[((stok_gdf["SZ Einheit"] == '30')), "nais"] = '30'



#checknohs=stok_gdf[((stok_gdf["tahs"]==""))]
#checknohs=stok_gdf[((stok_gdf["SZ Einheit"]=="49(50)"))]
stok_gdf.columns

#fill hs of ue
stok_gdf.loc[((stok_gdf["nais2"] != '')), "ue"] = 1
stok_gdf.loc[((stok_gdf["nais2"] != '') & (stok_gdf["ue"] == 1)&(stok_gdf["tahsue"] == '')), "tahsue"] = stok_gdf["tahs"]


#check empty values
stok_gdf["tahs"].unique().tolist()
stok_gdf["tahsue"].unique().tolist()
checknohs=stok_gdf[stok_gdf["tahs"]==""][['SZ Einheit','nais','nais1','nais2',"hs", 'hs1975', 'tahs','tahsue']]
print('Diese EInheiten haben keine Uebersetzung: '+str(checknohs['SZ Einheit'].unique().tolist()))
stok_gdf.loc[((stok_gdf["tahs"]=="")&(stok_gdf["SZ Einheit"]=="32V")),'tahs']='hochmontan'
len(stok_gdf)
stok_gdf=stok_gdf[stok_gdf['SZ Einheit']!='']
#korrigiere mit sheet1
fehlendeuebersetzungen=checknohs[['SZ Einheit', 'nais','nais1','nais2',"hs"]].drop_duplicates()
fehlendeuebersetzungen.to_excel(myworkspace+'/SZ/'+'fehlendeHoehenstufen.xlsx')
len(fehlendeuebersetzungen)
stok_gdfcopy=stok_gdf.copy()
print("write output")
stok_gdf.columns
#stok_gdf['BedingungHangneigung'].unique().tolist()
#stok_gdf['BedingungRegion'].unique().tolist()
#stok_gdf=stok_gdf[['g1','SZ Einheit', 'Einheit_Na', 'joinid', 'taheute', 'storeg', 'meanslopeprc','slpprzrec', 'rad', 'radiation', 'hs1975', 'nais', 'nais1','nais2', 'mo', 'ue', 'hs', 'tahs', 'tahsue', 'geometry']]
#stok_gdf=gpd.read_file(myworkspace+"/ZH/stok_gdf_attributed.gpkg")
stok_gdf=stok_gdf[['SZ Einheit','joinid', 'taheute', 'storeg', 'meanslopeprc','slpprzrec', 'rad', 'radiation', 'hs1975', 'nais', 'nais1','nais2', 'mo', 'ue', 'hs', 'tahs', 'tahsue', 'geometry']]
stok_gdf['fid']=stok_gdf.index
stok_gdf['area']=stok_gdf.geometry.area
len(stok_gdf)
stok_gdf=stok_gdf[stok_gdf['area']>0]
stok_gdf.to_file(myworkspace+"/SZ/stok_gdf_attributed.gpkg",layer='stok_gdf_attributed', driver="GPKG")
print("done")


#Export for tree-app
print('Export for Tree-App')
stok_gdf.columns
#stok_gdf.loc[((stok_gdf['ue']==1)&(stok_gdf['tahsue']=='')&(stok_gdf['tahs']!='')),'tahsue']=stok_gdf['tahs']
treeapp=stok_gdf[['SZ Einheit', 'nais','nais1', 'nais2', 'mo', 'ue','tahs', 'tahsue','geometry']]
treeapp.to_file(myworkspace+"/SZ/SZ_treeapp.gpkg", layer='SZ_treeapp', driver="GPKG")
treeapp.columns
print("done")

