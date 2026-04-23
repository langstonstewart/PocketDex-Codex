import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QUrl, QSize, pyqtSignal
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6 import sip
from functools import partial
from src.resource_path import resource_path



class ImageManager:

    def __init__(self):

        self.tcg_logo = QPixmap(self.img("src/images/ui/tcg_logo.png"))
        self.tcg_pocket_logo = QPixmap(self.img("src/images/ui/tcg_pocket_logo.png"))
        
        self.img_icon = (QPixmap(self.img("src/images/ui/img_icon_black.png")), QPixmap(self.img("src/images/ui/img_icon_white.png")))
        self.loading_icon = (QPixmap(self.img("src/images/ui/loading_icon_black.png")), QPixmap(self.img("src/images/ui/loading_icon_white.png")))
        self.theme_icon = (QPixmap(self.img("src/images/ui/sun.png")), QPixmap(self.img("src/images/ui/moon.png")))
        self.codex_icon = (QPixmap(self.img("src/images/ui/codex.png")), QPixmap(self.img("src/images/ui/codex.png")))
        self.codex_icon_mini = (QPixmap(self.img("src/images/ui/logo_icon.png")), QPixmap(self.img("src/images/ui/logo_icon.png")))
        self.arrow_icon = (QPixmap(self.img("src/images/ui/back_black.png")), QPixmap(self.img("src/images/ui/back_white.png")))
        self.forward_icon = (QPixmap(self.img("src/images/ui/forward_black.png")), QPixmap(self.img("src/images/ui/forward_white.png")))
        self.plus_icon = (QPixmap(self.img("src/images/ui/plus_black.png")), QPixmap(self.img("src/images/ui/plus_white.png")))
        self.minus_icon = (QPixmap(self.img("src/images/ui/minus_black.png")), QPixmap(self.img("src/images/ui/minus_white.png")))
        self.info_icon = (QPixmap(self.img("src/images/ui/info_black.png")), QPixmap(self.img("src/images/ui/info_white.png")))
        self.github_icon = (QPixmap(self.img("src/images/links/github_icon_dark.png")), QPixmap(self.img("src/images/links/github_icon_light.png")))
        self.ltcg_icon = (QPixmap(self.img("src/images/links/ltcg_icon_dark.png")), QPixmap(self.img("src/images/links/ltcg_icon_light.png")))
        self.pz_icon = (QPixmap(self.img("src/images/links/pz_icon_dark.png")), QPixmap(self.img("src/images/links/pz_icon_light.png")))
        self.serebii_icon = (QPixmap(self.img("src/images/links/serebii_icon_dark.png")), QPixmap(self.img("src/images/links/serebii_icon_light.png")))
        self.export_icon = (QPixmap(self.img("src/images/ui/export_black.png")), QPixmap(self.img("src/images/ui/export_white.png")))
        self.import_icon = (QPixmap(self.img("src/images/ui/import_black.png")), QPixmap(self.img("src/images/ui/import_white.png")))
        self.shadow_add_icon = (QPixmap(self.img("src/images/ui/shadow_add_black.png")), QPixmap(self.img("src/images/ui/shadow_add_white.png")))
        self.shadow_minus_icon = (QPixmap(self.img("src/images/ui/shadow_minus_black.png")), QPixmap(self.img("src/images/ui/shadow_minus_white.png")))
        self.refresh_icon = (QPixmap(self.img("src/images/ui/refresh_black.png")), QPixmap(self.img("src/images/ui/refresh_white.png")))
        self.favorite_icon = (QPixmap(self.img("src/images/ui/heart_black.png")), QPixmap(self.img("src/images/ui/heart_white.png")), QPixmap(self.img("src/images/ui/heart_active.png")))
        self.heart_button_icon = (QPixmap(self.img("src/images/ui/heart_button_black.png")), QPixmap(self.img("src/images/ui/heart_button_white.png")))
        self.f_tag = (QPixmap(self.img("src/images/tags/favorites_black.png")), QPixmap(self.img("src/images/tags/favorites_black.png")))
        self.ability_icon = QPixmap(self.img("src/images/card_data/ability_logo.png"))
        self.paint_icon = (QPixmap(self.img("src/images/card_data/paint_black.png")), QPixmap(self.img("src/images/card_data/paint_white.png")))
        self.exit_icon = (QPixmap(self.img("src/images/ui/exit_black.png")), QPixmap(self.img("src/images/ui/exit_white.png")))
        self.pokeball_icon = (QPixmap(self.img("src/images/rarities/TCG/none_black.png")), QPixmap(self.img("src/images/rarities/TCG/none_white.png")))
        self.ex_icon = self.img("src/images/name_icons/ex_icon.png")
        self.tcgplayer_icon = (QPixmap(self.img("src/images/links/tcgplayer_icon_dark.png")), QPixmap(self.img("src/images/links/tcgplayer_icon_light.png")))
        self.cm_icon = (QPixmap(self.img("src/images/links/cardmarket_icon_dark.png")), QPixmap(self.img("src/images/links/cardmarket_icon_light.png")))
        
        self.gx_icon = self.img("src/images/name_icons/gx_icon.png")
        self.gx_tag_team_icon = self.img("src/images/name_icons/gx_tag_team_icon.png")
        self.tera_icon = QPixmap(self.img("src/images/card_data/tera_icon.png"))
       
        self.star_icon = self.img("src/images/name_icons/star_logo.png")
      
        self.dice_icon = (QPixmap(self.img("src/images/ui/dice_black.png")), QPixmap(self.img("src/images/ui/dice_white.png")))

        self.sort_icon = (QPixmap(self.img("src/images/ui/sort_black.png")), QPixmap(self.img("src/images/ui/sort_white.png")))

        self.trait_dict = {
            "\u03b1": QPixmap(self.img("src/images/card_data/traits/alpha_icon.png")),
            "\u03a9": QPixmap(self.img("src/images/card_data/traits/omega_icon.png")),
            "\u0394": QPixmap(self.img("src/images/card_data/traits/delta_icon.png")),
            "\u03b8": QPixmap(self.img("src/images/card_data/traits/theta_icon.png")),
        }

        self.rarity_dict = {"TCG": [
                                            "Double Rare",
                                            "Common",
                                            "Rare",
                                            "Uncommon",
                                            "ACE SPEC Rare",
                                            "Illustration Rare",
                                            "Ultra Rare",
                                            "Special Illustration Rare",
                                            "Hyper Rare",
                                            "Shiny Rare",
                                            "Shiny Ultra Rare",
                                            "No Rarity",
                                            "Promo",
                                            "Holo Rare V",
                                            "Holo Rare VSTAR",
                                            "Rare Holo",
                                            "Radiant Rare",
                                            "Holo Rare VMAX",
                                            "Rare Secret",
                                            "Trainer Gallery Holo Rare",
                                            "Trainer Gallery Holo Rare V",
                                            "Trainer Gallery Ultra Rare",
                                            "Trainer Gallery Secret Rare",
                                            "Rainbow Rare",
                                            "Trainer Gallery Holo Rare V or VMAX",
                                            "Special Full Art",
                                            "Amazing Rare",
                                            "Shiny Rare V or VMAX",
                                            "Rare Holo GX",
                                            "Rare Prism Star",
                                            "Rare Shiny GX",
                                            "Rare Shining",
                                            "Rare Holo EX",
                                            "Rare BREAK",
                                            "Rare Prime",
                                            "LEGEND",
                                            "Mega Hyper Rare",
                                            "Mega Attack Rare",
                                            "Black White Rare",
                                            "Rare Holo LV.X",
                                            "Rare Holo ex",
                                            "Rare Holo Star"
                                        ],

                            "TCG Pocket": ["1 Diamond",
                                            "2 Diamond",
                                            "4 Diamond",
                                            "3 Diamond",
                                            "1 Star",
                                            "2 Star",
                                            "3 Star",
                                            "1 Shiny",
                                            "2 Shiny",
                                            "Crown"]}
        
        self.rule_list = [  'Mega-ex-Rule', 
                            'Mega-Evolution-Rule',
                            'ex-Rule',
                            'Tera-Rule',
                            'BREAK-Rule',
                            'V-Rule', 
                            'VSTAR-Rule',
                            'VMAX-Rule',
                            'V-UNION-Rule', 
                            'TAG-TEAM-Rule',
                            'GX-Rule', 
                            'Prism-Star-Rule', 
                            'Primal-Reversion-Rule', 
                            'LEGEND-Rule', 
                            'Level-Up-Rule', 
                            'Star-Rule', 
                            'Dual-Type-Rule']
        

        self.tag_dict  = {
            "-EX": self.img("src/images/name_icons/ex_legacy.png"),
            "BREAK": self.img("src/images/name_icons/break.png"),
            "V": self.img("src/images/name_icons/v_icon.png"),
            "VMAX": self.img("src/images/name_icons/v_max_icon.png"),
            "VSTAR": self.img("src/images/name_icons/v_star_icon.png"),
            "V-UNION": self.img("src/images/name_icons/v-union_icon.png"),
            "LV.X": self.img("src/images/name_icons/lv_x_logo.png"),
            "LEGEND": self.img("src/images/name_icons/legend.png"),
            "\u2662": self.img("src/images/name_icons/prism_star.png"),
            "-GX": self.img("src/images/name_icons/gx_icon.png")
        }


        self.ex_dict = {
            "Mega Evolution": self.img("src/images/name_icons/ex_sv.png"),
            "Scarlet & Violet": self.img("src/images/name_icons/ex_sv.png"),
            "XY": self.img("src/images/name_icons/ex_legacy.png"),
            "Black & White": self.img("src/images/name_icons/ex_legacy.png"),
            "Mega Pokemon": self.img("src/images/name_icons/ex_sv_mega.png")
        }

        self.counter_icon_dict = {
            4: (QPixmap(self.img("src/images/ui/counter_4_black.png")), QPixmap(self.img("src/images/ui/counter_4_white.png"))),
            6: (QPixmap(self.img("src/images/ui/counter_6_black.png")), QPixmap(self.img("src/images/ui/counter_6_white.png"))),
            8: (QPixmap(self.img("src/images/ui/counter_8_black.png")), QPixmap(self.img("src/images/ui/counter_8_white.png"))),
        }

        self.logo_dict = {}

        self.card_type_dict = {
            "Basic": QPixmap(self.img("src/images/card_data/stages/basic_logo.png")),
            "Stage 1": QPixmap(self.img("src/images/card_data/stages/stage1_logo.png")),
            "Stage 2": QPixmap(self.img("src/images/card_data/stages/stage2_logo.png")),
            "Supporter": QPixmap(self.img("src/images/card_data/stages/supporter_logo.png")),
            "Item": QPixmap(self.img("src/images/card_data/stages/item_logo.png")),
            "Tool": QPixmap(self.img("src/images/card_data/stages/tool_logo.png")),
            "Stadium": QPixmap(self.img("src/images/card_data/stages/stadium_logo.png")),
            "VMAX": QPixmap(self.img("src/images/card_data/stages/vmax_logo.png")),
            "VSTAR": QPixmap(self.img("src/images/card_data/stages/vstar_logo.png")),
            "V-UNION": QPixmap(self.img("src/images/card_data/stages/v-union_logo.png")),
            "Basic Energy": QPixmap(self.img("src/images/card_data/stages/energy_logo.png")),
            "Special Energy": QPixmap(self.img("src/images/card_data/stages/special_energy_logo.png")),
            "BREAK Evolution": QPixmap(self.img("src/images/card_data/stages/break_logo.png")),
            "Mega Evolution": QPixmap(self.img("src/images/card_data/stages/mega_logo.png")),
            "Level Up": QPixmap(self.img("src/images/card_data/stages/level_up_logo.png")),
            "Item/Technical Machine": QPixmap(self.img("src/images/card_data/stages/tm_logo.png")),
            "LEGEND": QPixmap(self.img("src/images/card_data/stages/legend_logo.png"))
        }

        self.type_dict = {
            "Colorless": QPixmap(self.img("src/images/card_data/energy/energy_colorless.png")),
            "Grass": QPixmap(self.img("src/images/card_data/energy/energy_grass.png")),
            "Fire": QPixmap(self.img("src/images/card_data/energy/energy_fire.png")),
            "Water": QPixmap(self.img("src/images/card_data/energy/energy_water.png")),
            "Lightning": QPixmap(self.img("src/images/card_data/energy/energy_lightning.png")),
            "Psychic": QPixmap(self.img("src/images/card_data/energy/energy_psychic.png")),
            "Fighting": QPixmap(self.img("src/images/card_data/energy/energy_fighting.png")),
            "Darkness": QPixmap(self.img("src/images/card_data/energy/energy_darkness.png")),
            "Metal": QPixmap(self.img("src/images/card_data/energy/energy_metal.png")),
            "Dragon": QPixmap(self.img("src/images/card_data/energy/energy_dragon.png")),
            "Fairy": QPixmap(self.img("src/images/card_data/energy/energy_fairy.png")),
        }


        self.energy_dict = {
            "C": self.img("src/images/card_data/energy/energy_colorless.png"),
            "G": self.img("src/images/card_data/energy/energy_grass.png"),
            "R": self.img("src/images/card_data/energy/energy_fire.png"),
            "W": self.img("src/images/card_data/energy/energy_water.png"),
            "L": self.img("src/images/card_data/energy/energy_lightning.png"),
            "P": self.img("src/images/card_data/energy/energy_psychic.png"),
            "F": self.img("src/images/card_data/energy/energy_fighting.png"),
            "D": self.img("src/images/card_data/energy/energy_darkness.png"),
            "M": self.img("src/images/card_data/energy/energy_metal.png"),
            "DR": self.img("src/images/card_data/energy/energy_dragon.png"),
            "N": self.img("src/images/card_data/energy/energy_dragon.png"),
            "Y": self.img("src/images/card_data/energy/energy_fairy.png"),
            "0": self.img("src/images/card_data/energy/no_energy.png"),
            "+": (self.img("src/images/card_data/energy/plus_icon_black.png"), self.img("src/images/card_data/energy/plus_icon_white.png"))
        }

        self.card_desc_dict = {
            "Item": "You may play any number of item cards during your turn.",
            "Supporter": "You may play only 1 Supporter card during your turn.",
            "Tool": "You use Pok\u00e9mon Tools by attaching them to your Pok\u00e9mon. You may only attach 1 Pok\u00e9mon Tool to each Pok\u00e9mon, and it stays attached.",
            "Stadium": "You may play only 1 Stadium card during your turn. Put it next to the Active Spot, and discard it if another Stadium comes into play. A Stadium with the same name can't be played."

        }


    def img(self, path: str):
        return resource_path(path)
    





R_manager = QNetworkRequest

class ImageLabel(QLabel):
    download_finished = pyqtSignal()
    
    def __init__(self, source, card_id=None, fp=None, cache=False, size=QSize(241, 337), network_manager: QNetworkAccessManager | None = None, is_pixmap=False):
        super().__init__()
        self.source = source
        self.target_size = size
        self.setFixedSize(size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._reply: QNetworkReply | None = None
        self._network_manager = network_manager

        if not is_pixmap:

            if self.is_remote_source():
                self.fetch_remote()
            else:
                self.grab_local()

        else:
            pixmap = QPixmap(is_pixmap) 
            scaled = pixmap.scaled(
            self.target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled)


    def is_remote_source(self):
        return isinstance(self.source, str) and QUrl(self.source).scheme() in {"http", "https"}

    def fetch_remote(self):
        if self._network_manager is None:
            self._network_manager = QNetworkAccessManager(self)

        request = R_manager(QUrl(self.source))
        self._reply = self._network_manager.get(request)

        self._reply.errorOccurred.connect(partial(self.handle_error, self.source)) # type: ignore
        self._reply.finished.connect(self.image_loaded) # type: ignore

    def handle_error(self, url, error):
        print(f"Network error: {error} | at {url}")
        if self._reply and not sip.isdeleted(self._reply):
            self._reply.deleteLater()
        self._reply = None
        self.download_finished.emit()
            

    def image_loaded(self):
        reply = self._reply
        if reply is None or sip.isdeleted(reply):
            self._reply = None
            self.download_finished.emit()
            return
        
        pixmap = QPixmap()
        try:
            pixmap.loadFromData(reply.readAll()) # type: ignore
        except RuntimeError:
            self._reply = None
            self.download_finished.emit()
            return
        scaled = pixmap.scaled(
            self.target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)

        if not sip.isdeleted(reply):
            reply.deleteLater() # type: ignore
        self._reply = None

        self.download_finished.emit()

    def grab_local(self):
        local_path = self.source if isinstance(self.source, str) and os.path.exists(self.source) else ""
        pixmap = QPixmap(local_path)
        scaled = pixmap.scaled(
            self.target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)

    def set_pixmap(self, pixmap):
        scaled = pixmap.scaled(
            self.target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)
    
    
