import pandas as pd
import geopandas as gpd

# Import the original dataset
print("Loading South Korea map data...")
url = "https://raw.githubusercontent.com/southkorea/southkorea-maps/refs/heads/master/kostat/2018/json/skorea-municipalities-2018-geo.json"
kostat = gpd.read_file(url)

kostat.head()

# Map counties to regions
level_1_map = {
    "11": "서울", "21": "부산", "22": "대구", "23": "인천",
    "24": "광주", "25": "대전", "26": "울산", "29": "세종",
    "31": "경기", "32": "강원", "33": "충북", "34": "충남",
    "35": "전북", "36": "전남", "37": "경북", "38": "경남", "39": "제주"
}
kostat["region"] = kostat["code"].str[:2].map(level_1_map)

# We want to remove 구, and instead use cities only, so we merge the big cities
# In order to merge, we first make a selection of these cities, and assign them to the nearest province
print("Merging metropolitan cities...")
merging = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종"]
merged_regions = ["경기", "경남", "경북", "경기", "전남", "충남", "경남", "충복"]

# We then make two selections of the array, one with the to-be-merged cities, and one without
to_merge = kostat[kostat["region"].isin(merging)]
no_merge = kostat[~kostat["region"].isin(merging)]

# Execute the merge, first we compress the 구 into one GEOPOLYGON per city
merged = to_merge.dissolve(by="region", as_index=False)

# We rename the names of the cities to their names, and set the nearby province as its region
merged["name"] = merged["region"]
merged["region"] = merged_regions

# Recombine the two sets
new_gdf = pd.concat([no_merge, merged], ignore_index=True)

# Now there are still some cities that are bigger, so have individual 구 in the dataset,
# but they are part of one of the provinces already (ex 수원시)
# We must filter these out manually
print("Merging other, smaller cities...")
other_cities = [[0,4], [4,6], [8,10], 
                [14,16], [16,19], [27,30], 
                [62,66], [74,76], [90,92], 
                [127,129], [158,163]]
other_city_names = ["수원시", "성남시", "안양시", 
                    "안산시", "고양시", "용인시", 
                    "청주시", "천안시", "전주시", 
                    "포항시", "창원시"]

# We go through each city and save the districts which were part of it, as well as the new combined city GEOPOLYGON objects
city_list = []
district_list = []
for x, c in enumerate(other_cities):
    city = new_gdf[c[0]:c[1]].copy()
    combined_city = city.dissolve()
    combined_city["name"] = other_city_names[x]
    city_list.append(combined_city)
    district_list.append(city)

# We go through each of the original districts and remove them from our original dataframe
for x in district_list:
    new_gdf = pd.merge(new_gdf, x, how="outer", indicator=True).query("_merge != 'both'").drop('_merge', axis=1)

# Finally, we recombine our dissolved cities with the original dataframe
game_gdf = pd.concat([new_gdf, pd.concat(city_list, ignore_index=True)], ignore_index=True)

# We need to reprocess the names, as they now contain the postfixes 시, 군, 구 etc. 
# Since these are mostly 1 long and only appear at the end, this is easy in our case
# TODO: Make this an optional step
newnames = []
for x, city in game_gdf.iterrows():
    if len(city["name"])>2:
        newnames.append(city["name"][:-1])
    else:
        newnames.append(city["name"])
game_gdf["name"] = newnames

# Finally, we can save this as our geojson file
print("Saving dataset to geojson file...")
game_gdf.to_file("processed_korea.geojson", driver="GeoJSON")