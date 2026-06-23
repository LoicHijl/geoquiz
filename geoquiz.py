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

# User selections:
# Province - list of options/full country
# Mode - see later comments

# Setup province selection:
menu_options = {str(i+1): level_1_map[code] for i, code in enumerate(level_1_map.keys())}

print("\n--- Available Provinces ---")
for num, prov in menu_options.items():
    print(f"[{num}] {prov}")

prov_choice = input("\nSelect a province number to filter (or type -1 for all of Korea): ")

if prov_choice != -1:
    selected_province = menu_options[prov_choice]
    quiz_gdf = gdf[gdf["region"] == selected_province].copy()
    print(f"Successfully loaded data for {selected_province}.")
else:
    quiz_gdf = gdf.copy()
    print(f"Successfully loaded full South Korean data")

# Select the game mode
print("--- Select game mode: ---")
print("[1]: Type the names of the municipalities and the region will be highlighted after")
print("[2]: Type the names of the highlighted municipalities")
print("[3]: Click on the named municipality")
mode = input("Select mode: ").strip()

# Currently only mode 1 exists: TODO: implement other modes and remove this
print("Note: currently only mode 1 is implemented, defaulting to 1")
mode = "1"

# Initialize the plot
plt.ion()
fig, ax = plt.subplots(figsize=(9, 9))

if mode == "1":
    # Setup pre-game variables
    guessed_municipalities = set()
    quiz_gdf["status"] = 0 # Color for the guessed municipalities will be different based on this
    total_countries = len(quiz_gdf) # Total number of municipalities to guess

    

# Goal: Make a quiz with several modes
# Mode 1: Type the names and it will highlight. Try to guess all.
# Mode 2: Type the name of the highlighted area.
# Mode 3: Click the named area.
# Each filterable by area/province/city