import os, json, time
from src import setmanager, themes, image_manager
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QStackedLayout, QMainWindow, QSizePolicy, QScrollArea, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QSize, QUrl, QTimer
from PyQt6.QtGui import QFont, QCursor, QIcon, QDesktopServices
from math import ceil
from functools import partial

class Application(QMainWindow):
    def __init__(self) -> None:
        self.app = QApplication([])
        super().__init__()
        
        self.set_manager = setmanager.SetManager()
        self.themes = themes.Themes()
        self.IM = image_manager.ImageManager()
        self.settings = self.init_app_data()
        self.resize(1400, 1150)
        self.setWindowIcon(QIcon("src/images/ui/logo_icon.png"))
        self.setWindowTitle(f"PocketDex Codex v{self.settings['UserData']['version']}")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.main_font = QFont("Gill Sans MT", 10, QFont.Weight.Normal, italic=False)
        self.main_font_bold = QFont("Gill Sans MT", 10, QFont.Weight.Bold, italic=False)

        self.fullscreen = False

        self.container = QWidget()

        self.stacked_layout = QStackedLayout(self.container)

        self.main_widget = QWidget()

        self.stacked_layout.addWidget(self.main_widget)

        self.header_layout = QVBoxLayout(self.main_widget)

        self.scroll_area.setWidget(self.container)

        self.main_widget.setLayout(self.header_layout)

        self.setCentralWidget(self.scroll_area)

        self.keyPressEvent = self.toggle_fullscreen # type: ignore

        self.mode = self.settings['UserData']['theme']
        self.switch_scrollbar()
        self.main_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)


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
        with open(f'src\\app_data\\app_settings.json', "r+") as settings_file:
            return json.load(settings_file)

    def init_set_dir(self):
        self.set_dir = f"src\\app_data"
        self.local_doc = os.path.join(os.path.expanduser("~"), "Documents", "PocketDex Codex")
        os.makedirs(f"{self.set_dir}\\set_data", exist_ok=True)
        os.makedirs(self.local_doc, exist_ok=True)

        
        with open(f'{self.set_dir}\\set_list.json', 'r+', encoding="UTF-8") as set_file:
            self.set_dict = json.load(set_file)

        if len(self.set_dict["SetList"]) != len(os.listdir(self.local_doc)) - 1:
            for set in self.set_dict["SetList"]:
                local_set_folder = f"{self.local_doc}\\{set["Name"]}"
                project_set_folder = f"{self.set_dir}\\set_data\\{set["Name"]}"
                os.makedirs(local_set_folder, exist_ok=True)
                os.makedirs(project_set_folder, exist_ok=True)
                if not os.listdir(local_set_folder):
                    self.set_manager.create_set(set["Name"], set["SetID"], local_set_folder)
                os.makedirs(f"{project_set_folder}\\cards", exist_ok=True)

    def init_cache(self):
        self.cache_dict = {}
        for set in self.set_dict["SetList"]:
            with open(f"{self.local_doc}\\{set["Name"]}\\{set["Name"]}.json", "r+") as set_file:
                self.set_list = json.load(set_file)
                
                if len(os.listdir(f"{self.set_dir}\\set_data\\{set["Name"]}\\cards")) != len(self.set_list):
                    for card in self.set_list:
                        card_cache = image_manager.ImageLabel(card["Image"], card["ID"], f"{self.set_dir}\\set_data\\{set["Name"]}\\cards", True)
                        self.cache_dict[card["ID"]] = card_cache
                    time.sleep(0.1)
                    self.app.processEvents()



    def title(self):
        self.title_layout = QHBoxLayout()
        self.h2_layout = QVBoxLayout()
        self.title_layout.setSpacing(0)
        self.title_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.header_layout.addLayout(self.title_layout)
        self.h2_layout.setSpacing(0)
        self.h2_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.header_layout.addLayout(self.h2_layout)

        self.title_icon = QLabel("", self.main_widget)
        self.title_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    
        self.h2 = QLabel("- An application for Pokémon Trading Card Game Pocket ™ -", self.main_widget)

        self.title_icon.setPixmap(self.IM.codex_icon[self.mode].scaled(650, 350, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self.title_icon.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.h2.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.h2.setProperty("class", "header2")
        self.h2.setFont(self.main_font)

        self.title_layout.addWidget(self.title_icon)
    
        self.h2_layout.addWidget(self.h2)

        self.seperator(self.header_layout)

        self.h3_layout = QHBoxLayout()
        self.h3_layout.setSpacing(0)
        self.h3_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.header_layout.addLayout(self.h3_layout)
        self.h3 = QLabel("Please select a set below:", self.main_widget)
        self.h3.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.h3.setProperty("class", "header2")
        self.h3.setFont(self.main_font)
        self.h3_layout.addWidget(self.h3)

    def seperator(self, layout):
        self.seperator_layout = QHBoxLayout()
        self.seperator_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.seperator_layout.setSpacing(0)
        
        layout.addLayout(self.seperator_layout)
        
        seperator = QLabel("")
        
        seperator.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        seperator.setProperty("class", "header4")
        seperator.setMinimumWidth(800 if layout == self.header_layout else 1100)
        seperator.setFixedHeight(25)
       
        self.seperator_layout.addWidget(seperator, alignment=Qt.AlignmentFlag.AlignHCenter)
        

    def calculate_total_quantity(self):
        
        return sum(1 for card in self.set_list if card["Quantity"] > 0)

    def print_set_title(self, set_name):

    
           

        self.set_header = QHBoxLayout()
        self.set_header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.set_main_layout.addLayout(self.set_header)

        self.data_header = QHBoxLayout()
        self.data_header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.set_main_layout.addLayout(self.data_header)

        for d in self.set_dict["SetList"]:
            if d["Name"] == self.set_name:
                set_data =  d

        formatted_name = set_name.split()
        del formatted_name[-1]
        formatted_name = " ".join(formatted_name)

        set_title = QLabel(f"{formatted_name}")
        set_tag = QLabel("")
        set_date = QLabel(f"{set_data["Release Date"]}")
        self.card_count = QLabel(f"{self.calculate_total_quantity()}/{len(self.set_list)} Cards")

        set_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        set_title.setProperty("class", "header1")
        set_title.setFont(self.main_font)
        self.set_header.addWidget(set_title)

        set_tag.setPixmap(self.IM.logo_dict[self.set_id][1].scaled(150, 88, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
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
        

    def display_sets(self):
        
        self.set_layout = QGridLayout()
        self.set_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.set_layout.setSpacing(5)
        self.header_layout.addLayout(self.set_layout)
        col_length = 4
        row_length = ceil(len(self.set_dict['SetList']) / col_length)
        current_set = 0
        all_rows = False
        while True:
            if all_rows:
                break
            for r in range(row_length):
                if all_rows:
                    break
                for c in range(col_length):
                    button = QPushButton(f"", self.main_widget)
                    button.setIcon(QIcon(self.IM.logo_dict[self.set_dict['SetList'][current_set]['SetID']][0]))
                    button.setIconSize(QSize(156, 156))
                    button.setMaximumHeight(125)
                    self.set_layout.addWidget(button, r, c)
                    button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                    
                    button.setProperty("class", "Main_Button")
                    button.setProperty("Name", self.set_dict['SetList'][current_set]['Name'])
                    button.setProperty("ID", self.set_dict['SetList'][current_set]['SetID'])

                    button.enterEvent = partial(self.on_button_enter, button)
                    button.leaveEvent = partial(self.on_button_enter, button) # type: ignore
                    
                    button.clicked.connect(self.clicked_set)
                    current_set += 1
                    if current_set == len(self.set_dict['SetList']):
                        all_rows = True
                        
                        break
        self.seperator(self.header_layout)

    def create_info_page(self):
        self.info_widget = QWidget()
        
        self.info_layout = QVBoxLayout()
        self.info_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.info_widget.setLayout(self.info_layout)
        
        self.info_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.info_header = QVBoxLayout()
        self.info_header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.info_layout.addLayout(self.info_header)
        
        info_title = QLabel("")

        info_title.setPixmap(self.IM.codex_icon[self.mode].scaled(650, 350, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        info_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        info_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.info_header.addWidget(info_title)

        self.seperator(self.info_header)

        dis_label = QLabel('''DISCLAIMER: 
This script is a fan-made project intended for personal and educational purposes.
All rights, trademarks, and intellectual property related to Pokémon, including names, images,
and game mechanics, belong to The Pokémon Company, Nintendo, Game Freak, and Creatures Inc.
This project is not affiliated with, endorsed by, or associated with these entities.''')
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

        self.seperator(self.info_header)

        self.init_back_button(self.info_header)


    def display_info_page(self):

        self.info_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)

        self.stacked_layout.addWidget(self.info_widget)

        self.stacked_layout.setCurrentWidget(self.info_widget)


    def clicked_set(self):
        button = self.sender()
        self.set_name = button.property('Name') # type: ignore
        self.set_id = button.property('ID') # type: ignore

        self.set_widget = QWidget()
        
        self.set_main_layout = QVBoxLayout()
        self.set_main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.set_widget.setLayout(self.set_main_layout)
        self.set_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)
        self.set_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.print_set_title(self.set_name)

        self.seperator(self.set_main_layout)

        self.card_grid = QGridLayout(self.set_widget)
        self.card_grid.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.card_grid.setVerticalSpacing(25)
        self.card_grid.setHorizontalSpacing(25)
        self.set_main_layout.addLayout(self.card_grid)

        self.display_loading_page()  

        QTimer.singleShot(100, self.await_cache)
        
        
        

    def await_cache(self): 
                
        if len(os.listdir(f"{self.set_dir}\\set_data\\{self.set_name}\\cards")) != len(self.set_list):
            QTimer.singleShot(100, self.await_cache)
            return
            
        self.display_cards()

        self.seperator(self.set_main_layout)

        self.init_back_button(self.set_main_layout)

        self.stacked_layout.addWidget(self.set_widget)

        self.stacked_layout.setCurrentWidget(self.set_widget)
                   

            
    
    def display_loading_page(self):
        self.loading_widget = QWidget()
        
        self.loading_layout = QVBoxLayout()
        self.loading_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.loading_widget.setLayout(self.loading_layout)
        self.loading_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)
        self.loading_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.print_loading_title(self.set_name)

        

    def print_loading_title(self, set_name: str):
        
        self.set_fp = f"{self.local_doc}\\{set_name}\\{set_name}.json"

        with open(self.set_fp, "r+") as set_file:
            self.set_list = json.load(set_file)


        self.loading_header = QHBoxLayout()
        self.loading_header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.loading_layout.addLayout(self.loading_header)

        self.ld_header = QHBoxLayout()
        self.ld_header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.loading_layout.addLayout(self.ld_header)

        self.set_info_layout = QVBoxLayout()
        self.set_info_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.set_info_layout
        self.loading_layout.addLayout(self.set_info_layout)

        for d in self.set_dict["SetList"]:
            if d["Name"] == self.set_name:
                set_data =  d

        formatted_name = set_name.split()
        del formatted_name[-1]
        formatted_name = " ".join(formatted_name)

        set_title = QLabel(f"{formatted_name} (Loading..)")
        set_tag = QLabel("")
        set_date = QLabel(f"{set_data["Release Date"]}")
        card_count = QLabel(f"{self.calculate_total_quantity()}/{len(self.set_list)} Cards")
        info_label = QLabel(f"{set_data["Info"]}")
        cache_label = QLabel(f"Please wait for images to finish downloading.\nOn first load, this will take roughly 1-2 minutes..")

        set_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        set_title.setProperty("class", "header1")
        set_title.setFont(self.main_font)
        self.loading_header.addWidget(set_title)

        set_tag.setPixmap(self.IM.logo_dict[self.set_id][1].scaled(150, 88, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
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

        self.seperator(self.set_info_layout)

        info_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        info_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        info_label.setProperty("class", "header2")
        info_label.setWordWrap(True)
        info_label.setFont(self.main_font)

        cache_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        cache_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        cache_label.setProperty("class", "header2")
        cache_label.setWordWrap(True)
        cache_label.setFont(self.main_font)

        self.set_info_layout.addWidget(info_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.set_info_layout.addWidget(cache_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.stacked_layout.addWidget(self.loading_widget)

        self.stacked_layout.setCurrentWidget(self.loading_widget)


    def display_cards(self):

        self.card_img_dict = {}
        self.card_quantity_dict = {}
        
        col_length = 4
        row_length = ceil(len(self.set_list) / col_length)
        current_card = 0
        all_rows = False

        while True:
            if all_rows:
                break
            for r in range(row_length):
                if all_rows:
                    break
                for c in range(col_length):
                    
                    card_widget = QWidget()

                    card_layout = QVBoxLayout(card_widget)
                    card_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    card_layout.setSpacing(10)

                    card_widget.setLayout(card_layout)

                    card_img = image_manager.ImageLabel(self.set_list[current_card]["Image"], self.set_list[current_card]["ID"], f"{self.set_dir}\\set_data\\{self.set_name}\\cards", False)
                    card_img.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                    
                    self.update_card_opacity(card_img, self.set_list[current_card]["Quantity"])
                    card_layout.addWidget(card_img)

                    self.card_img_dict[current_card] = card_img

                    card_name = QLabel(f"{self.set_list[current_card]["Name"]}")
                    
                    card_name.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
                    card_name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    card_name.setFont(self.main_font_bold)
                    card_name.setProperty("class", "header2")
                    card_name.setWordWrap(True)
                
                    card_name.setMaximumWidth(1000)
                    
                    card_layout.addWidget(card_name)

                    if self.set_list[current_card]["Rarity"] != "N/A":
                        card_rarity = QLabel("")
                        card_rarity.setPixmap(self.IM.rarity_dict[self.set_list[current_card]["Rarity"]])
                        card_rarity.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                        card_rarity.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                        card_layout.addWidget(card_rarity)

                    data_layout = QHBoxLayout()
                    data_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            
                    card_layout.addLayout(data_layout)

                    minus_button = QPushButton("")
                    minus_button.setProperty("index", current_card)
                    plus_button = QPushButton("")
                    plus_button.setProperty("index", current_card)

                    minus_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                    minus_button.setProperty("class", "Main_Button")
                    minus_button.setIcon(QIcon(self.IM.minus_icon[self.mode]))
                    minus_button.setIconSize(QSize(36, 36))
                    minus_button.setMinimumHeight(70)
                    minus_button.setMinimumWidth(70)

                    minus_button.enterEvent = partial(self.on_button_enter, minus_button)
                    minus_button.leaveEvent = partial(self.on_button_enter, minus_button) # type: ignore

                    minus_button.clicked.connect(self.decrement_quantity)

                    quantity_label = QLabel(f"{self.set_list[current_card]["Quantity"]}")
                    quantity_label.setFixedWidth(35)
                    quantity_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    quantity_label.setFont(self.main_font_bold)

                    quantity_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                    quantity_label.setProperty("class", "header3")

                    self.card_quantity_dict[current_card] = quantity_label

                    plus_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                    plus_button.setProperty("class", "Main_Button")
                    plus_button.setIcon(QIcon(self.IM.plus_icon[self.mode]))
                    plus_button.setIconSize(QSize(36, 36))
                    plus_button.setMinimumHeight(70)
                    plus_button.setMinimumWidth(70)
                    
                    plus_button.enterEvent = partial(self.on_button_enter, plus_button)
                    plus_button.leaveEvent = partial(self.on_button_enter, plus_button) # type: ignore

                    plus_button.clicked.connect(self.increment_quantity)

                    data_layout.addWidget(minus_button)
                    data_layout.addWidget(quantity_label)
                    data_layout.addWidget(plus_button)
                    
                    self.card_grid.addWidget(card_widget, r, c, alignment=Qt.AlignmentFlag.AlignHCenter)
                    current_card += 1
                    if current_card == len(self.set_list):
                        all_rows = True
                        break
    
    def update_card_opacity(self, card: QLabel, quan):
        card_op = QGraphicsOpacityEffect()
        op = 0.5 if quan == 0 else 1.0
        card_op.setOpacity(op)
        card.setGraphicsEffect(card_op)
        


    def decrement_quantity(self):
        button = self.sender()
        
        if self.set_list[button.property("index")]["Quantity"] > 0: # type: ignore
            self.set_list[button.property("index")]["Quantity"] -= 1 # type: ignore
        else:
            return
        
        self.card_count.setText(f"{self.calculate_total_quantity()}/{len(self.set_list)} Cards")
        
        self.update_card_opacity(self.card_img_dict[button.property("index")], self.set_list[button.property("index")]["Quantity"]) # type: ignore
    
        with open(self.set_fp, "w") as set_file:
            json.dump(self.set_list, set_file, indent=4)
        
        self.card_quantity_dict[button.property("index")].setText(f"{self.set_list[button.property("index")]["Quantity"]}") # type: ignore
    
    def increment_quantity(self):
        button = self.sender()

        if self.set_list[button.property("index")]["Quantity"] < 99: # type: ignore
            self.set_list[button.property("index")]["Quantity"] += 1 # type: ignore
        else:
            return
        
        self.card_count.setText(f"{self.calculate_total_quantity()}/{len(self.set_list)} Cards")
        
        self.update_card_opacity(self.card_img_dict[button.property("index")], self.set_list[button.property("index")]["Quantity"]) # type: ignore

        with open(self.set_fp, "w") as set_file:
            json.dump(self.set_list, set_file, indent=4)

        self.card_quantity_dict[button.property("index")].setText(f"{self.set_list[button.property("index")]["Quantity"]}") # type: ignore
            

    def toggle_theme_button(self):

        self.settings_layout = QHBoxLayout()

        self.header_layout.addLayout(self.settings_layout)
        

        self.theme_button = QPushButton("")
        self.theme_button.setProperty("class", "Setting_Button")

        self.theme_button.setIcon(QIcon(self.IM.theme_icon[self.mode]))
        self.theme_button.setIconSize(QSize(36, 36))

        self.theme_button.enterEvent = partial(self.on_button_enter, self.theme_button)
        self.theme_button.leaveEvent = partial(self.on_button_enter, self.theme_button) # type: ignore
        
        self.theme_button.clicked.connect(self.toggle_theme)

        self.settings_layout.addWidget(self.theme_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

    def create_info_button(self):

        self.info_button = QPushButton("")
        self.info_button.setProperty("class", "Setting_Button")
        

        self.info_button.setIcon(QIcon(self.IM.info_icon[self.mode]))
        self.info_button.setIconSize(QSize(36, 36))

        self.info_button.enterEvent = partial(self.on_button_enter, self.info_button)
        self.info_button.leaveEvent = partial(self.on_button_enter, self.info_button) # type: ignore
        
        self.info_button.clicked.connect(self.display_info_page)

        self.settings_layout.addWidget(self.info_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

        self.settings_layout.addStretch()


    def toggle_theme(self):
        if self.mode == 1:
            self.mode = 0
            self.settings['UserData']['theme'] = 0

            self.main_widget.setStyleSheet(self.themes.light_theme)
            self.switch_scrollbar()
            
        elif self.mode == 0:
            self.mode = 1
            self.settings['UserData']['theme'] = 1

            self.main_widget.setStyleSheet(self.themes.dark_theme)
            self.switch_scrollbar()

        with open("src/app_data/app_settings.json", "w+") as config_file:
                json.dump(self.settings, config_file, indent=4)

        self.reload_images()


    def init_back_button(self, layout):

        self.bb_layout = QHBoxLayout()

        layout.addLayout(self.bb_layout)

        self.back_button = QPushButton("")
        self.back_button.setProperty("class", "Setting_Button")

        self.back_button.setIcon(QIcon(self.IM.arrow_icon[self.mode]))
        self.back_button.setIconSize(QSize(36, 36))

        self.back_button.enterEvent = partial(self.on_button_enter, self.back_button)
        self.back_button.leaveEvent = partial(self.on_button_enter, self.back_button) # type: ignore

        self.back_button.clicked.connect(partial(self.go_back, layout))

        self.bb_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

        self.bb_layout.addStretch()

    def go_back(self, layout):
        self.stacked_layout.setCurrentWidget(self.main_widget)
        if layout != self.info_header:
            self.clear_layout(layout)

    def clear_layout(self, layout: QVBoxLayout):
        
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget() # type: ignore
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout() is not None: # type: ignore
                self.clear_layout(item.layout()) # type: ignore

    def reload_images(self):
        self.theme_button.setIcon(QIcon(self.IM.theme_icon[self.mode]))
        self.info_button.setIcon(QIcon(self.IM.info_icon[self.mode]))
        self.back_button.setIcon(QIcon(self.IM.arrow_icon[self.mode]))
        self.git_icon.setPixmap(self.IM.github_icon[self.mode].scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.pz_icon.setPixmap(self.IM.pz_icon[self.mode].scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.serebii_icon.setPixmap(self.IM.serebii_icon[self.mode].scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.ltcg_icon.setPixmap(self.IM.ltcg_icon[self.mode].scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def switch_scrollbar(self):
        if self.mode == 1:
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
        elif self.mode == 0:
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


        

    def run(self):
        self.init_set_dir()

        self.init_cache()

        self.title()

        self.display_sets()

        self.toggle_theme_button()

        self.create_info_page()

        self.create_info_button()

        self.show()

        self.app.exec()
        