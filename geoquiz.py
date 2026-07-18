import geopandas as gpd
import matplotlib.pyplot as plt
import random # TODO: implement random selection modes
import datetime

class Geoquiz:
    provinces = ["경기", "강원", "충북", 
                      "충남", "전북", "전남", 
                      "경북", "경남", "제주"]
    def __init__(self, gpd_loc = "processed_korea.geojson"):
        self.gdf = self.read_gpd(gpd_loc)
        self.prov_choice = -1
        self.mode = 1

        # Select province
        self.province_selector()
        self.load_province(self.gdf)
        self.game_mode_selector()
        
    def read_gpd(self, file_name = "processed_korea.geojson"):
        # Read the dataset
        return gpd.read_file(file_name)
    
    def province_selector(self):
        # First we print the available provinces
        # Optional TODO: Later add modes for the metropolitan cities and their 구
        print("\n--- Available Provinces ---")
        for num, prov in enumerate(self.provinces):
            print(f"[{num+1}] {prov}")

        prov_choice = int(input("\nSelect a province number to filter (or type -1 for all of Korea): "))
        self.prov_choice = prov_choice

    def game_mode_selector(self):
        # Select the game mode
        print("\n--- Select game mode: ---")
        print("[1]: Type the names of the municipalities and the region will be highlighted after")
        print("[2]: Type the names of the highlighted municipalities")
        print("[3]: Type the names of the highlighted municipalities, choose from options")
        print("[4]: Click on the named municipality")
        mode = input("\nSelect mode: ").strip()

        # Currently only mode 1 exists: TODO: implement other modes and remove this
        if not (mode == "1" or mode == "2"):
            print("Note: currently only mode 1 and 2 are implemented, defaulting to 1")
            mode = "1"
        self.mode = mode
        
    def load_province(self, gdf):
        if self.prov_choice != -1:
            selected_province = self.provinces[self.prov_choice-1]
            quiz_gdf = gdf[gdf["region"] == selected_province].copy()
            print(f"Successfully loaded data for {selected_province}.")
        else:
            quiz_gdf = gdf.copy()
            print(f"Successfully loaded full South Korean data")

        self.quiz_gdf = quiz_gdf
    
    def review(self, ax, total_municipalities, guessed_indices, score = None):
        # --- STOP / END REVIEW PHASE ---
        print("\n--- Review Phase ---")
        print("Revealing missed territories in red... Type 'exit' or '종료' in the terminal to close.")
        if not score:
            score = len(guessed_indices)
        # Identify what was left over and mark state to '2' (triggers color change)
        # self.quiz_gdf.loc[~self.quiz_gdf.index.isin(guessed_indices), 'status'] = 4

        # Final render for review
        ax.clear()

        self.quiz_gdf.plot(column='status', ax=ax, cmap='bwr', edgecolor='dimgray', vmin=0, vmax=2)


        # Label EVERYTHING now, using color distinctions for readability
        for idx, row in self.quiz_gdf.iterrows():
            is_guessed = idx in guessed_indices
            
            text_color = "darkblue" if is_guessed else "darkred"
            bg_color = "white" if is_guessed else "mistyrose"
            
            # Extract centroid coordinates on the fly from the geometry column
            centroid = row['geometry'].centroid
            ax.text(centroid.x, centroid.y, row['name'], 
                    fontsize=8, ha='center', va='center', weight='bold', color=text_color,
                    bbox=dict(boxstyle="round,pad=0.2", fc=bg_color, ec=text_color, alpha=0.8, lw=0.5))

        ax.set_title(f"Final Score: {score} / {total_municipalities}\nReviewing missed regions. Type 'exit' or '종료' to quit.")
        plt.draw()

    def save(self):
        save = input("Do you wish to save your results? [y/n]")
        if save.lower() == "Y":
            self.quiz_gdf.to_file(f"dresults-{str(datetime.date.today())}-mode{self.mode}({self.prov_choice}).geojson")
            print("Saving results....")

    def run(self):
        # Set font for Windows
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False  # Fixes negative signs breaking on plots

        # Initialize the plot
        plt.ion()
        fig, ax = plt.subplots(figsize=(9, 9))

        # Gamemode 1: Type names of regions and the region will be highlighted
        if self.mode == "1":
            # Setup pre-game variables
            guessed_indices = set()
            self.quiz_gdf["status"] = 0 # Color for the guessed municipalities will be different based on this
            total_municipalities = len(self.quiz_gdf) # Total number of municipalities to guess
            game_active = True # Used for review after stopping the game

            # Start our loop until we manually stop or find all municipalities
            while (game_active and (len(guessed_indices) < total_municipalities)):
                ax.clear()
                
                # Render map using custom values mapping to colors
                self.quiz_gdf.plot(column='status', ax=ax, cmap='Set3', edgecolor='darkgray', vmin=0, vmax=2)
                # Add text names dynamically to guessed municipalities
                for idx, row in self.quiz_gdf.iterrows():
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
                match = self.quiz_gdf[self.quiz_gdf['name'] == guess]
                if not match.empty:
                    match_indices = match.index.tolist()

                    # If we found a new one, add it to our set
                    if not set(match_indices).issubset(guessed_indices):
                        print(f"Correct! Found {guess}")
                        guessed_indices.update(match_indices)
                        self.quiz_gdf.loc[match_indices, 'status'] = 1
                    else:
                        print("You already found that one!")
                # Else, it is wrong
                else:
                    print("Not found, try again.")

            # Identify what was left over and mark state to '2' (triggers color change)
            self.quiz_gdf.loc[~self.quiz_gdf.index.isin(guessed_indices), 'status'] = 2

            self.review(ax, total_municipalities, guessed_indices)

            self.save()
            while True:
                leave = input("\nType 'exit' or '종료' to quit the application: ").strip().lower()
                if leave == "exit" or leave == "종료":
                    break

            plt.ioff()
            plt.close()
            print("Session closed.")

        # Gamemode 2: Type the names of the highlighted region
        if self.mode == "2":
            # Setup pre-game variables
            guessed_indices = set()
            all_municipality_names = self.quiz_gdf["name"].to_list()
            self.quiz_gdf["status"] = 0 # Color for the guessed municipalities will be different based on this
            total_municipalities = len(self.quiz_gdf) # Total number of municipalities to guess
            game_active = True # Used for review after stopping the game
            score = 0

            # Start our loop until we manually stop or find all municipalities
            while (game_active and (len(all_municipality_names) > 0)):
                ax.clear()

                # Pick one random region to highlight
                target = random.choice(all_municipality_names)
                all_municipality_names.remove(target)
                
                self.quiz_gdf.loc[self.quiz_gdf['name'] == target, "status"] = 3
                
                answer_guessed = False
                while not answer_guessed:
                    # Render map using custom values mapping to colors
                    self.quiz_gdf.plot(column='status', ax=ax, cmap='Set3', edgecolor='darkgray', vmin=0, vmax=4)
                    # Add text names dynamically to guessed municipalities
                    for idx, row in self.quiz_gdf.iterrows():
                        if idx in guessed_indices:
                            # Extract centroid coordinates on the fly from the geometry column
                            centroid = row['geometry'].centroid
                            ax.text(centroid.x, centroid.y, row['name'], 
                                    fontsize=8, ha='center', va='center', weight='bold',
                                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7))
                    
                    ax.set_title(f"Guessed: {score} / {total_municipalities}\nType 'stop' or '그만' to finish and review.\nType 'next' or '다음' to skip the current region.")

                    plt.draw()
                    plt.pause(0.1)
                    
                    # Get the user guess
                    guess = input("\nEnter the county's name or type '그만' to quit: ").strip().lower()

                    # If the user wants to stop, continue to review
                    if guess == "stop" or guess == "그만":
                        game_active = False
                        break
                    if guess == "next" or guess == "다음":
                        match = self.quiz_gdf[self.quiz_gdf['name'] == target]
                        match_indices = match.index.tolist()

                        # If we found a new one, add it to our set
                        print(f"Skipped {target}")
                        guessed_indices.update(match_indices)
                        self.quiz_gdf.loc[match_indices, 'status'] = 1
                        answer_guessed = True
                    # Check if there are any matches (i.e. user is correct)
                    elif guess == target:
                        match = self.quiz_gdf[self.quiz_gdf['name'] == guess]
                        match_indices = match.index.tolist()
                        score = score + len(match_indices)

                        # If we found a new one, add it to our set
                        print(f"Correct! Found {guess}")
                        guessed_indices.update(match_indices)
                        self.quiz_gdf.loc[match_indices, 'status'] = 2
                        answer_guessed = True
                        break
                    # Else, it is wrong
                    else:
                        print("Sorry, this is the wrong area!")

            # Swap around the color pallete so that red = wrong, white = skipped and blue = correct
            self.quiz_gdf.loc[self.quiz_gdf["status"] == 3, 'status'] = 1
            self.quiz_gdf.loc[self.quiz_gdf["status"] == 0, 'status'] = 3
            self.quiz_gdf.loc[self.quiz_gdf["status"] == 2, 'status'] = 0
            self.quiz_gdf.loc[self.quiz_gdf["status"] == 3, 'status'] = 2
            self.review(ax, total_municipalities, guessed_indices, score)


            self.save()

            while True:
                leave = input("\nType 'exit' or '종료' to quit the application: ").strip().lower()
                if leave == "exit" or leave == "종료":
                    break
            plt.ioff()
            plt.close()
            print("Session closed.")

gq = Geoquiz()
gq.run()