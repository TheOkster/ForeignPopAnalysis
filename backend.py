import numpy as np
import pandas as pd
import fuzzywuzzy.fuzz as fuzz
import geopandas as gpd
import unidecode

states_csv = pd.read_csv("data/EuropeCountries.csv")
country_to_abbr = dict(zip(states_csv['Country'].tolist(), states_csv['ISO'].tolist()))
abbr_to_country = dict(zip(states_csv['ISO'].tolist(), states_csv['Country'].tolist()))


def closest_match(threshold: int, value: str, collection: list):
    matches = []
    best = []
    for item in collection:
        score = fuzz.token_set_ratio(value, item)
        if threshold < score:
            matches.append([item, score])
    for match in matches:
        if not best:
            best = match
        else:
            if best[1] < match[1]:
                best = match
    # Exceptions
    if value == "Cologne":
        return "Köln"
    if value == "Ruhr area":
        return "Ruhrgebiet"
    # print(value + f" Match: {best[0]}")
    return best[0]


def closest_matches(threshold: int, value: str, metro_list: list):
    matches = []
    for item in metro_list:
        item = unidecode.unidecode(str(item))
        score = fuzz.token_set_ratio(value, item)
        if threshold < score:
            matches.append((item, score))
    return [name for name in sorted(matches, key=lambda element: element[1], reverse=True)]


def get_tract_info(data: pd.DataFrame, data_raw: pd.DataFrame, urban_areas: pd.DataFrame,
                   urban_areas_shp: gpd.GeoDataFrame, tracts: gpd.GeoDataFrame, name: str):
    city_and_country_full = zip(data['City'].tolist(), data['Country'].tolist())
    data_modified = data
    city_and_region_abbr = []
    tracts_dict = []
    for city, country in city_and_country_full:
        city_and_region_abbr.append([city, country_to_abbr[country]])
    tracts.crs = "3035"
    tracts = tracts.to_crs(urban_areas_shp.crs)
    for block in tracts.itertuples():
        if getattr(block, 'LAND_PC') > 0:
            if getattr(block, 'TOT_P_2018') / getattr(block, 'LAND_PC') * 100 > 3000:
                tracts_dict.append(block)
    # print(tracts_dict)
    # print(urban_areas_shp.keys())
    print("Step 2")
    for city, code in city_and_region_abbr:
        population = 0
        area = 0
        unmodified_city = city
        if city == "Birmingham":
            city = "West Midlands urban area"
        if city == "Essen":
            city = "Ruhr area"
        if city in ('Brussels', 'Copenhagen'):
            continue
        if code == "UK":
            continue
        fua_ids = set()
        eu_fuas = pd.read_excel("data/EU Blocks.xlsx", sheet_name=str(code), header=0, dtype=str)
        if code != 'UK':
            fua_ids.update(
                eu_fuas[eu_fuas['FUA_NAME'] == closest_match(0, city, eu_fuas["FUA_NAME"].tolist())]["FUA_ID"].tolist())
            # print(getattr(block, '_1'))
        else:
            fua_ids.update(
                eu_fuas[eu_fuas['FUA_NAME'] == closest_match(0, city, eu_fuas["FUA_NAME"].tolist())]["FUA_ID"].tolist())
        if np.NAN in fua_ids:
            fua_ids.remove(np.NAN)
        if "nan" in fua_ids:
            fua_ids.remove('nan')
        fua_ids = list(map(str.strip, fua_ids))
        # print(fua_ids)
        # print(codes)
        for block in tracts_dict:
            for fua_id in fua_ids:
                if getattr(block, 'LAND_PC') > 0:
                    if getattr(block, 'TOT_P_2018') / getattr(block, 'LAND_PC') * 100 >= 3000:
                        if getattr(block, 'geometry').within(
                                urban_areas_shp[urban_areas_shp['URAU_CODE'] == fua_id]['geometry'].item()):
                            population += getattr(block, 'TOT_P_2018')
                            area += (1 * getattr(block, 'LAND_PC') / 100)
        m = (data_modified['City'] == unmodified_city) & (
                data_modified['Country'] == abbr_to_country[code])
        print(m)
        data_modified.loc[m, 'Urban Population'] = population
        data_modified.loc[m, 'Area (km)'] = area
        print([unmodified_city, abbr_to_country[code], population, area])
    with pd.ExcelWriter(name) as writer:
        merged = data_modified.combine_first(data_raw)
        merged.to_excel(writer, index=False, sheet_name='Main')


def get_canada_tracts(name: str):
    areas = pd.read_csv('data/Canada.csv', dtype={'Population': float, 'Land Area': float})
    areas['Population'] = areas['Population'].replace(np.NAN, 0)
    areas['Population'] = areas['Population'].astype(int)
    data = pd.read_excel(name)
    canadian_cities = data[data['Country'] == 'Canada']
    cities = canadian_cities['City'].tolist()
    for city in cities:
        blocks = areas[areas['Metro Area'] == closest_match(0, city, areas['Metro Area'].tolist())]
        urban_population = 0
        urban_area = 0
        for block in blocks.itertuples():
            population = getattr(block, 'Population')
            area = getattr(block, '_4')
            if population/area > 3000:
                urban_population += population
                urban_area += area
        print([city, urban_population, urban_area])
        m = (data['City'] == city) & (
                data['Country'] == "Canada")
        data.loc[m, 'Urban Population'] = urban_population
        data.loc[m, 'Area (km)'] = urban_area
    with pd.ExcelWriter(name) as writer:
        data.to_excel(writer, index=False, sheet_name='Main')
'''
        population = areas[areas['Subzone'] == closest_match(0, getattr(block, 'SUBZONE_N'), areas['Subzone'])]['Population'].item()
        population = population.replace(',', '')
        population = population.replace('-', '0')
        area = getattr(block, 'SHAPE_Area')/(10**6)
        if int(population)/area > 3000:
            urban_population += int(population)
            urban_area += area
            print([getattr(block, 'SUBZONE_N'), int(population)/area])
    # print(tracts_dict)
    # print(urban_areas_shp.keys())
    print("Step 2")
    m = (data['City'] == "Singapore") & (
            data['Country'] == "Singapore")
    data.loc[m, 'Urban Population'] = urban_population
    data.loc[m, 'Area (km)'] = urban_area
    print(['Singapore', 'Singapore', urban_population, urban_area])
    with pd.ExcelWriter(name) as writer:
        data.to_excel(writer, index=False, sheet_name='Main')
'''


def get_singapore_tracts(tracts: gpd.GeoDataFrame, name: str):
    areas = pd.read_csv('data/Singapore Areas.csv')
    data = pd.read_excel(name)
    urban_population = 0
    urban_area = 0
    for block in tracts.itertuples():
        population = areas[areas['Subzone'] == closest_match(0, getattr(block, 'SUBZONE_N'), areas['Subzone'])][
            'Population'].item()
        population = population.replace(',', '')
        population = population.replace('-', '0')
        area = getattr(block, 'SHAPE_Area') / (10 ** 6)
        if int(population) / area > 3000:
            urban_population += int(population)
            urban_area += area
            print([getattr(block, 'SUBZONE_N'), int(population) / area])
    # print(tracts_dict)
    # print(urban_areas_shp.keys())
    print("Step 2")
    m = (data['City'] == "Singapore") & (
            data['Country'] == "Singapore")
    data.loc[m, 'Urban Population'] = urban_population
    data.loc[m, 'Area (km)'] = urban_area
    print(['Singapore', 'Singapore', urban_population, urban_area])
    with pd.ExcelWriter(name) as writer:
        data.to_excel(writer, index=False, sheet_name='Main')
