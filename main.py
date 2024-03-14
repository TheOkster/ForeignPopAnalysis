import pandas as pd
import geopandas as gpd
from backend import *
import timeit
import time
from geofeather import to_geofeather, from_geofeather

seconds = time.time()
# get_tract_info(main_sheet, urbanAreas)
# urban_shp = gpd.read_file('data/URAU_RG_100K_2021_3857_FUA.shp')
# metros = pd.read_excel('data/Metros_v2.xlsx', header=2)
# data_raw = pd.read_excel('Big Enough Metros.xlsx', sheet_name='Main')
# main_sheet = pd.read_excel('Big Enough Metros.xlsx', sheet_name='Main')
# main_sheet = main_sheet[main_sheet['Country'].isin(country_to_abbr)]
# urbanAreas = pd.read_excel("data/Metros_v2.xlsx")
#get_singapore_tracts(gpd.read_file('data/MP14_SUBZONE_NO_SEA_PL.shp'), 'Big Enough Metros.xlsx')
get_canada_tracts('Big Enough Metros.xlsx')
# data = from_geofeather('Urban Areas.feather')
# eu_tracts = from_geofeather('data/grid_1km_surf.feather')
# get_tract_info(data=main_sheet, data_raw=data_raw, urban_areas=urbanAreas, urban_areas_shp=urban_shp, tracts=eu_tracts, name='Big Enough Metros.xlsx')
seconds_2 = time.time()
print(str(seconds_2 - seconds) + " seconds")
# print(metros['Metropolitan region code'].tolist())
# for row in data.itertuples():
# print(row)

# if getattr(row, 'URAU_CODE') in metros['Metropolitan region code'].tolist():
# print(row)
