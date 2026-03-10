import argparse
import numpy as np
import pandas as pd
import geopandas as gpd
import warnings
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)


def main(canton, projectspace):
    kt = canton  # e.g. "AG"

    rcp45 = gpd.read_file(
        f"{projectspace}/{kt}/{kt}_rcp45_zukuenftigestandorte.gpkg",
        layer=f"{kt}_rcp45_zukuenftigestandorte", driver="GPKG"
    )
    rcp85 = gpd.read_file(
        f"{projectspace}/{kt}/{kt}_rcp85_zukuenftigestandorte.gpkg",
        layer=f"{kt}_rcp85_zukuenftigestandorte", driver="GPKG"
    )

    rcp45 = rcp45[['nais', 'nais1', 'nais2', 'mo', 'ue', 'taheute', 'storeg',
                   'tahs', 'tahsue', 'naiszuk1', 'naiszuk2', 'hszukcor', 'geometry']]
    rcp45 = rcp45.rename(columns={'naiszuk1': 'nais1_rcp45', 'naiszuk2': 'nais2_rcp45',
                                   'hszukcor': 'hs_rcp45'})

    rcp85 = rcp85[['nais', 'nais1', 'nais2', 'mo', 'ue', 'taheute', 'storeg',
                   'tahs', 'tahsue', 'naiszuk1', 'naiszuk2', 'hszukcor', 'geometry']]
    rcp85 = rcp85.rename(columns={'naiszuk1': 'nais1_rcp85', 'naiszuk2': 'nais2_rcp85',
                                   'hszukcor': 'hs_rcp85'})

    combi = gpd.overlay(rcp45, rcp85, how='intersection', make_valid=True, keep_geom_type=True)
    combi.loc[combi['hs_rcp85'] == combi['hs_rcp45'], 'nais1_rcp85'] = combi['nais1_rcp45']
    combi.loc[combi['hs_rcp85'] == combi['hs_rcp45'], 'nais2_rcp85'] = combi['nais2_rcp45']
    combi['area'] = combi.geometry.area

    combi = combi[combi['area'] >= 0]
    combi.to_file(f"{projectspace}/{kt}/{kt}_Projektionswege_combi.gpkg",
                  layer=f"{kt}_Projektionswege_combi", driver="GPKG")

    combi = combi[combi['area'] >= 100]
    combi_unique = combi[['nais_1', 'tahs_1', 'tahsue_1',
                           'nais1_rcp45', 'nais2_rcp45', 'hs_rcp45',
                           'nais1_rcp85', 'nais2_rcp85', 'hs_rcp85']].drop_duplicates()
    combi_unique = combi_unique[
        combi_unique['tahs_1'].isin([
            'obersubalpin', 'subalpin', 'hochmontan', 'obermontan',
            'untermontan', 'submontan', 'collin'
        ])
    ]
    combi_unique = combi_unique.sort_values(by=['nais_1'])
    combi_unique.to_excel(f"{projectspace}/{kt}/{kt}_Projektionspfade_unique.xlsx")

    areastatistics = combi.groupby(
        ['nais_1', 'tahs_1', 'tahsue_1',
         'nais1_rcp45', 'nais2_rcp45', 'hs_rcp45',
         'nais1_rcp85', 'nais2_rcp85', 'hs_rcp85']
    ).agg({'area': 'sum'})
    areastatistics.to_excel(f"{projectspace}/{kt}/{kt}_Projektionspfade_unique_area.xlsx")

    rcp45['area'] = rcp45.geometry.area
    rcp45 = rcp45[rcp45['area'] >= 100]
    rcp45unique = rcp45[['nais', 'nais1', 'nais2', 'tahs', 'tahsue',
                          'nais1_rcp45', 'nais2_rcp45', 'hs_rcp45',
                          'mo', 'ue', 'taheute', 'storeg']].drop_duplicates()
    rcp45unique.to_excel(f"{projectspace}/{kt}/{kt}_Projektionspfade_unique_RCP45.xlsx")
    areastatistics_rcp45 = rcp45.groupby(
        ['nais', 'nais1', 'nais2', 'tahs', 'tahsue',
         'nais1_rcp45', 'nais2_rcp45', 'hs_rcp45', 'mo', 'ue', 'taheute', 'storeg']
    ).agg({'area': 'sum'})
    areastatistics_rcp45.to_excel(
        f"{projectspace}/{kt}/{kt}_Projektionspfade_unique_area_RCP45.xlsx")

    rcp85['area'] = rcp85.geometry.area
    rcp85 = rcp85[rcp85['area'] >= 100]
    rcp85unique = rcp85[['nais', 'nais1', 'nais2', 'tahs', 'tahsue',
                          'nais1_rcp85', 'nais2_rcp85', 'hs_rcp85',
                          'mo', 'ue', 'taheute', 'storeg']].drop_duplicates()
    rcp85unique.to_excel(f"{projectspace}/{kt}/{kt}_Projektionspfade_unique_RCP85.xlsx")
    areastatistics_rcp85 = rcp85.groupby(
        ['nais', 'nais1', 'nais2', 'tahs', 'tahsue',
         'nais1_rcp85', 'nais2_rcp85', 'hs_rcp85', 'mo', 'ue', 'taheute', 'storeg']
    ).agg({'area': 'sum'})
    areastatistics_rcp85.to_excel(
        f"{projectspace}/{kt}/{kt}_Projektionspfade_unique_area_RCP85.xlsx")

    print('all done')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compute Projektionswege combi for a canton.")
    parser.add_argument("canton", help="Canton code, e.g. AG")
    parser.add_argument("--projectspace", default="D:/CCW24sensi",
                        help="Path to project data directory")
    args = parser.parse_args()
    main(args.canton, args.projectspace)
