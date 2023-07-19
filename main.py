import pandas as pd
from backend import *

data = pd.read_csv("data/EuropeCountries.csv")
data_raw = pd.read_excel('Big Enough Metros.xlsx', sheet_name='Main')
main_sheet = pd.read_excel('Big Enough Metros.xlsx', sheet_name='Main')
main_sheet = main_sheet[main_sheet['Country'].isin(country_to_abbr)]
urbanAreas = pd.read_excel("data/Metros.xlsx", header=2)
get_tract_info(main_sheet, urbanAreas)
