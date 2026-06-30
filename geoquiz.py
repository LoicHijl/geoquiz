import geopandas as gpd

# Read the dataset
gdf = gpd.read_file("processed_korea.geojson")

# Map to provinces/cities
provinces = ["경기", "강원", "충북", 
             "충남", "전북", "전남", 
             "경북", "경남", "제주"]

# User selections:
# Province - list of options/full country
# Mode - see later comments

# First we print the available provinces
# Optional TODO: Later add modes for the metropolitan cities and their 구
print("\n--- Available Provinces ---")
for num, prov in enumerate(provinces):
    print(f"[{num+1}] {prov}")

prov_choice = int(input("\nSelect a province number to filter (or type -1 for all of Korea): "))

if prov_choice != -1:
    selected_province = provinces[prov_choice-1]
    quiz_gdf = gdf[gdf["region"] == selected_province].copy()
    print(f"Successfully loaded data for {selected_province}.")
else:
    quiz_gdf = gdf.copy()
    print(f"Successfully loaded full South Korean data")

# Select the game mode
print("\n--- Select game mode: ---")
print("[1]: Type the names of the municipalities and the region will be highlighted after")
print("[2]: Type the names of the highlighted municipalities")
print("[3]: Click on the named municipality")
mode = input("\nSelect mode: ").strip()

# Currently only mode 1 exists: TODO: implement other modes and remove this
print("Note: currently only mode 1 is implemented, defaulting to 1")
mode = "1"
