import os, json, datetime, copy
from src import setmanager, themes, image_manager
from src.resource_path import resource_path
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QToolButton, QVBoxLayout, QHBoxLayout, QGridLayout, QStackedLayout, QMainWindow, QSizePolicy, QScrollArea, QGraphicsOpacityEffect, QGraphicsColorizeEffect, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QSize, QUrl, QTimer, QObject, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QIcon, QDesktopServices, QPixmap, QColor, QKeySequence, QShortcut
from math import ceil
from functools import partial
from PyQt6.QtNetwork import QNetworkAccessManager
import random




class Application(QMainWindow):
    def __init__(self) -> None:
        self.app = QApplication([])
        super().__init__()

        self.img_cache_dict = {}

        self.app_init = False
        
        self.card_img_dict = {}

        self.widget_list = []

        self.ui_button_list = []

        self.set_manager = setmanager.SetManager()
        self.themes = themes.Themes()
        self.IM = image_manager.ImageManager()
        self.settings = self.init_app_data()
        self.resize(1400, 1150)
        self.setWindowIcon(QIcon(resource_path(f"src/images/ui/logo_icon.png")))
        self.setWindowTitle(f"PocketDex Codex v{self.settings['UserData']['version']}")

        self.set_col_count = 6

        self.col_count = self.settings['UserData']['col_count']

        self.set_inverse = self.settings['UserData']['set_inverse']

        self.bb_dict = {}

        self.rarity_dict = {}

        self.set_sep_lens = {4: 1200, 
                             6: 1700,
                             8: 2250}

                             

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        

        self.main_font = QFont("Gill Sans MT", 10, QFont.Weight.Normal, italic=False)
        self.main_font_bold = QFont("Gill Sans MT", 10, QFont.Weight.Bold, italic=False)

        self.fullscreen = False

        self.container = QWidget()

        self.previous_widget = None

        self.stacked_layout = QStackedLayout(self.container)

        self.cd_widget = QWidget() 

        self.widget_list.append(self.cd_widget)

        self.main_layout = None

        self.set_main_layout = None
        
        self.cd_layout = None

        self.card_grid = None

        self.fav_widget = QWidget()
            
        self.fav_main_layout = QVBoxLayout()

        self.fav_widget.setLayout(self.fav_main_layout)

        self.scroll_area.setWidget(self.container)

        self.main_widget = QWidget()
        self.widget_list.append(self.main_widget)
        self.setCentralWidget(self.scroll_area)

        self.keyPressEvent = self.toggle_fullscreen # type: ignore

        self.mode = self.settings['UserData']['theme']
        self.switch_scrollbar()
        

    def on_button_enter(self, button: QPushButton, event):
            button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

            
    def on_button_leave(self, button: QPushButton, event):
        button.setCursor(QCursor(Qt.CursorShape.ArrowCursor))


    def toggle_fullscreen(self, event):
            if event.key() == Qt.Key.Key_F11:
                if self.fullscreen:
                    self.showNormal()  
                    self.fullscreen = False
                else:
                    self.showFullScreen()  
                    self.fullscreen = True
            else:
                QMainWindow.keyPressEvent(self, event)


    def init_app_data(self):
        with open(resource_path(f"src\\app_data\\app_settings.json"), "r+") as settings_file:
            return json.load(settings_file)

    def init_set_dir(self):
        self.project_dir = resource_path(f"src\\app_data")
        self.local_doc = os.path.join(os.path.expanduser("~"), "Documents", "PocketDex Codex")

        os.makedirs(self.local_doc, exist_ok=True)

        self.category_list = [("TCG", "set_list_tcg.json"), ("TCG Pocket", "set_list_pocket.json")]

        category_dirs = []

        for category in self.category_list:
            
            os.makedirs(f"{self.local_doc}\\{category[0]}", exist_ok=True)
            category_dirs.append(f"{self.local_doc}\\{category[0]}")
        
            with open(f'{self.project_dir}\\{category[1]}', 'r+', encoding="UTF-8") as set_file:
                self.set_dict = json.load(set_file) # type: dict

            for key in self.set_dict.keys():
                
                os.makedirs(f"{self.local_doc}\\{category[0]}\\{key}", exist_ok=True)
                for set in self.set_dict[key]:

                    set_dir = f"{self.local_doc}\\{category[0]}\\{key}\\{set["Name"]}"
                    
                    os.makedirs(set_dir, exist_ok=True)

                    if not os.listdir(set_dir):
                        
                        self.set_manager.create_set(set["Name"], category[0], key, set_dir)

            self.create_favorites_folder(f"{self.local_doc}\\{category[0]}")

           
            
        
    def create_favorites_folder(self, dir):
        os.makedirs(f"{dir}\\favorites", exist_ok=True)

        if not os.listdir(f"{dir}\\favorites"):
            with open(f"{dir}\\favorites\\favorites.json", "w+") as f_file:
                json.dump([], f_file, indent=4)

        with open(f"{dir}\\favorites\\favorites.json", "r") as f_file:
            self.favorite_list = json.load(f_file)

    


    def init_cache(self):
        self.init_loading_images_page()
        self.show()

        self.app.processEvents()
        self.network_manager = QNetworkAccessManager()

        for set_list in self.category_list:

            self.set_fp = f"{self.project_dir}\\{set_list[1]}"

            with open(self.set_fp, "r+") as set_file:
                self.set_dict = json.load(set_file)

                for key in self.set_dict:
                        
                    for set in self.set_dict[key]:

                        set_name = set['Name'].split(" (")[0].replace(" ", "").lower()

                        if set['SetID'] not in self.IM.logo_dict.keys():

                            if "Promo" in set.keys():
                                set_pixmap = QPixmap(resource_path(f"src/images/set_logo/{set_list[0]}/black_star_promo.png"))
                            else:
                                set_pixmap = QPixmap(resource_path(f"src/images/set_logo/{set_list[0]}/{set_name}.png"))

                            self.IM.logo_dict[set['SetID']] = set_pixmap

        self.cache_finished({})

    def cache_finished(self, cache_dict):
        self.cache_dict = cache_dict
        if not self.app_init:
            self.stacked_layout.setCurrentWidget(self.main_menu_widget)
            self.app_init = True
        self.show()


    def init_loading_images_page(self):
        self.li_widget = QWidget()    
        self.li_layout = QVBoxLayout()
        self.li_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.li_widget.setLayout(self.li_layout)
        self.li_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)
        self.li_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.display_loading_images_page()

    def display_loading_images_page(self):

        self.seperator(self.li_layout, 700)

        self.icon_layout = QVBoxLayout()
        self.icon_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.li_layout.addLayout(self.icon_layout)
        
        codex_icon = QLabel("")
        codex_icon.setPixmap(self.IM.codex_icon_mini[self.mode].scaled(175, 175, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        codex_icon.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        codex_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.icon_layout.addWidget(codex_icon)

        self.li_txt_layout = QHBoxLayout()
        self.li_txt_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.li_layout.addLayout(self.li_txt_layout)

        
        loading_icon_label = QLabel("")
        loading_txt_label = QLabel("Preparing application data..")

    
        
        loading_icon_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        loading_icon_label.setProperty("class", "header2")
        loading_icon_label.setPixmap(self.IM.loading_icon[self.mode].scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    
        self.li_txt_layout.addWidget(loading_icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        loading_txt_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        loading_txt_label.setProperty("class", "header2")
        loading_txt_label.setFont(self.main_font)

        self.li_txt_layout.addWidget(loading_txt_label, alignment=Qt.AlignmentFlag.AlignHCenter)
    
        self.stacked_layout.addWidget(self.li_widget)

        loading_txt_hint = QLabel(f"Please wait...")
        loading_txt_hint.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        loading_txt_hint.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        loading_txt_hint.setProperty("class", "header2")
        loading_txt_hint.setFont(self.main_font)
        self.li_layout.addWidget(loading_txt_hint)

        self.seperator(self.li_layout, 700)

        
       
        self.stacked_layout.setCurrentWidget(self.li_widget)


    def title(self):
        self.title_layout = QHBoxLayout()
        self.h2_layout = QVBoxLayout()
        self.title_layout.setSpacing(0)
        self.title_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.header_layout.addLayout(self.title_layout)
        self.h2_layout.setSpacing(0)
        self.h2_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.header_layout.addLayout(self.h2_layout)

        
    
        self.h2 = QLabel("- An application for Pokémon Trading Card Game ™ -")

        self.title_icon = QLabel("")
        self.title_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.title_icon.setPixmap(self.IM.codex_icon[self.mode].scaled(650, 350, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self.title_icon.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.h2.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.h2.setProperty("class", "header2")
        self.h2.setFont(self.main_font)

        self.title_layout.addWidget(self.title_icon)
    
        self.h2_layout.addWidget(self.h2)

        self.seperator(self.header_layout, 715)

        self.h3_layout = QHBoxLayout()
        self.h3_layout.setSpacing(0)
        self.h3_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.header_layout.addLayout(self.h3_layout)
        self.h3 = QLabel("Please select a TCG category:")
        self.h3.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.h3.setProperty("class", "header2")
        self.h3.setFont(self.main_font)
        self.h3_layout.addWidget(self.h3)

    def seperator(self, layout, width):
        self.seperator_layout = QHBoxLayout()
        self.seperator_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.seperator_layout.setSpacing(0)
        
        layout.addLayout(self.seperator_layout)
        
        seperator = QLabel("")
        
        seperator.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        seperator.setProperty("class", "header4")
        seperator.setMinimumWidth(width)
        seperator.setFixedHeight(25)
       
        self.seperator_layout.addWidget(seperator, alignment=Qt.AlignmentFlag.AlignHCenter)
        

    def calculate_total_quantity(self):
        
        return sum(1 for card in self.set_list if card["Quantity"] > 0)

    def print_set_title(self, set_name):

        self.set_fp = f"{self.local_doc}\\{self.category_dir}\\{self.series}\\{set_name}\\{set_name}.json"

        with open(self.set_fp, "r+") as set_file:
            self.set_list = json.load(set_file)
           

        self.set_header = QHBoxLayout()
        self.set_header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.set_main_layout.addLayout(self.set_header) # type: ignore

        self.data_header = QHBoxLayout()
        self.data_header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.set_main_layout.addLayout(self.data_header) # type: ignore

        for s in self.set_dict[self.series]:
            if s["Name"] == self.set_name:
                set_data =  s

        formatted_name = set_name.split()
        del formatted_name[-1]
        formatted_name = " ".join(formatted_name)

        set_title = QLabel(f"{formatted_name}")
        
        set_date = QLabel(f"{set_data["Release Date"]}")
        self.card_count = QLabel(f"{self.calculate_total_quantity()}/{len(self.set_list)} Cards")

        set_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        set_title.setProperty("class", "header1")
        set_title.setFont(self.main_font)
        self.set_header.addWidget(set_title)

        set_tag = QLabel(f"{set_data["SetID"]}")
        set_tag.setProperty("class", "Set_Tag")
        set_tag.setFont(self.main_font)
        set_tag.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.set_header.addWidget(set_tag)

        set_date.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        set_date.setProperty("class", "header2")
        set_date.setFont(self.main_font)
        self.data_header.addWidget(set_date)

        self.card_count.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.card_count.setProperty("class", "header2")
        self.card_count.setFont(self.main_font)
        self.data_header.addWidget(self.card_count)

    def init_main_menu(self):
        self.main_menu_widget = QWidget()
        self.widget_list.append(self.main_menu_widget)

        self.main_menu_layout = QVBoxLayout()
        self.main_menu_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)
        
        self.main_menu_widget.setLayout(self.main_menu_layout)

        self.header_layout = QVBoxLayout()
        self.header_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.main_menu_layout.addLayout(self.header_layout)
        
        self.stacked_layout.addWidget(self.main_menu_widget)

        

    def display_categories(self):

        self.cat_layout = QHBoxLayout()
        self.cat_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.header_layout.addLayout(self.cat_layout)

        cat_list = ((self.IM.tcg_logo, self.IM.tcg_pocket_logo))

        self.cat_layout.addStretch()

        for i in range(len(cat_list)):
            cat_button = QPushButton()
            cat_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            cat_button.setMaximumWidth(350)
            cat_button.setMaximumHeight(250)
            cat_button.setProperty("class", "Main_Button")
            cat_button.setIcon(QIcon(cat_list[i]))
            cat_button.setIconSize(QSize(500, 250))

            cat_button.clicked.connect(partial(self.display_sets, self.category_list[i][1])) # change 0 to i later

            self.cat_layout.addWidget(cat_button)
        
        self.cat_layout.addStretch()

        self.seperator(self.header_layout, 715)


    def display_sets(self, category):

        self.category_file_name = category

        with open(f'{self.project_dir}\\{category}', 'r+', encoding="UTF-8") as set_file:
                self.set_dict = json.load(set_file) # type: dict

        set_count = 0
        for key in self.set_dict.keys():
            set_count  += len(self.set_dict[key])

        if category == "set_list_tcg.json":
            self.category_dir = "TCG"
            
        elif category == "set_list_pocket.json":
            self.category_dir = "TCG Pocket"

        self.rarity_dict = {}

        date_text = f"{self.set_dict[list(self.set_dict.keys())[-1]][-2]["Release Date"]} - {self.set_dict[list(self.set_dict.keys())[0]][0]["Release Date"]} | {set_count} Sets"
        
        with open(f'{self.local_doc}\\{self.category_dir}\\favorites\\favorites.json', 'r+', encoding="UTF-8") as f_file:
                self.favorite_list = json.load(f_file) # type: dict


        title_dict = {"set_list_tcg.json": ("Pokemon Trading Card Game ™", self.IM.tcg_logo),
                      "set_list_pocket.json": ("Pokemon Trading Card Game Pocket ™", self.IM.tcg_pocket_logo)}
    
                
        self.main_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)

        existing_layout = self.main_widget.layout()
        if existing_layout is not None:
            self.clear_layout(existing_layout)  # type: ignore
            self.main_layout = existing_layout
        else:
            self.main_layout = QVBoxLayout()
            self.main_widget.setLayout(self.main_layout)

        if self.stacked_layout.indexOf(self.main_widget) == -1:
            self.stacked_layout.addWidget(self.main_widget)

        self.set_button_dict = {}

        category_title_layout = QHBoxLayout()
        category_title_layout.setSpacing(50)
        category_title_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addLayout(category_title_layout) # type: ignore

        img_layout = QVBoxLayout()
        img_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        category_title_layout.addLayout(img_layout)

        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        category_title_layout.addLayout(text_layout)


        self.title_icon = QLabel("")
        self.title_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.title_icon.setPixmap(title_dict[category][1].scaled(650, 350, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.title_icon.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        img_layout.addWidget(self.title_icon)

        category_label = QLabel(f"{title_dict[category][0]}")
        category_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        category_label.setProperty("class", "header_title")
        category_label.setFont(self.main_font)
        category_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        text_layout.addWidget(category_label)

        date_label = QLabel(f"")
        date_label.setText(date_text)
        date_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        date_label.setProperty("class", "header2")
        date_label.setFont(self.main_font)
        date_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        text_layout.addWidget(date_label)

        for key in (reversed(self.set_dict.keys()) if self.set_inverse else self.set_dict.keys()):

            self.seperator(self.main_layout, 1200)

            series_label = QLabel(f"{key}")
            series_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            series_label.setProperty("class", "header2")
            series_label.setFont(self.main_font)
            series_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

            self.main_layout.addWidget(series_label)
        
        
            self.set_layout = QGridLayout()
            self.set_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.set_layout.setSpacing(5)

            self.main_layout.addLayout(self.set_layout) # type: ignore

            col_length = self.set_col_count
            row_length = ceil(len(self.set_dict[key]) / col_length)
            current_set = len(self.set_dict[key]) - 1 if self.set_inverse else 0
            all_rows = False
            while True:
                if all_rows:
                    break
                for r in range(row_length):
                    if all_rows:
                        break
                    for c in range(col_length):

                        button_layout = QVBoxLayout()
                        button_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

                        self.set_layout.addLayout(button_layout, r, c)

                        button = QToolButton()
                      
                        button.setIcon(QIcon(self.IM.logo_dict[self.set_dict[key][current_set]['SetID']]))
                        button.setIconSize(QSize(156, 156))
                        button.setMaximumHeight(125)
                        
                        button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

                        button.setProperty("class", "Main_Button")
                        button.setFont(self.main_font)
                        
                        button.setProperty("Name", self.set_dict[key][current_set]['Name'])
                        button.setProperty("ID", self.set_dict[key][current_set]['SetID'])
                        button.setProperty("Series", f"{key}")

                        button.enterEvent = partial(self.on_button_enter, button) # type: ignore
                        button.leaveEvent = partial(self.on_button_leave, button) # type: ignore
                        
                        button.clicked.connect(self.clicked_set)

                        button_layout.addWidget(button)

                        self.set_button_dict[self.set_dict[key][current_set]['Name']] = button
                        
                        if self.set_inverse:
                            current_set -= 1
                            if current_set < 0:
                                all_rows = True
                                break
                        else:
                            current_set += 1
                            if current_set == len(self.set_dict[key]):
                                all_rows = True
                                break

            
        self.seperator(self.main_layout, 1200)


        self.init_back_button(self.main_layout, "Set_Page")

        self.create_favorite_cards_button()

        self.create_inverse_button()

        self.stacked_layout.setCurrentWidget(self.main_widget)


    def create_inverse_button(self):
        self.inverse_button = QPushButton(f"Sort by Newest.." if self.set_inverse else "Sort by Oldest..")
        self.ui_button_list.append((self.inverse_button, self.IM.sort_icon, None, None))
        self.inverse_button.setFont(self.main_font)
        self.inverse_button.setProperty("class", "Setting_Button")
        
        self.inverse_button.setIcon(QIcon(self.IM.sort_icon[self.mode]))
        self.inverse_button.setIconSize(QSize(36, 36))

        self.inverse_button.enterEvent = partial(self.on_button_enter, self.inverse_button)
        self.inverse_button.leaveEvent = partial(self.on_button_leave, self.inverse_button) # type: ignore
        
        self.inverse_button.clicked.connect(self.switch_set_inverse)

        self.bb_layout.addWidget(self.inverse_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

        self.bb_layout.addStretch()

    def switch_set_inverse(self):
        if self.set_inverse == 1:
            self.set_inverse = 0
            self.settings['UserData']['set_inverse'] = 0
            
        elif self.set_inverse == 0:
            self.set_inverse = 1
            self.settings['UserData']['set_inverse'] = 1
            
        with open(resource_path(f"src/app_data/app_settings.json"), "w+") as config_file:
                json.dump(self.settings, config_file, indent=4)

        self.go_back(self.main_layout)

        self.display_sets(self.category_file_name)

    def create_info_page(self):
        self.info_widget = QWidget()
        
        self.info_layout = QVBoxLayout()
        
        self.info_widget.setLayout(self.info_layout)
        
        self.info_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.info_header = QVBoxLayout()
        
        self.info_layout.addLayout(self.info_header)
        
        info_title = QLabel("")

        info_title.setPixmap(self.IM.codex_icon[self.mode].scaled(650, 350, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        info_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        info_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.info_header.addWidget(info_title)

        self.seperator(self.info_header, 1100)

        dis_label = QLabel('''DISCLAIMER: 
This application is a fan-made project intended for personal and educational purposes.
All rights, trademarks, and intellectual property related to Pokémon, including names, images,
and game mechanics, belong to The Pokémon Company, Nintendo, Game Freak, and Creatures Inc.
This project is not affiliated with or associated with these entities.''')
        dis_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        dis_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        dis_label.setProperty("class", "header2")
        dis_label.setFont(self.main_font)
        self.info_header.addWidget(dis_label)

        codex_icon = QLabel("")
        codex_icon.setPixmap(self.IM.codex_icon_mini[self.mode].scaled(175, 175, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        codex_icon.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        codex_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.info_header.addWidget(codex_icon)

        self.v_layout = QHBoxLayout()
        self.v_layout.setSpacing(0)  
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter) 
        self.info_header.addLayout(self.v_layout)
        

        v_label = QLabel(f"Version {self.settings['UserData']['version']}.  Work-in-Progress.")
        v_label.setProperty("class", "header2")
        v_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        v_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        v_label.setFont(self.main_font)

        self.v_layout.addWidget(v_label)

        self.github_layout = QHBoxLayout()
        self.github_layout.setSpacing(0)  
        self.github_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter) 

        self.info_header.addLayout(self.github_layout)
        
        c_label = QLabel(f"Programmed and created by ")
        c_label.setProperty("class", "header2")
        c_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        c_label.setFont(self.main_font)

        self.github_layout.addWidget(c_label)

        self.git_icon = QLabel(f"")
        self.ui_button_list.append((self.git_icon, self.IM.github_icon, 24, 24) )
        self.git_icon.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.git_icon.setPixmap(self.IM.github_icon[self.mode].scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self.github_layout.addWidget(self.git_icon)

        git_label = QLabel(f"Jevv")
        git_label.setProperty("class", "Link_Label")
        git_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        git_label.setFont(self.main_font)

        self.github_layout.addWidget(git_label)

        date_label = QLabel(f"© 2026")
        date_label.setProperty("class", "header2")
        date_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        date_label.setFont(self.main_font)

        self.github_layout.addWidget(date_label)

        self.pz_layout = QHBoxLayout()
        self.pz_layout.setSpacing(0)  
        self.pz_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter) 

        self.info_header.addLayout(self.pz_layout)
        
        c_label = QLabel(f"Set descriptions sourced from ")
        c_label.setProperty("class", "header2")
        c_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        c_label.setFont(self.main_font)

        self.pz_layout.addWidget(c_label)

        self.pz_icon = QLabel(f"")
        self.ui_button_list.append((self.pz_icon, self.IM.pz_icon, 24, 24))
        self.pz_icon.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.pz_icon.setPixmap(self.IM.pz_icon[self.mode].scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self.pz_layout.addWidget(self.pz_icon)

        pz_label = QLabel(f"Pokémon Zone")
        pz_label.setProperty("class", "Link_Label")
        pz_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        pz_label.setFont(self.main_font)

        self.pz_layout.addWidget(pz_label)

        pz_date_label = QLabel(f"© 2024 - 2026")
        pz_date_label.setProperty("class", "header2")
        pz_date_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        pz_date_label.setFont(self.main_font)

        self.pz_layout.addWidget(pz_date_label)

        self.serebii_layout = QHBoxLayout()
        self.serebii_layout.setSpacing(0)  
        self.serebii_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter) 

        self.info_header.addLayout(self.serebii_layout)
        
        c_label = QLabel(f"Data sourced from ")
        c_label.setProperty("class", "header2")
        c_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        c_label.setFont(self.main_font)

        self.serebii_layout.addWidget(c_label)

        self.serebii_icon = QLabel(f"")
        self.ui_button_list.append((self.serebii_icon, self.IM.serebii_icon, 24, 24))
        self.serebii_icon.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.serebii_icon.setPixmap(self.IM.serebii_icon[self.mode].scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self.serebii_layout.addWidget(self.serebii_icon)

        serebii_label = QLabel(f"Serebii")
        serebii_label.setProperty("class", "Link_Label")
        serebii_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        serebii_label.setFont(self.main_font)

        self.serebii_layout.addWidget(serebii_label)

        serebii_date_label = QLabel(f"© 1999 - 2026")
        serebii_date_label.setProperty("class", "header2")
        serebii_date_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        serebii_date_label.setFont(self.main_font)

        self.serebii_layout.addWidget(serebii_date_label)

        self.ltcg_layout = QHBoxLayout()
        self.ltcg_layout.setSpacing(0)  
        self.ltcg_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter) 

        self.info_header.addLayout(self.ltcg_layout)
        
        c_label = QLabel(f"Images sourced from ")
        c_label.setProperty("class", "header2")
        c_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        c_label.setFont(self.main_font)

        self.ltcg_layout.addWidget(c_label)

        self.ltcg_icon = QLabel(f"")
        self.ui_button_list.append((self.ltcg_icon, self.IM.ltcg_icon, 24, 24))
        self.ltcg_icon.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.ltcg_icon.setPixmap(self.IM.ltcg_icon[self.mode].scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self.ltcg_layout.addWidget(self.ltcg_icon)

        ltcg_label = QLabel(f"Limitless TCG")
        ltcg_label.setProperty("class", "Link_Label")
        ltcg_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        ltcg_label.setFont(self.main_font)

        self.ltcg_layout.addWidget(ltcg_label)

        ltcg_date_label = QLabel(f"© 2017 - 2026")
        ltcg_date_label.setProperty("class", "header2")
        ltcg_date_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        ltcg_date_label.setFont(self.main_font)

        self.ltcg_layout.addWidget(ltcg_date_label)

        def on_enter(label: QLabel, event):
            label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            
            
        def on_leave(label: QLabel, event):
            label.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            
        
        def on_click(url, event):
            QDesktopServices.openUrl(QUrl(url))
            
        git_label.enterEvent = partial(on_enter, git_label)
        git_label.leaveEvent = partial(on_leave, git_label) # type: ignore
        git_label.mousePressEvent = partial(on_click, "https://github.com/langstonstewart") # type: ignore

        pz_label.enterEvent = partial(on_enter, pz_label)
        pz_label.leaveEvent = partial(on_leave, pz_label) # type: ignore
        pz_label.mousePressEvent = partial(on_click, "https://www.pokemon-zone.com") # type: ignore

        serebii_label.enterEvent = partial(on_enter, serebii_label)
        serebii_label.leaveEvent = partial(on_leave, serebii_label) # type: ignore
        serebii_label.mousePressEvent = partial(on_click, "https://www.serebii.net") # type: ignore

        ltcg_label.enterEvent = partial(on_enter, ltcg_label)
        ltcg_label.leaveEvent = partial(on_leave, ltcg_label) # type: ignore
        ltcg_label.mousePressEvent = partial(on_click, "https://pocket.limitlesstcg.com") # type: ignore

        self.seperator(self.info_header, 1100)

        self.init_back_button(self.info_header, "Info")


    def display_info_page(self):

        self.info_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)

        self.stacked_layout.addWidget(self.info_widget)

        self.stacked_layout.setCurrentWidget(self.info_widget)


    def clicked_set(self, refresh=False):
        
        if not refresh:
            
            button = self.sender()
            self.set_name = button.property('Name') # type: ignore
            self.set_id = button.property('ID') # type: ignore
            self.series = button.property('Series') # type: ignore
        else:
            self.clear_layout(self.set_main_layout) # type: ignore
            button = self.set_button_dict[self.set_name]
        

        self.set_widget = QWidget()
        
        self.set_main_layout = QVBoxLayout()
        self.set_main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.set_widget.setLayout(self.set_main_layout)
        self.set_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)
        self.set_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.print_set_title(self.set_name)

        self.seperator(self.set_main_layout, self.set_sep_lens[self.col_count])

        self.card_grid = QGridLayout()
        self.card_grid.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.card_grid.setVerticalSpacing(25)
        self.card_grid.setHorizontalSpacing(25)
        self.set_main_layout.addLayout(self.card_grid)
        
        self.display_loading_page()

        QTimer.singleShot(100, self.await_cache)
        
        
    def await_cache(self): 
                
        self.display_cards()

        self.seperator(self.set_main_layout, self.set_sep_lens[self.col_count])

        self.set_action_buttons()

        self.init_back_button(self.set_main_layout, "Set")

        self.change_col_button(self.set_main_layout)

        
        


    def set_action_buttons(self):
        self.ex_layout = QHBoxLayout()
        self.ex_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.set_main_layout.addLayout(self.ex_layout) # type: ignore

        self.shadow_add_button = QPushButton("Add 1 to All..")
        self.shadow_add_button.setProperty("class", "Setting_Button")
        self.shadow_add_button.setFont(self.main_font)

        self.shadow_add_button.setIcon(QIcon(self.IM.shadow_add_icon[self.mode]))
        self.shadow_add_button.setIconSize(QSize(36, 36))

        self.shadow_add_button.enterEvent = partial(self.on_button_enter, self.shadow_add_button)
        self.shadow_add_button.leaveEvent = partial(self.on_button_leave, self.shadow_add_button) # type: ignore
        self.shadow_add_button.clicked.connect(self.add_one_all)

        self.shadow_minus_button = QPushButton("Remove 1 from All..")
        self.shadow_minus_button.setProperty("class", "Setting_Button")
        self.shadow_minus_button.setFont(self.main_font)

        self.shadow_minus_button.setIcon(QIcon(self.IM.shadow_minus_icon[self.mode]))
        self.shadow_minus_button.setIconSize(QSize(36, 36))

        self.shadow_minus_button.enterEvent = partial(self.on_button_enter, self.shadow_minus_button)
        self.shadow_minus_button.leaveEvent = partial(self.on_button_leave, self.shadow_minus_button) # type: ignore
        self.shadow_minus_button.clicked.connect(self.remove_one_all)

        self.export_button = QPushButton("Export as Excel Spreadsheet..")
        self.export_button.setProperty("class", "Setting_Button")
        self.export_button.setFont(self.main_font)

        self.export_button.setIcon(QIcon(self.IM.export_icon[self.mode]))
        self.export_button.setIconSize(QSize(36, 36))

        self.export_button.enterEvent = partial(self.on_button_enter, self.export_button)
        self.export_button.leaveEvent = partial(self.on_button_leave, self.export_button) # type: ignore
        
        self.export_button.clicked.connect(partial(self.set_manager.export_excel, f"{self.local_doc}\\{self.category_dir}\\{self.series}", self.set_name, self.set_list))

        self.import_button = QPushButton("Import as Excel Spreadsheet..")
        self.import_button.setProperty("class", "Setting_Button")
        self.import_button.setFont(self.main_font)

        self.import_button.setIcon(QIcon(self.IM.import_icon[self.mode]))
        self.import_button.setIconSize(QSize(36, 36))

        self.import_button.enterEvent = partial(self.on_button_enter, self.import_button)
        self.import_button.leaveEvent = partial(self.on_button_leave, self.import_button) # type: ignore

        self.import_button.clicked.connect(self.import_excel_main)

        self.refresh_button = QPushButton("Update Set Data..")
        self.refresh_button.setProperty("class", "Setting_Button")
        self.refresh_button.setFont(self.main_font)

        self.refresh_button.setIcon(QIcon(self.IM.refresh_icon[self.mode]))
        self.refresh_button.setIconSize(QSize(36, 36))

        self.refresh_button.enterEvent = partial(self.on_button_enter, self.refresh_button)
        self.refresh_button.leaveEvent = partial(self.on_button_leave, self.refresh_button) # type: ignore

        self.refresh_button.clicked.connect(self.update_set_data)

        self.ex_layout.addWidget(self.shadow_add_button)
        self.ex_layout.addWidget(self.shadow_minus_button)
        self.ex_layout.addWidget(self.export_button)
        self.ex_layout.addWidget(self.import_button)
        self.ex_layout.addWidget(self.refresh_button)

    def change_col_button(self, layout):
      
        change_col_button = QPushButton("Change Column Count...")
        change_col_button.setProperty("class", "Setting_Button")
        change_col_button.setFont(self.main_font)
        

        change_col_button.setIcon(QIcon(self.IM.counter_icon_dict[self.col_count][self.mode]))
        change_col_button.setIconSize(QSize(36, 36))

        change_col_button.enterEvent = partial(self.on_button_enter, change_col_button)
        change_col_button.leaveEvent = partial(self.on_button_leave, change_col_button) # type: ignore
        
        change_col_button.clicked.connect(partial(self.change_col_amount, layout))

        self.bb_layout.addWidget(change_col_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

        self.bb_layout.addStretch()


    def change_col_amount(self, layout):
        if self.col_count == 4:
            self.col_count = 6
            self.settings["UserData"]["col_count"] = 6

        elif self.col_count == 6:
            self.col_count = 8
            self.settings["UserData"]["col_count"] = 8

        elif self.col_count == 8:
            self.col_count = 4
            self.settings["UserData"]["col_count"] = 4
        
        with open(resource_path(f"src/app_data/app_settings.json"), "w+") as config_file:
                json.dump(self.settings, config_file, indent=4)

        
        if layout != self.fav_main_layout:
            self.clicked_set(True) # HERE
        else:
            self.clear_layout(self.fav_main_layout) # type: ignore
            self.display_favorites()
            
        

    def update_set_data(self):

        if self.set_manager.update_set(self.set_list, self.category_dir, self.series, self.set_name, self.local_doc):
            self.init_cache()
            self.go_back(self.set_main_layout)
            self.clicked_set(True)
        else:
            self.display_message("Set Data Unchanged", f"Set data is already up to date (as of {datetime.datetime.now().strftime("%B %d, %Y")}).\nIf you believe this is a mistake, contact the maintainer below:\nhttps://github.com/langstonstewart/PocketDex-Codex")

    
    def file_picker(self):
        fp = QFileDialog.getOpenFileName(self.main_widget, "Select a File...", "", "Excel 2007+ Spreadsheet (*.xlsx)")
        
        return fp[0]
    
    def display_message(self, title: str, message: str):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def import_excel_main(self):
        excel_fp = self.file_picker()
        if excel_fp:
            if not self.set_manager.import_excel(f"{self.local_doc}\\{self.category_dir}\\{self.series}", excel_fp, self.set_name, self.set_list):
                self.display_message("Invalid Spreadsheet", "ERROR: This xlsx spreadsheet does not match the set data.\nPlease try a different file.\nIf you believe this is a mistake, contact the maintainer below:\nhttps://github.com/langstonstewart/PocketDex-Codex")

            with open(self.set_fp, "r+") as set_file:
                self.set_list = json.load(set_file)

            self.go_back(self.set_main_layout)
            self.clicked_set(True)
        

    def add_one_all(self):
        for button in self.plus_button_list:
            self.increment_quantity(self.data_header, self.set_name, True, button)
        self.app.processEvents()

       
        with open(self.set_fp, "w") as set_file:
            json.dump(self.set_list, set_file, indent=4)

    def remove_one_all(self):
        for button in self.plus_button_list:
            self.decrement_quantity(self.data_header, self.set_name, True, button)
        self.app.processEvents()

        with open(self.set_fp, "w") as set_file:
            json.dump(self.set_list, set_file, indent=4)
    
    def display_loading_page(self):
        self.loading_widget = QWidget()
          
        self.loading_layout = QVBoxLayout()
        self.loading_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.loading_widget.setLayout(self.loading_layout)
        self.loading_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)
        self.loading_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.print_loading_title(self.set_name)

    def print_loading_title(self, set_name: str):

        scale_int = 1 if self.category_dir == "TCG Pocket" else 3
        
        self.set_fp = f"{self.local_doc}\\{self.category_dir}\\{self.series}\\{set_name}\\{set_name}.json"

        with open(self.set_fp, "r+") as set_file:
            self.set_list = json.load(set_file)

            for card in self.set_list:
                if card["Rarity"] is None:
                    card["Rarity"] = "N/A"

            with open(self.set_fp, "w+") as set_file:
                json.dump(self.set_list, set_file, indent=4)

            self.loading_header = QHBoxLayout()
            self.loading_header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.loading_layout.addLayout(self.loading_header)

            self.ld_header = QHBoxLayout()
            self.ld_header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.loading_layout.addLayout(self.ld_header)

            self.set_info_layout = QVBoxLayout()
            self.set_info_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            
            self.loading_layout.addLayout(self.set_info_layout)

        for s in self.set_dict[self.series]:
            if s["Name"] == self.set_name:
                set_data =  s

        formatted_name = set_name.split()
        del formatted_name[-1]
        formatted_name = " ".join(formatted_name)

        set_title = QLabel(f"{formatted_name} (Loading..)")
        set_tag = QLabel("")
        set_date = QLabel(f"{set_data["Release Date"]}")
        card_count = QLabel(f"{self.calculate_total_quantity()}/{len(self.set_list)} Cards")
        
        cache_label = QLabel(f"Please wait...")

        set_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        set_title.setProperty("class", "header1")
        set_title.setFont(self.main_font)
        self.loading_header.addWidget(set_title)

        set_tag = QLabel(f"{set_data["SetID"]}")
        set_tag.setProperty("class", "Set_Tag")
        set_tag.setFont(self.main_font)
        set_tag.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.loading_header.addWidget(set_tag)


        set_date.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        set_date.setProperty("class", "header2")
        set_date.setFont(self.main_font)
        self.ld_header.addWidget(set_date)
        
        card_count.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        card_count.setProperty("class", "header2")
        card_count.setFont(self.main_font)
        self.ld_header.addWidget(card_count)

        self.seperator(self.set_info_layout, 1100)

        if "Info" in set_data.keys():
            info_label = QLabel(set_data["Info"])
            info_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            info_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            info_label.setProperty("class", "header2")
            info_label.setWordWrap(True)
            info_label.setFont(self.main_font)
            self.set_info_layout.addWidget(info_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        cache_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        cache_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        cache_label.setProperty("class", "header2")
        cache_label.setWordWrap(True)
        cache_label.setFont(self.main_font)

        
        self.set_info_layout.addWidget(cache_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.stacked_layout.addWidget(self.loading_widget)

        self.scroll_area.verticalScrollBar().setValue(0) # type: ignore

        self.stacked_layout.setCurrentWidget(self.loading_widget)

        self.clear_layout(self.main_layout) # type: ignore
        

    def init_card_data_page(self):
           
        self.cd_layout = QVBoxLayout()
        
        self.cd_widget.setLayout(self.cd_layout)
        self.cd_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)
        self.cd_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        
    def display_card_data_page(self, card_index, favorites_menu):

        if favorites_menu:
            self.clear_layout(self.fav_main_layout) # type: ignore
        else:

            self.clear_layout(self.set_main_layout) # type: ignore

        self.clear_layout(self.cd_layout) # type: ignore

        self.fb_list = []

        self.seperator(self.cd_layout, 1100)

        self.main_card_data_layout = QVBoxLayout()
        self.main_card_data_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.cd_layout.addLayout(self.main_card_data_layout) # type: ignore

        card_header_layout = QHBoxLayout()
        
        
        self.main_card_data_layout.addLayout(card_header_layout)

        card_layout = QVBoxLayout()
        card_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.main_card_data_layout.addLayout(card_layout)

        if self.set_list[card_index]["Card-Type"] == "Pokemon":
            card_type = self.set_list[card_index]["Stage"]
        else:
            card_type = self.set_list[card_index]["Card-Type"]

        card_type_banner = QLabel("")
        
        card_type_banner.setPixmap(self.IM.card_type_dict[card_type].scaled(self.IM.card_type_dict[card_type].width() // 3, self.IM.card_type_dict[card_type].height() // 3, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        card_type_banner.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        card_type_banner.setAlignment(Qt.AlignmentFlag.AlignLeft if self.set_list[card_index]["Card-Type"] == "Pokemon" else Qt.AlignmentFlag.AlignHCenter)

        card_header_layout.addWidget(card_type_banner)

        self.create_card(card_index, card_layout, False)


        if self.set_list[card_index]["Card-Type"] == "Pokemon":
            card_header_hp_layout = QHBoxLayout()
            card_header_layout.addLayout(card_header_hp_layout)

            hp_label = QLabel()

            hp_txt = f'<span style="font-size:16px;">HP</span><span style="font-size:24px;">{self.set_list[card_index]["HP"]}</span>'

            energy_map = ''

            for type in self.set_list[card_index]["Type"].split("/"):
                energy_map += f'<img src="{self.IM.type_dict[type]}" width="20" height="20" style="vertical-align: middle;">'
                
            hp_label.setText(f'{hp_txt}&nbsp;&nbsp;{energy_map}')
                
            hp_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            hp_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            hp_label.setFont(self.main_font_bold)

            card_header_hp_layout.addWidget(hp_label)

            self.seperator(self.cd_layout, 1100)

            move_data_layout = QVBoxLayout()
            
            move_data_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            move_data_layout.setContentsMargins(0, 20, 0, 20)
            self.cd_layout.addLayout(move_data_layout) # type: ignore

            if "Tera" in self.set_list[card_index].keys():

                tera_img = self.IM.tera_icon.scaled(self.IM.tera_icon.width() // 4, self.IM.tera_icon.height() // 4, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                tera_layout = QVBoxLayout()
                        
                tera_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                move_data_layout.addLayout(tera_layout) # type: ignore

                tera_banner = QLabel("")
                tera_banner.setPixmap(tera_img)
                tera_banner.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
                tera_banner.setAlignment(Qt.AlignmentFlag.AlignHCenter)

                tera_layout.addWidget(tera_banner)

                move_effect_label = QLabel(self.set_list[card_index]["Tera-Effect"])
                move_effect_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                move_effect_label.setFont(self.main_font)
                move_effect_label.setTextFormat(Qt.TextFormat.RichText)
                move_effect_label.setProperty("class", "header2")
                move_effect_label.setMinimumWidth(1000)
                move_effect_label.setMaximumWidth(1000)
                move_effect_label.setWordWrap(True)
                move_effect_label.setMinimumHeight(move_effect_label.sizeHint().height() * 5)
                move_effect_label.setMaximumHeight(move_effect_label.sizeHint().height() * 5)
                move_effect_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
                
                tera_layout.addWidget(move_effect_label)

           

            if "Ability" in self.set_list[card_index].keys():

        
                for i in range (len(self.set_list[card_index]["Ability"])):

                    ability_text = f"{self.set_list[card_index]["Ability"][i]}"

                    ability_set = False

                    for trait in self.IM.trait_dict.keys():
                        if trait in ability_text:
                            
                            ability_img = self.IM.trait_dict[trait].scaled(self.IM.trait_dict[trait].width() // 2, self.IM.trait_dict[trait].height() // 2, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                            ability_text = ability_text.replace(f"{trait} ", "")
                            property = "theta_header"
                            ability_set = True

                    if not ability_set:
                        ability_img = self.IM.ability_icon.scaled(128, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        property = "ability_header"

                    ability_layout = QHBoxLayout()
                    
                    ability_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    move_data_layout.addLayout(ability_layout) # type: ignore

                    ability_banner = QLabel("")
                    ability_banner.setPixmap(ability_img)
                    ability_banner.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                    ability_banner.setAlignment(Qt.AlignmentFlag.AlignHCenter)

                    ability_layout.addWidget(ability_banner)

                    ability_label = QLabel(ability_text)
                    ability_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    ability_label.setFont(self.main_font_bold)
                    ability_label.setProperty("class", property)
                    ability_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

                    ability_layout.addWidget(ability_label)


                    ability_effect_data = self.set_list[card_index]["Ability-Effect"][i] # type: str

                    for symbol, img_path in self.IM.energy_dict.items():
                        if isinstance(img_path, tuple):
                            html_img = f'<img src="{img_path[self.mode]}" width="20" height="20">'
                            ability_effect_data = ability_effect_data.replace(f"[{symbol}]", html_img)
                        else:
                            html_img = f'<img src="{img_path}" width="20" height="20">'
                            ability_effect_data = ability_effect_data.replace(f"[{symbol}]", html_img)

                    ability_effect_text = QLabel(ability_effect_data)
                    ability_effect_text.setTextFormat(Qt.TextFormat.RichText)
                    ability_effect_text.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    ability_effect_text.setFont(self.main_font)
                    ability_effect_text.setProperty("class", "header2")
                    ability_effect_text.setMinimumWidth(1000)
                    ability_effect_text.setMaximumWidth(1000)
                    ability_effect_text.setWordWrap(True)
                    ability_effect_text.setMinimumHeight(ability_effect_text.sizeHint().height() * 5)
                    ability_effect_text.setMaximumHeight(ability_effect_text.sizeHint().height() * 5)
                    ability_effect_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
                    move_data_layout.addWidget(ability_effect_text)


            for i in range(len(self.set_list[card_index]["Moves"])):
                move_layout = QHBoxLayout()
               
                move_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
                move_data_layout.addLayout(move_layout) # type: ignore

                for energy in self.set_list[card_index]["Move-Energy"][i]:

                    m_energy = QLabel(f"")
                    if isinstance(self.IM.energy_dict[energy], tuple):
                        m_energy.setPixmap(QPixmap(self.IM.energy_dict[energy][self.mode]).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    else:
                        m_energy.setPixmap(QPixmap(self.IM.energy_dict[energy]).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    m_energy.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                    m_energy.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

                    move_layout.addWidget(m_energy)

                
                move_name = QLabel(f"{self.set_list[card_index]["Moves"][i]}")
                move_name.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
                move_name.setFont(self.main_font_bold)
                move_name.setProperty("class", "header2")
                move_name.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

                move_layout.addWidget(move_name)

                move_damage = self.set_list[card_index]["Move-Damage"][i]

                if move_damage:
                    move_damage_label = QLabel(move_damage)
                    move_damage_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    move_damage_label.setFont(self.main_font_bold)
                    move_damage_label.setProperty("class", "header2")
                    move_damage_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

                    move_layout.addWidget(move_damage_label)

                move_effect = self.set_list[card_index]["Effects"][i] # type: str

                if move_effect:

                    for symbol, img_path in self.IM.energy_dict.items():
                        html_img = f'<img src="{img_path}" width="20" height="20">'
                        move_effect = move_effect.replace(f"[{symbol}]", html_img)

                    move_effect_label = QLabel(move_effect)
                    move_effect_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    move_effect_label.setFont(self.main_font)
                    move_effect_label.setTextFormat(Qt.TextFormat.RichText)
                    move_effect_label.setProperty("class", "header2")
                    move_effect_label.setMinimumWidth(1000)
                    move_effect_label.setMaximumWidth(1000)
                    move_effect_label.setWordWrap(True)
                    move_effect_label.setMinimumHeight(move_effect_label.sizeHint().height() * 5)
                    move_effect_label.setMaximumHeight(move_effect_label.sizeHint().height() * 5)
                    move_effect_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
                    
                    move_data_layout.addWidget(move_effect_label)

            

            w_r_layout = QHBoxLayout()
            w_r_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            if "Ability" in self.set_list[card_index].keys():
                pass
                #self.cd_layout.addStretch() # type: ignore
            
            self.cd_layout.addLayout(w_r_layout) # type: ignore

            weakness_data = self.set_list[card_index]["Weakness"]

            if weakness_data:

                for weakness in weakness_data.split('/'):

                    w_layout = QHBoxLayout()
                    w_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    w_r_layout.addLayout(w_layout) # type: ignore

                    weakness_txt = QLabel("Weakness")
                    weakness_txt.setFont(self.main_font)
                    weakness_txt.setProperty("class", "header2")
                    weakness_txt.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                    w_layout.addWidget(weakness_txt)

                    weakness_energy = QLabel("")
                    weakness_energy.setPixmap(QPixmap(self.IM.type_dict[weakness]).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # type: ignore
                    weakness_energy.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                    w_layout.addWidget(weakness_energy)

                    weakness_dmg = QLabel("+20" if self.category_dir == "TCG Pocket" else f"\u00782")
                    weakness_dmg.setFont(self.main_font)
                    weakness_dmg.setProperty("class", "header2")
                    weakness_dmg.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                    w_layout.addWidget(weakness_dmg)
                

            resist_data = self.set_list[card_index]["Resistance"] if "Resistance" in self.set_list[card_index].keys() else None

            if resist_data:

                

                r_layout = QHBoxLayout()
                r_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                w_r_layout.addLayout(r_layout) # type: ignore

                resist_txt = QLabel("Resistance")
                resist_txt.setFont(self.main_font)
                resist_txt.setProperty("class", "header2")
                resist_txt.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                r_layout.addWidget(resist_txt)

                for resistance in resist_data.split('/'):
                    resist_energy = QLabel("")
                    resist_energy.setPixmap(QPixmap(self.IM.type_dict[resistance]).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # type: ignore
                    resist_energy.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                    r_layout.addWidget(resist_energy)

                resist_dmg = QLabel("-20")
                resist_dmg.setFont(self.main_font)
                resist_dmg.setProperty("class", "header2")
                resist_dmg.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                r_layout.addWidget(resist_dmg)


            retreat_cost = int(self.set_list[card_index]["Retreat-Cost"]) if self.set_list[card_index]["Retreat-Cost"] else None

            if retreat_cost:
                
                rt_layout = QHBoxLayout()
                rt_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                w_r_layout.addLayout(rt_layout) # type: ignore

                retreat_txt = QLabel("Retreat")
                retreat_txt.setFont(self.main_font)
                retreat_txt.setProperty("class", "header2")
                retreat_txt.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                rt_layout.addWidget(retreat_txt)

                for r in range(retreat_cost):
                    rc_icon = QLabel("")
                    rc_icon.setPixmap(QPixmap(self.IM.energy_dict["C"]).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # type: ignore
                    rc_icon.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                    rc_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    rt_layout.addWidget(rc_icon, alignment=Qt.AlignmentFlag.AlignHCenter)
            

            self.seperator(self.cd_layout, 1100)

            flavor_text = self.set_list[card_index]["Flavor-Text"]

            card_rule_list = []

            for rule in self.IM.rule_list:
                if rule in self.set_list[card_index].keys():
                    card_rule_list.append(rule)


            

            if flavor_text:

                ft_layout = QVBoxLayout()
                ft_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                self.cd_layout.addLayout(ft_layout) # type: ignore

                ft_label = QLabel(f"{flavor_text}")
                ft_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                ft_label.setFont(self.main_font)
                ft_label.setProperty("class", "header2")
                ft_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
                ft_label.setWordWrap(True)

                ft_label.setMinimumHeight(ft_label.sizeHint().height() * 3)
                ft_label.setMaximumHeight(ft_label.sizeHint().height() * 3)
                    
                ft_layout.addWidget(ft_label)

            elif card_rule_list:
                for card_rule in card_rule_list:
                    ex_layout = QVBoxLayout()
                    ex_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    self.cd_layout.addLayout(ex_layout) # type: ignore

                    ex_label = QLabel(f"{self.set_list[card_index][card_rule]}")
                    ex_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    ex_label.setFont(self.main_font)
                    ex_label.setProperty("class", "header2")
                    ex_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
                    ex_label.setWordWrap(True)
                    ex_label.setMinimumHeight(ex_label.sizeHint().height() * 3)
                    ex_label.setMaximumHeight(ex_label.sizeHint().height() * 3)
                        
                    ex_layout.addWidget(ex_label)

        else:
            self.seperator(self.cd_layout, 1100)

            desc_layout = QVBoxLayout()
            desc_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.cd_layout.addLayout(desc_layout) # type: ignore

            card_desc = self.set_list[card_index]["Description"] # type: str

            if card_desc:

                for symbol, img_path in self.IM.energy_dict.items():
                    html_img = f'<img src="{img_path}" width="20" height="20">'
                    card_desc = card_desc.replace(f"[{symbol}]", html_img)

                card_desc_label = QLabel(card_desc)
                card_desc_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                card_desc_label.setFont(self.main_font)
                card_desc_label.setTextFormat(Qt.TextFormat.RichText)
                card_desc_label.setProperty("class", "header2")
                card_desc_label.setMinimumWidth(1000)
                card_desc_label.setMaximumWidth(1000)
                card_desc_label.setWordWrap(True)
                card_desc_label.setMinimumHeight(card_desc_label.sizeHint().height() * 5)
                card_desc_label.setMaximumHeight(card_desc_label.sizeHint().height() * 5)
                card_desc_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
                
                desc_layout.addWidget(card_desc_label, alignment=Qt.AlignmentFlag.AlignHCenter)


                if "Moves" in self.set_list[card_index].keys():
                    move_data_layout = QVBoxLayout()
            
                    move_data_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    move_data_layout.setContentsMargins(0, 20, 0, 20)
                    self.cd_layout.addLayout(move_data_layout) # type: ignore
                    
                    for i in range(len(self.set_list[card_index]["Moves"])):
                        move_layout = QHBoxLayout()
                    
                        move_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
                        move_data_layout.addLayout(move_layout) # type: ignore

                        for energy in self.set_list[card_index]["Move-Energy"][i]:

                            m_energy = QLabel(f"")
                            if isinstance(self.IM.energy_dict[energy], tuple):
                                m_energy.setPixmap(QPixmap(self.IM.energy_dict[energy][self.mode]).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                            else:
                                m_energy.setPixmap(QPixmap(self.IM.energy_dict[energy]).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                            m_energy.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                            m_energy.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

                            move_layout.addWidget(m_energy)

                        
                        move_name = QLabel(f"{self.set_list[card_index]["Moves"][i]}")
                        move_name.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
                        move_name.setFont(self.main_font_bold)
                        move_name.setProperty("class", "header2")
                        move_name.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

                        move_layout.addWidget(move_name)

                        move_damage = self.set_list[card_index]["Move-Damage"][i]

                        if move_damage:
                            move_damage_label = QLabel(move_damage)
                            move_damage_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                            move_damage_label.setFont(self.main_font_bold)
                            move_damage_label.setProperty("class", "header2")
                            move_damage_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

                            move_layout.addWidget(move_damage_label)

                        move_effect = self.set_list[card_index]["Effects"][i] # type: str

                        if move_effect:

                            for symbol, img_path in self.IM.energy_dict.items():
                                html_img = f'<img src="{img_path}" width="20" height="20">'
                                move_effect = move_effect.replace(f"[{symbol}]", html_img)

                            move_effect_label = QLabel(move_effect)
                            move_effect_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                            move_effect_label.setFont(self.main_font)
                            move_effect_label.setTextFormat(Qt.TextFormat.RichText)
                            move_effect_label.setProperty("class", "header2")
                            move_effect_label.setMinimumWidth(1000)
                            move_effect_label.setMaximumWidth(1000)
                            move_effect_label.setWordWrap(True)
                            move_effect_label.setMinimumHeight(move_effect_label.sizeHint().height() * 5)
                            move_effect_label.setMaximumHeight(move_effect_label.sizeHint().height() * 5)
                            move_effect_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
                            
                            move_data_layout.addWidget(move_effect_label)


                self.seperator(desc_layout, 1100)

        rule_layout = QVBoxLayout()
        rule_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.cd_layout.addLayout(rule_layout) # type: ignore

        

        misc_extra_layout = QHBoxLayout()
        misc_extra_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        rule_layout.addLayout(misc_extra_layout) # type: ignore

        if self.set_list[card_index]["Illustrator"]:

            paint_icon = QLabel("")
            paint_icon.setPixmap(self.IM.paint_icon[self.mode].scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # type: ignore
            paint_icon.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            paint_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            misc_extra_layout.addWidget(paint_icon)

            i_label = QLabel(f"Illustrated by {self.set_list[card_index]["Illustrator"]}")
            i_label.setFont(self.main_font)
            i_label.setProperty("class", "header2")
            i_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            misc_extra_layout.addWidget(i_label)

            misc_extra_layout.addSpacing(25)

        pb_icon = QLabel("")
        pb_icon.setPixmap(self.rarity_dict["N/A"][self.mode].scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # type: ignore
        pb_icon.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        pb_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        misc_extra_layout.addWidget(pb_icon)

        card_index_label = QLabel(f"{card_index + 1} of {len(self.set_list)}")
        card_index_label.setFont(self.main_font)
        card_index_label.setProperty("class", "header2")
        card_index_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        misc_extra_layout.addWidget(card_index_label)

        self.seperator(rule_layout, 1100)

        prices_layout = QHBoxLayout()
        prices_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        rule_layout.addLayout(prices_layout) # type: ignore

        def on_enter(label: QLabel, event):
            label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            
            
        def on_leave(label: QLabel, event):
            label.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            
        
        def on_click(url, event):
            QDesktopServices.openUrl(QUrl(url))

        if "tcg_player_link" in self.set_list[card_index].keys() and self.set_list[card_index]["tcg_player_link"] is not None:

            tp_icon = QLabel("")
            tp_icon.setPixmap(self.IM.tcgplayer_icon[self.mode].scaled(self.IM.tcgplayer_icon[self.mode].width() // 10, self.IM.tcgplayer_icon[self.mode].height() // 10, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # type: ignore
            tp_icon.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            tp_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            prices_layout.addWidget(tp_icon)

            tp_text = QLabel(f"View Card on TCGPlayer...")
            tp_text.setFont(self.main_font)
            tp_text.setProperty("class", "Link_Label")
            tp_text.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

            tp_text.enterEvent = partial(on_enter, tp_text)
            tp_text.leaveEvent = partial(on_leave, tp_text) # type: ignore
            tp_text.mousePressEvent = partial(on_click, self.set_list[card_index]["tcg_player_link"]) # type: ignore

            prices_layout.addWidget(tp_text)

        if "cardmarket_link" in self.set_list[card_index].keys() and self.set_list[card_index]["cardmarket_link"] is not None:

            cm_icon = QLabel("")
            cm_icon.setPixmap(self.IM.cm_icon[self.mode].scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # type: ignore
            cm_icon.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            cm_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            prices_layout.addWidget(cm_icon)

            cm_text = QLabel(f"View Card on Cardmarket...")
            cm_text.setFont(self.main_font)
            cm_text.setProperty("class", "Link_Label")
            cm_text.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

            cm_text.enterEvent = partial(on_enter, cm_text)
            cm_text.leaveEvent = partial(on_leave, cm_text) # type: ignore
            cm_text.mousePressEvent = partial(on_click, self.set_list[card_index]["cardmarket_link"]) # type: ignore
            prices_layout.addWidget(cm_text)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

        random_button = QPushButton("Random..")
        random_button.setProperty("class", "Setting_Button")
        random_button.setFont(self.main_font)

        random_button.setIcon(QIcon(self.IM.dice_icon[self.mode]))
        random_button.setIconSize(QSize(36, 36))

        random_button.enterEvent = partial(self.on_button_enter, random_button)
        random_button.leaveEvent = partial(self.on_button_leave, random_button) # type: ignore
        random_button.clicked.connect(partial(self.display_card_data_page, random.randint(0, len(self.set_list) - 1), True if favorites_menu else False))

        button_layout.addWidget(random_button)


        if hasattr(self, 'l_button_shortcut'):
            self.l_button_shortcut.setEnabled(False) # type: ignore
            self.l_button_shortcut.deleteLater() # type: ignore
            del self.l_button_shortcut


        if hasattr(self, 'r_button_shortcut'):
            self.r_button_shortcut.setEnabled(False) # type: ignore
            self.r_button_shortcut.deleteLater() # type: ignore
            del self.r_button_shortcut
                

        if card_index - 1 >= 0:

            self.prev_card_button = QPushButton(f'View Previous Card.. ({self.set_list[card_index - 1]["Name"].replace("&", "&&")})')
            self.prev_card_button.setProperty("class", "Setting_Button")
            self.prev_card_button.setFont(self.main_font)

            self.prev_card_button.setIcon(QIcon(self.IM.arrow_icon[self.mode]))
            self.prev_card_button.setIconSize(QSize(36, 36))

            self.prev_card_button.enterEvent = partial(self.on_button_enter, self.prev_card_button)
            self.prev_card_button.leaveEvent = partial(self.on_button_leave, self.prev_card_button) # type: ignore
            
            self.prev_card_button.clicked.connect(partial(self.display_card_data_page, card_index - 1, True if favorites_menu else False))

            self.l_button_shortcut = QShortcut(QKeySequence("Left"), self)
            self.l_button_shortcut.activated.connect(self.prev_card_button.click)

            button_layout.addWidget(self.prev_card_button)

        if card_index != len(self.set_list) - 1:

                self.next_card_button = QPushButton(f'View Next Card.. ({self.set_list[card_index + 1]["Name"].replace("&", "&&")})')
                self.next_card_button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
                self.next_card_button.setProperty("class", "Setting_Button")
                self.next_card_button.setFont(self.main_font)

                self.next_card_button.setIcon(QIcon(self.IM.forward_icon[self.mode]))
                self.next_card_button.setIconSize(QSize(36, 36))

                self.next_card_button.enterEvent = partial(self.on_button_enter, self.next_card_button)
                self.next_card_button.leaveEvent = partial(self.on_button_leave, self.next_card_button) # type: ignore

                self.next_card_button.clicked.connect(partial(self.display_card_data_page, card_index + 1, True if favorites_menu else False))

                self.r_button_shortcut = QShortcut(QKeySequence("Right"), self)
                self.r_button_shortcut.activated.connect(self.next_card_button.click)

                button_layout.addWidget(self.next_card_button)

        self.cd_layout.addStretch() # type: ignore

        self.init_back_button(self.cd_layout, "Card_Data")

        self.bb_layout.addLayout(button_layout) # type: ignore

        set_logo = QLabel("")
        set_logo.setPixmap(self.IM.logo_dict[self.set_id].scaled(156, 156, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        self.bb_layout.addWidget(set_logo, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        self.stacked_layout.addWidget(self.cd_widget)
    
        self.stacked_layout.setCurrentWidget(self.cd_widget)

        self.scroll_area.verticalScrollBar().setValue(0) # type: ignore

    def create_card(self, card_index, layout, clickable=True, row=0, col=0, favorites_menu=False, f_index=0):
        
        card_widget = QWidget()

        card_layout = QVBoxLayout(card_widget)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        card_layout.setSpacing(10)

        card_widget.setLayout(card_layout)
        
        def on_card_hover(event, img: QLabel):
            img.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            card_highlight = QGraphicsColorizeEffect()
            card_highlight.setColor(QColor(255, 255, 255))
            card_highlight.setStrength(0.2)
            img.setGraphicsEffect(card_highlight)

        def on_card_leave(event, img: QLabel):
            if favorites_menu:
                self.set_name = img.property("Set")

                self.set_fp = f"{self.local_doc}\\{self.category_dir}\\{img.property("series")}\\{self.set_name}\\{self.set_name}.json"

                with open(self.set_fp, "r+") as set_file:
                    self.set_list = json.load(set_file)
                

            self.update_card_opacity(img, self.set_list[img.property("index")]["Quantity"])


        def on_card_click(event, img: QLabel):
            if event.button() == Qt.MouseButton.LeftButton:
                if favorites_menu:
                    self.set_name = img.property("Set")

                    self.set_id = self.set_name.split("(")[-1].replace(")", "")

                    self.set_fp = f"{self.local_doc}\\{self.category_dir}\\{img.property("series")}\\{self.set_name}\\{self.set_name}.json"

                    self.series = img.property("series")

                    with open(self.set_fp, "r+") as set_file:
                        self.set_list = json.load(set_file)

                self.display_card_data_page(card_index, favorites_menu)

        def cache_img(widget):
            pix = widget.pixmap()
            if pix and not pix.isNull():
                self.img_cache_dict[self.set_id][self.set_list[card_index]["ID"]] = pix

                self.card_cache_count += 1

                if self.card_cache_count == len(self.set_list) and not favorites_menu:
                    self.stacked_layout.addWidget(self.set_widget)
                    self.stacked_layout.setCurrentWidget(self.set_widget)

        def load_from_cache():
            if self.card_cache_count != len(self.set_list):
                self.card_cache_count += 1
    
                if self.card_cache_count == len(self.set_list) and not favorites_menu:
                    self.stacked_layout.addWidget(self.set_widget)
                    self.stacked_layout.setCurrentWidget(self.set_widget)

        if self.set_id in self.img_cache_dict.keys():
            if self.set_list[card_index]["ID"] in self.img_cache_dict[self.set_id].keys():
                card_img = image_manager.ImageLabel(self.set_list[card_index]["Image"], network_manager=self.network_manager, is_pixmap=self.img_cache_dict[self.set_id][self.set_list[card_index]["ID"]])
                card_img.cache_pixmap_set.connect(partial(load_from_cache))
                card_img.load_from_cache()
            else:
                card_img = image_manager.ImageLabel(self.set_list[card_index]["Image"], network_manager=self.network_manager)
                card_img.download_finished.connect(partial(cache_img, card_img))
        else:
            self.img_cache_dict[self.set_id] = {}
            card_img = image_manager.ImageLabel(self.set_list[card_index]["Image"], network_manager=self.network_manager)
            card_img.download_finished.connect(partial(cache_img, card_img))


        card_img.setProperty("index", card_index)
        card_img.setProperty("series", self.series)
        
        card_img.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card_img.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        card_img.setProperty("Set", self.set_name)

        if clickable:
            card_img.setProperty("class", "Card_Label")
            card_img.enterEvent = lambda event, img=card_img: on_card_hover(event, img)
            card_img.leaveEvent = lambda event, img=card_img: on_card_leave(event, img) # type: ignore
            card_img.mousePressEvent = lambda event, img=card_img: on_card_click(event, img)  # type: ignore
                
        self.update_card_opacity(card_img, self.set_list[card_img.property("index")]["Quantity"])

        card_layout.addWidget(card_img)
        card_layout.addSpacing(10)

        self.card_img_dict[self.set_list[card_index]["ID"]] = card_img

        name_container = QWidget()
        name_container.setFixedWidth(card_img.width())
        name_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.MinimumExpanding) 
        card_name_layout = QHBoxLayout(name_container)
        card_name_layout.setContentsMargins(0, 6, 0, 6)
        card_name_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card_name_layout.setSpacing(10)

        card_text = f"{self.set_list[card_index]["Name"]}"

        name_tags = [("-EX", "vertical-align: bottom;"), 
                     ("BREAK", "vertical-align: middle;"), 
                     ("VMAX", "vertical-align: bottom;"), 
                     ("VSTAR", "vertical-align: bottom;"), 
                     ("V-UNION", "vertical-align: bottom;"), 
                     ("LEGEND", "vertical-align: middle;"), 
                     ("\u2662", "vertical-align: middle;"), 
                     ("-GX", "vertical-align: middle;"), 
                     ("LV.X", "vertical-align: top;")]

        if self.category_dir == "TCG Pocket" and " ex" in card_text:

            img_path = self.IM.ex_dict["Mega Pokemon"] if "Mega " in card_text else self.IM.ex_icon

            html_img = f'<img src="{img_path}" style="vertical-align: middle;">'
            card_text = card_text.replace(" ex", f' {html_img}')

            
        elif " ex" in card_text and self.series in self.IM.ex_dict.keys():

            img_path = self.IM.ex_dict["Mega Pokemon"] if "Mega " in card_text else self.IM.ex_dict[self.series]

            html_img = f'<img src="{img_path}" style="vertical-align: middle;">'
            card_text = card_text.replace(" ex", f' {html_img}')

        elif card_text[-2:] == " V":

            img_path = self.IM.tag_dict["V"]

            html_img = f'<img src="{img_path}" style="vertical-align: top;">'
            card_text = card_text.replace(card_text[-2:], f' {html_img}').strip()
            

        elif "Ex-Rule" in self.set_list[card_index].keys() and self.set_list[card_index]["Ex-Rule"] is not None and "TAG TEAM" in self.set_list[card_index]["Ex-Rule"]:

            img_path = self.IM.gx_tag_team_icon

            html_img = f'<img src="{img_path}" style="vertical-align: middle;">'
            card_text = card_text.replace("-GX", f' {html_img}').strip()

        elif card_text[-5:] == " Star":

            img_path = self.IM.star_icon

            html_img = f'<img src="{img_path}" style="vertical-align: top;">'
            card_text = card_text.replace(card_text[-5:], f' {html_img}').strip()

        elif self.series:
            for tag in name_tags:
                if tag[0] in card_text:
                   
                    img_path = self.IM.tag_dict[tag[0]]

                    html_img = f'<img src="{img_path}" style="{tag[1]}">'
                    card_text = card_text.replace(tag[0], f' {html_img}').strip()

        card_text = card_text.replace("&", "&amp;")

        card_name = QLabel(card_text)
        card_name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card_name.setFont(self.main_font_bold)
        card_name.setTextFormat(Qt.TextFormat.RichText)
        card_name.setProperty("class", "header2")
        
        card_name.setWordWrap(True)
        
        card_name.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        
        card_name_layout.addWidget(card_name)
        
        card_layout.addWidget(name_container, alignment=Qt.AlignmentFlag.AlignHCenter)

        card_layout.addStretch(1) 

        card_rarity = QLabel("")
        try:
            card_rarity.setPixmap(self.rarity_dict[self.set_list[card_index]["Rarity"]] if self.set_list[card_index]["Rarity"] != "N/A" else self.rarity_dict["N/A"][self.mode].scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # type: ignore
        except KeyError:
            card_rarity.setPixmap(self.rarity_dict["N/A"][self.mode].scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            
        card_rarity.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        card_rarity.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card_layout.addWidget(card_rarity)

        if not favorites_menu:

            data_layout = QHBoxLayout()
            data_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            card_layout.addLayout(data_layout)

            minus_button = QPushButton("")
            minus_button.setProperty("index", card_index)
            minus_button.setProperty("id", self.set_list[card_index]["ID"])
            plus_button = QPushButton("")
            plus_button.setProperty("index", card_index)
            plus_button.setProperty("id", self.set_list[card_index]["ID"])

            minus_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            minus_button.setProperty("class", "Main_Button")
            minus_button.setIcon(QIcon(self.IM.minus_icon[self.mode]))
            minus_button.setIconSize(QSize(36, 36))
            minus_button.setMinimumHeight(70)
            minus_button.setMinimumWidth(70)

            minus_button.enterEvent = partial(self.on_button_enter, minus_button)
            minus_button.leaveEvent = partial(self.on_button_leave, minus_button) # type: ignore

            minus_button.clicked.connect(partial(self.decrement_quantity, layout, self.set_name))

            self.minus_button_list.append(minus_button)

            quantity_label = QLabel(f"{self.set_list[card_index]["Quantity"]}")
            quantity_label.setFixedWidth(35)
            quantity_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            quantity_label.setFont(self.main_font_bold)

            quantity_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            quantity_label.setProperty("class", "header3")

            self.card_quantity_dict[card_index] = quantity_label

            plus_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            plus_button.setProperty("class", "Main_Button")
            plus_button.setIcon(QIcon(self.IM.plus_icon[self.mode]))
            plus_button.setIconSize(QSize(36, 36))
            plus_button.setMinimumHeight(70)
            plus_button.setMinimumWidth(70)
            
            plus_button.enterEvent = partial(self.on_button_enter, plus_button)
            plus_button.leaveEvent = partial(self.on_button_leave, plus_button) # type: ignore

            plus_button.clicked.connect(partial(self.increment_quantity, layout, self.set_name))

            self.plus_button_list.append(plus_button)

            data_layout.addWidget(minus_button)
            data_layout.addWidget(quantity_label)
            data_layout.addWidget(plus_button)

        f_layout = QHBoxLayout()
        f_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        card_layout.addLayout(f_layout)

        favorite_button = QPushButton("")
        favorite_button.setProperty("index", card_index)
        favorite_button.setProperty("id", self.set_list[card_index]["ID"])
        favorite_button.setProperty("series", self.series)
        favorite_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        favorite_button.setProperty("class", "Main_Button")
        favorite_button.setIcon(QIcon(self.IM.favorite_icon[self.mode if not self.set_list[card_index]["Favorite"] else 2]))
        favorite_button.setIconSize(QSize(24, 24))
        favorite_button.setFixedWidth(205)

        favorite_button.enterEvent = partial(self.on_button_enter, favorite_button)
        favorite_button.leaveEvent = partial(self.on_button_leave, favorite_button) # type: ignore

        favorite_button.clicked.connect(partial(self.favorite_card, layout) if not favorites_menu else partial(self.remove_from_favorites, self.set_name, f_index))

        self.fb_list.append(favorite_button)

        f_layout.addWidget(favorite_button)
        
        if type(layout) == QGridLayout:
            layout.addWidget(card_widget, row, col, alignment=Qt.AlignmentFlag.AlignHCenter)
        else:
            layout.addWidget(card_widget, alignment=Qt.AlignmentFlag.AlignHCenter) # type: ignore



    def display_cards(self):

        self.previous_widget = self.cd_layout
        
        self.card_quantity_dict = {}
        self.minus_button_list = []
        self.plus_button_list = []
        self.fb_list = []
        
        col_length = self.col_count
        row_length = ceil(len(self.set_list) / col_length)
        current_card = 0
        all_rows = False

        data_changed = False
        for card in self.set_list:
            if card["Rarity"] is None:
                card["Rarity"] = "N/A"
                data_changed = True
        
        if data_changed:
            with open(self.set_fp, "w+") as set_file:
                json.dump(self.set_list, set_file, indent=4)

        if not self.rarity_dict:
            self.init_rarities()

        
        self.card_cache_count = 0

        while True:
            if all_rows:
                break
            for r in range(row_length):
                if all_rows:
                    break
                for c in range(col_length):
                    
                    self.create_card(current_card, self.card_grid, True, r, c)
                    
                    current_card += 1
                    
                    if current_card == len(self.set_list):
                        all_rows = True
                        break
        
        
        

    def favorite_card(self, layout):
        fb = self.sender()
        if not self.set_list[fb.property("index")]["Favorite"]: # type: ignore
            self.set_list[fb.property("index")]["Favorite"] = 1 # type: ignore
          
            
            

            card_data = copy.deepcopy(self.set_list[fb.property("index")]) # type: ignore
            card_data["Set"] = self.set_name
            card_data["Index"] = fb.property("index") # type: ignore
            card_data["Series"] = fb.property("series") # type: ignore
            

            self.favorite_list.append(card_data) # type: ignore
            if layout == self.card_grid:
                self.fb_list[fb.property("index")].setIcon(QIcon(self.IM.favorite_icon[2])) # type: ignore
            else:
                self.fb_list[0].setIcon(QIcon(self.IM.favorite_icon[2])) # type: ignore
            
        else:
            self.set_list[fb.property("index")]["Favorite"] = 0 # type: ignore
            
            for index, f in enumerate(self.favorite_list):
                if f["ID"] == self.set_list[fb.property("index")]["ID"]: # type: ignore
                    self.favorite_list.pop(index)
            if layout == self.card_grid:
                self.fb_list[fb.property("index")].setIcon(QIcon(self.IM.favorite_icon[self.mode])) # type: ignore
            else:
                self.fb_list[0].setIcon(QIcon(self.IM.favorite_icon[self.mode])) # type: ignore
        
        with open(f"{self.local_doc}\\{self.category_dir}\\favorites\\favorites.json", "w") as f_file:
            json.dump(self.favorite_list, f_file, indent=4)

        with open(self.set_fp, "w") as set_file:
            json.dump(self.set_list, set_file, indent=4)
        
    
    def update_card_opacity(self, card: QLabel, quan):
        card_op = QGraphicsOpacityEffect()
        op = 0.5 if quan == 0 else 1.0
        card_op.setOpacity(op)
        card.setGraphicsEffect(card_op)
        

    def decrement_quantity(self, layout=None, set_name=None, all=False, object=QPushButton):

        if set_name:
            if not all:
                self.set_fp = f"{self.local_doc}\\{self.category_dir}\\{self.series}\\{self.set_name}\\{self.set_name}.json"

                with open(self.set_fp, "r+") as set_file:
                    self.set_list = json.load(set_file)

            

        if all:
            button = object
        else:
            button = self.sender()
        
        if self.set_list[button.property("index")]["Quantity"] > 0: # type: ignore
            self.set_list[button.property("index")]["Quantity"] -= 1 # type: ignore
        else:
            return
        
        if layout == self.card_grid:
            self.card_count.setText(f"{self.calculate_total_quantity()}/{len(self.set_list)} Cards")
        
        self.update_card_opacity(self.card_img_dict[button.property("id")], self.set_list[button.property("index")]["Quantity"]) # type: ignore

        if not all:
            with open(self.set_fp, "w") as set_file:
                json.dump(self.set_list, set_file, indent=4)
        
        self.card_quantity_dict[button.property("index")].setText(f"{self.set_list[button.property("index")]["Quantity"]}") # type: ignore

    
    def increment_quantity(self, layout=None, set_name=None, all=False, object=QPushButton):

        if set_name:
            if not all:
                self.set_fp = f"{self.local_doc}\\{self.category_dir}\\{self.series}\\{self.set_name}\\{self.set_name}.json"

                with open(self.set_fp, "r+") as set_file:
                    self.set_list = json.load(set_file)

        if all:
            button = object
        else:
            button = self.sender()

        if self.set_list[button.property("index")]["Quantity"] < 99: # type: ignore
            self.set_list[button.property("index")]["Quantity"] += 1 # type: ignore
        else:
            return
        
        if layout == self.card_grid:
            self.card_count.setText(f"{self.calculate_total_quantity()}/{len(self.set_list)} Cards")
        
        self.update_card_opacity(self.card_img_dict[button.property("id")], self.set_list[button.property("index")]["Quantity"]) # type: ignore

        if not all:
            with open(self.set_fp, "w") as set_file:
                json.dump(self.set_list, set_file, indent=4)

        self.card_quantity_dict[button.property("index")].setText(f"{self.set_list[button.property("index")]["Quantity"]}") # type: ignore
            


    def toggle_theme_button(self):

        self.settings_layout = QHBoxLayout()
        self.settings_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.header_layout.addLayout(self.settings_layout)
        

        self.theme_button = QPushButton("Toggle Theme..")
        self.ui_button_list.append((self.theme_button, self.IM.theme_icon, None, None))

        self.theme_button.setFont(self.main_font)
        self.theme_button.setProperty("class", "Setting_Button")

        self.theme_button.setIcon(QIcon(self.IM.theme_icon[self.mode]))
        self.theme_button.setIconSize(QSize(36, 36))

        self.theme_button.enterEvent = partial(self.on_button_enter, self.theme_button)
        self.theme_button.leaveEvent = partial(self.on_button_leave, self.theme_button) # type: ignore
        
        self.theme_button.clicked.connect(self.toggle_theme)

        self.settings_layout.addWidget(self.theme_button, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

    def create_favorite_cards_button(self):

        self.f_button = QPushButton("")
        self.ui_button_list.append((self.f_button, self.IM.heart_button_icon, None, None))
        self.f_button.setFont(self.main_font)
        self.f_button.setProperty("class", "Setting_Button")
        self.f_button.setText("View Favorites..")
        

        self.f_button.setIcon(QIcon(self.IM.heart_button_icon[self.mode]))
        self.f_button.setIconSize(QSize(36, 36))

        self.f_button.enterEvent = partial(self.on_button_enter, self.f_button)
        self.f_button.leaveEvent = partial(self.on_button_leave, self.f_button) # type: ignore
        
        self.f_button.clicked.connect(self.display_favorites)

        self.bb_layout.addWidget(self.f_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)


    def init_rarities(self):
        scale_int = 1 if self.category_dir == "TCG Pocket" else 3

        self.rarity_dict["N/A"] = (QPixmap(resource_path(f"src/images/rarities/TCG/none_black.png")), QPixmap(resource_path(f"src/images/rarities/TCG/none_white.png")))

        for rarity in self.IM.rarity_dict[self.category_dir]:
                
            rarity_pixmap = QPixmap(resource_path(f"src/images/rarities/{self.category_dir}/{rarity.replace(" ", "_").lower()}.png"))

            self.rarity_dict[rarity] = rarity_pixmap.scaled(rarity_pixmap.width() // scale_int, rarity_pixmap.width() // scale_int, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)


    def display_favorites(self):

        self.fb_list = []
        
        if len(self.favorite_list):

            self.card_cache_count = 0

            self.previous_widget = self.fav_main_layout
           
            self.fav_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)
            self.fav_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

            self.fav_title_layout = QHBoxLayout()
            self.fav_title_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.fav_main_layout.addLayout(self.fav_title_layout)

            self.fav_info_layout = QVBoxLayout()
            self.fav_info_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.fav_main_layout.addLayout(self.fav_info_layout)

            self.fav_title = QLabel("Favorites")
            self.fav_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            self.fav_title.setProperty("class", "header1")
            self.fav_title.setFont(self.main_font)
            self.fav_title_layout.addWidget(self.fav_title)

            set_tag = QLabel(f" \u2665 ")
            set_tag.setProperty("class", "Set_Tag")
            
            set_tag.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            self.fav_title_layout.addWidget(set_tag)

            self.fav_info = QLabel(f"{len(self.favorite_list)} {"Card" if len(self.favorite_list) <= 1 else "Cards"}")
            self.fav_info.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            self.fav_info.setProperty("class", "header2")
            self.fav_info.setFont(self.main_font)
            self.fav_info_layout.addWidget(self.fav_info)


            self.seperator(self.fav_main_layout, self.set_sep_lens[self.col_count])

            self.fav_grid = QGridLayout()
            self.fav_grid.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.fav_grid.setVerticalSpacing(25)
            self.fav_grid.setHorizontalSpacing(25)
            self.fav_main_layout.addLayout(self.fav_grid)

            self.card_quantity_dict = {}
            self.minus_button_list = []
            self.plus_button_list = []
            self.fb_list = []

            
            col_length = self.col_count
            row_length = ceil(len(self.favorite_list) / col_length)
            current_card = 0
            all_rows = False

            
            if not self.rarity_dict:
                self.init_rarities()

            while True:
                if all_rows:
                    break
                for r in range(row_length):
                    if all_rows:
                        break
                    for c in range(col_length):

                        self.set_name = self.favorite_list[current_card]["Set"]

                        self.card_series = self.favorite_list[current_card]["Series"]

                        self.set_id = self.set_name.split("(")[-1].replace(")", "")
                   

                        self.set_fp = f"{self.local_doc}\\{self.category_dir}\\{self.card_series}\\{self.set_name}\\{self.set_name}.json"

                        with open(self.set_fp, "r+") as set_file:
                            self.set_list = json.load(set_file)

                        self.series = self.card_series

                        
                        self.create_card(self.favorite_list[current_card]["Index"], self.fav_grid, True, r, c, True, current_card)
                        
                        current_card += 1
                        if current_card == len(self.favorite_list):
                            all_rows = True
                            break
            
            self.seperator(self.fav_main_layout, self.set_sep_lens[self.col_count])
            self.fav_main_layout.addStretch(100)
            self.init_back_button(self.fav_main_layout, "Favorites")
            self.change_col_button(self.fav_main_layout)

            self.stacked_layout.addWidget(self.fav_widget)
            self.stacked_layout.setCurrentWidget(self.fav_widget)

            if self.main_layout is not None:
                self.clear_layout(self.main_layout) # type: ignore
                
        
        else:
            self.f_button.setText("Your Favorites collection is empty!")
         

    def remove_from_favorites(self, set_name, f_index):
        fb = self.sender()

        self.set_name = set_name

        self.series = fb.property("series") # type: ignore

        self.set_fp = f"{self.local_doc}\\{self.category_dir}\\{self.series}\\{self.set_name}\\{self.set_name}.json"
        with open(self.set_fp, "r") as set_file:
                self.set_list = json.load(set_file)

        card_origin_index = fb.property("index") # type: ignore

        if not self.set_list[card_origin_index]["Favorite"]:
           
            self.set_list[card_origin_index]["Favorite"] = 1

            card_data = copy.deepcopy(self.set_list[card_origin_index]) # type: ignore
            card_data["Set"] = self.set_name
            card_data["Index"] = card_origin_index # type: ignore
            self.favorite_list.append(card_data) # type: ignore

        else:
            
            self.set_list[card_origin_index]["Favorite"] = 0

          
            self.favorite_list.pop(f_index) # type: ignore
            
                

        with open(f"{self.local_doc}\\{self.category_dir}\\favorites\\favorites.json", "w") as f_file:
            json.dump(self.favorite_list, f_file, indent=4)

        with open(self.set_fp, "w") as set_file:
            json.dump(self.set_list, set_file, indent=4)

        self.go_back(self.fav_main_layout)
        if len(self.favorite_list):
            self.display_favorites()

        


    def create_info_button(self):

        self.info_button = QPushButton("About..")
        self.ui_button_list.append((self.info_button, self.IM.info_icon, None, None))
        self.info_button.setProperty("class", "Setting_Button")
        self.info_button.setFont(self.main_font)
        

        self.info_button.setIcon(QIcon(self.IM.info_icon[self.mode]))
        self.info_button.setIconSize(QSize(36, 36))

        self.info_button.enterEvent = partial(self.on_button_enter, self.info_button)
        self.info_button.leaveEvent = partial(self.on_button_leave, self.info_button) # type: ignore
        
        self.info_button.clicked.connect(self.display_info_page)

        self.settings_layout.addWidget(self.info_button, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

        #self.settings_layout.addStretch()


    def toggle_theme(self):
        if self.mode == 1:
            self.mode = 0
            self.settings['UserData']['theme'] = 0
            
            for widget in self.widget_list: 
                widget.setStyleSheet(self.themes.light_theme)
                
            self.switch_scrollbar()
            
        elif self.mode == 0:
            self.mode = 1
            self.settings['UserData']['theme'] = 1
            
            for widget in self.widget_list: 
                widget.setStyleSheet(self.themes.dark_theme)

            self.switch_scrollbar()

        with open(resource_path(f"src/app_data/app_settings.json"), "w+") as config_file:
                json.dump(self.settings, config_file, indent=4)

        self.reload_images()


    def init_back_button(self, layout, key):

        self.bb_layout = QHBoxLayout()

        layout.addLayout(self.bb_layout)

        back_button = QPushButton("")
        back_button.setProperty("class", "Setting_Button")

        back_button.setIcon(QIcon(self.IM.arrow_icon[self.mode]))
        back_button.setIconSize(QSize(36, 36))

        back_button.enterEvent = partial(self.on_button_enter, back_button)
        back_button.leaveEvent = partial(self.on_button_leave, back_button) # type: ignore

        back_button.clicked.connect(partial(self.go_back, layout))

        self.bb_dict[key] = back_button

        self.ui_button_list.append((back_button, self.IM.arrow_icon, None, None))

        self.bb_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

        

        

    def go_back(self, layout):    

        if layout == self.main_layout or layout == self.info_header:
            self.scroll_area.verticalScrollBar().setValue(0) # type: ignore
            self.stacked_layout.setCurrentWidget(self.main_menu_widget)
            if self.main_layout is not None:
                self.clear_layout(self.main_layout) # type: ignore
            return
        if layout == self.fav_main_layout:
            self.scroll_area.verticalScrollBar().setValue(0) # type: ignore
            self.display_sets(self.category_file_name)
            self.clear_layout(self.fav_main_layout) # type: ignore
            return

        elif layout == self.set_main_layout:
            self.scroll_area.verticalScrollBar().setValue(0) # type: ignore
            self.display_sets(self.category_file_name)
            self.clear_layout(self.set_main_layout) # type: ignore
            return

        elif layout == self.cd_layout:
            if self.previous_widget == self.cd_layout:
                self.scroll_area.verticalScrollBar().setValue(0) # type: ignore
                self.clicked_set(True)
                self.clear_layout(self.cd_layout) # type: ignore
                return

            elif self.previous_widget == self.fav_main_layout:

                if len(self.favorite_list):
                    self.display_favorites()

            return
            

        

        '''if layout != self.info_header:
            self.stacked_layout.setCurrentWidget(self.main_widget)
        else:
            self.stacked_layout.setCurrentWidget(self.main_menu_widget)
        if layout != self.info_header:
            
            self.clear_layout(layout)
            self.card_img_dict = {}
        if layout == self.cd_layout:
         
            if self.previous_widget == self.cd_layout:
                self.clicked_set(True)

            elif self.previous_widget == self.fav_main_layout:

                if len(self.favorite_list):
                    self.display_favorites()'''
            

    def clear_layout(self, layout: QVBoxLayout):
        
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget() # type: ignore
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
                for bd in self.ui_button_list:
                    if bd[0] == widget:
                        self.ui_button_list.remove(bd)
            elif item.layout() is not None: # type: ignore
                self.clear_layout(item.layout()) # type: ignore

    def reload_images(self):
  
        if "Info" in self.bb_dict.keys():
        
            self.bb_dict["Info"].setIcon(QIcon(self.IM.arrow_icon[self.mode]))

        for button_data in self.ui_button_list:
            if button_data[2] is None:
                button_data[0].setIcon(QIcon(button_data[1][self.mode]))  
            else:
                button_data[0].setPixmap(button_data[1][self.mode].scaled(button_data[2], button_data[3], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))


    def switch_scrollbar(self):
        if self.mode == 1:
            self.scroll_area.setStyleSheet("""
            QAbstractScrollArea {
                background: #8d8d8d;
                border: #1a1a1a;
            }"""
                    )
            self.scroll_area.verticalScrollBar().setStyleSheet("QScrollBar" # type: ignore
                                "{"
                                "background : #1a1a1a;"
                                "}"
                                "QScrollBar::handle"
                                "{"
                                "background : #8d8d8d;"
                                "border-radius: 5px;"
                                "}"
                                "QScrollBar::handle::pressed"
                                "{"
                                "background : #aeaeae;"
                                "}"
                                
                                )
            self.scroll_area.horizontalScrollBar().setStyleSheet("QScrollBar" # type: ignore
                                "{"
                                "background : #1a1a1a;"
                                "}"
                                "QScrollBar::handle"
                                "{"
                                "background : #8d8d8d;"
                                "border-radius: 5px;"
                                "}"
                                "QScrollBar::handle::pressed"
                                "{"
                                "background : #aeaeae;"
                                "}"
                                
                                )
        elif self.mode == 0:
            self.scroll_area.setStyleSheet("""
            QAbstractScrollArea {
                background: #aeaeae;
                border: #8d8d8d;
            }"""
                    )
            self.scroll_area.verticalScrollBar().setStyleSheet("QScrollBar" # type: ignore
                                "{"
                                "background : #8d8d8d;"
                                "}"
                                "QScrollBar::handle"
                                "{"
                                "background : #aeaeae;"
                                "border-radius: 5px;"
                                "}"
                                "QScrollBar::handle::pressed"
                                "{"
                                "background : #b6b6b6;"
                                "}"
                                
                                )
            self.scroll_area.horizontalScrollBar().setStyleSheet("QScrollBar" # type: ignore
                                "{"
                                "background : #8d8d8d;"
                                "}"
                                "QScrollBar::handle"
                                "{"
                                "background : #aeaeae;"
                                "border-radius: 5px;"
                                "}"
                                "QScrollBar::handle::pressed"
                                "{"
                                "background : #b6b6b6;"
                                "}"
                                
                                )
            
    def create_exit_button(self):

        self.e_button = QPushButton("")
        self.ui_button_list.append((self.e_button, self.IM.exit_icon, None, None))
        self.e_button.setFont(self.main_font)
        self.e_button.setProperty("class", "Setting_Button")
        self.e_button.setText("Exit..")
        

        self.e_button.setIcon(QIcon(self.IM.exit_icon[self.mode]))
        self.e_button.setIconSize(QSize(36, 36))

        self.e_button.enterEvent = partial(self.on_button_enter, self.e_button)
        self.e_button.leaveEvent = partial(self.on_button_leave, self.e_button) # type: ignore
        
        self.e_button.clicked.connect(self.close)

        self.settings_layout.addWidget(self.e_button, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

    

    def run(self):
      
        self.init_set_dir()

        self.init_main_menu()
        
        self.init_cache()

        self.title()
        
        self.display_categories()

        self.toggle_theme_button()

        self.create_info_page()

        self.create_info_button()

        self.create_exit_button()

        self.init_card_data_page()

        self.app.exec()
        
