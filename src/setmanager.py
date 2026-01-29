import json, requests, bs4 , pandas, os

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

        # bandage until site fixes
        if set_name == "Mega Rising (B1)":
            card_rarities.insert(276, "2 Star")
        elif set_name == "Fantastical Parade (B2)":
            card_rarities.insert(135, "3 Diamond")
        
        card_ids = [str(i).zfill(3) for i in range(1, len(card_names) + 1)]

        try:
            img_site = requests.get(f"https://pocket.limitlesstcg.com/cards/{set_id}")
            img_site.raise_for_status()
            card_imgs = [f"https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/pocket/{set_id}/{set_id}_{card_id}_EN_SM.webp" for card_id in card_ids]
        except Exception:
            card_imgs = [f"https://www.serebii.net/tcgpocket/{f_name}/{int(card_id)}.jpg" for card_id in card_ids]
        

        for i in range(len(card_ids)):
            set_dict = {}
            set_dict["ID"] = f"{set_id}-{card_ids[i]}"
            set_dict["Name"] = card_names[i]
            set_dict["Rarity"] = card_rarities[i]
            set_dict["Image"] = card_imgs[i]
            set_dict["Quantity"] = 0
            frame.append(set_dict)

        df = {"ID": card_ids,
              "Name": card_names,
              "Rarity": card_rarities,
              "Image": card_imgs,
              "Quantity": [0 for i in range(len(card_names))]}
        
        with open(f"{dir}\\{set_name}.json", "w+") as set_file:
            json.dump(frame, set_file, indent=4)
       

    def export_excel(self, fp, set_name, set_data: dict): # type: ignore
        df = {"ID": [dic["ID"] for dic in set_data],
              "Name": [dic["Name"] for dic in set_data],
              "Rarity": [dic["Rarity"] for dic in set_data],
              "Image": [dic["Image"] for dic in set_data],
              "Quantity": [dic["Quantity"] for dic in set_data]}
        
        pandas.DataFrame(df).to_excel(f"{fp}\\{set_name}\\{set_name}.xlsx", index=False)

        os.startfile(f"{fp}\\{set_name}")

    def import_excel(self, fp, excel_fp, set_name, set_data: dict):
        set_sheet = pandas.read_excel(excel_fp, keep_default_na=False)

        import_list = []

        for i in range(len(set_data)):
            card_data = {}
            card_data["ID"] = set_sheet["ID"][i]
            card_data["Name"] = set_sheet["Name"][i]
            card_data["Rarity"] = set_sheet["Rarity"][i]
            card_data["Image"] = set_sheet["Image"][i]
            card_data["Quantity"] = int(set_sheet["Quantity"][i])
            import_list.append(card_data)

        if len(set_data) == len(set_sheet["ID"]):
            
            with open(f"{fp}\\{set_name}\\{set_name}.json", "w+") as set_file:
                json.dump(import_list, set_file, indent=4)
            return True
        return False

        


        



        
        
        
        

        





            