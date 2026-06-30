import geopandas as gpd
import matplotlib.pyplot as plt
import random # TODO: implement random selection modes

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

# Set font for Windows
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False  # Fixes negative signs breaking on plots

# Initialize the plot
plt.ion()
fig, ax = plt.subplots(figsize=(9, 9))

# Gamemode 1: Type names of regions and the region will be highlighted
if mode == "1":
    # Setup pre-game variables
    guessed_indices = set()
    quiz_gdf["status"] = 0 # Color for the guessed municipalities will be different based on this
    total_municipalities = len(quiz_gdf) # Total number of municipalities to guess
    game_active = True # Used for review after stopping the game

    # Start our loop until we manually stop or find all municipalities
    while (game_active and (len(guessed_indices) < total_municipalities)):
        ax.clear()
        
        # Render map using custom values mapping to colors
        quiz_gdf.plot(column='status', ax=ax, cmap='Set3', edgecolor='darkgray', vmin=0, vmax=2)
        # Add text names dynamically to guessed municipalities
        for idx, row in quiz_gdf.iterrows():
            if idx in guessed_indices:
                # Extract centroid coordinates on the fly from the geometry column
                centroid = row['geometry'].centroid
                ax.text(centroid.x, centroid.y, row['name'], 
                        fontsize=8, ha='center', va='center', weight='bold',
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7))
        
        ax.set_title(f"Guessed: {len(guessed_indices)} / {total_municipalities}\nType 'stop' or '그만' to finish and review.")

        plt.draw()
        plt.pause(0.1)
        
        # Get the user guess
        guess = input("\nEnter a county name: ").strip().lower()

        # If the user wants to stop, continue to review
        if guess == "stop" or guess == "그만":
            game_active = False
            break

        # Check if there are any matches (i.e. user is correct)
        match = quiz_gdf[quiz_gdf['name'] == guess]
        if not match.empty:
            match_indices = match.index.tolist()

            # If we found a new one, add it to our set
            if not set(match_indices).issubset(guessed_indices):
                print(f"Correct! Found {guess}")
                guessed_indices.update(match_indices)
                quiz_gdf.loc[match_indices, 'status'] = 1
            else:
                print("You already found that one!")
        # Else, it is wrong
        else:
            print("Not found, try again.")

    # --- STOP / END REVIEW PHASE ---
    print("\n--- Review Phase ---")
    print("Revealing missed territories in red... Type 'exit' or '종료' in the terminal to close.")

    # Identify what was left over and mark state to '2' (triggers color change)
    quiz_gdf.loc[~quiz_gdf.index.isin(guessed_indices), 'status'] = 2

    # Final render for review
    ax.clear()
    quiz_gdf.plot(column='status', ax=ax, cmap='bwr', edgecolor='dimgray', vmin=0, vmax=2)

    # Label EVERYTHING now, using color distinctions for readability
    for idx, row in quiz_gdf.iterrows():
        is_guessed = idx in guessed_indices
        
        text_color = "darkblue" if is_guessed else "darkred"
        bg_color = "white" if is_guessed else "mistyrose"
        
        # Extract centroid coordinates on the fly from the geometry column
        centroid = row['geometry'].centroid
        ax.text(centroid.x, centroid.y, row['name'], 
                fontsize=8, ha='center', va='center', weight='bold', color=text_color,
                bbox=dict(boxstyle="round,pad=0.2", fc=bg_color, ec=text_color, alpha=0.8, lw=0.5))

    ax.set_title(f"Final Score: {len(guessed_indices)} / {total_municipalities}\nReviewing missed regions. Type 'exit' to quit.")
    plt.draw()

    while True:
        leave = input("\nType 'exit' or '종료' to quit the application: ").strip().lower()
        if leave == "exit" or leave == "종료":
            break

    plt.ioff()
    plt.close()
    print("Session closed.")

   