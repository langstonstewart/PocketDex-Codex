import json, requests, bs4 , pandas, os
from concurrent.futures import ThreadPoolExecutor, as_completed


class SetCreator:
    def __init__(self) -> None:
        self.http = requests.Session()
        self.http.headers.update({"User-Agent": "PocketDex-Codex/2.x"})
       

        self.rarity_filter = ["diamond1", "diamond2", "diamond3", "diamond4", "star1", 
                         "star2", "star3", "shiny1", "shiny2", "crown"]
        
        self.rarity_dict = {"/tcgpocket/image/diamond1.png": "1 Diamond",
                            "/tcgpocket/image/diamond2.png": "2 Diamond",
                            "/tcgpocket/image/diamond3.png": "3 Diamond",
                            "/tcgpocket/image/diamond4.png": "4 Diamond",
                            "/tcgpocket/image/star1.png": "1 Star",
                            "/tcgpocket/image/star2.png": "2 Star",
                            "/tcgpocket/image/star3.png": "3 Star",
                            "/tcgpocket/image/shiny1.png": "1 Shiny",
                            "/tcgpocket/image/shiny2.png": "2 Shiny",
                            "/tcgpocket/image/crown.png": "Crown"
        }

    def create_parser(self, link):

        res = self.http.get(link, timeout=8)
        try:
            res.raise_for_status()
        except Exception as e:
            print(f"An error occurred: {e}")
        
        return bs4.BeautifulSoup(res.text, 'html.parser')

    def create_set(self, set_name: str, set_id, dir, copy=False):

        print(f"Scraping {set_name} ({set_id})..")
        frame = []
        self.f_name = set_name.split()
        
        name_filter = " ".join(self.f_name)
        self.f_name = "".join(self.f_name).lower()
        self.main_link = f"https://www.serebii.net/tcgpocket/{self.f_name}/"
        main_page = self.create_parser(self.main_link)
        
        self.card_names = [name.get_text().strip() for name in main_page.select('tr td.cen a') if name.get_text().strip() and name_filter.lower() not in name.get_text().strip().lower()]

        card_rarities = [self.rarity_dict[card.get('src')] for card in main_page.select('tr td img') if any(rar in card.get('src', '') for rar in self.rarity_filter)] # type: ignore
        if not card_rarities:
            card_rarities = ["N/A" for i in range(1, len(self.card_names) + 1)]

        # bandages until site fixes
        if set_name == "Mega Rising":
            card_rarities.insert(276, "2 Star")

        elif set_name == "Crimson Blaze":
            for i in [13, 76, 87]:
                self.card_names[i] = "Mega Charizard Y ex"
            

        elif set_name == "Fantastical Parade":
            card_rarities.insert(135, "3 Diamond")
        
        card_ids = [str(i).zfill(3) for i in range(1, len(self.card_names) + 1)]

        try:
            img_site = requests.get(f"https://pocket.limitlesstcg.com/cards/{set_id}")
            img_site.raise_for_status()
            card_imgs = [f"https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/pocket/{set_id}/{set_id}_{card_id}_EN_SM.webp" for card_id in card_ids]
        except Exception:
            card_imgs = [f"https://www.serebii.net/tcgpocket/{self.f_name}/{int(card_id)}.jpg" for card_id in card_ids]
        

        card_sum_map = self.fetch_extra_card_info(set_id, card_ids)

        print(card_sum_map)

        for i in range(len(card_ids)):
            set_dict = {}
            set_dict["ID"] = f"{set_id}-{card_ids[i]}"
            set_dict["Name"] = self.card_names[i]
            set_dict["Rarity"] = card_rarities[i]
            set_dict["Image"] = card_imgs[i]

            for key, value in card_sum_map[card_ids[i]].items():

                set_dict[key] = value

            frame.append(set_dict)

        
        if not copy:

            
            
            with open(f"{dir}", "w+", encoding='UTF-8') as set_file:
                json.dump(frame, set_file, indent=4)

        else:
            return frame

    def scrape_card_data(self, set_id, card_id):
        self.card_data_dict = {}

        try:
            card_data_link = f"https://pocket.limitlesstcg.com/cards/{set_id}/{str(int(card_id))}"
            
            self.card_data_dict["Summary-Available"] = 1
            card_page = self.create_parser(card_data_link)

            card_type_data = [" ".join(text.get_text().strip().replace("\n", "").split()).split("-") for text in card_page.select('p.card-text-type')]

            print(f"{card_id} - {card_type_data[0][0].strip()}")

            ill_data = [text.get_text().strip() for text in card_page.select('div.card-text-artist a')]

            

            if 'Trainer' == card_type_data[0][0].strip():
                desc_data = [text.get_text().strip().replace("\n", "") for text in card_page.select('div.card-text-section')]
                
                self.card_data_dict["Card-Type"] = card_type_data[0][-1].strip()
                self.card_data_dict["Description"] = desc_data[-2]
                self.card_data_dict["Illustrator"] = ill_data[0]
                

            else:
                basic_data = ["".join(text.get_text().split()) for text in card_page.select('p.card-text-title')]
              
                f_basic_data = basic_data[0].replace(f"{self.card_names[int(card_id) - 1].replace(" ", "")}-", "")
                
                flavor_txt_data = [text.get_text().strip().replace("\n", "") for text in card_page.select('div.card-text-flavor')]
                w_r_data = ["-".join(text.get_text().split()) for text in card_page.select('div p.card-text-wrr')]
               
               
                move_data = [text.get_text().strip().split() for text in card_page.select('p.card-text-attack-info')]
                move_effect_data = [text.get_text().strip().replace("\n", "") for text in card_page.select('p.card-text-attack-effect')]
                ability_data = [" ".join(text.get_text().split()) for text in card_page.select('p.card-text-ability-info')]
                ability_desc_data = [" ".join(text.get_text().split()) for text in card_page.select('p.card-text-ability-effect')]

                self.card_data_dict["Card-Type"] = card_type_data[0][0].strip().replace("\u00e9", "e")
                self.card_data_dict["Stage"] = card_type_data[0][1].strip()
                self.card_data_dict["Type"] = f_basic_data.split("-")[0]
                self.card_data_dict["HP"] = f_basic_data.split("-")[1].replace("HP", "")
                self.card_data_dict["Ability"] = ability_data[0].replace("Ability: ", "") if ability_data else None
                self.card_data_dict["Ability-Effect"] = ability_desc_data[0] if ability_desc_data else None
                self.card_data_dict["Moves"] = [" ".join(move[1:-1]) if not move[-1].isalpha() else " ".join(move[1:]) for move in move_data]
                self.card_data_dict["Move-Energy"] = ["".join(move[0]) if move_data else None for move in move_data]
                self.card_data_dict["Move-Damage"] = ["".join(move[-1]) if not move[-1].isalpha() else None for move in move_data]
                self.card_data_dict["Effects"] = ["".join(move) if move_effect_data else None for move in move_effect_data]
                self.card_data_dict["Weakness"] = w_r_data[0].split("-")[1].capitalize() if w_r_data[0].split("-")[1].capitalize() != "None" else None
                self.card_data_dict["Retreat-Cost"] = w_r_data[0].split("-")[3] if w_r_data else None
              
                self.card_data_dict["Ex-Rule"] = w_r_data[-1].replace("Mega-Evolution-ex-rule:", "").replace("ex-rule:", "").replace("-", " ").lstrip() if "ex-rule:" in w_r_data[-1] else None
    
                self.card_data_dict["Flavor-Text"] = flavor_txt_data[0] if flavor_txt_data else None
                self.card_data_dict["Illustrator"] = ill_data[0]
            
        except Exception as e:
            print(f"An error occurred scraping: {e}. Pulling from serebii..")
            self.card_data_dict["Image"] = f"https://www.serebii.net/tcgpocket/{self.f_name}/{int(card_id)}.jpg"
            self.card_data_dict["Summary-Available"] = 0

     
        return self.card_data_dict

    def fetch_extra_card_info(self, set_id, card_ids, max_workers=1):
        if not card_ids:
            return {}

        info_map = {}
        worker_count = min(max_workers, len(card_ids))
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = {
                executor.submit(self.scrape_card_data, set_id, card_id): card_id
                for card_id in card_ids
            }
            for future in as_completed(futures):
                card_id = futures[future]
                try:
                    info_map[card_id] = future.result()
                except Exception:
                    info_map[card_id] = []
        print(info_map)
        return info_map



    
    

        
 



scrape_set_name = "Paldean Wonders"

scrape_set_id = "B2a"

SetCreator().create_set(scrape_set_name, scrape_set_id, f"{scrape_set_name} ({scrape_set_id}).json")





            
