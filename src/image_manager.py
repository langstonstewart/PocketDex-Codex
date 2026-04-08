from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QUrl, QSize, pyqtSignal
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6 import sip
from functools import partial



class ImageManager:

    def __init__(self):

        self.tcg_logo = QPixmap("src/images/ui/tcg_logo.png")
        self.tcg_pocket_logo = QPixmap("src/images/ui/tcg_pocket_logo.png")
        
        self.img_icon = (QPixmap("src/images/ui/img_icon_black.png"), QPixmap("src/images/ui/img_icon_white.png"))
        self.loading_icon = (QPixmap("src/images/ui/loading_icon_black.png"), QPixmap("src/images/ui/loading_icon_white.png"))
        self.theme_icon = (QPixmap("src/images/ui/sun.png"), QPixmap("src/images/ui/moon.png"))
        self.codex_icon = (QPixmap("src/images/ui/codex.png"), QPixmap("src/images/ui/codex.png"))
        self.codex_icon_mini = (QPixmap("src/images/ui/logo_icon.png"), QPixmap("src/images/ui/logo_icon.png"))
        self.arrow_icon = (QPixmap("src/images/ui/back_black.png"), QPixmap("src/images/ui/back_white.png"))
        self.forward_icon = (QPixmap("src/images/ui/forward_black.png"), QPixmap("src/images/ui/forward_white.png"))
        self.plus_icon = (QPixmap("src/images/ui/plus_black.png"), QPixmap("src/images/ui/plus_white.png"))
        self.minus_icon = (QPixmap("src/images/ui/minus_black.png"), QPixmap("src/images/ui/minus_white.png"))
        self.info_icon = (QPixmap("src/images/ui/info_black.png"), QPixmap("src/images/ui/info_white.png"))
        self.github_icon = (QPixmap("src/images/links/github_icon_dark.png"), QPixmap("src/images/links/github_icon_light.png"))
        self.ltcg_icon = (QPixmap("src/images/links/ltcg_icon_dark.png"), QPixmap("src/images/links/ltcg_icon_light.png"))
        self.pz_icon = (QPixmap("src/images/links/pz_icon_dark.png"), QPixmap("src/images/links/pz_icon_light.png"))
        self.serebii_icon = (QPixmap("src/images/links/serebii_icon_dark.png"), QPixmap("src/images/links/serebii_icon_light.png"))
        self.export_icon = (QPixmap("src/images/ui/export_black.png"), QPixmap("src/images/ui/export_white.png"))
        self.import_icon = (QPixmap("src/images/ui/import_black.png"), QPixmap("src/images/ui/import_white.png"))
        self.shadow_add_icon = (QPixmap("src/images/ui/shadow_add_black.png"), QPixmap("src/images/ui/shadow_add_white.png"))
        self.shadow_minus_icon = (QPixmap("src/images/ui/shadow_minus_black.png"), QPixmap("src/images/ui/shadow_minus_white.png"))
        self.refresh_icon = (QPixmap("src/images/ui/refresh_black.png"), QPixmap("src/images/ui/refresh_white.png"))
        self.favorite_icon = (QPixmap("src/images/ui/heart_black.png"), QPixmap("src/images/ui/heart_white.png"), QPixmap("src/images/ui/heart_active.png"))
        self.heart_button_icon = (QPixmap("src/images/ui/heart_button_black.png"), QPixmap("src/images/ui/heart_button_white.png"))
        self.f_tag = (QPixmap("src/images/tags/favorites_black.png"), QPixmap("src/images/tags/favorites_black.png"))
        self.ability_icon = QPixmap("src/images/card_data/ability_logo.png")
        self.paint_icon = (QPixmap("src/images/card_data/paint_black.png"), QPixmap("src/images/card_data/paint_white.png"))
        self.exit_icon = (QPixmap("src/images/ui/exit_black.png"), QPixmap("src/images/ui/exit_white.png"))
        self.pokeball_icon = (QPixmap("src/images/rarities/TCG/none_black.png"), QPixmap("src/images/rarities/TCG/none_white.png"))
        self.ex_icon = f"src/images/card_data/ex_icon.png"
        
        self.gx_icon = f"src/images/name_icons/gx_icon.png"
        self.gx_tag_team_icon = "src/images/name_icons/gx_tag_team_icon.png"
        self.tera_icon = QPixmap(f"src/images/card_data/tera_icon.png")
       
        self.star_icon = f"src/images/name_icons/star_logo.png"
      
        self.dice_icon = (QPixmap(f"src/images/ui/dice_black.png"), QPixmap(f"src/images/ui/dice_white.png"))

        self.trait_dict = {
            "\u03b1": QPixmap("src/images/card_data/traits/alpha_icon.png"),
            "\u03a9": QPixmap("src/images/card_data/traits/omega_icon.png"),
            "\u0394": QPixmap("src/images/card_data/traits/delta_icon.png"),
            "\u03b8": QPixmap("src/images/card_data/traits/theta_icon.png"),
        }

        

        self.tag_dict  = {
            "-EX": "src/images/name_icons/ex_legacy.png",
            "BREAK": "src/images/name_icons/break.png",
            "V": "src/images/name_icons/v_icon.png",
            "VMAX": "src/images/name_icons/v_max_icon.png",
            "VSTAR": "src/images/name_icons/v_star_icon.png",
            "V-UNION": "src/images/name_icons/v-union_icon.png",
            "LV.X": "src/images/name_icons/lv_x_logo.png",
            "LEGEND": "src/images/name_icons/legend.png",
            "\u2662": "src/images/name_icons/prism_star.png"
        }


        self.ex_dict = {
            "Mega Evolution": "src/images/name_icons/ex_sv.png",
            "Scarlet & Violet": "src/images/name_icons/ex_sv.png",
            "XY": "src/images/name_icons/ex_legacy.png",
            "Black & White": "src/images/name_icons/ex_legacy.png",
            "Mega Pokemon": "src/images/name_icons/ex_sv_mega.png"
        }

        self.counter_icon_dict = {
            4: (QPixmap("src/images/ui/counter_4_black.png"), QPixmap("src/images/ui/counter_4_white.png")),
            6: (QPixmap("src/images/ui/counter_6_black.png"), QPixmap("src/images/ui/counter_6_white.png")),
            8: (QPixmap("src/images/ui/counter_8_black.png"), QPixmap("src/images/ui/counter_8_white.png")),
        }

        self.logo_dict = {}

        self.card_type_dict = {
            "Basic": QPixmap("src/images/card_data/stages/basic_logo.png"),
            "Stage 1": QPixmap("src/images/card_data/stages/stage1_logo.png"),
            "Stage 2": QPixmap("src/images/card_data/stages/stage2_logo.png"),
            "Supporter": QPixmap("src/images/card_data/stages/supporter_logo.png"),
            "Item": QPixmap("src/images/card_data/stages/item_logo.png"),
            "Tool": QPixmap("src/images/card_data/stages/tool_logo.png"),
            "Stadium": QPixmap("src/images/card_data/stages/stadium_logo.png"),
            "VMAX": QPixmap("src/images/card_data/stages/vmax_logo.png"),
            "VSTAR": QPixmap("src/images/card_data/stages/vstar_logo.png"),
            "V-UNION": QPixmap("src/images/card_data/stages/v-union_logo.png"),
            "Basic Energy": QPixmap("src/images/card_data/stages/energy_logo.png"),
            "Special Energy": QPixmap("src/images/card_data/stages/special_energy_logo.png"),
            "BREAK Evolution": QPixmap("src/images/card_data/stages/break_logo.png"),
            "Mega Evolution": QPixmap("src/images/card_data/stages/mega_logo.png"),
            "Level Up": QPixmap("src/images/card_data/stages/level_up_logo.png"),
            "Item/Technical Machine": QPixmap("src/images/card_data/stages/tm_logo.png"),
            "LEGEND": QPixmap("src/images/card_data/stages/legend_logo.png")
        }

        self.type_dict = {
            "Colorless": QPixmap("src/images/card_data/energy/energy_colorless.png"),
            "Grass": QPixmap("src/images/card_data/energy/energy_grass.png"),
            "Fire": QPixmap("src/images/card_data/energy/energy_fire.png"),
            "Water": QPixmap("src/images/card_data/energy/energy_water.png"),
            "Lightning": QPixmap("src/images/card_data/energy/energy_lightning.png"),
            "Psychic": QPixmap("src/images/card_data/energy/energy_psychic.png"),
            "Fighting": QPixmap("src/images/card_data/energy/energy_fighting.png"),
            "Darkness": QPixmap("src/images/card_data/energy/energy_darkness.png"),
            "Metal": QPixmap("src/images/card_data/energy/energy_metal.png"),
            "Dragon": QPixmap("src/images/card_data/energy/energy_dragon.png"),
            "Fairy": QPixmap("src/images/card_data/energy/energy_fairy.png"),
        }


        self.energy_dict = {
            "C": "src/images/card_data/energy/energy_colorless.png",
            "G": "src/images/card_data/energy/energy_grass.png",
            "R": "src/images/card_data/energy/energy_fire.png",
            "W": "src/images/card_data/energy/energy_water.png",
            "L": "src/images/card_data/energy/energy_lightning.png",
            "P": "src/images/card_data/energy/energy_psychic.png",
            "F": "src/images/card_data/energy/energy_fighting.png",
            "D": "src/images/card_data/energy/energy_darkness.png",
            "M": "src/images/card_data/energy/energy_metal.png",
            "DR": "src/images/card_data/energy/energy_dragon.png",
            "N": "src/images/card_data/energy/energy_dragon.png",
            "Y": "src/images/card_data/energy/energy_fairy.png",
            "0": "src/images/card_data/energy/no_energy.png",
            "+": ("src/images/card_data/energy/plus_icon_black.png", "src/images/card_data/energy/plus_icon_white.png")
        }

        self.card_desc_dict = {
            "Item": "You may play any number of item cards during your turn.",
            "Supporter": "You may play only 1 Supporter card during your turn.",
            "Tool": "You use Pok\u00e9mon Tools by attaching them to your Pok\u00e9mon. You may only attach 1 Pok\u00e9mon Tool to each Pok\u00e9mon, and it stays attached.",
            "Stadium": "You may play only 1 Stadium card during your turn. Put it next to the Active Spot, and discard it if another Stadium comes into play. A Stadium with the same name can't be played."

        }



R_manager = QNetworkRequest

class ImageLabel(QLabel):
    download_finished = pyqtSignal()
    
    def __init__(self, url, card_id, fp, cache=False, size=QSize(241, 337), network_manager: QNetworkAccessManager | None = None):
        super().__init__()
        self.card_id = card_id
        self.filepath = fp
        self.cache = cache
        
        self.target_size = size
        self.setFixedSize(size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._reply: QNetworkReply | None = None

        self.fp = f"{self.filepath}\\{self.card_id}.png"

        if cache:
            if network_manager is None:
                raise ValueError("network_manager is required when cache=True")

            request = R_manager(QUrl(url))
            self._reply = network_manager.get(request)
           

            self._reply.errorOccurred.connect(partial(self.handle_error, url)) # type: ignore

            self._reply.finished.connect(self.image_loaded) # type: ignore
        else:
            self.grab_local()

    def handle_error(self, url, error):
        print(f"Network error: {error} | at {url}")
        if self._reply and not sip.isdeleted(self._reply):
            self._reply.deleteLater()
        self._reply = None
        self.download_finished.emit()
            

    def image_loaded(self):
        reply = self.sender()
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
        
        scaled.save(self.fp, "PNG")

        if not sip.isdeleted(reply):
            reply.deleteLater() # type: ignore
        self._reply = None

        self.download_finished.emit()

    def grab_local(self):

        pixmap = QPixmap(self.fp)
        scaled = pixmap.scaled(
            self.target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)
    
    
