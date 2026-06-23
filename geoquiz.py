import geopandas as gpd
import matplotlib.pyplot as plt
import random

# Load data from dataset into geopandas
print("Loading South Korea map data...")
# urls = ["https://raw.githubusercontent.com/southkorea/southkorea-maps/refs/heads/master/kostat/2018/json/skorea-municipalities-2018-geo.json",
#         "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/gadm/json/skorea-municipalities-geo.json",
#         "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/gadm/json/skorea-provinces-geo.json"]
url = "https://raw.githubusercontent.com/southkorea/southkorea-maps/refs/heads/master/kostat/2018/json/skorea-municipalities-2018-geo.json"
gdf = gpd.read_file(url)

# Clean up english name and force lower case
gdf["name_eng_clean"] = gdf["name_eng"].str.strip().str.lower()

# Map to provinces/cities
level_1_map = {
    "11": "서울", "21": "부산", "22": "대구", "23": "인천",
    "24": "광주", "25": "대전", "26": "울산", "29": "세종",
    "31": "경기", "32": "강원", "33": "충북", "34": "충남",
    "35": "전북", "36": "전남", "37": "경북", "38": "경남", "39": "제주"
}
gdf["region"] = gdf["code"].str[:2].map(level_1_map)


# Goal: Make a quiz with several modes
# Mode 1: Type the names and it will highlight. Try to guess all.
# Mode 2: Type the name of the highlighted area.
# Mode 3: Click the named area.
# Each filterable by area/province/city