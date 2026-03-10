import argparse
import numpy as np
import pandas as pd
import geopandas as gpd
import warnings
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

from config import load_config


def main(canton, projectspace):
    cfg = load_config(canton)
    kt = canton

    baumartenempfehlungenrcp45 = gpd.read_file(
        f"{projectspace}/{kt}/{kt}_rcp45_baumartenempfehlungen.gpkg",
        layer=f"{kt}_rcp45_baumartenempfehlungen", driver="GPKG"
    )
    baumartenbedeutungenrcp45 = gpd.read_file(
        f"{projectspace}/{kt}/{kt}_rcp45_baumartenbedeutungen.gpkg",
        layer=f"{kt}_rcp45_baumartenbedeutungen", driver="GPKG"
    )
    baumartenbedeutungenrcp85 = gpd.read_file(
        f"{projectspace}/{kt}/{kt}_rcp85_baumartenbedeutungen.gpkg",
        layer=f"{kt}_rcp85_baumartenbedeutungen", driver="GPKG"
    )

    combi = gpd.overlay(baumartenbedeutungenrcp45, baumartenbedeutungenrcp85,
                        how='intersection', make_valid=True, keep_geom_type=True)

    arvenundlaerchen = [
        '59', '59A', '59C', '59E', '59J', '59L', '59S', '59V', '59H', '59R',
        '72,', '59*', '59G', '59AG', '59EG', '59VG', '72G',
        '57CLä', '57VLä', '58Lä', '59Lä', '59ELä', '59LLä', '59VLä', '59LLä',
    ]

    col_start = cfg["treeapp_col_start"]
    col_end = cfg["treeapp_col_end"]   # negative int, e.g. -2
    treetypeslist = baumartenempfehlungenrcp45.columns.tolist()[col_start:col_end]

    for col in treetypeslist:
        combi[col] = 0
        combi[col + "Fall"] = 0
        for index, row in combi.iterrows():
            # Empfohlen 1
            if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] in ['a', 'b'] and row[col + 'zuk1_2'] in ['a', 'b']:
                combi.loc[index, col] = 1
                combi.loc[index, col + "Fall"] = 1
            if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] in ['c'] and row[col + 'zuk1_2'] in ['a', 'b']:
                combi.loc[index, col] = 1
                combi.loc[index, col + "Fall"] = 2
            if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] in ['a', 'b'] and row[col + 'zuk1_2'] in ['c']:
                combi.loc[index, col] = 1
                combi.loc[index, col + "Fall"] = 3
            # bedingt empfohlen 2
            if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] in ['c'] and row[col + 'zuk1_2'] in ['c']:
                combi.loc[index, col] = 2
                combi.loc[index, col + "Fall"] = 7
            if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] in ['c'] and row[col + 'zuk1_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 2
                combi.loc[index, col + "Fall"] = 8
            if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] not in ['a', 'b', 'c'] and row[col + 'zuk1_2'] in ['a', 'b']:
                combi.loc[index, col] = 2
                combi.loc[index, col + "Fall"] = 9
            # gefaehrdet 3
            if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] in ['c'] and row[col + 'zuk1_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 3
                combi.loc[index, col + "Fall"] = 15
            if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] not in ['a', 'b', 'c'] and row[col + 'zuk1_2'] in ['c']:
                combi.loc[index, col] = 3
                combi.loc[index, col + "Fall"] = 16
            if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 3
                combi.loc[index, col + "Fall"] = 17
            # in Zukunft empfohlen 4
            if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] in ['a', 'b'] and row[col + 'zuk1_2'] in ['a', 'b']:
                combi.loc[index, col] = 4
                combi.loc[index, col + "Fall"] = 4
            if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] in ['a', 'b'] and row[col + 'zuk1_2'] in ['c']:
                combi.loc[index, col] = 4
                combi.loc[index, col + "Fall"] = 5
            if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] in ['c'] and row[col + 'zuk1_2'] in ['a', 'b']:
                combi.loc[index, col] = 4
                combi.loc[index, col + "Fall"] = 6
            # in Zukunft bedingt empfohlen 5
            if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] in ['c'] and row[col + 'zuk1_2'] in ['c']:
                combi.loc[index, col] = 5
                combi.loc[index, col + "Fall"] = 10
            if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] in ['a', 'b'] and \
                    row[col + 'zuk1_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 5
                combi.loc[index, col + "Fall"] = 11
            if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] not in ['a', 'b', 'c'] and row[col + 'zuk1_2'] in ['a', 'b']:
                combi.loc[index, col] = 5
                combi.loc[index, col + "Fall"] = 12
            if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] in ['c'] and row[col + 'zuk1_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 5
                combi.loc[index, col + "Fall"] = 13
            if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zuk1_1'] not in ['a', 'b', 'c'] and row[col + 'zuk1_2'] in ['c']:
                combi.loc[index, col] = 5
                combi.loc[index, col + "Fall"] = 14

            # Uebergang
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] in ['a', 'b'] and row[col + 'zukUE_2'] in ['a', 'b']:
                combi.loc[index, col] = 1
                combi.loc[index, col + "Fall"] = 1
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] in ['c'] and row[col + 'zukUE_2'] in ['a', 'b']:
                combi.loc[index, col] = 1
                combi.loc[index, col + "Fall"] = 2
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] in ['a', 'b'] and row[col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 1
                combi.loc[index, col + "Fall"] = 3
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] in ['c'] and row[col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 2
                combi.loc[index, col + "Fall"] = 7
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] in ['c'] and row[col + 'zukUE_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 2
                combi.loc[index, col + "Fall"] = 8
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] not in ['a', 'b', 'c'] and row[col + 'zukUE_2'] in ['a', 'b']:
                combi.loc[index, col] = 2
                combi.loc[index, col + "Fall"] = 9
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] in ['c'] and row[col + 'zukUE_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 3
                combi.loc[index, col + "Fall"] = 15
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] not in ['a', 'b', 'c'] and row[col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 3
                combi.loc[index, col + "Fall"] = 16
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 3
                combi.loc[index, col + "Fall"] = 17
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] in ['a', 'b'] and row[col + 'zukUE_2'] in ['a', 'b']:
                combi.loc[index, col] = 4
                combi.loc[index, col + "Fall"] = 4
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] in ['a', 'b'] and row[col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 4
                combi.loc[index, col + "Fall"] = 5
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] in ['c'] and row[col + 'zukUE_2'] in ['a', 'b']:
                combi.loc[index, col] = 4
                combi.loc[index, col + "Fall"] = 6
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] in ['c'] and row[col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 5
                combi.loc[index, col + "Fall"] = 10
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] in ['a', 'b'] and \
                    row[col + 'zukUE_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 5
                combi.loc[index, col + "Fall"] = 11
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] not in ['a', 'b', 'c'] and row[col + 'zukUE_2'] in ['a', 'b']:
                combi.loc[index, col] = 5
                combi.loc[index, col + "Fall"] = 12
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] in ['c'] and row[col + 'zukUE_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 5
                combi.loc[index, col + "Fall"] = 13
            if row['ue_1'] == 1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] not in ['a', 'b', 'c'] and row[col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 5
                combi.loc[index, col + "Fall"] = 14
            # Achtung 6 (only for col=="GO")
            if col == "GO" and row['ue_1'] == 1 and row[col + 'heuUE_1'] in ['c'] and \
                    row[col + 'zukUE_1'] in ['c'] and row[col + 'zukUE_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 6
                combi.loc[index, col + "Fall"] = 18
            if col == "GO" and row['ue_1'] == 1 and row[col + 'heuUE_1'] in ['c'] and \
                    row[col + 'zukUE_1'] not in ['a', 'b', 'c'] and row[col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 6
                combi.loc[index, col + "Fall"] = 19
            if col == "GO" and row['ue_1'] == 1 and \
                    row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] in ['c'] and row[col + 'zukUE_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 6
                combi.loc[index, col + "Fall"] = 20
            if col == "GO" and row['ue_1'] == 1 and \
                    row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and \
                    row[col + 'zukUE_1'] not in ['a', 'b', 'c'] and row[col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 6
                combi.loc[index, col + "Fall"] = 21

    combi.loc[combi['hszukcor_2'] == combi['hszukcor_1'], 'naiszuk1_2'] = combi['naiszuk1_1']
    combi.loc[combi['hszukcor_2'] == combi['hszukcor_1'], 'naiszuk2_2'] = combi['naiszuk2_1']

    for col in treetypeslist:
        for suffix in ['heu1_1', 'heu2_1', 'zuk1_1', 'zuk2_1', 'heuUE_1', 'zukUE_1',
                       'heu1_2', 'heu2_2', 'zuk1_2', 'zuk2_2', 'heuUE_2', 'zukUE_2']:
            if col + suffix in combi.columns:
                combi.drop(columns=col + suffix, inplace=True)

    for column in combi.columns.tolist():
        if '_1' in column and column not in ['Art_1', 'Art_2']:
            combi.rename(columns={column: column[:-2]}, inplace=True)
        elif '_2' in column and column not in ['Art_1', 'Art_2']:
            combi.drop(columns=column, inplace=True)

    combi.to_file(
        f"{projectspace}/{kt}/{kt}_baumartenempfehlungen_combi.gpkg",
        layer=f"{kt}_baumartenempfehlungen_combi", driver="GPKG"
    )
    print('all done')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compute sensi treeapp combi RCP45+RCP85 for a canton.")
    parser.add_argument("canton", help="Canton code, e.g. AG")
    parser.add_argument("--projectspace", default="D:/CCW24sensi",
                        help="Path to project data directory")
    args = parser.parse_args()
    main(args.canton, args.projectspace)
