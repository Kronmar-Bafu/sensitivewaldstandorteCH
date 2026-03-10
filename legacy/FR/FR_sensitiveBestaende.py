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
import warnings
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)


#input data
codeworkspace="C:/DATA/develops/sensitivewaldstandorteCH"
projectspace="D:/CCW24sensi"
climatescenarios=['rcp45','rcp85']
#climatescenario="rcp85"
#climatescenario="rcp45"
#climatescenario="rcp26"
varname='var1'
#varname='var2'

#thresholds for claissifying climate-sensitive stocks (klimasensitive Bestaende)
threshold_nicht_empfohlen_min=0
threshold_nicht_empfohlen_max=95
threshold_nicht_bedingt_min=0
threshold_nicht_bedingt_max=20
threshold_nicht_gef_min=0
threshold_nicht_gef_max=10

threshold_schwach_empfohlen_min=95
threshold_schwach_empfohlen_max=100
threshold_schwach_bedingt_min=20
threshold_schwach_bedingt_max=70
threshold_schwach_gef_min=10
threshold_schwach_gef_max=20

threshold_mittel_bedingt_min=70
threshold_mittel_bedingt_max=95
threshold_mittel_gef_min=20
threshold_mittel_gef_max=40

threshold_stark_bedingt_min=95
threshold_stark_bedingt_max=100
threshold_stark_gef_min=40

##var2
#varname='var2'
#threshold_schwach_gef_max=30
#threshold_mittel_gef_min=30
#threshold_mittel_gef_max=50
#threshold_stark_gef_min=50

#read Bestandeskarte shape
bk_gdf=gpd.read_file(projectspace+"/FR"+"/BestandeskarteFR/BestandeskarteFRv240206.shp")
bk_gdf.columns
bk_gdf['FI']=bk_gdf['EP'] #Fichte
bk_gdf['TA']=bk_gdf['SA'] #Tanne
bk_gdf['LA']=bk_gdf['ME'] #Laerche
bk_gdf['WFO']=bk_gdf['PI'] #Foehre
bk_gdf['BU']=bk_gdf['HE'] #Buche
bk_gdf['TEI']=bk_gdf['CH'] #Trauben-Eiche
bk_gdf['BAH']=bk_gdf['ER'] #Berg-Ahorn --> Feldahorn?
bk_gdf['ES']=bk_gdf['FR'] #Esche

#******************************************************************************************************
#Sensitive Bestaende
#******************************************************************************************************
treetypes=["FI", "TA", "LA", "WFO", "BU","TEI", "BAH", "ES"]
treetypesplusgeometry=treetypes.copy()
treetypesplusgeometry.append('geometry')
#sb= sensitiver Bestand
treetypes_sb=[]
for item in treetypes:
    treetypes_sb.append("sb"+item)

bk_gdf.crs
len(bk_gdf)
bk_gdf.columns
bk_gdf["bkid"]=bk_gdf.index
#bk_gdf=bk_gdf[['bkid','mischung', 'entwicklun','schlussgra','nhd_anteil', 'hdom', 'hmax', 'gru_strukt','dg_os','dg_ms', 'dg_us','geometry']]#,"TACODE","BUCODE"
bk_gdf.dtypes
len(bk_gdf)
for climatescenario in climatescenarios:
    print(climatescenario)
    rcp_baumartenempfehlungen_gdf_in=joblib.load(projectspace+"/FR/FR_"+climatescenario+"_baumartenempfehlungen.sav")
    len(rcp_baumartenempfehlungen_gdf_in)
    rcp_baumartenempfehlungen_gdf_in.columns
    rcp_baumartenempfehlungen_gdf_in=rcp_baumartenempfehlungen_gdf_in[treetypesplusgeometry]#"TA_1", #,"BU","TA",,"WFO","BAH"
    rcp_baumartenempfehlungen_gdf_in.columns
    ##intersect Baumartenempfehlungen layer with Bestandeskarte layer
    print('intersect')
    rcp_bk_gdf_in=gpd.overlay(rcp_baumartenempfehlungen_gdf_in, bk_gdf, how='intersection', make_valid=True, keep_geom_type=True)
    rcp_bk_gdf_in["area"] = rcp_bk_gdf_in['geometry'].area
    mainlayercolumnslist=rcp_bk_gdf_in.columns.tolist()
    if 'index' in mainlayercolumnslist:
        rcp_bk_gdf_in.drop('index', axis=1, inplace=True)
    #rcp_bk_gdf_in.to_file(projectspace+"/FR/"+"FR_"+climatescenario+"_baumartenempfehlungen_intsct_bk.gpkg")
    rcp_bk_gdf_out=rcp_bk_gdf_in.copy()
    mainlayercolumnslist=rcp_bk_gdf_out.columns.tolist()
    len(rcp_bk_gdf_out)
    #gr_treetypes_LFI=joblib.load(projectspace+"/FR/"+"treetypes_LFI.sav")
    #for item in ["BUL", "FUL", "KA"]:#"ES"
    #    if item in mainlayercolumnslist:
    #        rcp_bk_gdf_out.drop(labels=item, axis=1, inplace=True)
    #    if item in gr_treetypes_LFI:
    #        gr_treetypes_LFI.remove(item)
    ##"BUL" in gr_treetypes_LFI
    ##"ES" in gr_treetypes_LFI
    mainlayercolumnslist=rcp_bk_gdf_out.columns.tolist()
    #"BUL" in mainlayercolumnslist
    #add columns to main layer
    #senstitive Bestaende pro Baumart:
    #-999 keine Angabe, 0 nicht klimasensitiv, 1 schwach klimasensitiv, 2 mittel klimasensitiv, 3 stark klimasensitiv, 4 bedingt klimasensitiv
    #Baumartenempfehlung:
    #-999 keine Angabe, 1 empfohlen, 2 bedingt empfohlen, 3 gefaehrdet, 4 in Zukunft empfohlen, 5 in Zukunft bedingt empfohlen

    print("sb")
    for col in treetypes:#_in_bk_list:
        print(col)
        #if col in mainlayercolumnslist:
        rcp_bk_gdf_out["sb" + col] = -999
        #nicht klimasensitiv - empfohlen
        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + '_2'] >= threshold_nicht_empfohlen_min) & (rcp_bk_gdf_out[col + '_2'] <= threshold_nicht_empfohlen_max) & (rcp_bk_gdf_out[col + '_1'].isin([1, 4])))].index, "sb" + col] = 0
        #nicht klimasensitiv - bedingt empfohlen
        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + '_2'] >= threshold_nicht_bedingt_min) & (rcp_bk_gdf_out[col + '_2'] <= threshold_nicht_bedingt_max) & (rcp_bk_gdf_out[col + '_1'].isin([2, 5])))].index, "sb" + col] = 0
        #nicht klimasensitiv - gefaehrdet
        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + '_2'] >= threshold_nicht_gef_min) & (rcp_bk_gdf_out[col + '_2'] <= threshold_nicht_gef_max) & (rcp_bk_gdf_out[col + '_1'].isin([3])))].index, "sb" + col] = 0
        #schwach klimasensitiv - empfohlen
        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col+'_2'] >threshold_schwach_empfohlen_min)&(rcp_bk_gdf_out[col+'_1'].isin([1,4])))].index, "sb"+col]=1
        #schwach klimasensitiv - bedingt empfohlen
        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + '_2'] > threshold_schwach_bedingt_min) & (rcp_bk_gdf_out[col + '_2'] <= threshold_schwach_bedingt_max) & (rcp_bk_gdf_out[col + '_1'].isin([2, 5])))].index, "sb" + col] = 1
        #schwach klimasensitiv - gefaehrdet
        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + '_2'] > threshold_schwach_gef_min) & (rcp_bk_gdf_out[col + '_2'] <= threshold_schwach_gef_max) & (rcp_bk_gdf_out[col + '_1'].isin([3])))].index, "sb" + col] = 1
        #mittel klimasensitiv - bedingt empfohlen
        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + '_2'] > threshold_mittel_bedingt_min) & (rcp_bk_gdf_out[col + '_2'] <= threshold_mittel_bedingt_max) & (rcp_bk_gdf_out[col + '_1'].isin([2, 5])))].index, "sb" + col] = 2
        #mittel klimasensitiv - gefaehrdet
        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + '_2'] > threshold_mittel_gef_min) & (rcp_bk_gdf_out[col + '_2'] <= threshold_mittel_gef_max) & (rcp_bk_gdf_out[col + '_1'].isin([3])))].index, "sb" + col] = 2
        #stark klimasensitiv - bedingt empfohlen
        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col+'_2'] > threshold_stark_bedingt_min) & (rcp_bk_gdf_out[col+'_1'].isin([2, 5])))].index, "sb" + col] = 3
        # stark klimasensitiv - gefaehrdet
        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col+'_2'] > threshold_stark_gef_min) & (rcp_bk_gdf_out[col+'_1'].isin([3])))].index, "sb" + col] = 3


    #Arve
    if 'AR_2' in mainlayercolumnslist:
        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col+'_2']> 95) & (
            rcp_bk_gdf_out[col+'_1'].isin([2, 5])))].index, "sb" + col] = 4
        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col+'_2']> 40) & (
            rcp_bk_gdf_out[col+'_1'].isin([3])))].index, "sb" + col] = 4

    #calculate maximum sensitivity over all treetypes
    rcp_bk_gdf_out["maxsens"]=-999
    rcp_bk_gdf_out["maxsens"]=rcp_bk_gdf_out[treetypes_sb].max(axis=1)
    rcp_bk_gdf_out["area"] = rcp_bk_gdf_out["geometry"].area

    #write the output
    print('write output '+climatescenario)
    #rcp_bk_gdf_out.to_file(projectspace+"/FR/"+"FR_"+climatescenario+"_sensitivebestaende.shp")
    rcp_bk_gdf_out.to_file(projectspace+"/FR/"+"FR_"+climatescenario+"_sensitivebestaende_"+varname+".gpkg")
    ##del rcp_bk_gdf_in
    ##data for analysis
    #if climatescenario=='rcp45':
    #    sensi45=rcp_bk_gdf_out.copy()
    #elif climatescenario=='rcp85':
    #    sensi85=rcp_bk_gdf_out.copy()


    #******************************************************************************************************
    #Aggregation to Bestandeskarte
    print('aggregate BK')
    bk_gdf["bksensi"]=-999
    bk_gdf["share0"]=-999
    bk_gdf["share1"]=-999
    bk_gdf["share2"]=-999
    bk_gdf["share3"]=-999
    bk_gdf["area"]=bk_gdf["geometry"].area
    #Angabe ob Aussagekraft sicher ist oder nicht
    bk_gdf["sicher"]=-999
    for index, row in bk_gdf.iterrows():
        if index%10000==0:
            print(index)
        bestand_id=row["bkid"]
        bestandtotalarea=row["area"]
        flaeche_nichtsensitiv=0
        flaeche_schwachsensitiv = 0
        flaeche_mittelsensitiv = 0
        flaeche_starksensitiv = 0
        extractfromintersect=rcp_bk_gdf_out[((rcp_bk_gdf_out["bkid"]==bestand_id)&(rcp_bk_gdf_out["maxsens"]==0))]
        extractgrouped=extractfromintersect.groupby(["maxsens"])["area"].sum()
        if len(extractgrouped)>0:
            bk_gdf.loc[index, "share0"] = extractgrouped.values[0]/bestandtotalarea*100.0
        else:
            bk_gdf.loc[index, "share0"] = 0
        extractfromintersect = rcp_bk_gdf_out[((rcp_bk_gdf_out["bkid"] == bestand_id) & (rcp_bk_gdf_out["maxsens"] == 1))]
        extractgrouped = extractfromintersect.groupby(["maxsens"])["area"].sum()
        if len(extractgrouped) > 0:
            bk_gdf.loc[index, "share1"] = extractgrouped.values[0]/bestandtotalarea*100.0
        else:
            bk_gdf.loc[index, "share1"] = 0
        extractfromintersect = rcp_bk_gdf_out[((rcp_bk_gdf_out["bkid"] == bestand_id) & (rcp_bk_gdf_out["maxsens"] == 2))]
        extractgrouped = extractfromintersect.groupby(["maxsens"])["area"].sum()
        if len(extractgrouped) > 0:
            bk_gdf.loc[index, "share2"] = extractgrouped.values[0]/bestandtotalarea*100.0
        else:
            bk_gdf.loc[index, "share2"] = 0
        extractfromintersect = rcp_bk_gdf_out[((rcp_bk_gdf_out["bkid"] == bestand_id) & (rcp_bk_gdf_out["maxsens"] == 3))]
        extractgrouped = extractfromintersect.groupby(["maxsens"])["area"].sum()
        if len(extractgrouped) > 0:
            bk_gdf.loc[index, "share3"] = extractgrouped.values[0]/bestandtotalarea*100.0
        else:
            bk_gdf.loc[index, "share3"] = 0
        #****************************************
        if bk_gdf.loc[index, "share0"]>=99.99:
            flaeche_nichtsensitiv = 100.0
        else:
            if bk_gdf.loc[index, "share1"] <= 50:
                flaeche_nichtsensitiv += bk_gdf.loc[index, "share1"]
            else:
                flaeche_schwachsensitiv += bk_gdf.loc[index, "share1"]
            if bk_gdf.loc[index, "share2"] <= 10:
                flaeche_nichtsensitiv += bk_gdf.loc[index, "share2"]
            elif bk_gdf.loc[index, "share2"] > 10 and bk_gdf.loc[index, "share2"] <= 20:
                flaeche_schwachsensitiv += bk_gdf.loc[index, "share2"]
            else:
                flaeche_mittelsensitiv += bk_gdf.loc[index, "share2"]
            if bk_gdf.loc[index, "share3"] <= 10:
                flaeche_nichtsensitiv += bk_gdf.loc[index, "share3"]
            elif bk_gdf.loc[index, "share3"] > 10 and bk_gdf.loc[index, "share3"] <= 20:
                flaeche_schwachsensitiv += bk_gdf.loc[index, "share3"]
            elif bk_gdf.loc[index, "share3"] > 20 and bk_gdf.loc[index, "share3"] <= 40:
                flaeche_mittelsensitiv += bk_gdf.loc[index, "share3"]
            else:
                flaeche_starksensitiv += bk_gdf.loc[index, "share3"]
        fl_list=[flaeche_nichtsensitiv,flaeche_schwachsensitiv,flaeche_mittelsensitiv,flaeche_starksensitiv]
        bk_gdf.loc[index,"bksensi"] =fl_list.index(max(fl_list))

    #Berechne Aussagekraft 1..sichere Aussage, 0...unsicher
    for index, row in bk_gdf.iterrows():
        if index % 10000 == 0:
            print(index)
        proz0=row["share0"]
        proz1 = row["share1"]
        proz2 = row["share2"]
        proz3 = row["share3"]
        if proz0<0:
            proz0=0
        if proz1<0:
            proz1=0
        if proz2<0:
            proz2=0
        if proz3<0:
            proz3=0
        if sum([proz0,proz1,proz2,proz3])>0.75:#*row["area"]:
            bk_gdf.loc[index, "sicher"] = 1
        else:
            bk_gdf.loc[index, "sicher"] = 0

    #write the file
    print('write max sensi BK '+climatescenario)
    #bk_gdf.to_file(projectspace+"/FR/"+"FR_"+climatescenario+"_bk_maxsensitivitaet.shp")
    bk_gdf.to_file(projectspace+"/FR/"+"FR_"+climatescenario+"_bk_maxsensitivitaet_"+varname+".gpkg")

print('all done')

print('analysis ...')
#Auswertungen
sensi45var1=gpd.read_file(projectspace+"/FR/"+"FR_"+"rcp45"+"_sensitivebestaende_"+"var1"+".gpkg")
sensi45var1=sensi45var1[sensi45var1["maxsens"]>=0]
sensi45var2=gpd.read_file(projectspace+"/FR/"+"FR_"+"rcp45"+"_sensitivebestaende_"+"var2"+".gpkg")
sensi45var2=sensi45var2[sensi45var2["maxsens"]>=0]
sensi85var1=gpd.read_file(projectspace+"/FR/"+"FR_"+"rcp85"+"_sensitivebestaende_"+"var1"+".gpkg")
sensi85var1=sensi85var1[sensi85var1["maxsens"]>=0]
sensi85var2=gpd.read_file(projectspace+"/FR/"+"FR_"+"rcp85"+"_sensitivebestaende_"+"var2"+".gpkg")
sensi85var2=sensi85var2[sensi85var2["maxsens"]>=0]

outfile = open(projectspace + "/FR/" + "FR_"+"sensitiveBestaende_stat.txt", "w")
outfile.write("var;totarea;prz_nichtsensitiv;prz_schwachsensitiv;prz_mittelsensitiv;prz_starksensitiv;prz_bedingtsensitiv\n")
shapes=[sensi45var1,sensi45var2,sensi85var1,sensi85var2]
varnames=['sensi45var1','sensi45var2','sensi85var1','sensi85var2']
i=0
for shape in shapes:
    areatot=np.sum(shape.area)
    area0=round(np.sum(shape[shape["maxsens"]==0].area)/areatot*100.0,2)
    area1 = round(np.sum(shape[shape["maxsens"] == 1].area) / areatot * 100.0, 2)
    area2 = round(np.sum(shape[shape["maxsens"] == 2].area) / areatot * 100.0, 2)
    area3 = round(np.sum(shape[shape["maxsens"] == 3].area) / areatot * 100.0, 2)
    area4 = round(np.sum(shape[shape["maxsens"] == 4].area) / areatot * 100.0, 2)
    outfile.write(varnames[i] + ";" + str(areatot) + ";" + str(area0) + ";" + str(area1)+ ";" + str(area2)+ ";" + str(area3)+ ";" + str(area4) + "\n")
    i+=1
outfile.close()
print('analysis done')