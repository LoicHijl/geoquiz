import geopandas as gpd
import matplotlib.pyplot as plt
import random

# 1. LOAD DATA (Clean, compressed GeoJSON directly from open source repo)
print("Loading South Korea map data...")
# urls = ["https://raw.githubusercontent.com/southkorea/southkorea-maps/refs/heads/master/kostat/2018/json/skorea-municipalities-2018-geo.json",
#         "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/gadm/json/skorea-municipalities-geo.json",
#         "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/gadm/json/skorea-provinces-geo.json"]
url = "https://raw.githubusercontent.com/southkorea/southkorea-maps/refs/heads/master/kostat/2018/json/skorea-municipalities-2018-geo.json"
gdf = gpd.read_file(url)

# Goal: Make a quiz with several modes
# Mode 1: Type the names and it will highlight. Try to guess all.
# Mode 2: Type the name of the highlighted area.
# Mode 3: Click the named area.
# Each filterable by area/province/city