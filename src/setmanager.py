import json, requests, bs4

class SetManager:
    def __init__(self) -> None:
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

        res = requests.get(link)
        try:
            res.raise_for_status()
        except Exception as e:
            print(f"An error occurred: {e}")
        
        return bs4.BeautifulSoup(res.text, 'html.parser')

    def create_set(self, set_name: str, set_id, dir):
        frame = []
        f_name = set_name.split()
        del f_name[-1]
        name_filter = " ".join(f_name)
        f_name = "".join(f_name).lower()
        self.main_link = f"https://www.serebii.net/tcgpocket/{f_name}/"
        main_page = self.create_parser(self.main_link)
        
        card_names = [name.get_text().strip() for name in main_page.select('tr td.cen a') if name.get_text().strip() and name_filter.lower() not in name.get_text().strip().lower()]

        card_rarities = [self.rarity_dict[card.get('src')] for card in main_page.select('tr td img') if any(rar in card.get('src', '') for rar in self.rarity_filter)] # type: ignore
        if not card_rarities:
            card_rarities = ["N/A" for i in range(1, len(card_names) + 1)]

        # bandage until fix
        if set_name == "Mega Rising (B1)":
            card_rarities.insert(276, "2 Star")
        
        card_ids = [str(i).zfill(3) for i in range(1, len(card_names) + 1)]

        card_imgs = [f"https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/pocket/{set_id}/{set_id}_{card_id}_EN_SM.webp" for card_id in card_ids]

        for i in range(len(card_ids)):
            set_dict = {}
            set_dict["ID"] = f"{set_id}-{card_ids[i]}"
            set_dict["Name"] = card_names[i]
            set_dict["Rarity"] = card_rarities[i]
            set_dict["Image"] = card_imgs[i]
            set_dict["Quantity"] = 0
            frame.append(set_dict)
        
        with open(f"{dir}\\{set_name}.json", "w+") as set_file:
            json.dump(frame, set_file, indent=4)





            