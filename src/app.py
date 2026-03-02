import os, json, datetime, copy
from src import setmanager, themes, image_manager
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QStackedLayout, QMainWindow, QSizePolicy, QScrollArea, QGraphicsOpacityEffect, QGraphicsColorizeEffect, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QSize, QUrl, QTimer, QObject, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QCursor, QIcon, QDesktopServices, QPixmap, QColor
from math import ceil
from functools import partial
from PyQt6.QtNetwork import QNetworkAccessManager

class CacheWorker(QObject):
    finished = pyqtSignal(dict)      
    progress = pyqtSignal(str)
    

    def __init__(self, queue_label: QLabel, n_m, set_dict, set_dir, local_doc, max_concurrent=10):
        super().__init__()
        self.set_dict = set_dict
        self.project_dir = set_dir
        self.local_doc = local_doc
        self.queue_label = queue_label
        self.n_m = n_m
        self.max_concurrent = max_concurrent

        

        

        self.queue = []
        self.queue_status = 0
        self.queue_count = 0
        self.cache_dict = {}
        self.active = 0
        

    def run(self):
        for set in self.set_dict["SetList"]:

    
            with open(f"{self.local_doc}\\{set["Name"]}\\{set["Name"]}.json", "r") as set_file:
                self.set_list = json.load(set_file)
                
            

            cards_folder = f"{self.project_dir}\\set_data\\{set["Name"]}\\cards"

            if len(os.listdir(f"{self.project_dir}\\set_data\\{set["Name"]}\\cards")) != len(self.set_list):
                    
                    for card in self.set_list:
                        self.queue.append((card, cards_folder))
                        self.queue_count += 1

        self.start_downloads()

    def start_downloads(self):
        while self.active < self.max_concurrent and self.queue:
            self.start_one()

        if not self.queue and self.active == 0:
            self.finished.emit(self.cache_dict)

    def start_one(self):
        card, cards_folder = self.queue.pop(0)
        card_label = image_manager.ImageLabel(card["Image"], card["ID"], cards_folder, True, network_manager=self.n_m)
        self.cache_dict[card["ID"]] = card_label
        self.active += 1
        self.queue_status += 1
        card_label.download_finished.connect(
            lambda: self.queue_label.setText(f"({self.queue_status}\\{self.queue_count})")
        )
        card_label.download_finished.connect(self.on_download_finished)

    def on_download_finished(self):
        self.active -= 1
        self.start_downloads()

class Application(QMainWindow):
    def __init__(self) -> None:
        self.app = QApplication([])
        super().__init__()
        
        self.card_img_dict = {}

        self.set_manager = setmanager.SetManager()
        self.themes = themes.Themes()
        self.IM = image_manager.ImageManager()
        self.settings = self.init_app_data()
        self.resize(1400, 1150)
        self.setWindowIcon(QIcon("src/images/ui/logo_icon.png"))
        self.setWindowTitle(f"PocketDex Codex v{self.settings['UserData']['version']}")

        self.set_col_count = 6

        self.col_count = self.settings['UserData']['col_count']

        self.bb_dict = {}

        self.set_sep_lens = {4: 1200, 
                             6: 1700,
                             8: 2250}

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.main_font = QFont("Gill Sans MT", 10, QFont.Weight.Normal, italic=False)
        self.main_font_bold = QFont("Gill Sans MT", 10, QFont.Weight.Bold, italic=False)

        self.fullscreen = False

        self.container = QWidget()

        self.stacked_layout = QStackedLayout(self.container)

        self.cd_layout = None

        self.main_widget = QWidget()

        self.stacked_layout.addWidget(self.main_widget)

        self.header_layout = QVBoxLayout(self.main_widget)
        self.header_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

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
        self.project_dir = f"src\\app_data"
        self.local_doc = os.path.join(os.path.expanduser("~"), "Documents", "PocketDex Codex")
        os.makedirs(f"{self.project_dir}\\set_data", exist_ok=True)
        os.makedirs(self.local_doc, exist_ok=True)

        
        with open(f'{self.project_dir}\\set_list.json', 'r+', encoding="UTF-8") as set_file:
            self.set_dict = json.load(set_file)

        
        if (len(self.set_dict["SetList"]) + 1) != (len(os.listdir(self.local_doc))):
            for set in self.set_dict["SetList"]:
                local_set_folder = f"{self.local_doc}\\{set["Name"]}"
                project_set_folder = f"{self.project_dir}\\set_data\\{set["Name"]}"
                os.makedirs(local_set_folder, exist_ok=True)
                os.makedirs(project_set_folder, exist_ok=True)
                if not os.listdir(local_set_folder):
                    self.set_manager.create_set(set["Name"], local_set_folder)
                os.makedirs(f"{project_set_folder}\\cards", exist_ok=True)

        elif len(self.set_dict["SetList"]) != len(os.listdir(f"{self.project_dir}\\set_data")):
            for set in self.set_dict["SetList"]:
                project_set_folder = f"{self.project_dir}\\set_data\\{set["Name"]}"
                os.makedirs(project_set_folder, exist_ok=True)
                os.makedirs(f"{project_set_folder}\\cards", exist_ok=True)

    def create_favorites_folder(self):
        os.makedirs(f"{self.local_doc}\\favorites", exist_ok=True)

        if not os.listdir(f"{self.local_doc}\\favorites"):
            with open(f"{self.local_doc}\\favorites\\favorites.json", "w+") as f_file:
                json.dump([], f_file, indent=4)

        with open(f"{self.local_doc}\\favorites\\favorites.json", "r") as f_file:
            self.favorite_list = json.load(f_file)

        self.fav_main_layout = None


    def init_cache(self):
        self.init_loading_images_page()
        self.show()

        self.app.processEvents()

        self.cache_thread = QThread()
        
        self.network_manager = QNetworkAccessManager()
        self.network_manager.moveToThread(self.cache_thread)

        self.cache_worker = CacheWorker(self.queue_label, self.network_manager, self.set_dict, self.project_dir, self.local_doc)
        self.cache_worker.moveToThread(self.cache_thread)
        
        self.cache_thread.started.connect(self.cache_worker.run)
        self.cache_worker.finished.connect(self.cache_finished)
        self.cache_worker.finished.connect(self.cache_thread.quit)
        self.cache_worker.finished.connect(self.cache_worker.deleteLater)
        
        self.cache_thread.finished.connect(self.cache_thread.deleteLater)

        self.cache_thread.start()


    def cache_finished(self, cache_dict):
        self.cache_dict = cache_dict
        self.stacked_layout.setCurrentWidget(self.main_widget)
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
        loading_txt_label = QLabel("Downloading application data..")

        self.queue_label = QLabel("( )")
        self.queue_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.queue_label.setProperty("class", "header2")
        self.queue_label.setFont(self.main_font)
        
        loading_icon_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        loading_icon_label.setProperty("class", "header2")
        loading_icon_label.setPixmap(self.IM.loading_icon[self.mode].scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    
        self.li_txt_layout.addWidget(loading_icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        loading_txt_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        loading_txt_label.setProperty("class", "header2")
        loading_txt_label.setFont(self.main_font)

        self.li_txt_layout.addWidget(loading_txt_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.li_txt_layout.addWidget(self.queue_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.stacked_layout.addWidget(self.li_widget)

        loading_txt_hint = QLabel("This should take roughly 1 - 2 minutes.")
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

        self.seperator(self.header_layout, 1200)

        self.h3_layout = QHBoxLayout()
        self.h3_layout.setSpacing(0)
        self.h3_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.header_layout.addLayout(self.h3_layout)
        self.h3 = QLabel("Please select a set below:", self.main_widget)
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

        self.set_fp = f"{self.local_doc}\\{set_name}\\{set_name}.json"

        with open(self.set_fp, "r+") as set_file:
            self.set_list = json.load(set_file)
           

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

        self.set_button_dict = {}
        
        
        self.set_layout = QGridLayout()
        self.set_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.set_layout.setSpacing(5)
        self.header_layout.addLayout(self.set_layout)
        col_length = self.set_col_count
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
                    button.leaveEvent = partial(self.on_button_leave, button) # type: ignore
                    
                    button.clicked.connect(self.clicked_set)

                    self.set_button_dict[self.set_dict['SetList'][current_set]['Name']] = button

                    current_set += 1
                    if current_set == len(self.set_dict['SetList']):
                        all_rows = True
                        break
        
        self.seperator(self.header_layout, 1200)
        next_date = self.set_dict["NextSetDate"]
        self.next_set_label = QLabel(f"Next set releases {f"on {next_date}!" if next_date else f"soon!"}", self.main_widget)
        self.next_set_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.next_set_label.setProperty("class", "header2")
        self.next_set_label.setFont(self.main_font)
        self.header_layout.addWidget(self.next_set_label, alignment=Qt.AlignmentFlag.AlignHCenter)

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

        self.seperator(self.info_header, 1100)

        self.init_back_button(self.info_header, "Info")


    def display_info_page(self):

        self.info_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)

        

        self.stacked_layout.addWidget(self.info_widget)

        self.stacked_layout.setCurrentWidget(self.info_widget)


    def clicked_set(self, refresh=False):
        if not refresh:
            button = self.sender()
        else:
            button = self.set_button_dict[self.set_name]
        self.set_name = button.property('Name') # type: ignore
        self.set_id = button.property('ID') # type: ignore

        self.set_widget = QWidget()
        
        self.set_main_layout = QVBoxLayout()
        self.set_main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.set_widget.setLayout(self.set_main_layout)
        self.set_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)
        self.set_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.print_set_title(self.set_name)

        self.seperator(self.set_main_layout, self.set_sep_lens[self.col_count])

        self.card_grid = QGridLayout(self.set_widget)
        self.card_grid.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.card_grid.setVerticalSpacing(25)
        self.card_grid.setHorizontalSpacing(25)
        self.set_main_layout.addLayout(self.card_grid)

        self.display_loading_page()  

        QTimer.singleShot(100, self.await_cache)
        
        
    def await_cache(self): 
                
        if len(os.listdir(f"{self.project_dir}\\set_data\\{self.set_name}\\cards")) != len(self.set_list):
            QTimer.singleShot(100, self.await_cache)
            return
            
        self.display_cards()

        self.seperator(self.set_main_layout, self.set_sep_lens[self.col_count])

        self.set_action_buttons()

        self.init_back_button(self.set_main_layout, "Set")

        self.change_col_button(self.set_main_layout)

        self.stacked_layout.addWidget(self.set_widget)

        self.stacked_layout.setCurrentWidget(self.set_widget)


    def set_action_buttons(self):
        self.ex_layout = QHBoxLayout()
        self.ex_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.set_main_layout.addLayout(self.ex_layout)

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
        
        self.export_button.clicked.connect(partial(self.set_manager.export_excel, self.local_doc, self.set_name, self.set_list))

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
        
        with open("src/app_data/app_settings.json", "w+") as config_file:
                json.dump(self.settings, config_file, indent=4)

        self.go_back(layout)
        if layout != self.fav_main_layout:
            self.clicked_set(True)
        else:
            self.display_favorites()
            
        

    def update_set_data(self):

        if self.set_manager.update_set(self.set_list, self.set_name, self.local_doc):
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
            if not self.set_manager.import_excel(self.local_doc, excel_fp, self.set_name, self.set_list):
                self.display_message("Invalid Spreadsheet", "ERROR: This xlsx spreadsheet does not match the set data.\nPlease try a different file.\nIf you believe this is a mistake, contact the maintainer below:\nhttps://github.com/langstonstewart/PocketDex-Codex")

            with open(self.set_fp, "r+") as set_file:
                self.set_list = json.load(set_file)

            self.go_back(self.set_main_layout)
            self.clicked_set(True)
        

    def add_one_all(self):
        for button in self.plus_button_list:
            self.increment_quantity(self.data_header, True, button)

        with open(self.set_fp, "w") as set_file:
            json.dump(self.set_list, set_file, indent=4)

    def remove_one_all(self):
        for button in self.plus_button_list:
            self.decrement_quantity(self.data_header, True, button)

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
        cache_label = QLabel(f"Please wait...")

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

        self.seperator(self.set_info_layout, 1100)

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

    def init_card_data_page(self):
        self.cd_widget = QWidget()    
        self.cd_layout = QVBoxLayout()
        
        self.cd_widget.setLayout(self.cd_layout)
        self.cd_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)
        self.cd_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        
    def display_card_data_page(self, card_index):

        self.clear_layout(self.set_main_layout)
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
        
        card_type_banner.setPixmap(self.IM.card_type_dict[card_type].scaled(100, 25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        card_type_banner.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        card_type_banner.setAlignment(Qt.AlignmentFlag.AlignLeft if self.set_list[card_index]["Card-Type"] == "Pokemon" else Qt.AlignmentFlag.AlignHCenter)

        card_header_layout.addWidget(card_type_banner)

        self.create_card(card_index, card_layout, False)


        if self.set_list[card_index]["Card-Type"] == "Pokemon":
            card_header_hp_layout = QHBoxLayout()
      
            
            card_header_layout.addLayout(card_header_hp_layout)

            hp_small = QLabel("HP")
            hp_small.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            hp_small.setAlignment(Qt.AlignmentFlag.AlignRight)
            hp_small.setFont(self.main_font_bold)
            hp_small.setProperty("class", "small_header")
           
            card_header_hp_layout.addWidget(hp_small)

            hp_main = QLabel(f"{self.set_list[card_index]["HP"]}")
            hp_main.setAlignment(Qt.AlignmentFlag.AlignRight)
            hp_main.setFont(self.main_font_bold)
            hp_main.setProperty("class", "header2")
            hp_main.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
         
            card_header_hp_layout.addWidget(hp_main)

            energy_map = QLabel(f"")
            energy_map.setPixmap(self.IM.type_dict[self.set_list[card_index]["Type"]].scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            energy_map.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            energy_map.setAlignment(Qt.AlignmentFlag.AlignRight)
         
            card_header_hp_layout.addWidget(energy_map)

            

            self.seperator(self.cd_layout, 1100)

            move_data_layout = QVBoxLayout()
            
            move_data_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            move_data_layout.setContentsMargins(0, 20, 0, 20)
            self.cd_layout.addLayout(move_data_layout) # type: ignore

            if self.set_list[card_index]["Ability"]:
                ability_layout = QHBoxLayout()
                
                ability_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                move_data_layout.addLayout(ability_layout) # type: ignore

                ability_banner = QLabel("")
                ability_banner.setPixmap(self.IM.ability_icon.scaled(128, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                ability_banner.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                ability_banner.setAlignment(Qt.AlignmentFlag.AlignHCenter)

                ability_layout.addWidget(ability_banner)

                ability_text = QLabel(f"{self.set_list[card_index]["Ability"]}")
                ability_text.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                ability_text.setFont(self.main_font_bold)
                ability_text.setProperty("class", "header2")
                ability_text.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

                ability_layout.addWidget(ability_text)


                ability_effect_data = self.set_list[card_index]["Ability-Effect"] # type: str

                for symbol, img_path in self.IM.energy_dict.items():
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
               
                move_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                move_data_layout.addLayout(move_layout) # type: ignore

                for energy in self.set_list[card_index]["Move-Energy"][i]:

                    m_energy = QLabel(f"")
                    m_energy.setPixmap(QPixmap(self.IM.energy_dict[energy]).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    m_energy.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                    m_energy.setAlignment(Qt.AlignmentFlag.AlignHCenter)

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

    
                weakness_energy = QLabel("")
                weakness_energy.setPixmap(self.IM.type_dict[weakness_data].scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # type: ignore
                weakness_energy.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                w_layout.addWidget(weakness_energy)

                weakness_dmg = QLabel("+20")
                weakness_dmg.setFont(self.main_font)
                weakness_dmg.setProperty("class", "header2")
                weakness_dmg.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                w_layout.addWidget(weakness_dmg)

                retreat_cost = int(self.set_list[card_index]["Retreat-Cost"])

                if retreat_cost:
                 
                    sub_cost = 30 * retreat_cost
                    w_r_layout.addSpacing(795 - sub_cost)

                    r_layout = QHBoxLayout()
                    r_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    w_r_layout.addLayout(r_layout) # type: ignore

                    retreat_txt = QLabel("Retreat")
                    retreat_txt.setFont(self.main_font)
                    retreat_txt.setProperty("class", "header2")
                    retreat_txt.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                    r_layout.addWidget(retreat_txt)

                    for r in range(retreat_cost):
                        rc_icon = QLabel("")
                        rc_icon.setPixmap(QPixmap(self.IM.energy_dict["C"]).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # type: ignore
                        rc_icon.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                        rc_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                        r_layout.addWidget(rc_icon, alignment=Qt.AlignmentFlag.AlignHCenter)
                else:
                    w_r_layout.addSpacing(890)

            self.seperator(self.cd_layout, 1100)

            flavor_text = self.set_list[card_index]["Flavor-Text"]

            ex_rule = self.set_list[card_index]["Ex-Rule"]

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

            elif ex_rule:

                ex_layout = QVBoxLayout()
                ex_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                self.cd_layout.addLayout(ex_layout) # type: ignore

                ex_label = QLabel(f"{ex_rule}")
                ex_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                ex_label.setFont(self.main_font)
                ex_label.setProperty("class", "header2")
                ex_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
                ex_label.setWordWrap(True)
                ex_label.setMinimumHeight(ex_label.sizeHint().height() * 3)
                ex_label.setMaximumHeight(ex_label.sizeHint().height() * 3)
                    
                ex_layout.addWidget(ex_label)

            card_extra_layout = QHBoxLayout()
            card_extra_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.cd_layout.addLayout(card_extra_layout) # type: ignore

            paint_icon = QLabel("")
            paint_icon.setPixmap(self.IM.paint_icon[self.mode].scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # type: ignore
            paint_icon.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            paint_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            card_extra_layout.addWidget(paint_icon)

            i_label = QLabel(f"Illustrated by {self.set_list[card_index]["Illustrator"]}")
            i_label.setFont(self.main_font)
            i_label.setProperty("class", "header2")
            i_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            card_extra_layout.addWidget(i_label)

            card_extra_layout.addSpacing(25)

            pb_icon = QLabel("")
            pb_icon.setPixmap(self.IM.rarity_dict["None"][self.mode].scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # type: ignore
            pb_icon.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            pb_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            card_extra_layout.addWidget(pb_icon)

            card_index_label = QLabel(f"{card_index + 1} of {len(self.set_list)}")
            card_index_label.setFont(self.main_font)
            card_index_label.setProperty("class", "header2")
            card_index_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            card_extra_layout.addWidget(card_index_label)

            self.seperator(self.cd_layout, 1100)

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


            self.seperator(desc_layout, 1100)

            rule_layout = QVBoxLayout()
            rule_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.cd_layout.addLayout(rule_layout) # type: ignore

            card_rule_label = QLabel(f"{self.IM.card_desc_dict[self.set_list[card_index]["Card-Type"]]}")
            card_rule_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            card_rule_label.setFont(self.main_font)
            card_rule_label.setTextFormat(Qt.TextFormat.RichText)
            card_rule_label.setProperty("class", "header2")
            card_rule_label.setMinimumWidth(1000)
            card_rule_label.setMaximumWidth(1000)
            card_rule_label.setWordWrap(True)
            card_rule_label.setMinimumHeight(card_rule_label.sizeHint().height() * 5)
            card_rule_label.setMaximumHeight(card_rule_label.sizeHint().height() * 5)
            card_rule_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
            
            rule_layout.addWidget(card_rule_label, alignment=Qt.AlignmentFlag.AlignHCenter)

            misc_extra_layout = QHBoxLayout()
            misc_extra_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            rule_layout.addLayout(misc_extra_layout) # type: ignore

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
            pb_icon.setPixmap(self.IM.rarity_dict["None"][self.mode].scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)) # type: ignore
            pb_icon.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            pb_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            misc_extra_layout.addWidget(pb_icon)

            card_index_label = QLabel(f"{card_index + 1} of {len(self.set_list)}")
            card_index_label.setFont(self.main_font)
            card_index_label.setProperty("class", "header2")
            card_index_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            misc_extra_layout.addWidget(card_index_label)

            self.seperator(self.cd_layout, 1100)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.cd_layout.addLayout(button_layout) # type: ignore

        if card_index != 0:
            self.prev_card_button = QPushButton(f'View Previous Card.. ({self.set_list[card_index - 1]["Name"]})')
            self.prev_card_button.setProperty("class", "Setting_Button")
            self.prev_card_button.setFont(self.main_font)

            self.prev_card_button.setIcon(QIcon(self.IM.arrow_icon[self.mode]))
            self.prev_card_button.setIconSize(QSize(36, 36))

            self.prev_card_button.enterEvent = partial(self.on_button_enter, self.prev_card_button)
            self.prev_card_button.leaveEvent = partial(self.on_button_leave, self.prev_card_button) # type: ignore
            self.prev_card_button.clicked.connect(partial(self.display_card_data_page, card_index - 1))

            button_layout.addWidget(self.prev_card_button)

        if card_index != len(self.set_list) - 1:
            self.next_card_button = QPushButton(f'View Next Card.. ({self.set_list[card_index + 1]["Name"]})')
            self.next_card_button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.next_card_button.setProperty("class", "Setting_Button")
            self.next_card_button.setFont(self.main_font)

            self.next_card_button.setIcon(QIcon(self.IM.forward_icon[self.mode]))
            self.next_card_button.setIconSize(QSize(36, 36))

            self.next_card_button.enterEvent = partial(self.on_button_enter, self.next_card_button)
            self.next_card_button.leaveEvent = partial(self.on_button_leave, self.next_card_button) # type: ignore
            self.next_card_button.clicked.connect(partial(self.display_card_data_page, card_index + 1))

            button_layout.addWidget(self.next_card_button)

        self.cd_layout.addStretch() # type: ignore

        self.init_back_button(self.cd_layout, "Card_Data")

        set_logo = QLabel("")
        set_logo.setPixmap(self.IM.logo_dict[self.set_id][0].scaled(156, 156, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        self.bb_layout.addWidget(set_logo, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        self.stacked_layout.addWidget(self.cd_widget)
        self.scroll_area.verticalScrollBar().setValue(0) # type: ignore
        self.stacked_layout.setCurrentWidget(self.cd_widget)

    def create_card(self, card_index, layout, clickable=True, row=0, col=0):
        card_widget = QWidget()
        

        card_layout = QVBoxLayout(card_widget)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card_layout.setSpacing(10)

        card_widget.setLayout(card_layout)
        
        def on_card_hover(event, img: QLabel):
            img.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            card_highlight = QGraphicsColorizeEffect()
            card_highlight.setColor(QColor(255, 255, 255))
            card_highlight.setStrength(0.2)
            img.setGraphicsEffect(card_highlight)

        def on_card_leave(event, img: QLabel):
            self.update_card_opacity(img, self.set_list[img.property("index")]["Quantity"])


        def on_card_click(event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.display_card_data_page(card_index)

        card_img = image_manager.ImageLabel(self.set_list[card_index]["Image"], self.set_list[card_index]["ID"], f"{self.project_dir}\\set_data\\{self.set_name}\\cards", False)
        card_img.setProperty("index", card_index)
        card_img.setAlignment(Qt.AlignmentFlag.AlignHCenter)
      

        if clickable:
            
            if "Summary-Available" in self.set_list[card_index].keys() and self.set_list[card_index]["Summary-Available"]:
                card_img.setProperty("class", "Card_Label")
                card_img.enterEvent = lambda event, img=card_img: on_card_hover(event, img)
                card_img.leaveEvent = lambda event, img=card_img: on_card_leave(event, img) # type: ignore
                card_img.mousePressEvent = on_card_click # type: ignore
    
        
        
        self.update_card_opacity(card_img, self.set_list[card_img.property("index")]["Quantity"])
        card_layout.addWidget(card_img)
        card_layout.addSpacing(8)

        self.card_img_dict[self.set_list[card_index]["ID"]] = card_img

        card_name_layout = QHBoxLayout()
        card_name_layout.setContentsMargins(0, 6, 0, 6)
        card_name_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card_name_layout.setSpacing(0)

        card_text = f"{self.set_list[card_index]["Name"]}"

        if " ex" in card_text:
            
            ex_icon = QLabel("")
            ex_icon.setPixmap(self.IM.ex_icon.scaled(46, 25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            ex_icon.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
            ex_icon.setContentsMargins(0, 2, 0, 0)
            ex_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            card_name = QLabel(card_text.replace(" ex", ""))
        else:
            card_name = QLabel(card_text)

        if type(layout) == QGridLayout:
            card_name.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        else:
            card_name.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            
        card_name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card_name.setFont(self.main_font_bold)
        card_name.setProperty("class", "header2")
        card_name.setWordWrap(True)
    
        card_name.setMaximumWidth(1000)
        
        card_name_layout.addWidget(card_name)
        card_layout.addLayout(card_name_layout)
        if " ex" in card_text:
            if len(card_text) >= 17:
                ex_layout = QVBoxLayout()
                ex_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                card_layout.addLayout(ex_layout)
                ex_layout.addWidget(ex_icon)
            else:
                card_name_layout.addWidget(ex_icon)

        
        
        card_rarity = QLabel("")
        card_rarity.setPixmap(self.IM.rarity_dict[self.set_list[card_index]["Rarity"]] if self.set_list[card_index]["Rarity"] != "N/A" else self.IM.rarity_dict["None"][self.mode].scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        card_rarity.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        card_rarity.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card_layout.addWidget(card_rarity)

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

        minus_button.clicked.connect(partial(self.decrement_quantity, layout))

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

        plus_button.clicked.connect(partial(self.increment_quantity, layout))

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
        favorite_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        favorite_button.setProperty("class", "Main_Button")
        favorite_button.setIcon(QIcon(self.IM.favorite_icon[self.mode if not self.set_list[card_index]["Favorite"] else 2]))
        favorite_button.setIconSize(QSize(24, 24))
        favorite_button.setFixedWidth(205)

        favorite_button.enterEvent = partial(self.on_button_enter, favorite_button)
        favorite_button.leaveEvent = partial(self.on_button_leave, favorite_button) # type: ignore

        favorite_button.clicked.connect(partial(self.favorite_card, layout))

        self.fb_list.append(favorite_button)

        f_layout.addWidget(favorite_button)
        
        if type(layout) == QGridLayout:
            layout.addWidget(card_widget, row, col, alignment=Qt.AlignmentFlag.AlignHCenter)
        else:
            layout.addWidget(card_widget, alignment=Qt.AlignmentFlag.AlignHCenter) # type: ignore



    def display_cards(self):
        
        self.card_quantity_dict = {}
        self.minus_button_list = []
        self.plus_button_list = []
        self.fb_list = []

        self.f_button.setText("View Favorites..")
        
        col_length = self.col_count
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
        
        with open(f"{self.local_doc}\\favorites\\favorites.json", "w") as f_file:
            json.dump(self.favorite_list, f_file, indent=4)

        with open(self.set_fp, "w") as set_file:
            json.dump(self.set_list, set_file, indent=4)
        
    
    def update_card_opacity(self, card: QLabel, quan):
        card_op = QGraphicsOpacityEffect()
        op = 0.5 if quan == 0 else 1.0
        card_op.setOpacity(op)
        card.setGraphicsEffect(card_op)
        

    def decrement_quantity(self, layout=None, all=False, object=None):
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
    
        with open(self.set_fp, "w") as set_file:
            json.dump(self.set_list, set_file, indent=4)
        
        self.card_quantity_dict[button.property("index")].setText(f"{self.set_list[button.property("index")]["Quantity"]}") # type: ignore

    
    def increment_quantity(self, layout=None, all=False, object=None):
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

        with open(self.set_fp, "w") as set_file:
            json.dump(self.set_list, set_file, indent=4)

        self.card_quantity_dict[button.property("index")].setText(f"{self.set_list[button.property("index")]["Quantity"]}") # type: ignore
            


    def toggle_theme_button(self):

        self.settings_layout = QHBoxLayout()
        self.settings_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.header_layout.addLayout(self.settings_layout)
        

        self.theme_button = QPushButton("Toggle Theme..")
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
        self.f_button.setFont(self.main_font)
        self.f_button.setProperty("class", "Setting_Button")
        self.f_button.setText("View Favorites..")
        

        self.f_button.setIcon(QIcon(self.IM.heart_button_icon[self.mode]))
        self.f_button.setIconSize(QSize(36, 36))

        self.f_button.enterEvent = partial(self.on_button_enter, self.f_button)
        self.f_button.leaveEvent = partial(self.on_button_leave, self.f_button) # type: ignore
        
        self.f_button.clicked.connect(self.display_favorites)

        self.settings_layout.addWidget(self.f_button, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)


    def display_favorites(self):

        self.fb_list = []
        
        if len(self.favorite_list):
            self.fav_widget = QWidget()
            
            self.fav_main_layout = QVBoxLayout()
           
            self.fav_widget.setLayout(self.fav_main_layout)
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

            self.fav_tag = QLabel("")
            self.fav_tag.setPixmap(self.IM.f_tag[self.mode].scaled(150, 88, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.fav_tag.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            self.fav_title_layout.addWidget(self.fav_tag)

            self.fav_info = QLabel(f"{len(self.favorite_list)} {"Card" if len(self.favorite_list) <= 1 else "Cards"}")
            self.fav_info.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            self.fav_info.setProperty("class", "header2")
            self.fav_info.setFont(self.main_font)
            self.fav_info_layout.addWidget(self.fav_info)


            self.seperator(self.fav_main_layout, self.set_sep_lens[self.col_count])

            self.fav_grid = QGridLayout(self.fav_widget)
            self.fav_grid.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.fav_grid.setVerticalSpacing(25)
            self.fav_grid.setHorizontalSpacing(25)
            self.fav_main_layout.addLayout(self.fav_grid)

            
            col_length = self.col_count
            row_length = ceil(len(self.favorite_list) / col_length)
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
                        
                        card_layout.setSpacing(8)

                        card_widget.setLayout(card_layout)
                        
                        
                        if self.favorite_list[current_card]["ID"] in self.card_img_dict.keys():
                            card_img = self.card_img_dict[self.favorite_list[current_card]["ID"]]
                        else:
                            card_img = image_manager.ImageLabel(self.favorite_list[current_card]["Image"], self.favorite_list[current_card]["ID"], f"{self.project_dir}\\set_data\\{self.favorite_list[current_card]["Set"]}\\cards", False)
                        
                            card_img.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                        
                        card_layout.addWidget(card_img)

                        self.card_img_dict[self.favorite_list[current_card]["ID"]] = card_img

                        card_name_layout = QHBoxLayout()
                        card_name_layout.setContentsMargins(0, 6, 0, 6)
                        card_name_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                        card_name_layout.setSpacing(0)

                        card_text = f"{self.favorite_list[current_card]["Name"]}"

                        if " ex" in card_text:
                            
                            ex_icon = QLabel("")
                            ex_icon.setPixmap(self.IM.ex_icon.scaled(46, 25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                            ex_icon.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
                            ex_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                            ex_icon.setContentsMargins(0, 5, 0, 0)

                            card_name = QLabel(card_text.replace(" ex", ""))
                        else:
                            card_name = QLabel(card_text)

                        
                        card_name.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
                       
                            
                        card_name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                        card_name.setFont(self.main_font_bold)
                        card_name.setProperty("class", "header2")
                        card_name.setWordWrap(True)
                    
                        card_name.setMaximumWidth(1000)
                        
                        card_name_layout.addWidget(card_name)
                        card_layout.addLayout(card_name_layout)
                        if " ex" in card_text:
                            if len(card_text) >= 17:
                                ex_layout = QVBoxLayout()
                                ex_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                                card_layout.addLayout(ex_layout)
                                ex_layout.addWidget(ex_icon)
                            else:
                                card_name_layout.addWidget(ex_icon)

                        
                        card_rarity = QLabel("")
                        card_rarity.setPixmap(self.IM.rarity_dict[self.favorite_list[current_card]["Rarity"]] if self.favorite_list[current_card]["Rarity"] != "N/A" else self.IM.rarity_dict["None"][self.mode].scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                        card_rarity.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                        card_rarity.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                        card_layout.addWidget(card_rarity)

                        f_layout = QHBoxLayout()
                        f_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                        
                        card_layout.addLayout(f_layout)

                        favorite_button = QPushButton("")
                        favorite_button.setProperty("index", current_card)
                        favorite_button.setProperty("id", self.favorite_list[current_card]["ID"])
                        favorite_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                        favorite_button.setProperty("class", "Main_Button")
                        favorite_button.setIcon(QIcon(self.IM.favorite_icon[self.mode if not self.favorite_list[current_card]["Favorite"] else 2]))
                        favorite_button.setIconSize(QSize(24, 24))
                        favorite_button.setMinimumHeight(30)
                        favorite_button.setMinimumWidth(205)

                        favorite_button.clicked.connect(partial(self.remove_from_favorites, self.favorite_list[current_card]["Set"]))

                        self.fb_list.append(favorite_button)

                        f_layout.addWidget(favorite_button, alignment=Qt.AlignmentFlag.AlignHCenter)
                        
                        self.fav_grid.addWidget(card_widget, r, c, alignment=Qt.AlignmentFlag.AlignHCenter)
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

            
        
        else:
            self.f_button.setText("Your Favorites collection is empty!")
         

    def remove_from_favorites(self, set_name):
        self.set_name = set_name

        self.set_fp = f"{self.local_doc}\\{self.set_name}\\{self.set_name}.json"
        with open(self.set_fp, "r") as set_file:
                self.set_list = json.load(set_file)

        fb = self.sender()

        card_origin_index = self.favorite_list[fb.property("index")]["Index"] # type: ignore

        if not self.set_list[card_origin_index]["Favorite"]:
           
            self.set_list[card_origin_index]["Favorite"] = 1

            card_data = copy.deepcopy(self.set_list[card_origin_index]) # type: ignore
            card_data["Set"] = self.set_name
            card_data["Index"] = card_origin_index # type: ignore
            self.favorite_list.append(card_data) # type: ignore

        else:
            
            self.set_list[card_origin_index]["Favorite"] = 0

          
            self.favorite_list.pop(fb.property("index")) # type: ignore
            
                

        with open(f"{self.local_doc}\\favorites\\favorites.json", "w") as f_file:
            json.dump(self.favorite_list, f_file, indent=4)

        with open(self.set_fp, "w") as set_file:
            json.dump(self.set_list, set_file, indent=4)

        self.go_back(self.fav_main_layout)

        if len(self.favorite_list):
            self.display_favorites()


    def create_info_button(self):

        self.info_button = QPushButton("About..")
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
            for key, value in self.set_button_dict.items():
                self.set_button_dict[key].setProperty("class", f"Main_Button")

            self.main_widget.setStyleSheet(self.themes.light_theme)
            self.cd_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)
            self.switch_scrollbar()
            
        elif self.mode == 0:
            self.mode = 1
            self.settings['UserData']['theme'] = 1
            for key in self.set_button_dict.keys():
                self.set_button_dict[key].setProperty("class", f"Main_Button")
                
            self.main_widget.setStyleSheet(self.themes.dark_theme)
            self.cd_widget.setStyleSheet(self.themes.dark_theme if self.mode == 1 else self.themes.light_theme)
            self.switch_scrollbar()

        with open("src/app_data/app_settings.json", "w+") as config_file:
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

        self.bb_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

        

        

    def go_back(self, layout):
        self.stacked_layout.setCurrentWidget(self.main_widget)
        if layout != self.info_header:
            
            self.clear_layout(layout)
            self.card_img_dict = {}
        if layout == self.cd_layout:
            self.clicked_set(True)

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
        if "Info" in self.bb_dict.keys():
        
            self.bb_dict["Info"].setIcon(QIcon(self.IM.arrow_icon[self.mode]))

        self.theme_button.setIcon(QIcon(self.IM.theme_icon[self.mode]))
        self.f_button.setIcon(QIcon(self.IM.heart_button_icon[self.mode]))
        self.info_button.setIcon(QIcon(self.IM.info_icon[self.mode]))
        self.git_icon.setPixmap(self.IM.github_icon[self.mode].scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.pz_icon.setPixmap(self.IM.pz_icon[self.mode].scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.serebii_icon.setPixmap(self.IM.serebii_icon[self.mode].scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.ltcg_icon.setPixmap(self.IM.ltcg_icon[self.mode].scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.e_button.setIcon(QIcon(self.IM.exit_icon[self.mode]))

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
            
    def create_exit_button(self):

        self.e_button = QPushButton("")
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

        self.create_favorites_folder()

        self.init_cache()

        self.title()

        self.display_sets()

        self.toggle_theme_button()

        self.create_favorite_cards_button()

        self.create_info_page()

        self.create_info_button()

        self.create_exit_button()

        self.init_card_data_page()

        self.app.exec()
        
