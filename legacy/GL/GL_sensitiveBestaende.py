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

fichtenanteil=0.7


#******************************************************************************************************
#Sensitive Bestaende
#******************************************************************************************************
treetypes_in_bk_list=["FI"]#, "TA","BU"]#,"TA","FOE","BU","ESAH"]
treetypes=["FI"]#, "TA","BU"]#,"TA","WFO","BU","ES","BAH"]
#sb= sensitiver Bestand
treetypes_sb=[]
for item in treetypes:
    treetypes_sb.append("sb"+item)
#read Bestandeskarte shape
bk_gdf=gpd.read_file(projectspace+"/GL"+"/waldbestaende/esri_shapefile/pub_gl_waldbestaende/waldbestaende.shp")
bk_gdf.crs
len(bk_gdf)
bk_gdf.columns
bk_gdf["bkid"]=bk_gdf.index
bk_gdf=bk_gdf[['bkid','mischung', 'entwicklun','schlussgra','nhd_anteil', 'hdom', 'hmax', 'gru_strukt','dg_os','dg_ms', 'dg_us','geometry']]#,"TACODE","BUCODE"
bk_gdf.dtypes
len(bk_gdf)
for climatescenario in climatescenarios:
    print(climatescenario)
    rcp_baumartenempfehlungen_gdf_in=joblib.load(projectspace+"/GL/GL_"+climatescenario+"_baumartenempfehlungen.sav")
    len(rcp_baumartenempfehlungen_gdf_in)
    rcp_baumartenempfehlungen_gdf_in.columns
    rcp_baumartenempfehlungen_gdf_in=rcp_baumartenempfehlungen_gdf_in[["FI","geometry"]]#"TA_1", #,"BU","TA",,"WFO","BAH"
    rcp_baumartenempfehlungen_gdf_in.columns
    ##intersect Baumartenempfehlungen layer with Bestandeskarte layer
    rcp_bk_gdf_in=gpd.overlay(rcp_baumartenempfehlungen_gdf_in, bk_gdf, how='intersection', make_valid=True, keep_geom_type=True)
    rcp_bk_gdf_in["area"] = rcp_bk_gdf_in['geometry'].area
    mainlayercolumnslist=rcp_bk_gdf_in.columns.tolist()
    if 'index' in mainlayercolumnslist:
        rcp_bk_gdf_in.drop('index', axis=1, inplace=True)
    #rcp_bk_gdf_in.to_file(projectspace+"/GL/"+"GL_"+climatescenario+"_baumartenempfehlungen_intsct_bk.gpkg")
    rcp_bk_gdf_out=rcp_bk_gdf_in.copy()
    mainlayercolumnslist=rcp_bk_gdf_out.columns.tolist()
    len(rcp_bk_gdf_out)
    gr_treetypes_LFI=joblib.load(projectspace+"/GL/"+"treetypes_LFI.sav")
    for item in ["BUL", "FUL", "KA"]:#"ES"
        if item in mainlayercolumnslist:
            rcp_bk_gdf_out.drop(labels=item, axis=1, inplace=True)
        if item in gr_treetypes_LFI:
            gr_treetypes_LFI.remove(item)
    #"BUL" in gr_treetypes_LFI
    #"ES" in gr_treetypes_LFI
    mainlayercolumnslist=rcp_bk_gdf_out.columns.tolist()
    #"BUL" in mainlayercolumnslist
    #add columns to main layer
    #senstitive Bestaende pro Baumart:
    #-999 keine Angabe, 0 nicht sensitiv, 1 schwach sensitiv, 2 mittel sensitiv, 3 stark sensitiv
    #Baumartenempfehlung:
    #-999 keine Angabe, 1 empfohlen, 2 bedingt empfohlen, 3 gefaehrdet, 4 in Zukunft empfohlen, 5 in Zukunft bedingt empfohlen
    #for col in treetypes:#_in_bk_list:
    #    print(col)
    #    if col in mainlayercolumnslist:
    #        rcp_bk_gdf_out["sb" + col] = -999
    #        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + "CODE"] >95)&(rcp_bk_gdf_out[col].isin([1,4])))].index, "sb"+col]=1
    #        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + "CODE"] > 0)&(rcp_bk_gdf_out[col + "CODE"] <= 95) & (rcp_bk_gdf_out[col].isin([1, 4])))].index, "sb" + col] = 0
    #        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + "CODE"] > 95) & (rcp_bk_gdf_out[col].isin([2, 5])))].index, "sb" + col] = 3
    #        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + "CODE"] >= 70) & (rcp_bk_gdf_out[col + "CODE"] <= 95) & (rcp_bk_gdf_out[col].isin([2, 5])))].index, "sb" + col] = 2
    #        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + "CODE"] >20) & (rcp_bk_gdf_out[col + "CODE"] <70) & (rcp_bk_gdf_out[col].isin([2, 5])))].index, "sb" + col] = 1
    #        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + "CODE"] >0) & (rcp_bk_gdf_out[col + "CODE"] <=20) & (rcp_bk_gdf_out[col].isin([2, 5])))].index, "sb" + col] = 0
    #        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + "CODE"] > 40) & (rcp_bk_gdf_out[col].isin([3])))].index, "sb" + col] = 3
    #        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + "CODE"] >20) & (rcp_bk_gdf_out[col + "CODE"] <= 40) & (rcp_bk_gdf_out[col].isin([3])))].index, "sb" + col] = 2
    #        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + "CODE"] >10) & (rcp_bk_gdf_out[col + "CODE"] <=20) & (rcp_bk_gdf_out[col].isin([3])))].index, "sb" + col] = 1
    #        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out[col + "CODE"] >0) & (rcp_bk_gdf_out[col + "CODE"] <= 10) & (rcp_bk_gdf_out[col].isin([3])))].index, "sb" + col] = 0

    for col in treetypes:#_in_bk_list:
        print(col)
        if col in mainlayercolumnslist:
            rcp_bk_gdf_out["sb" + col] = -999
            rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil >95)&(rcp_bk_gdf_out[col].isin([1,4])))].index, "sb"+col]=1
            rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil > 0)&(rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil <= 95) & (rcp_bk_gdf_out[col].isin([1, 4])))].index, "sb" + col] = 0
            rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil > 95) & (rcp_bk_gdf_out[col].isin([2, 5])))].index, "sb" + col] = 3
            rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil >= 70) & (rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil <= 95) & (rcp_bk_gdf_out[col].isin([2, 5])))].index, "sb" + col] = 2
            rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil >20) & (rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil <70) & (rcp_bk_gdf_out[col].isin([2, 5])))].index, "sb" + col] = 1
            rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil >0) & (rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil <=20) & (rcp_bk_gdf_out[col].isin([2, 5])))].index, "sb" + col] = 0
            rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil > 40) & (rcp_bk_gdf_out[col].isin([3])))].index, "sb" + col] = 3
            rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil >20) & (rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil <= 40) & (rcp_bk_gdf_out[col].isin([3])))].index, "sb" + col] = 2
            rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil >10) & (rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil <=20) & (rcp_bk_gdf_out[col].isin([3])))].index, "sb" + col] = 1
            rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil >0) & (rcp_bk_gdf_out["nhd_anteil"]*fichtenanteil <= 10) & (rcp_bk_gdf_out[col].isin([3])))].index, "sb" + col] = 0
    #Arve
    if 'AR' in mainlayercolumnslist:
        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out["nhd_anteil"] * fichtenanteil > 95) & (
            rcp_bk_gdf_out[col].isin([2, 5])))].index, "sb" + col] = 4
        rcp_bk_gdf_out.loc[rcp_bk_gdf_out[((rcp_bk_gdf_out["nhd_anteil"] * fichtenanteil > 40) & (
            rcp_bk_gdf_out[col].isin([3])))].index, "sb" + col] = 4

    #calculate maximum sensitivity over all treetypes
    rcp_bk_gdf_out["maxsens"]=-999
    rcp_bk_gdf_out["maxsens"]=rcp_bk_gdf_out[treetypes_sb].max(axis=1)

    #write the output
    #rcp_bk_gdf_out.to_file(projectspace+"/GL/"+"GL_"+climatescenario+"_sensitivebestaende.shp")
    rcp_bk_gdf_out.to_file(projectspace+"/GL/"+"GL_"+climatescenario+"_sensitivebestaende"+str(int(fichtenanteil*100)).replace('.','_')+".gpkg")
    #del rcp_bk_gdf_in


    #******************************************************************************************************
    #Aggregation to Bestandeskarte
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
    #bk_gdf.to_file(projectspace+"/GL/"+"GL_"+climatescenario+"_bk_maxsensitivitaet.shp")
    bk_gdf.to_file(projectspace+"/GL/"+"GL_"+climatescenario+"_bk_maxsensitivitaet"+str(int(fichtenanteil*100)).replace('.','_')+".gpkg")


    ##Auswertungen
    #sensi45=joblib.load(projectspace+"/GL/GL_rcp45_sensitivestandorte.sav")
    #sensi45=sensi45[["geometry","sensi3ba","sensi4ba"]]
    #sensi45=sensi45.set_crs(epsg=2056,allow_override=True)
    #sensi85=joblib.load(projectspace+"/GL/GL_rcp85_sensitivestandorte.sav")
    #sensi85=sensi85[["geometry","sensi3ba","sensi4ba"]]
    #sensi85=sensi85.set_crs(epsg=2056,allow_override=True)
    #regionen=gpd.read_file(projectspace+"/Regionalisierung20220125.shp")
    #regionen=regionen[["geometry","Regionen","Reg_Nr"]]
    #regionen.crs
    #regionen=regionen.set_crs(epsg=2056,allow_override=True)
    ##sensi45reg=gpd.overlay(sensi45, regionen, how='intersection', make_valid=True, keep_geom_type=True)
    ##sensi85reg=gpd.overlay(sensi85, regionen, how='intersection', make_valid=True, keep_geom_type=True)
    #sensi45reg["area"]=sensi45reg["geometry"].area
    #sensi85reg["area"]=sensi85reg["geometry"].area
    #sensi45["area"]=sensi45["geometry"].area/1000000.0
    #sensi85["area"]=sensi85["geometry"].area/1000000.0
    #stat45_3ba=sensi45.groupby(["sensi3ba"])["area"].sum()
    #stat45_4ba=sensi45.groupby(["sensi4ba"])["area"].sum()
    #stat85_3ba=sensi85.groupby(["sensi3ba"])["area"].sum()
    #stat85_4ba=sensi85.groupby(["sensi4ba"])["area"].sum()