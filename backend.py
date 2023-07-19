import numpy as np
import pandas as pd
import fuzzywuzzy.fuzz as fuzz

states_csv = pd.read_csv("data/EuropeCountries.csv")
country_to_abbr = dict(zip(states_csv['Country'].tolist(), states_csv['ISO'].tolist()))


def closest_match(threshold: int, value: str, metro_list: list):
    matches = []
    best = []
    for item in metro_list:
        score = fuzz.token_set_ratio(value, item)
        if threshold < score:
            matches.append([item, score])
    for match in matches:
        if not best:
            best = match
        else:
            if best[1] < match[1]:
                best = match
    return best[0]


def closest_matches(threshold: int, value: str, metro_list: list):
    matches = []
    best = []
    for item in metro_list:
        score = fuzz.token_set_ratio(value, item)
        if threshold < score:
            matches.append(item)
    return set(matches)


def get_tract_info(data: pd.DataFrame, urbanAreas: pd.DataFrame):
    city_and_country_full = zip(data['City'].tolist(), data['Country'].tolist())
    city_and_region_abbr = []
    data_modified = data
    for city, country in city_and_country_full:
        city_and_region_abbr.append([city, country_to_abbr[country]])
    for city, code in city_and_region_abbr:
        population = 0
        area = 0
        output_df = pd.DataFrame()
        if city == "Birmingham":
            city = "West Midlands urban area"
        if city == "Essen":
            city = "Ruhr area"
        matches = closest_matches(95, city, urbanAreas['English Name'].tolist())
        blocks = urbanAreas[urbanAreas['English Name'].isin(matches)]
        print(city)
        # print("   " + str(matches))
        # print("   " + str(blocks))
        fua_ids = set()
        eu_blocks = pd.read_excel("data/EU Blocks.xlsx", sheet_name=code, header=0)
        for block in blocks.itertuples():
            if code != 'UK':
                fua_ids.update(eu_blocks[eu_blocks['NUTS 3 CODE'] == getattr(block, '_1')]["FUA_ID"].tolist())
            if code == 'UK':
                fua_ids.update(eu_blocks[eu_blocks['old NUTS 3 CODE'] == getattr(block, '_1')]["FUA_ID"].tolist())
        if np.NAN in fua_ids:
            fua_ids.remove(np.NAN)
        print("   FUA_IDS:" + str(fua_ids))
        for fua_id in fua_ids:
            eu_blocks_filtered = eu_blocks[eu_blocks['FUA_ID'] == fua_id]
            eu_blocks_filtered = eu_blocks_filtered[eu_blocks_filtered['POPULATION']/eu_blocks_filtered['TOTAL AREA (m2)'] >= 3*10**-3]
            for block in eu_blocks_filtered.itertuples():
                population += getattr(block, 'POPULATION')
                area += getattr(block, '_7')
        print("Population: " + str(population))
        print("Area: " + str(area))
