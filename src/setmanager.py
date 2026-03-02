import json, requests, bs4 , pandas, os
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed


class SetManager:
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

        res = requests.get(link, timeout=8)
        try:
            res.raise_for_status()
        except Exception as e:
            print(f"An error occurred: {e}")
        
        return json.loads(res.text)

    def create_set(self, set_name: str, dir, copy=False):
        
        set_data_git = self.create_parser(f"https://raw.githubusercontent.com/langstonstewart/PocketDex-Codex/refs/heads/main/set_data_git/{quote(set_name)}.json")

        for card in set_data_git:
            card['Quantity'] = 0
            card['Favorite'] = 0

        if not copy:
  
            with open(f"{dir}\\{set_name}.json", "w+") as set_file:
                json.dump(set_data_git, set_file, indent=4)
            
        else:
            return set_data_git


    def update_set(self, curr_set, set_name: str, dir):

        new_set = self.create_set(set_name, dir, True)

        if len(curr_set) != len(new_set) or "Favorite" not in curr_set[0].keys(): # type: ignore
            for i in range(len(curr_set)):
                new_set[i]["Quantity"] = curr_set[i]["Quantity"] # type: ignore
                if "Favorite" in curr_set[0].keys():
                    new_set[i]["Favorite"] = curr_set[i]["Favorite"] # type: ignore

            with open(f"{dir}\\{set_name}\\{set_name}.json", "w+") as set_file:
                
                json.dump(new_set, set_file, indent=4)
                return True

        else:
            return False


    def export_excel(self, fp, set_name, set_data: dict): # type: ignore
        df = {"Quantity": [dic["Quantity"] for dic in set_data],
              "Favorite": [dic["Favorite"] for dic in set_data]}
        
        pandas.DataFrame(df).to_excel(f"{fp}\\{set_name}\\{set_name}.xlsx", index=False)

        os.startfile(f"{fp}\\{set_name}")

    def import_excel(self, fp, excel_fp, set_name, set_data: dict):
        set_sheet = pandas.read_excel(excel_fp, keep_default_na=False)

        with open(f"{fp}\\{set_name}\\{set_name}.json", "r+") as set_file:
            set_data = json.load(set_file)

        for i in range(len(set_data)):
            set_data[i]['Quantity'] = int(set_sheet["Quantity"][i])
            set_data[i]['Favorite'] = int(set_sheet["Favorite"][i])

        if len(set_data) == len(set_sheet["Quantity"]):
            
            with open(f"{fp}\\{set_name}\\{set_name}.json", "w+") as set_file:
                json.dump(set_data, set_file, indent=4)
            return True
        return False