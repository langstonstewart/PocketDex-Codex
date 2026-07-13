from functools import partial
from PyQt6.QtWidgets import QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
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

class DexManager:
    def __init__(self, main_app) -> None:
        self.main_app = main_app

        self.local_doc = os.path.join(os.path.expanduser("~"), "Documents", "PocketDex Codex")

        self.dex_data = self.dex_data_init() # type: dict

        self.poke_to_dex_num_dict = {}

        self.dex_num_to_poke_dict = {}

        self.dex_img_cache = {}

        self._dex_image_loaders = [] 

        self.IM = image_manager.ImageManager()

        self._fade_animations = []  

        self.search_query = None   

        


    def create_dex_button(self):
        self.settings_layout = QHBoxLayout()
        self.settings_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.main_app.header_layout.addLayout(self.settings_layout)

        self.dex_button = QPushButton("")
        self.main_app.ui_button_list.append((self.dex_button, self.main_app.IM.dex_icon, None, None))
        self.dex_button.setFont(self.main_app.main_font)
        self.dex_button.setProperty("class", "Setting_Button")
        self.dex_button.setText("View Pokédex..")
        
        self.dex_button.setIcon(QIcon(self.main_app.IM.dex_icon[self.main_app.mode]))
        self.dex_button.setIconSize(QSize(36, 36))

        self.dex_button.enterEvent = partial(self.main_app.on_button_enter, self.dex_button)
        self.dex_button.leaveEvent = partial(self.main_app.on_button_leave, self.dex_button)
        
        self.dex_button.clicked.connect(self.display_dex_page)

        self.settings_layout.addWidget(self.dex_button, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)


    def dex_data_init(self):
        with open(resource_path(f"{self.local_doc}\\dex_data.json"), "r+") as dex_file:
            return json.load(dex_file)
        
        
    def save_dex_data(self):
        with open(resource_path(f"{self.local_doc}\\dex_data.json"), "w+") as dex_file:
            json.dump(self.dex_data, dex_file, indent=4)

    def return_national_count(self):
        national_count = 0
        for region in self.main_app.IM.region_dict.keys():
            national_count += self.dex_data[f"{region.lower()}_obtained"]

        return national_count
    

    def dex_page_init(self, favorites=False):

        self.main_dex_widget = QWidget()
        
        self.main_dex_layout = QVBoxLayout()
        
        self.main_dex_widget.setLayout(self.main_dex_layout)

        self.main_app.init_back_button(self.main_dex_layout, "Top")

        self.main_app.create_favorite_cards_button("dex")

        self.main_app.create_inverse_button("dex")

        self.main_app.change_col_button(self.main_dex_layout, "Top")

        self.main_app.bb_layout.addStretch(1)

        self.collection_layout = QVBoxLayout()

        self.main_app.bb_layout.addLayout(self.collection_layout)

        region_obtained_count = self.dex_data[f"{self.main_app.selected_region.lower()}_obtained"]

        region_obtained_max = self.IM.region_dict[self.main_app.selected_region][1] - self.IM.region_dict[self.main_app.selected_region][0]


        if region_obtained_count != region_obtained_max:
            obt_path = self.IM.star_outline_icon[self.main_app.mode]
        else:
            obt_path = self.IM.star_full_icon[self.main_app.mode]


        regional_txt = QLabel()
        regional_txt.setText(f'Regional: {region_obtained_count} / {region_obtained_max}  <img src="{obt_path}" width="24" height="24" style="vertical-align: bottom;" />')
        regional_txt.setProperty("class", "dex_text")

        regional_txt.setFont(self.main_app.main_font)
        regional_txt.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        regional_txt.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        
        self.collection_layout.addWidget(regional_txt)

        national_obtained_count = self.return_national_count()

        national_obtained_max = len(self.poke_to_dex_num_dict.keys())


        if national_obtained_count != national_obtained_max:
            obt_path = self.IM.star_outline_icon[self.main_app.mode]
        else:
            obt_path = self.IM.star_full_icon[self.main_app.mode]

    
        national_txt = QLabel()
        national_txt.setText(f'National: {national_obtained_count} / {national_obtained_max} <img src="{obt_path}" width="24" height="24" style="vertical-align: bottom;" />')
        national_txt.setProperty("class", "dex_text")

        national_txt.setFont(self.main_app.main_font)
        national_txt.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        national_txt.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        
        self.collection_layout.addWidget(national_txt)

        self.dex_header_layout = QHBoxLayout()

        self.icon_layout = QVBoxLayout()

        self.header_filler_layout = QVBoxLayout()

        self.dex_header_layout.addLayout(self.icon_layout)

        self.dex_header_layout.addLayout(self.header_filler_layout)


        self.main_dex_layout.addLayout(self.dex_header_layout)

        codex_icon = QLabel("")

        codex_icon.setPixmap(self.IM.codex_icon_mini[self.main_app.mode].scaled(175, 175, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        codex_icon.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        codex_icon.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.icon_layout.addWidget(codex_icon)

        self.dex_title_layout = QHBoxLayout()

        self.header_filler_layout.addLayout(self.dex_title_layout)


        dex_title = QLabel(f"Pokédex - {self.main_app.selected_region}")
        dex_title.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        dex_title.setProperty("class", "dex_header_title")
        dex_title.setFont(self.main_app.main_font)
        dex_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self.dex_title_layout.addWidget(dex_title)

        self.dex_title_layout.addStretch(1)

    
        self.region_layout = QHBoxLayout()
        self.header_filler_layout.addLayout(self.region_layout)

        for region in self.IM.region_dict:
            self.create_region_button(region, self.region_layout)

        self.main_app.seperator(self.main_dex_layout, 0)

        self.search_bar_layout = QHBoxLayout()

        self.main_dex_layout.addLayout(self.search_bar_layout)

        self.create_search_bar(self.search_bar_layout)

        self.dex_grid_layout = QGridLayout()
        self.dex_grid_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.dex_grid_layout.setSpacing(5)
        
        self.main_dex_layout.addLayout(self.dex_grid_layout)

        self.display_dex_entries(self.main_app.selected_region, self.dex_grid_layout, favorites)

        self.dex_header_layout.addStretch(1)
        self.main_dex_layout.addStretch(1)

        self.main_app.stacked_layout.addWidget(self.main_dex_widget)

    def create_region_button(self, region, layout: QHBoxLayout):

        self.r_button = QPushButton("")
        self.main_app.ui_button_list.append((self.r_button, self.IM.pokeball_icon, None, None))
        self.r_button.setFont(self.main_app.main_font)
        self.r_button.setProperty("class", "Setting_Button")
        self.r_button.setText(region)
        
        self.r_button.setIcon(QIcon(self.IM.pokeball_icon[self.main_app.mode]))
        self.r_button.setIconSize(QSize(36, 36))

        self.r_button.enterEvent = partial(self.main_app.on_button_enter, self.r_button)
        self.r_button.leaveEvent = partial(self.main_app.on_button_leave, self.r_button) # type: ignore
        self.r_button.clicked.connect(partial(self.refresh_dex, region))

        layout.addWidget(self.r_button, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

    def create_search_bar(self, layout: QHBoxLayout):
        
        self.dex_search_bar = QLineEdit()
        self.dex_search_bar.setPlaceholderText("Search for a Pokémon...")
        self.dex_search_bar.setClearButtonEnabled(True)


        self.dex_search_button = QPushButton("Reset Search..")

        self.dex_search_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.dex_search_button.setProperty("class", "Setting_Button")
        self.dex_search_button.setFont(self.main_app.main_font)
        self.dex_search_button.setIcon(QIcon(self.IM.refresh_icon[self.main_app.mode]))
        self.dex_search_button.setIconSize(QSize(36, 36))

        self.dex_search_button.enterEvent = partial(self.main_app.on_button_enter, self.dex_search_button)
        self.dex_search_button.leaveEvent = partial(self.main_app.on_button_leave, self.dex_search_button)  # type: ignore

        self.dex_search_button.clicked.connect(partial(self.refresh_dex, self.main_app.selected_region))
        
        self.dex_search_bar.returnPressed.connect(partial(self.refresh_dex, self.main_app.selected_region, True))

        layout.addWidget(self.dex_search_bar)
        layout.addWidget(self.dex_search_button)

    def display_dex_entries(self, region, layout: QGridLayout, favorites=False):

        self.dex_favorite_list = self.dex_data["Favorites"]

        self.dex_fb_dict = {}
        
        col_length = self.main_app.col_count
        row_length = ceil(len(self.main_app.dex_name_list) / col_length)
        current_poke_index = 0
        all_rows = False

        
        if favorites:
            if self.dex_favorite_list:
                self.filtered_list = self.dex_data["Favorites"]
            else:
                self.main_app.f_button.setText("Your Favorites collection is empty!")
                self.filtered_list = self.main_app.dex_name_list[self.IM.region_dict[region][0]:self.IM.region_dict[region][1]] if not self.main_app.dex_inverse else sorted(self.main_app.dex_name_list[self.IM.region_dict[region][0]:self.IM.region_dict[region][1]])
        else:
            self.filtered_list = self.main_app.dex_name_list[self.IM.region_dict[region][0]:self.IM.region_dict[region][1]] if not self.main_app.dex_inverse else sorted(self.main_app.dex_name_list[self.IM.region_dict[region][0]:self.IM.region_dict[region][1]])
    

        if self.search_query:
            self.search_results = [name for name in self.filtered_list if self.search_query.lower() in name.lower()]
            if self.search_results:
                self.filtered_list = self.search_results
                self.dex_search_bar.setPlaceholderText("Search for a Pokémon...")
            else:
                self.dex_search_bar.setPlaceholderText("There were no results for your search.")

        while True:
            if all_rows:
                break
            for r in range(row_length):
                if all_rows:
                    break
                for c in range(col_length):

                    self.create_poke_button(layout, self.filtered_list[current_poke_index], r, c, favorites)

                    current_poke_index += 1
                    if current_poke_index == len(self.filtered_list):
                        all_rows = True
                        break

    def refresh_dex(self, region, search=False, favorites=False):
        self.main_app.selected_region = region

        if search:
            self.search_query = self.dex_search_bar.text()
        else:
            self.search_query = None

        self.main_app.settings['UserData']['selected_region'] = self.main_app.selected_region

        self.main_app.save_settings()

        self.main_app.go_back(self.main_dex_layout)
        
        self.display_dex_page(favorites)


    def scrub_name(self, name: str):
        return (name
               .strip()
               .replace(" ", "_")
               .replace("♂", "-M")
               .replace("♀", "-F")
               .replace("'", "")
               .replace(".", "")
               .replace("é", "e")
               .replace(":", "")
               .replace("%", "_percent")
               .replace("’", "")
               .lower())

    def _faded_pixmap(self, pixmap: QPixmap, opacity: float) -> QPixmap:
     
        if pixmap is None or pixmap.isNull():
            return pixmap
        if opacity >= 1.0:
            return pixmap

        faded = QPixmap(pixmap.size())
        faded.setDevicePixelRatio(pixmap.devicePixelRatio())
        faded.fill(Qt.GlobalColor.transparent)

        painter = QPainter(faded)
        painter.setOpacity(max(0.0, opacity))
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return faded

    def _fade_in_icon(self, button: QToolButton, pixmap: QPixmap):
   
        if sip.isdeleted(button) or pixmap is None or pixmap.isNull():
            return

        anim = QVariantAnimation(button)
        anim.setDuration(300)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        def _apply(value, button=button, pixmap=pixmap):
            if sip.isdeleted(button):
                return
            button.setIcon(QIcon(self._faded_pixmap(pixmap, value)))

        anim.valueChanged.connect(_apply)

        self._fade_animations.append(anim)

        def _cleanup(anim=anim):
            if anim in self._fade_animations:
                self._fade_animations.remove(anim)

        anim.finished.connect(_cleanup)

        anim.start()

    def _on_dex_image_fetched(self, button: QToolButton, image_link: str, pixmap: QPixmap):
       
        if sip.isdeleted(button):
            return
        self._fade_in_icon(button, pixmap)

    def _scale_pixmap(self, pixmap: QPixmap) -> QPixmap:
        """Scale pixmap down by half."""

        new_size = QSize(
            pixmap.width() // 2,
            pixmap.height() // 2
        )

        return pixmap.scaled(
            new_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

    def create_poke_button(self, layout: QGridLayout, poke_name, r, c, favorites, form=1):

        self.dex_num = self.dex_data["Pokedex"][poke_name]["Form_1"]["Dex_Number"]

        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        button_layout.setContentsMargins(15, 15, 15, 50)

        layout.addLayout(button_layout, r, c)

        title_layout = QHBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        button_layout.addLayout(title_layout)

        num_title = QLabel(self.dex_num.replace("#0", "#"))
        num_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        num_title.setProperty("class", "dex_num_header")
        num_title.setFont(self.main_app.main_font)
        num_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        title_layout.addWidget(num_title)

        poke_title = QLabel(poke_name)
        poke_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        poke_title.setProperty("class", "header2")
        poke_title.setFont(self.main_app.main_font)
        poke_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        title_layout.addWidget(poke_title)

        if self.dex_data["Pokedex"][poke_name]["Registered"]:

            pb_icon = QLabel()
            pb_icon.setPixmap(self.IM.pokeball_icon[self.main_app.mode].scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            pb_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            pb_icon.setProperty("class", "header2")
            pb_icon.setFont(self.main_app.main_font)
            pb_icon.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

            title_layout.addWidget(pb_icon)

        f_dex_num = self.dex_num.replace("#", "")  # type: str

        form_list = [key for key in self.dex_data["Pokedex"][poke_name].keys() if "Form_" in key]

        for form_i in form_list:

            cleaned_name = self.scrub_name(self.dex_data["Pokedex"][poke_name][form_i]["Dex_Name"])

            button = QToolButton()

            img_url = f"https://pocketdex-codex.pages.dev/artwork/{f_dex_num}_{cleaned_name}.png"

            dex_img = image_manager.DexImage(img_url, self.dex_img_cache)

            self._dex_image_loaders.append(dex_img)

            cached_pixmap = dex_img.get_pixmap()

            if cached_pixmap is not None:
                pass
            else:
                dex_img.image_fetched.connect(
                    partial(self._on_dex_image_fetched, button)
                )

        cleaned_name = self.scrub_name(self.dex_data["Pokedex"][poke_name][f"Form_{form}"]["Dex_Name"])

        button = QToolButton()

        img_url = f"https://pocketdex-codex.pages.dev/artwork/{f_dex_num}_{cleaned_name}.png"

        dex_img = image_manager.DexImage(img_url, self.dex_img_cache)

        self._dex_image_loaders.append(dex_img)

        cached_pixmap = dex_img.get_pixmap()


        if cached_pixmap is not None:
            cached_pixmap = self._scale_pixmap(cached_pixmap)
            self._fade_in_icon(button, cached_pixmap)
        else:
            dex_img.image_fetched.connect(
                partial(self._on_dex_image_fetched, button)
            )

        button.setIconSize(QSize(192, 192))

        button.setMinimumHeight(256)
        button.setMinimumWidth(256)

        button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        button.setProperty("class", "Main_Button")
        button.setFont(self.main_app.main_font)

        button.enterEvent = partial(self.main_app.on_button_enter, button)  # type: ignore
        button.leaveEvent = partial(self.main_app.on_button_leave, button)  # type: ignore
        button.clicked.connect(partial(self.init_dex_data_page, poke_name, "Form_1"))

        button_layout.addWidget(button)

        typing_layout = QHBoxLayout()
        typing_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        button_layout.addLayout(typing_layout)

        type_data = self.dex_data["Pokedex"][poke_name]["Form_1"]["Dex_Type"].split("/")  # type: list

        for poke_type in type_data:
            self.create_type_banner(poke_type, typing_layout)

        fav_button_layout = QHBoxLayout()
        button_layout.addLayout(fav_button_layout)

        favorite_button = QPushButton("")

        favorite_button.setProperty("name", poke_name)

        favorite_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        favorite_button.setProperty("class", "Main_Button")
        favorite_button.setIcon(QIcon(self.IM.favorite_icon[self.main_app.mode if poke_name not in self.dex_favorite_list else 2]))
        favorite_button.setIconSize(QSize(24, 24))

        favorite_button.enterEvent = partial(self.main_app.on_button_enter, favorite_button)
        favorite_button.leaveEvent = partial(self.main_app.on_button_leave, favorite_button)  # type: ignore

        favorite_button.clicked.connect(partial(self.favorite_poke, poke_name, favorites))

        fav_button_layout.addWidget(favorite_button)

        self.dex_fb_dict[poke_name] = favorite_button

    def favorite_poke(self, poke_name, favorites):
        refresh_page = False
        self.main_app.pend_reset = False

        if poke_name not in self.dex_favorite_list:
            self.dex_favorite_list.append(poke_name)

            if poke_name in self.dex_fb_dict.keys():
                self.dex_fb_dict[poke_name].setIcon(QIcon(self.IM.favorite_icon[self.main_app.mode if poke_name not in self.dex_favorite_list else 2])) 
                self.main_app.pend_reset = False
        else:
            self.dex_favorite_list.remove(poke_name)

            if poke_name in self.dex_fb_dict.keys():
                self.dex_fb_dict[poke_name].setIcon(QIcon(self.IM.favorite_icon[self.main_app.mode if poke_name not in self.dex_favorite_list else 2])) 
                if favorites:
                    self.main_app.pend_reset = True

            if favorites:
                refresh_page = True

        
        sending_button = self.main_app.sender()
        sending_button.setIcon(QIcon(self.IM.favorite_icon[self.main_app.mode if poke_name not in self.dex_favorite_list else 2]))  # type: ignore
    

        self.dex_data["Favorites"] = self.dex_favorite_list

        self.save_dex_data()

        
        if refresh_page:
            self.refresh_dex(self.main_app.selected_region, False, favorites)
        

    def create_bullet(self, layout):

        bullet = QLabel()
        bullet.setText(f'⦿')
        bullet.setProperty("class", "header2")

        bullet.setFont(self.main_app.main_font_bold)
        bullet.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        layout.addWidget(bullet)

        


    def create_type_banner(self, poke_type, layout: QHBoxLayout):

        type_title = QLabel(poke_type)
        type_title.setText(f'<img src="{self.IM.dex_type_dict[poke_type]}" width="32" height="32" style="vertical-align: bottom;" />{poke_type} ')
        type_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        type_title.setProperty("class", "type_header")
        type_title.setProperty("poke_type", poke_type.lower())

        type_title.setFont(self.main_app.main_font)
        type_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        layout.addWidget(type_title)

    def create_gender_banners(self, gender_data, layout: QHBoxLayout):
        
        if isinstance(gender_data, dict): # valid M-F data
            if gender_data["Male"] != "0":

                gender_banner = QLabel()
                gender_banner.setText(f'<img src="{self.IM.gender_dict["Male"]}" width="32" height="32" style="vertical-align: bottom;" />{gender_data["Male"]}%')
                gender_banner.setProperty("class", "type_header")
                gender_banner.setProperty("gender", "male")

                gender_banner.setFont(self.main_app.main_font)
                gender_banner.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                
                layout.addWidget(gender_banner)

            if gender_data["Female"] != "0":

                gender_banner = QLabel()
                gender_banner.setText(f'<img src="{self.IM.gender_dict["Female"]}" width="32" height="32" style="vertical-align: bottom;" />{gender_data["Female"]}%')
                gender_banner.setProperty("class", "type_header")
                gender_banner.setProperty("gender", "female")

                gender_banner.setFont(self.main_app.main_font)
                gender_banner.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                
                layout.addWidget(gender_banner)
        else:
            gender_banner = QLabel()
            gender_banner.setText('Genderless')
            gender_banner.setProperty("class", "type_header")
            gender_banner.setProperty("gender", "genderless")
          
            gender_banner.setFont(self.main_app.main_font)
            gender_banner.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
           
            
            layout.addWidget(gender_banner)

    def create_height_weight_banners(self, h_w_data, layout: QHBoxLayout):
        h_banner = QLabel()
        h_banner.setText(f'<img src="{self.IM.height_icon[self.main_app.mode]}" width="32" height="32" style="vertical-align: bottom;" /> {h_w_data["Height"]}')
        h_banner.setProperty("class", "dex_text_icon")

        h_banner.setFont(self.main_app.main_font)
        h_banner.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        layout.addWidget(h_banner)

        w_banner = QLabel()
        w_banner.setText(f'<img src="{self.IM.weight_icon[self.main_app.mode]}" width="32" height="32" style="vertical-align: bottom;" /> {h_w_data["Weight"]}')
        w_banner.setProperty("class", "dex_text_icon")
    
        w_banner.setFont(self.main_app.main_font)
        w_banner.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        layout.addWidget(w_banner)
                
            


    def display_dex_page(self, favorites=False):

        self.dex_page_init(favorites)

        self.main_dex_widget.setStyleSheet(self.main_app.themes.dark_theme if self.main_app.mode == 1 else self.main_app.themes.light_theme)

        if hasattr(self, 'scroll_area'):
            self.saved_scroll_position = self.scroll_area.verticalScrollBar().value() # type: ignore

        self.main_app.stacked_layout.setCurrentWidget(self.main_dex_widget)

    def init_dex_data_page(self, poke_name, form):

        self.search_query = None

        if hasattr(self, 'u_button_shortcut'):
            self.u_button_shortcut.setEnabled(False) # type: ignore
            self.u_button_shortcut.deleteLater() # type: ignore
            del self.u_button_shortcut


        if hasattr(self, 'd_button_shortcut'):
            self.d_button_shortcut.setEnabled(False) # type: ignore
            self.d_button_shortcut.deleteLater() # type: ignore
            del self.d_button_shortcut

        if hasattr(self, 'cry_button_shortcut'):
            self.cry_button_shortcut.setEnabled(False) # type: ignore
            self.cry_button_shortcut.deleteLater() # type: ignore
            del self.cry_button_shortcut

        self.dex_data_widget = QWidget()
        
        self.dex_data_layout = QVBoxLayout()
        
        self.dex_data_widget.setLayout(self.dex_data_layout)

        self.main_app.init_back_button(self.dex_data_layout, "Top")


        self.main_title_layout = QHBoxLayout()
        self.main_title_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.dex_data_layout.addLayout(self.main_title_layout)

        self.codex_layout = QVBoxLayout()
        self.main_title_layout.addLayout(self.codex_layout)

        codex_icon = QLabel("")

        codex_icon.setPixmap(self.IM.codex_icon_mini[self.main_app.mode].scaled(175, 175, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        codex_icon.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        codex_icon.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.codex_layout.addWidget(codex_icon)

        self.nd_layout = QVBoxLayout()
        self.main_title_layout.addLayout(self.nd_layout)

        self.nd_layout.addStretch()

        self.name_layout = QHBoxLayout()
        self.nd_layout.addLayout(self.name_layout)

        dex_title = QLabel(poke_name)
       
        dex_title.setProperty("class", "dex_header_title")
        dex_title.setFont(self.main_app.main_font)
        dex_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self.name_layout.addWidget(dex_title)

        if self.dex_data["Pokedex"][poke_name]["Registered"]:

            pb_icon = QLabel()
            pb_icon.setPixmap(self.IM.pokeball_icon[self.main_app.mode].scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
          
            pb_icon.setProperty("class", "header2")
            pb_icon.setFont(self.main_app.main_font)
            pb_icon.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

            self.name_layout.addWidget(pb_icon)

            self.name_layout.addStretch()

        self.main_title_layout.addStretch()

        self.data_layout = QHBoxLayout()
        self.nd_layout.addLayout(self.data_layout)

        dex_num = self.dex_data["Pokedex"][poke_name][form]["Dex_Number"] # type: str

        f_dex_num = dex_num.replace("#", "")

        num_title = QLabel(dex_num.replace("#0", "#"))
        num_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        num_title.setProperty("class", "dex_num_header")
        num_title.setFont(self.main_app.main_font)
        num_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.data_layout.addWidget(num_title)

        self.create_bullet(self.data_layout)

        type_data = self.dex_data["Pokedex"][poke_name][form]["Dex_Type"].split("/")  # type: list

        for poke_type in type_data:
            self.create_type_banner(poke_type, self.data_layout)

        self.create_bullet(self.data_layout)

        raw_g_data = self.dex_data["Pokedex"][poke_name][form]["Gender"]

        cleaned_g_data = raw_g_data if raw_g_data == "Genderless" else raw_g_data.split("-")

        if cleaned_g_data != "Genderless":
            gender_data = {}
            gender_data["Male"] = cleaned_g_data[0]
            gender_data["Female"] = cleaned_g_data[1]
        else:
            gender_data = cleaned_g_data

    
        self.create_gender_banners(gender_data, self.data_layout)

        self.create_bullet(self.data_layout)

        self.main_app.seperator(self.dex_data_layout, 0)

        h_w_data = {}

        h_w_data["Height"] = self.dex_data["Pokedex"][poke_name][form]["Height"]

        h_w_data["Weight"] = self.dex_data["Pokedex"][poke_name][form]["Weight"]

        self.create_height_weight_banners(h_w_data, self.data_layout)

        self.create_arrow_dex_buttons(poke_name, self.main_app.bb_layout)

        self.data_layout.addStretch()

        self.dex_data_container = QHBoxLayout()


        self.dex_data_layout.addLayout(self.dex_data_container)

    
        self.basic_txt_layout = QVBoxLayout()
        self.dex_data_container.addStretch(1)
        self.dex_data_container.addLayout(self.basic_txt_layout)
        self.dex_data_container.addStretch(1)

        basic_txt = QLabel(self.dex_data["Pokedex"][poke_name]["Description"])
        basic_txt.setProperty("class", "dex_text")

        basic_txt.setFont(self.main_app.main_font)
        basic_txt.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        basic_txt.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        
        self.basic_txt_layout.addWidget(basic_txt)

        self.forms_layout = QHBoxLayout()
        self.basic_txt_layout.addLayout(self.forms_layout)

        form_list = [form for form in self.dex_data["Pokedex"][poke_name].keys() if "Form_" in form]

        if len(form_list) > 1:
            for form_i in form_list:
                form_button = QPushButton(self.dex_data["Pokedex"][poke_name][form_i]["Dex_Name"])
                form_button.setFont(self.main_app.main_font)
                form_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                form_button.setProperty("class", "Main_Button")

                form_button.enterEvent = partial(self.main_app.on_button_enter, form_button)
                form_button.leaveEvent = partial(self.main_app.on_button_leave, form_button)  # type: ignore

                form_button.clicked.connect(partial(self.refresh_dex_data_page, poke_name, form_i))

                self.forms_layout.addWidget(form_button)
    

        main_poke_bg = QToolButton()

        main_poke_bg.setMinimumHeight(512)
        main_poke_bg.setMinimumWidth(512)

        main_poke_bg.setIconSize(QSize(512, 512))

        main_poke_bg.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        main_poke_bg.setProperty("class", "Dex_Button_D")

        main_poke_bg.setFont(self.main_app.main_font)

        self.basic_txt_layout.addWidget(main_poke_bg)

        cleaned_name = self.scrub_name(self.dex_data["Pokedex"][poke_name][form]["Dex_Name"])

        img_url = f"https://pocketdex-codex.pages.dev/artwork/{f_dex_num}_{cleaned_name}.png"

        dex_img = image_manager.DexImage(img_url, self.dex_img_cache)

        self._dex_image_loaders.append(dex_img)

        cached_pixmap = dex_img.get_pixmap()

        if cached_pixmap is not None:
            self._fade_in_icon(main_poke_bg, cached_pixmap)
        else:
            dex_img.image_fetched.connect(
                partial(self._on_dex_image_fetched, main_poke_bg)
            )


        self.poke_flavor_text = self.dex_data["Pokedex"][poke_name]["Flavor_Text"]

        self.fl_layout = QVBoxLayout()
        self.entry_counter_layout = QHBoxLayout()

        self.basic_txt_layout.addLayout(self.entry_counter_layout)
        self.basic_txt_layout.addLayout(self.fl_layout)

        self.fl_index = 0
       
        self.curr_txt = QLabel(f'<img src="{self.IM.entry_icon[self.main_app.mode]}" width="32" height="32" style="vertical-align: bottom;" /> Entry {self.fl_index + 1}/{len(self.poke_flavor_text)}:')
        self.curr_txt.setProperty("class", "dex_text")
        self.curr_txt.setWordWrap(True)
        self.curr_txt.setFont(self.main_app.main_font)
        self.curr_txt.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.curr_txt.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        
        self.entry_counter_layout.addWidget(self.curr_txt)

        up_button = QPushButton("")
        up_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        up_button.setProperty("class", "Main_Button")
        up_button.setIcon(QIcon(self.IM.arrow_up_icon[self.main_app.mode]))
        up_button.setIconSize(QSize(32, 32))

        up_button.enterEvent = partial(self.main_app.on_button_enter, up_button)
        up_button.leaveEvent = partial(self.main_app.on_button_leave, up_button)  # type: ignore

        up_button.clicked.connect(partial(self.change_flavor_text, "+"))

        self.u_button_shortcut = QShortcut(QKeySequence("Up"), self.main_app)
        self.u_button_shortcut.activated.connect(up_button.click)

        self.entry_counter_layout.addWidget(up_button)

        down_button = QPushButton("")
        down_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        down_button.setProperty("class", "Main_Button")
        down_button.setIcon(QIcon(self.IM.arrow_down_icon[self.main_app.mode]))
        down_button.setIconSize(QSize(32, 32))

        down_button.enterEvent = partial(self.main_app.on_button_enter, down_button)
        down_button.leaveEvent = partial(self.main_app.on_button_leave, down_button)  # type: ignore

        down_button.clicked.connect(partial(self.change_flavor_text, "-"))

        self.d_button_shortcut = QShortcut(QKeySequence("Down"), self.main_app)
        self.d_button_shortcut.activated.connect(down_button.click)

        self.entry_counter_layout.addWidget(down_button)

        
        self.flavor_txt = QLabel(self.poke_flavor_text[self.fl_index])
        self.flavor_txt.setProperty("class", "dex_text")
        self.flavor_txt.setWordWrap(True)
        self.flavor_txt.setFont(self.main_app.main_font)
        self.flavor_txt.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.flavor_txt.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        
        self.fl_layout.addWidget(self.flavor_txt)

        self.extra_op_layout = QHBoxLayout()

        self.fl_layout.addLayout(self.extra_op_layout)

        favorite_button = QPushButton("")

        favorite_button.setProperty("name", poke_name)

        favorite_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        favorite_button.setProperty("class", "Main_Button")
        favorite_button.setIcon(QIcon(self.IM.favorite_icon[self.main_app.mode if poke_name not in self.dex_favorite_list else 2]))
        favorite_button.setIconSize(QSize(24, 24))

        favorite_button.enterEvent = partial(self.main_app.on_button_enter, favorite_button)
        favorite_button.leaveEvent = partial(self.main_app.on_button_leave, favorite_button)  # type: ignore

        favorite_button.clicked.connect(partial(self.favorite_poke, poke_name, False))

        self.extra_op_layout.addWidget(favorite_button)

        cry_button = QPushButton("Hear Cry.. (R)")
        cry_button.setFont(self.main_app.main_font)
        cry_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        cry_button.setProperty("class", "Main_Button")

        cry_button.setIcon(QIcon(self.IM.sound_icon[self.main_app.mode]))
        cry_button.setIconSize(QSize(24, 24))

        cry_button.enterEvent = partial(self.main_app.on_button_enter, cry_button)
        cry_button.leaveEvent = partial(self.main_app.on_button_leave, cry_button)  # type: ignore

        self.cry_button_shortcut = QShortcut(QKeySequence("R"), self.main_app)
        self.cry_button_shortcut.activated.connect(cry_button.click)

        cry_button.clicked.connect(partial(self.media_manager.play_cry, f_dex_num, 0.7))

        self.extra_op_layout.addWidget(cry_button)

        self.dex_data_layout.addStretch(1)

        self.display_dex_data_page()

    def media_player_init(self):
        self.media_manager = media_manager.MediaManager()


    def change_flavor_text(self, value):
        
        if value == "+":
            if self.fl_index < len(self.poke_flavor_text) - 1:
                self.fl_index += 1

                self.curr_txt.setText(f'<img src="{self.IM.entry_icon[self.main_app.mode]}" width="32" height="32" style="vertical-align: bottom;" /> Entry {self.fl_index + 1}/{len(self.poke_flavor_text)}:')
                self.flavor_txt.setText(self.poke_flavor_text[self.fl_index])
        else:
            if self.fl_index:
                self.fl_index -= 1

                self.curr_txt.setText(f'<img src="{self.IM.entry_icon[self.main_app.mode]}" width="32" height="32" style="vertical-align: bottom;" /> Entry {self.fl_index + 1}/{len(self.poke_flavor_text)}:')
                self.flavor_txt.setText(self.poke_flavor_text[self.fl_index])


    def create_arrow_dex_buttons(self, poke_name, layout):

        dex_num_int = self.poke_to_dex_num_dict[poke_name]

        if hasattr(self, 'l_button_shortcut'):
            self.l_button_shortcut.setEnabled(False) # type: ignore
            self.l_button_shortcut.deleteLater() # type: ignore
            del self.l_button_shortcut


        if hasattr(self, 'r_button_shortcut'):
            self.r_button_shortcut.setEnabled(False) # type: ignore
            self.r_button_shortcut.deleteLater() # type: ignore
            del self.r_button_shortcut


        if dex_num_int - 1 > 0:

            self.prev_poke_button = QPushButton(f'View Previous Pokémon.. ({self.dex_num_to_poke_dict[dex_num_int - 1].replace("&", "&&")})')
            self.prev_poke_button.setProperty("class", "Setting_Button")
            self.prev_poke_button.setFont(self.main_app.main_font)

            self.prev_poke_button.setIcon(QIcon(self.IM.arrow_icon[self.main_app.mode]))
            self.prev_poke_button.setIconSize(QSize(36, 36))

            self.prev_poke_button.enterEvent = partial(self.main_app.on_button_enter, self.prev_poke_button)
            self.prev_poke_button.leaveEvent = partial(self.main_app.on_button_leave, self.prev_poke_button) # type: ignore
            
            self.prev_poke_button.clicked.connect(partial(self.refresh_dex_data_page, self.dex_num_to_poke_dict[dex_num_int - 1], "Form_1"))

            self.l_button_shortcut = QShortcut(QKeySequence("Left"), self.main_app)
            self.l_button_shortcut.activated.connect(self.prev_poke_button.click)

            layout.addWidget(self.prev_poke_button)

        if dex_num_int != len(self.main_app.dex_name_list):

            self.next_poke_button = QPushButton(f'View Next Pokémon.. ({self.dex_num_to_poke_dict[dex_num_int + 1].replace("&", "&&")})')
            self.next_poke_button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.next_poke_button.setProperty("class", "Setting_Button")
            self.next_poke_button.setFont(self.main_app.main_font)

            self.next_poke_button.setIcon(QIcon(self.IM.forward_icon[self.main_app.mode]))
            self.next_poke_button.setIconSize(QSize(36, 36))

            self.next_poke_button.enterEvent = partial(self.main_app.on_button_enter, self.next_poke_button)
            self.next_poke_button.leaveEvent = partial(self.main_app.on_button_leave, self.next_poke_button) # type: ignore

            self.next_poke_button.clicked.connect(partial(self.refresh_dex_data_page, self.dex_num_to_poke_dict[dex_num_int + 1], "Form_1"))

            self.r_button_shortcut = QShortcut(QKeySequence("Right"), self.main_app)
            self.r_button_shortcut.activated.connect(self.next_poke_button.click)

            layout.addWidget(self.next_poke_button)


        random_button = QPushButton("Random..")
        random_button.setProperty("class", "Setting_Button")
        random_button.setFont(self.main_app.main_font)

        random_button.setIcon(QIcon(self.IM.dice_icon[self.main_app.mode]))
        random_button.setIconSize(QSize(36, 36))

        random_button.enterEvent = partial(self.main_app.on_button_enter, random_button)
        random_button.leaveEvent = partial(self.main_app.on_button_leave, random_button) # type: ignore
        
        random_button.clicked.connect(partial(self.refresh_dex_data_page, random.choice(self.main_app.dex_name_list), "Form_1"))

        layout.addWidget(random_button)

    def refresh_dex_data_page(self, poke_name, form):
        self.main_app.go_back(self.dex_data_layout)
        self.init_dex_data_page(poke_name, form)


    def display_dex_data_page(self):
        
        self.dex_data_widget.setStyleSheet(self.main_app.themes.dark_theme if self.main_app.mode == 1 else self.main_app.themes.light_theme)

        self.main_app.stacked_layout.addWidget(self.dex_data_widget)

        self.main_app.stacked_layout.setCurrentWidget(self.dex_data_widget)

        if self.dex_data_widget:
            self.main_dex_widget.setSizePolicy(
                QSizePolicy.Policy.Ignored, 
                QSizePolicy.Policy.Ignored
            )


    def scrub_card_name(self, poke_name):

   
        poke_name = re.sub(r'<[^>]+>', '', poke_name).strip()

        for suffix in self.IM.scrub_list:
            poke_name = poke_name.replace(suffix, "")

        for alpha in string.ascii_uppercase + string.punctuation:
            if poke_name.endswith(alpha):
                poke_name = poke_name.rstrip(alpha)
        
        return poke_name.replace(" Male", "-M").replace(" Female", "-F").replace("'", "’").strip()

    def add_to_dex(self, poke_name):
        poke_name = self.scrub_card_name(poke_name)

        if poke_name in self.dex_data["Pokedex"].keys():

            if not self.dex_data["Pokedex"][poke_name]["Registered"]:
                self.dex_data["Pokedex"][poke_name]["Registered"] = True

                dex_num = self.poke_to_dex_num_dict[poke_name]

                for region, index_tuple in self.IM.region_dict.items():
                    
                    if (index_tuple[0] + 1) <= dex_num <= index_tuple[1]:
                        self.dex_data[f"{region.lower()}_obtained"] += 1
                    

