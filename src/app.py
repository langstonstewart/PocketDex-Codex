import os, json, datetime, copy, random, string, re
from functools import partial
from math import ceil

from src import (
    setmanager, 
    themes, 
    image_manager,
    media_manager,
    dex_manager
    )

from src.resource_path import resource_path

from PyQt6.QtWidgets import (
    QApplication, 
    QWidget, 
    QLabel, 
    QPushButton, 
    QToolButton, 
    QVBoxLayout, 
    QHBoxLayout, 
    QGridLayout, 
    QStackedLayout, 
    QMainWindow, 
    QSizePolicy, 
    QScrollArea, 
    QGraphicsOpacityEffect, 
    QGraphicsColorizeEffect, 
    QFileDialog, 
    QMessageBox, 
    QLineEdit
    )

from PyQt6.QtCore import (
    Qt, 
    QSize, 
    QUrl, 
    QTimer, 
    QObject, 
    pyqtSignal,
    QVariantAnimation,
    QEasingCurve
    )

from PyQt6.QtGui import (
    QFont, 
    QCursor, 
    QIcon, 
    QDesktopServices, 
    QPixmap, 
    QColor, 
    QKeySequence, 
    QShortcut, 
    QTextDocument,
    QPainter
    )

from PyQt6.QtNetwork import QNetworkAccessManager

from PyQt6 import sip

from PyQt6.QtMultimedia import (
    QMediaPlayer, 
    QAudioOutput
    )


class Application(QMainWindow):
    def __init__(self) -> None:
        self.app = QApplication([])
        super().__init__()
        os.environ['QT_MULTIMEDIA_PREFERRED_PLUGINS'] = 'windowsmediafoundation'

        self.dex_manager = dex_manager.DexManager(self)

        self.img_cache_dict = {}

        self.app_init = False
        
        self.card_img_dict = {}
         
        self.pend_reset = None

        self.widget_list = []

        self.ui_button_list = []

        self.set_manager = setmanager.SetManager()
        self.themes = themes.Themes()
        self.IM = image_manager.ImageManager()
        
        self.settings = self.init_app_data()
        
        self.setWindowIcon(QIcon(resource_path(f"src/images/ui/logo_icon.png")))
        self.setWindowTitle(f"PocketDex Codex v{self.settings['UserData']['version']}")

    
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry() # type: ignore
        
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        window_width = int(screen_width * 0.7)
        window_height = int(screen_height * 0.8)
        
        self.resize(window_width, window_height)
        
      
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        self.move(x, y)

        self.set_col_count = 6

        self.col_count = self.settings['UserData']['col_count']

        self.set_inverse = self.settings['UserData']['set_inverse']

        self.dex_inverse = self.settings['UserData']['dex_inverse']

        self.bb_dict = {}

        self.rarity_dict = {}

        self.set_sep_lens = {4: 1200, 
                             6: 1700,
                             8: 2250}
        

        
        self.selected_region = self.settings['UserData']['selected_region']
                             
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

        if 'dex_data.json' not in os.listdir(self.local_doc):
            self.set_manager.dex_data_init(self.local_doc)

        
        self.dex_manager.dex_data_init()


        self.dex_name_list = [name for name in self.dex_manager.dex_data["Pokedex"].keys()]

        if not self.dex_manager.poke_to_dex_num_dict:
            for i in range(len(self.dex_name_list)):

                self.dex_manager.poke_to_dex_num_dict[self.dex_name_list[i]] = (i + 1)

                self.dex_manager.dex_num_to_poke_dict[(i + 1)] = (self.dex_name_list[i])


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
                        if "Locked" not in set:
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
        if width:
            self.seperator_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.seperator_layout.setSpacing(0)
        
        layout.addLayout(self.seperator_layout)
        
        seperator = QLabel("")
        
        seperator.setSizePolicy(QSizePolicy.Policy.Preferred if width else QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        seperator.setProperty("class", "header4")
        seperator.setMinimumWidth(width)
        seperator.setFixedHeight(25)
        if width:
            self.seperator_layout.addWidget(seperator, alignment=Qt.AlignmentFlag.AlignHCenter)
        else:
            self.seperator_layout.addWidget(seperator)
        

    def calculate_total_quantity(self):
        
        return sum(1 for card in self.set_list if card["Quantity"] > 0)

    def print_set_title(self, set_name):

        self.set_fp = f"{self.local_doc}\\{self.category_dir}\\{self.series}\\{set_name}\\{set_name}.json"

        with open(self.set_fp, "r+") as set_file:
            self.set_list = json.load(set_file)
           

        self.set_header = QHBoxLayout()
        self.set_main_layout.addLayout(self.set_header) # type: ignore

        self.init_back_button(self.set_header, "Top")

        self.change_col_button(self.set_header, "Top")

        self.title_header = QHBoxLayout()
        self.title_header.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        #self.set_header.addStretch(1)
        self.set_main_layout.addLayout(self.title_header) # type: ignore
        #self.set_header.addStretch(1)

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
        self.title_header.addWidget(set_title)

        set_tag = QLabel(f"{set_data["SetID"]}")
        set_tag.setProperty("class", "Set_Tag")
        set_tag.setFont(self.main_font)
        set_tag.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.title_header.addWidget(set_tag)

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

            cat_button.clicked.connect(partial(self.display_sets, self.category_list[i][1])) 

            self.cat_layout.addWidget(cat_button)
        
        self.cat_layout.addStretch()

        self.seperator(self.header_layout, 715)


    def display_sets(self, category):

        if hasattr(self, 'l_button_shortcut'):
            self.l_button_shortcut.setEnabled(False) # type: ignore
            self.l_button_shortcut.deleteLater() # type: ignore
            del self.l_button_shortcut

        if hasattr(self, 'r_button_shortcut'):
            self.r_button_shortcut.setEnabled(False) # type: ignore
            self.r_button_shortcut.deleteLater() # type: ignore
            del self.r_button_shortcut

        if hasattr(self.dex_manager, 'l_button_shortcut'):
            self.dex_manager.l_button_shortcut.setEnabled(False) # type: ignore
            self.dex_manager.l_button_shortcut.deleteLater() # type: ignore
            del self.dex_manager.l_button_shortcut


        if hasattr(self.dex_manager, 'r_button_shortcut'):
            self.dex_manager.r_button_shortcut.setEnabled(False) # type: ignore
            self.dex_manager.r_button_shortcut.deleteLater() # type: ignore
            del self.dex_manager.r_button_shortcut


        self.category_file_name = category

        self.dex_manager.search_query = None

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

        

        self.category_title_layout = QHBoxLayout()
       
        
        self.main_layout.addLayout(self.category_title_layout) # type: ignore

        self.init_back_button(self.category_title_layout, "Top")

        self.create_favorite_cards_button()

        self.create_inverse_button()


        self.category_tst_layout = QVBoxLayout()

        self.main_layout.addLayout(self.category_tst_layout) # type: ignore
        
        self.cat_con_layout = QHBoxLayout()
        self.cat_con_layout.setSpacing(50)
        self.cat_con_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        self.category_tst_layout.addLayout(self.cat_con_layout) # type: ignore
        
        

        img_layout = QVBoxLayout()
        img_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        self.cat_con_layout.addLayout(img_layout)

        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.cat_con_layout.addLayout(text_layout)


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

                        if "Locked" not in self.set_dict[key][current_set]:

                            button.enterEvent = partial(self.on_button_enter, button) # type: ignore
                            button.leaveEvent = partial(self.on_button_leave, button) # type: ignore
                            button.clicked.connect(self.clicked_set)
                        else:
                            button.setEnabled(False)
                            pass

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

        self.stacked_layout.setCurrentWidget(self.main_widget)

    def save_settings(self):
        with open(resource_path(f"src/app_data/app_settings.json"), "w+") as config_file:
                json.dump(self.settings, config_file, indent=4)


    def create_inverse_button(self, key=""):

        if key != "dex":
            self.inverse_button = QPushButton(f"Sort by Newest.." if self.set_inverse else "Sort by Oldest..")
        else:
            self.inverse_button = QPushButton(f"Sort by Dex Number.." if self.dex_inverse else "Sort by Name..")

        self.ui_button_list.append((self.inverse_button, self.IM.sort_icon, None, None))
        self.inverse_button.setFont(self.main_font)
        self.inverse_button.setProperty("class", "Setting_Button")
        
        self.inverse_button.setIcon(QIcon(self.IM.sort_icon[self.mode]))
        self.inverse_button.setIconSize(QSize(36, 36))

        self.inverse_button.enterEvent = partial(self.on_button_enter, self.inverse_button)
        self.inverse_button.leaveEvent = partial(self.on_button_leave, self.inverse_button) # type: ignore
        
        if key != "dex":
            self.inverse_button.clicked.connect(self.switch_set_inverse)
        else:
            self.inverse_button.clicked.connect(self.switch_dex_inverse)

        self.bb_layout.addWidget(self.inverse_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        if key != "dex":
            self.bb_layout.addStretch()

    def switch_set_inverse(self):
        if self.set_inverse == 1:
            self.set_inverse = 0
            self.settings['UserData']['set_inverse'] = 0
            
        elif self.set_inverse == 0:
            self.set_inverse = 1
            self.settings['UserData']['set_inverse'] = 1
            
        self.save_settings()

        self.go_back(self.main_layout)

        self.display_sets(self.category_file_name)

    def switch_dex_inverse(self):
        if self.dex_inverse == 1:
            self.dex_inverse = 0
            self.settings['UserData']['dex_inverse'] = 0
            
        elif self.dex_inverse == 0:
            self.dex_inverse = 1
            self.settings['UserData']['dex_inverse'] = 1
            
        self.save_settings()

        self.go_back(self.dex_manager.main_dex_layout)

        self.dex_manager.display_dex_page()


    def create_info_page(self):
        def add_text_label(layout, text, css_class="header2"):
            label = QLabel(text)
            label.setProperty("class", css_class)
            label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            label.setFont(self.main_font)
            layout.addWidget(label)
            return label

        def add_link_label(layout, text):
            return add_text_label(layout, text, "Link_Label")

        def create_row_layout():
            row = QHBoxLayout()
            row.setSpacing(0)
            row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.info_header.addLayout(row)
            return row

        def add_icon_to_row(row, icon_dict):
            icon_label = QLabel("")
            self.ui_button_list.append((icon_label, icon_dict, 24, 24))
            icon_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            icon_label.setPixmap(icon_dict[self.mode].scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            row.addWidget(icon_label)
            return icon_label

        self.info_widget = QWidget()
        self.info_layout = QVBoxLayout()
        self.info_widget.setLayout(self.info_layout)
        self.info_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.info_header = QVBoxLayout()
        self.info_layout.addLayout(self.info_header)

        info_title = QLabel("")
        info_title.setPixmap(self.IM.codex_icon[self.mode].scaled(325, 175, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
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

        self.v_layout = create_row_layout()
        add_text_label(self.v_layout, f"Version {self.settings['UserData']['version']}.")

        self.github_layout = create_row_layout()
        add_text_label(self.github_layout, "Programmed and created by ")
        add_icon_to_row(self.github_layout, self.IM.github_icon)
        git_label = add_link_label(self.github_layout, "Jevv")
        add_text_label(self.github_layout, " © 2026")

        self.pz_layout = create_row_layout()
        add_text_label(self.pz_layout, "Set descriptions sourced from ")
        add_icon_to_row(self.pz_layout, self.IM.pz_icon)
        pz_label = add_link_label(self.pz_layout, "Pokémon Zone")
        add_text_label(self.pz_layout, " © 2024 - 2026")

        self.pc_layout = create_row_layout()
        add_text_label(self.pc_layout, "Card data sourced from ")
        add_icon_to_row(self.pc_layout, self.IM.pc_icon)
        pc_label = add_link_label(self.pc_layout, "PkmnCards")
        add_text_label(self.pc_layout, " © 2011 - 2026")

        self.pkdb_layout = create_row_layout()
        add_text_label(self.pkdb_layout, "Pokédex data sourced from ")
        add_icon_to_row(self.pkdb_layout, self.IM.pkdb_icon)
        pkdb_label = add_link_label(self.pkdb_layout, "Pokémon Database")
        add_text_label(self.pkdb_layout, " © 2008 - 2026")

        self.d_art_layout1 = create_row_layout()
        mf_art_label = add_link_label(self.d_art_layout1, "Maushold (Family of Three) Render")
        add_text_label(self.d_art_layout1, " by ")
        add_icon_to_row(self.d_art_layout1, self.IM.d_art_icon)
        bz_art_label = add_link_label(self.d_art_layout1, "Big-Z-2015")

        self.d_art_layout2 = create_row_layout()
        svr_art_label = add_link_label(self.d_art_layout2, "Squawkabilly Variant Renders")
        add_text_label(self.d_art_layout2, " by ")
        add_icon_to_row(self.d_art_layout2, self.IM.d_art_icon)
        bl_art_label = add_link_label(self.d_art_layout2, "Bloxables")

        self.dts_art_layout = create_row_layout()
        dts_art_label = add_link_label(self.dts_art_layout, "Dudunsparce Three Segment Render")
        add_text_label(self.dts_art_layout, " by ")
        add_icon_to_row(self.dts_art_layout, self.IM.d_art_icon)
        jm_art_label = add_link_label(self.dts_art_layout, "JorMxDos")

        self.serebii_layout = create_row_layout()
        add_text_label(self.serebii_layout, "Extra data sourced from ")
        add_icon_to_row(self.serebii_layout, self.IM.serebii_icon)
        serebii_label = add_link_label(self.serebii_layout, "Serebii")
        add_text_label(self.serebii_layout, " © 1999 - 2026")

        self.ltcg_layout = create_row_layout()
        add_text_label(self.ltcg_layout, "Images sourced from ")
        add_icon_to_row(self.ltcg_layout, self.IM.ltcg_icon)
        ltcg_label = add_link_label(self.ltcg_layout, "Limitless TCG")
        add_text_label(self.ltcg_layout, " © 2017 - 2026")

        self.pa_layout = create_row_layout()
        et_label = add_link_label(self.pa_layout, "EssentiarumTCG")
        add_text_label(self.pa_layout, " by ")
        nick_label = add_link_label(self.pa_layout, "Nick15")
        add_text_label(self.pa_layout, " at ")
        pal_label = add_link_label(self.pa_layout, "Pokémon Aaah!")
        add_text_label(self.pa_layout, " © 1999 - 2026")

        def on_enter(label: QLabel, event):
            label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        def on_leave(label: QLabel, event):
            label.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        def on_click(url, event):
            QDesktopServices.openUrl(QUrl(url))

        label_links = {
            git_label: "https://github.com/langstonstewart",
            pz_label: "https://www.pokemon-zone.com",
            pc_label: "https://pkmncards.com",
            serebii_label: "https://www.serebii.net",
            ltcg_label: "https://pocket.limitlesstcg.com",
            et_label: "https://www.pokemonaaah.net/art/fonts/#EssenTCG",
            nick_label: "https://www.pokemonaaah.net/news/author/nick15/",
            pal_label: "https://www.pokemonaaah.net",
            pkdb_label: "https://pokemondb.net",
            mf_art_label: "https://www.deviantart.com/big-z-2015/art/Maushold-Family-of-Three-Render-951711618",
            bz_art_label: "https://www.deviantart.com/big-z-2015/gallery",
            svr_art_label: "https://www.deviantart.com/bloxables/art/0931-Squawkabilly-Blue-Plumage-1228686230",
            bl_art_label: "https://www.deviantart.com/bloxables/gallery",
            dts_art_label: "https://www.deviantart.com/jormxdos/art/0982-Dudunsparce-Three-Segment-Form-Edit-953450838",
            jm_art_label: "https://www.deviantart.com/jormxdos/gallery",
        }

        for label, link in label_links.items():
            label.enterEvent = partial(on_enter, label)
            label.leaveEvent = partial(on_leave, label) # type: ignore
            label.mousePressEvent = partial(on_click, link) # type: ignore

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

    def change_col_button(self, layout, key=""):
      
        change_col_button = QPushButton("Change Column Count...")
        change_col_button.setProperty("class", "Setting_Button")
        change_col_button.setFont(self.main_font)
        

        change_col_button.setIcon(QIcon(self.IM.counter_icon_dict[self.col_count][self.mode]))
        change_col_button.setIconSize(QSize(36, 36))

        change_col_button.enterEvent = partial(self.on_button_enter, change_col_button)
        change_col_button.leaveEvent = partial(self.on_button_leave, change_col_button) # type: ignore
        
        change_col_button.clicked.connect(partial(self.change_col_amount, layout))

        self.bb_layout.addWidget(change_col_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom if not key else Qt.AlignmentFlag.AlignTop)

        if not key:
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
        
        self.save_settings()

        if hasattr(self.dex_manager, 'main_dex_layout') and layout == self.dex_manager.main_dex_layout:
            self.dex_manager.refresh_dex(self.selected_region)

        elif hasattr(self, 'fav_main_layout') and layout != self.fav_main_layout:
            self.clicked_set(True)
        
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

        self.dex_manager.save_dex_data()

    def remove_one_all(self):
        for button in self.plus_button_list:
            self.decrement_quantity(self.data_header, self.set_name, True, button)
        self.app.processEvents()

        with open(self.set_fp, "w") as set_file:
            json.dump(self.set_list, set_file, indent=4)

        self.dex_manager.save_dex_data()
    
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

        set_title = QLabel(f"{formatted_name}")
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
        
        if self.set_list[card_index]["Card-Type"] != 'Basic Energy':
            
            self.seperator(self.cd_layout, 1100)

        move_data_layout = QVBoxLayout()
        move_data_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        move_data_layout.setContentsMargins(0, 20, 0, 20)

        self.cd_layout.addLayout(move_data_layout) # type: ignore

        if self.set_list[card_index]["Card-Type"] == "Pokemon":
            card_header_hp_layout = QHBoxLayout()
            card_header_layout.addLayout(card_header_hp_layout)

            hp_label = QLabel()

            hp_txt = f'<span style="font-size:16px;">HP</span><span style="font-size:24px;">{self.set_list[card_index]["HP"]}</span>'

            energy_map = ''

            for type in self.set_list[card_index]["Type"].split("/"):
                energy_map += f' <img src="{self.IM.type_dict[type]}" width="20" height="20" style="vertical-align: middle;"> '
                
            hp_label.setText(f'{hp_txt}&nbsp;&nbsp;{energy_map}')
                
            hp_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            hp_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            hp_label.setFont(self.main_font_bold)

            card_header_hp_layout.addWidget(hp_label)


            if self.set_list[card_index]["Type"] in ['Fire', 'Psychic']:
                pmp_property = 'purple_ability_header'
            else:
                pmp_property = 'red_ability_header'

        else:
            

            pmp_property = 'red_ability_header'

            desc_layout = QVBoxLayout()
            desc_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            move_data_layout.addLayout(desc_layout) # type: ignore

            card_desc = self.set_list[card_index]["Description"] # type: str

            if card_desc:
                if '[' in card_desc:
                    for symbol, img_path in self.IM.energy_dict.items():
                        if not isinstance(img_path, tuple):
                            html_img = f'<img src="{img_path}" width="20" height="20">'
                        else:
                            html_img = f'<img src="{img_path[self.mode]}" width="20" height="20">'

                        card_desc = card_desc.replace(f"[{symbol}]", f" {html_img} ")

                if any(key in card_desc for key in self.IM.txt_tag_dict):

                    for tag, img_path in self.IM.txt_tag_dict.items():
                        
                        html_img = f'<img src="{img_path[self.mode]}" width="{img_path[2]}" height="{img_path[3]}">'
                        card_desc = card_desc.replace(tag, (f"Pokémon {html_img} ") if 'Pokémon' in tag else f" {html_img} ")
                        

                width = 1000

                card_desc_label = QLabel()
                card_desc_label.setTextFormat(Qt.TextFormat.RichText)
                card_desc_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                card_desc_label.setFont(self.main_font)
                card_desc_label.setProperty("class", "header2")
                card_desc_label.setFixedWidth(width)
                card_desc_label.setWordWrap(True)
                card_desc_label.setContentsMargins(0, 0, 0, 0)

                doc = QTextDocument()
                doc.setDefaultFont(self.main_font)
                doc.setHtml(card_desc)
                doc.setTextWidth(width)


                height = int(doc.size().height()) + 100
                
                card_desc_label.setFixedHeight(height)
                card_desc_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

                card_desc_label.setText(card_desc)

                desc_layout.addWidget(card_desc_label)


        
        if "Ancient-Trait" in self.set_list[card_index]:
            self.display_ancient_trait(card_index, move_data_layout)
                

        self.ability_types = [('Ability', 'Ability-Effect', 'red_ability_header'),
                                ('Poké-BODY', 'Poké-BODY-Effect', 'green_ability_header'),
                                ('Poké-POWER', 'Poké-POWER-Effect', 'red_ability_header'),
                                ('Pokémon-Power', 'Pokémon-Power-Effect', pmp_property),
                                ('Held-Item', 'Held-Item-Effect', 'lime_ability_header')]
        
            
        if "Ability" in self.set_list[card_index] and self.set_list[card_index]['Ability'] is not None:
            if any('VSTAR Power:' in a for a in self.set_list[card_index]["Ability"]):
            
                if "Moves" in self.set_list[card_index].keys():
                    self.display_moves(card_index, move_data_layout)

                self.display_abilities(card_index, move_data_layout)

            else:
                self.display_abilities(card_index, move_data_layout)

                if "Moves" in self.set_list[card_index].keys():
                    self.display_moves(card_index, move_data_layout)
                
        else:

            self.display_abilities(card_index, move_data_layout)

            if "Moves" in self.set_list[card_index].keys():
                self.display_moves(card_index, move_data_layout)

        


        if "Weakness" in self.set_list[card_index] or "Resistance" in self.set_list[card_index]:
            
            w_r_layout = QHBoxLayout()
            w_r_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            self.cd_layout.addLayout(w_r_layout) # type: ignore

            weakness_data = self.set_list[card_index]["Weakness"]

            if weakness_data:

                w_layout = QHBoxLayout()
                w_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                w_r_layout.addLayout(w_layout) # type: ignore

                weakness_txt = QLabel("Weakness")
                weakness_txt.setFont(self.main_font)
                weakness_txt.setProperty("class", "header2")
                weakness_txt.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                w_layout.addWidget(weakness_txt)

                for weakness in weakness_data.split('/'):

                    weakness_energy = QLabel("")
                    weakness_energy.setPixmap(QPixmap(self.IM.type_dict[weakness]).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # type: ignore
                    weakness_energy.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                    w_layout.addWidget(weakness_energy)

                weakness_dmg = QLabel("+20" if self.category_dir == "TCG Pocket" else self.set_list[card_index]["Weakness-Modifier"])
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

                resist_dmg = QLabel("-20" if self.category_dir == "TCG Pocket" else self.set_list[card_index]["Resistance-Modifier"])
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

        if 'Flavor-Text' in self.set_list[card_index]:
            flavor_text = self.set_list[card_index]["Flavor-Text"]
        else:
            flavor_text = None

        card_rule_list = []

        pocket_rule_list = []

        
        for rule in (self.IM.pokemon_rule_list if self.set_list[card_index]["Card-Type"] == 'Pokemon' else self.IM.trainer_rule_list):
            if rule in self.set_list[card_index].keys() and self.set_list[card_index][rule] is not None:
                card_rule_list.append(rule)
        
        if self.category_dir == "TCG Pocket" and self.set_list[card_index]["Card-Type"] != 'Pokemon':
            pocket_rule_list.append(self.IM.pocket_card_desc_dict[self.set_list[card_index]["Card-Type"]])


        if flavor_text:

            ft_layout = QVBoxLayout()
            ft_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.cd_layout.addLayout(ft_layout) # type: ignore

            width = 800

            ft_label = QLabel()
            ft_label.setTextFormat(Qt.TextFormat.RichText)
            ft_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            ft_label.setFont(self.main_font)
            ft_label.setProperty("class", "header2")
            ft_label.setFixedWidth(width)
            ft_label.setWordWrap(True)
            ft_label.setContentsMargins(0, 0, 0, 0)

            doc = QTextDocument()
            doc.setDefaultFont(self.main_font)
            doc.setHtml(flavor_text)
            doc.setTextWidth(width)

            height = int(doc.size().height()) + 100
            ft_label.setFixedHeight(height)
            ft_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

            ft_label.setText(flavor_text)

            ft_layout.addWidget(ft_label)

        rule_list = card_rule_list if card_rule_list else pocket_rule_list

        if rule_list:
            for card_rule in rule_list:

                rule_desc = card_rule if pocket_rule_list else f"{self.set_list[card_index][card_rule]}"

                if '[' in rule_desc:
                    for symbol, img_path in self.IM.energy_dict.items():
                        if not isinstance(img_path, tuple):
                            html_img = f'<img src="{img_path}" width="20" height="20">'
                        else:
                            html_img = f'<img src="{img_path[self.mode]}" width="20" height="20">'

                        rule_desc = rule_desc.replace(f"[{symbol}]", f" {html_img} ")

                if any(key in rule_desc for key in self.IM.txt_tag_dict):

                    for tag, img_path in self.IM.txt_tag_dict.items():
                        
                        html_img = f'<img src="{img_path[self.mode]}" width="{img_path[2]}" height="{img_path[3]}">'
                        rule_desc = rule_desc.replace(tag, (f"Pokémon {html_img} ") if 'Pokémon' in tag else f" {html_img} ")


                card_rule_layout = QVBoxLayout()
                card_rule_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                self.cd_layout.addLayout(card_rule_layout) # type: ignore


                width = 800

                card_rule_label = QLabel()
                card_rule_label.setTextFormat(Qt.TextFormat.RichText)
                card_rule_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                card_rule_label.setFont(self.main_font)
                card_rule_label.setProperty("class", "header2")
                card_rule_label.setFixedWidth(width)
                card_rule_label.setWordWrap(True)
                card_rule_label.setContentsMargins(0, 0, 0, 0)

                doc = QTextDocument()
                doc.setDefaultFont(self.main_font)
                doc.setHtml(rule_desc)
                doc.setTextWidth(width)

                height = int(doc.size().height()) + 100
                card_rule_label.setFixedHeight(height)
                card_rule_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

                card_rule_label.setText(rule_desc)

                card_rule_layout.addWidget(card_rule_label)


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

        button_layout.addStretch()

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

        button_layout.addStretch()
        button_layout.setContentsMargins(75, 0, 0, 0)

        self.cd_layout.addStretch() # type: ignore

        self.init_back_button(self.cd_layout, "Card_Data")

        self.bb_layout.addLayout(button_layout) # type: ignore

        set_logo = QLabel("")
        set_logo.setPixmap(self.IM.logo_dict[self.set_id].scaled(156, 156, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        self.bb_layout.addWidget(set_logo, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        self.stacked_layout.addWidget(self.cd_widget)
    
        self.stacked_layout.setCurrentWidget(self.cd_widget)

        self.scroll_area.verticalScrollBar().setValue(0) # type: ignore

    def display_moves(self, card_index, layout: QVBoxLayout):
        for i in range(len(self.set_list[card_index]["Moves"])):
            
            move_name_data = f"{self.set_list[card_index]["Moves"][i]}"

            if 'VSTAR Power:' in move_name_data:
                vsb_layout = QVBoxLayout()
                vsb_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
                layout.addLayout(vsb_layout)

                move_name_data = move_name_data.replace('VSTAR Power: ', '')
                vstar_banner = QLabel('')
                vstar_banner.setPixmap(self.IM.vstar_banner.scaled(self.IM.vstar_banner.width() // 2, self.IM.vstar_banner.height() // 2, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                vstar_banner.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
                vstar_banner.setProperty("class", "header2")
                vstar_banner.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

                vsb_layout.addWidget(vstar_banner)

            move_layout = QHBoxLayout()
            move_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            layout.addLayout(move_layout)

            for energy in self.set_list[card_index]["Move-Energy"][i]:

                m_energy = QLabel(f"")
                if isinstance(self.IM.energy_dict[energy], tuple):
                    m_energy.setPixmap(QPixmap(self.IM.energy_dict[energy][self.mode]).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                else:
                    m_energy.setPixmap(QPixmap(self.IM.energy_dict[energy]).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                m_energy.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                m_energy.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

                move_layout.addWidget(m_energy)

            

            if any(key in move_name_data for key in self.IM.txt_tag_dict):

                for tag, img_path in self.IM.txt_tag_dict.items():
                    
                    html_img = f'<img src="{img_path[self.mode]}" width="{img_path[2]}" height="{img_path[3]}">'
                    move_name_data = move_name_data.replace(tag, f" {html_img} ")

            
        
            move_name = QLabel(move_name_data)
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

                if '[' in move_effect:
                    for symbol, img_path in self.IM.energy_dict.items():
                        if not isinstance(img_path, tuple):
                            html_img = f'<img src="{img_path}" width="20" height="20">'
                        else:
                            html_img = f'<img src="{img_path[self.mode]}" width="20" height="20">'
                        
                        move_effect = move_effect.replace(f"[{symbol}]", f" {html_img} ")
                
                if any(key in move_effect for key in self.IM.txt_tag_dict):

                    for tag, img_path in self.IM.txt_tag_dict.items():
                        
                        html_img = f'<img src="{img_path[self.mode]}" width="{img_path[2]}" height="{img_path[3]}">'
                        move_effect = move_effect.replace(tag, (f"Pokémon {html_img} ") if 'Pokémon' in tag else f" {html_img} ")

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
                move_effect_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
                
                layout.addWidget(move_effect_label)

    def display_ancient_trait(self, card_index, layout: QVBoxLayout):

       
        at_data = self.set_list[card_index]["Ancient-Trait"].split(" ")

        at_name = at_data[-1] # type: str

        at_effect = self.set_list[card_index]["Ancient-Trait-Effect"] # type: str

        for symbol, img_path in self.IM.energy_dict.items():
            if not isinstance(img_path, tuple):
                html_img = f'<img src="{img_path}" width="20" height="20">'
            else:
                html_img = f'<img src="{img_path[self.mode]}" width="20" height="20">'

            at_effect = at_effect.replace(f"[{symbol}]", f" {html_img} ")

        
        at_layout = QHBoxLayout()
        at_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addLayout(at_layout) # type: ignore


        at_icon = QLabel()
        
        at_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        at_icon.setFont(self.main_font_bold)
        at_icon.setProperty("class", "header2")

        at_icon.setPixmap(self.IM.trait_dict[at_data[0]].scaled(self.IM.trait_dict[at_data[0]].width() // 2, self.IM.trait_dict[at_data[0]].height() // 2, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        at_icon.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        at_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        at_layout.addWidget(at_icon)
            

        at_txt = QLabel(at_name)
        
        at_txt.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        at_txt.setFont(self.main_font_bold)
        at_txt.setProperty("class", "header2")

        at_txt.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        at_txt.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        at_layout.addWidget(at_txt)

        ate_layout = QHBoxLayout()
        ate_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addLayout(ate_layout) # type: ignore

        width = 1000

        at_effect_label = QLabel(at_effect)
        at_effect_label.setTextFormat(Qt.TextFormat.RichText)
        at_effect_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        at_effect_label.setFont(self.main_font)
        at_effect_label.setProperty("class", "header2")
        at_effect_label.setFixedWidth(width)
        at_effect_label.setWordWrap(True)
        at_effect_label.setContentsMargins(0, 0, 0, 0)

        doc = QTextDocument()
        doc.setDefaultFont(self.main_font)
        doc.setHtml(at_effect)
        doc.setTextWidth(width)

        height = int(doc.size().height()) + 100
        at_effect_label.setFixedHeight(height)
        at_effect_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        at_effect_label.setText(at_effect)

        ate_layout.addWidget(at_effect_label)



    def display_abilities(self, card_index, layout: QVBoxLayout):

        for ability_type in self.ability_types:

            if ability_type[0] in self.set_list[card_index].keys() and self.set_list[card_index][ability_type[0]] is not None:

                for i in range (len(self.set_list[card_index][ability_type[0]])):

                    ability_text = f"{self.set_list[card_index][ability_type[0]][i]}"

                    ability_property = ability_type[2]

                    if ability_type[0] == "Pokémon-Power":
                        label_txt = "Pokémon-Power:"

                    elif ability_type[0] == 'Held-Item':
                        label_txt = "Held Item:"
                    else:
                        label_txt = ""

                    if 'VSTAR Power:' in ability_text:
                        vsb_layout = QVBoxLayout()
                        vsb_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
                        layout.addLayout(vsb_layout)

                        ability_text = ability_text.replace('VSTAR Power: ', '')
                        vstar_banner = QLabel('')
                        vstar_banner.setPixmap(self.IM.vstar_banner.scaled(self.IM.vstar_banner.width() // 2, self.IM.vstar_banner.height() // 2, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                        vstar_banner.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
                        vstar_banner.setProperty("class", "header2")
                        vstar_banner.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

                        vsb_layout.addWidget(vstar_banner)

                    ability_layout = QHBoxLayout()
                    
                    ability_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    layout.addLayout(ability_layout) # type: ignore

                    ability_banner = QLabel(label_txt)
                    ability_banner.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    ability_banner.setFont(self.main_font_bold)
                    ability_banner.setProperty("class", ability_property)

                    if ability_type[0] not in ['Pokémon-Power', 'Held-Item']:
                        ability_img = self.IM.ability_img_dict[ability_type[0]]
                        ability_banner.setPixmap(ability_img)

                    ability_banner.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                    ability_banner.setAlignment(Qt.AlignmentFlag.AlignHCenter)

                    ability_layout.addWidget(ability_banner)

                    ability_label = QLabel(ability_text)
                    ability_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    ability_label.setFont(self.main_font_bold)
                    ability_label.setProperty("class", ability_property)
                    ability_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

                    ability_layout.addWidget(ability_label)


                    ability_effect_data = self.set_list[card_index][ability_type[1]][i] # type: str
 
                    for symbol, img_path in self.IM.energy_dict.items():
                        if not isinstance(img_path, tuple):
                            html_img = f'<img src="{img_path}" width="20" height="20">'
                        else:
                            html_img = f'<img src="{img_path[self.mode]}" width="20" height="20">'

                        ability_effect_data = ability_effect_data.replace(f"[{symbol}]", f" {html_img} ")

                    if any(key in ability_effect_data for key in self.IM.txt_tag_dict):

                        for tag, img_path in self.IM.txt_tag_dict.items():
                            
                            html_img = f'<img src="{img_path[self.mode]}" width="{img_path[2]}" height="{img_path[3]}">'
                            ability_effect_data = ability_effect_data.replace(tag, (f"Pokémon {html_img} ") if 'Pokémon' in tag else f" {html_img} ")

                    width = 1000

                    ability_effect_text = QLabel()
                    ability_effect_text.setTextFormat(Qt.TextFormat.RichText)
                    ability_effect_text.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    ability_effect_text.setFont(self.main_font)
                    ability_effect_text.setProperty("class", "header2")
                    ability_effect_text.setFixedWidth(width)
                    ability_effect_text.setWordWrap(True)
                    ability_effect_text.setContentsMargins(0, 0, 0, 0)

                    doc = QTextDocument()
                    doc.setDefaultFont(self.main_font)
                    doc.setHtml(ability_effect_data)
                    doc.setTextWidth(width)

                    height = int(doc.size().height()) + 100
                    ability_effect_text.setFixedHeight(height)
                    ability_effect_text.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

                    ability_effect_text.setText(ability_effect_data)

                    layout.addWidget(ability_effect_text)

        

    def create_card(self, card_index, layout, clickable=True, row=0, col=0, favorites_menu=False, f_index=0):
        
        card_widget = QWidget()
        current_set_id = self.set_id
        current_card_id = self.set_list[card_index]["ID"]

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
                if current_set_id not in self.img_cache_dict:
                    self.img_cache_dict[current_set_id] = {}
                self.img_cache_dict[current_set_id][current_card_id] = pix

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
                     ("LEGEND", "vertical-align: top;"), 
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
            
        elif '-GX' in card_text:

            if 'Ultra Beast' in self.set_list[card_index]["Card-Categories"]:
                if 'TAG TEAM' in self.set_list[card_index]["Card-Categories"]:

                    img_path = self.IM.tag_dict["GX-UB-TAG-TEAM"]
                else:
                    img_path = self.IM.tag_dict["GX-UB"]
            else:
                if 'TAG TEAM' in self.set_list[card_index]["Card-Categories"]:

                    img_path = self.IM.tag_dict["GX-TAG-TEAM"]
                else:
                    img_path = self.IM.tag_dict["GX"]

            html_img = f'<img src="{img_path}" style="vertical-align: top;">'
            card_text = card_text.replace('-GX', f' {html_img}').strip()

        elif "Prism Star" in card_text:

            img_path = self.IM.tag_dict["Prism Star"]

            html_img = f'<img src="{img_path}" style="vertical-align: top;">'
            card_text = card_text.replace("Prism Star", f' {html_img}').strip()

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

        if any(tag in card_text for tag in self.IM.txt_tag_energy_dict):
            for tag in self.IM.txt_tag_energy_dict:
                if tag in card_text:
                   
                    img_path = self.IM.txt_tag_energy_dict[tag][self.mode]

                    html_img = f'<img src="{img_path}" style="vertical-align: top;">'
                    card_text = card_text.replace(tag, f' {html_img} ').strip()

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
            card_rarity.setPixmap(self.rarity_dict[self.set_list[card_index]["Rarity"]] if self.set_list[card_index]["Rarity"] not in ["N/A", "No Rarity"] else self.rarity_dict["N/A"][self.mode].scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # type: ignore
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
            plus_button.setProperty("name", card_text)
            plus_button.setProperty("card_type", self.set_list[card_index]["Card-Type"])
            plus_button.setIcon(QIcon(self.IM.plus_icon[self.mode]))
            plus_button.setIconSize(QSize(36, 36))
            plus_button.setMinimumHeight(70)
            plus_button.setMinimumWidth(70)
            
            plus_button.enterEvent = partial(self.on_button_enter, plus_button)
            plus_button.leaveEvent = partial(self.on_button_leave, plus_button) # type: ignore

            plus_button.clicked.connect(partial(self.increment_quantity, layout, self.set_name, False, QPushButton))

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

                    if 'skeleton' in self.set_list[current_card]:
                        card_clickable = False
                    else:
                        card_clickable = True
                    
                    self.create_card(current_card, self.card_grid, card_clickable, r, c)
                    
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
            
            if hasattr(self, 'card_grid') and layout == self.card_grid:
                self.fb_list[fb.property("index")].setIcon(QIcon(self.IM.favorite_icon[2])) # type: ignore

            else:
                self.fb_list[0].setIcon(QIcon(self.IM.favorite_icon[2])) # type: ignore
            
        else:
            self.set_list[fb.property("index")]["Favorite"] = 0 # type: ignore
            
            for index, f in enumerate(self.favorite_list):
                if f["ID"] == self.set_list[fb.property("index")]["ID"]: # type: ignore
                    self.favorite_list.pop(index)

            if hasattr(self, 'card_grid') and layout == self.card_grid:
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
        
        if hasattr(self, 'card_grid') and layout == self.card_grid:
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

        poke_name = button.property("name") # type: ignore

        if button.property("card_type") == "Pokemon": # type: ignore
            self.dex_manager.add_to_dex(poke_name)
        
        if self.set_list[button.property("index")]["Quantity"] < 99: # type: ignore
            self.set_list[button.property("index")]["Quantity"] += 1 # type: ignore
        else:
            return
        
        if hasattr(self, 'card_grid') and layout == self.card_grid:
            self.card_count.setText(f"{self.calculate_total_quantity()}/{len(self.set_list)} Cards")
        
        self.update_card_opacity(self.card_img_dict[button.property("id")], self.set_list[button.property("index")]["Quantity"]) # type: ignore

        if not all:
            with open(self.set_fp, "w") as set_file:
                json.dump(self.set_list, set_file, indent=4)

            self.dex_manager.save_dex_data()

        self.card_quantity_dict[button.property("index")].setText(f"{self.set_list[button.property("index")]["Quantity"]}") # type: ignore

            

    def toggle_theme_button(self):

    
        self.theme_button = QPushButton("Toggle Theme..")
        self.ui_button_list.append((self.theme_button, self.IM.theme_icon, None, None))

        self.theme_button.setFont(self.main_font)
        self.theme_button.setProperty("class", "Setting_Button")

        self.theme_button.setIcon(QIcon(self.IM.theme_icon[self.mode]))
        self.theme_button.setIconSize(QSize(36, 36))

        self.theme_button.enterEvent = partial(self.on_button_enter, self.theme_button)
        self.theme_button.leaveEvent = partial(self.on_button_leave, self.theme_button) # type: ignore
        
        self.theme_button.clicked.connect(self.toggle_theme)

        self.dex_manager.settings_layout.addWidget(self.theme_button, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

    def create_favorite_cards_button(self, key=""):

        self.f_button = QPushButton("")
        self.ui_button_list.append((self.f_button, self.IM.heart_button_icon, None, None))
        self.f_button.setFont(self.main_font)
        self.f_button.setProperty("class", "Setting_Button")
        self.f_button.setText("View Favorites..")
        

        self.f_button.setIcon(QIcon(self.IM.heart_button_icon[self.mode]))
        self.f_button.setIconSize(QSize(36, 36))

        self.f_button.enterEvent = partial(self.on_button_enter, self.f_button)
        self.f_button.leaveEvent = partial(self.on_button_leave, self.f_button) # type: ignore
        
        if key != "dex":
            self.f_button.clicked.connect(self.display_favorites)
        else:
            self.f_button.clicked.connect(partial(self.dex_manager.refresh_dex, self.selected_region, False, True))

        self.bb_layout.addWidget(self.f_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

    def init_rarities(self):
        scale_int = 1 if self.category_dir == "TCG Pocket" else 3

        self.rarity_dict["N/A"] = (QPixmap(resource_path(f"src/images/rarities/TCG/no_rarity_black.png")), QPixmap(resource_path(f"src/images/rarities/TCG/no_rarity_white.png")))
        self.rarity_dict["No Rarity"] = (QPixmap(resource_path(f"src/images/rarities/TCG/no_rarity_black.png")), QPixmap(resource_path(f"src/images/rarities/TCG/no_rarity_white.png")))

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

                        if 'skeleton' in self.favorite_list[current_card]:
                            card_clickable = False
                        else:
                            card_clickable = True
                        
                        self.create_card(self.favorite_list[current_card]["Index"], self.fav_grid, card_clickable, r, c, True, current_card)
                        
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

            if hasattr(self, 'main_layout') and self.main_layout is not None:
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

        self.dex_manager.settings_layout.addWidget(self.info_button, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

        
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

        self.save_settings()

        self.reload_images()


    def init_back_button(self, layout, key):

        self.bb_layout = QHBoxLayout()
        self.bb_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addLayout(self.bb_layout)
        

        back_button = QPushButton("")
        back_button.setProperty("class", "Setting_Button")
        back_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        back_button.setIcon(QIcon(self.IM.arrow_icon[self.mode]))
        back_button.setIconSize(QSize(36, 36))

        back_button.enterEvent = partial(self.on_button_enter, back_button)
        back_button.leaveEvent = partial(self.on_button_leave, back_button) # type: ignore

        back_button.clicked.connect(partial(self.go_back, layout))

        self.bb_dict[key] = back_button

        self.ui_button_list.append((back_button, self.IM.arrow_icon, None, None))

        self.bb_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop if key == 'Top' else Qt.AlignmentFlag.AlignBottom)



    def go_back(self, layout):    

    
        if hasattr(self, 'main_layout') and layout == self.main_layout or hasattr(self, 'info_header') and layout == self.info_header or hasattr(self, 'category_title_layout') and layout == self.category_title_layout:
            self.scroll_area.verticalScrollBar().setValue(0) # type: ignore
            self.stacked_layout.setCurrentWidget(self.main_menu_widget)

            if hasattr(self, 'main_layout') and self.main_layout is not None:
                self.clear_layout(self.main_layout) # type: ignore
            return
        
        if hasattr(self, 'fav_main_layout') and layout == self.fav_main_layout:
            self.scroll_area.verticalScrollBar().setValue(0) # type: ignore
            self.display_sets(self.category_file_name)
            self.clear_layout(self.fav_main_layout) # type: ignore
            return

        elif hasattr(self.dex_manager, 'main_dex_layout') and layout == self.dex_manager.main_dex_layout:
            self.scroll_area.verticalScrollBar().setValue(0) # type: ignore
            self.stacked_layout.setCurrentWidget(self.main_menu_widget)


            if hasattr(self.dex_manager, 'main_dex_layout') and self.dex_manager.main_dex_layout is not None:
                self.clear_layout(self.dex_manager.main_dex_layout) # type: ignore
                
            return
        
        elif hasattr(self.dex_manager, 'dex_data_layout') and layout == self.dex_manager.dex_data_layout:
            self.scroll_area.verticalScrollBar().setValue(0) # type: ignore

            self.dex_manager.main_dex_widget.setSizePolicy(
                    QSizePolicy.Policy.Expanding, 
                    QSizePolicy.Policy.Expanding
                )
            self.stacked_layout.setCurrentWidget(self.dex_manager.main_dex_widget)

            self.clear_layout(self.dex_manager.dex_data_layout) # type: ignore
            

            if self.pend_reset:
        
                self.dex_manager.refresh_dex(self.selected_region, False, False)

                self.pend_reset = False
                

        
        elif (hasattr(self, 'set_main_layout') and layout == self.set_main_layout) or self.set_header:
            self.scroll_area.verticalScrollBar().setValue(0) # type: ignore
            self.display_sets(self.category_file_name)
            self.clear_layout(self.set_main_layout) # type: ignore
            return

        elif hasattr(self, 'cd_layout') and layout == self.cd_layout:
            if self.previous_widget == self.cd_layout:
                self.scroll_area.verticalScrollBar().setValue(0) # type: ignore
                self.clicked_set(True)
                self.clear_layout(self.cd_layout) # type: ignore
                return

            elif self.previous_widget == self.fav_main_layout:

                if len(self.favorite_list):
                    self.display_favorites()

            return


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

        self.dex_manager.settings_layout.addWidget(self.e_button, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

        

    def run(self):
      
        self.init_set_dir()
        
        self.init_main_menu()
        
        self.init_cache()

        self.title()
        
        self.display_categories()

        self.dex_manager.media_player_init()

        self.dex_manager.create_dex_button()

        self.toggle_theme_button()

        self.create_info_page()

        self.create_info_button()

        self.create_exit_button()

        self.init_card_data_page()

        self.app.exec()