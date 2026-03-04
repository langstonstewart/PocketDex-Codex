from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QUrl, QSize, pyqtSignal
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6 import sip


class ImageManager:

    def __init__(self):
        
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
        self.ex_icon = QPixmap("src/images/card_data/ex_icon.png")
        self.ability_icon = QPixmap("src/images/card_data/ability_logo.png")
        self.paint_icon = (QPixmap("src/images/card_data/paint_black.png"), QPixmap("src/images/card_data/paint_white.png"))
        self.exit_icon = (QPixmap("src/images/ui/exit_black.png"), QPixmap("src/images/ui/exit_white.png"))

        self.counter_icon_dict = {
            4: (QPixmap("src/images/ui/counter_4_black.png"), QPixmap("src/images/ui/counter_4_white.png")),
            6: (QPixmap("src/images/ui/counter_6_black.png"), QPixmap("src/images/ui/counter_6_white.png")),
            8: (QPixmap("src/images/ui/counter_8_black.png"), QPixmap("src/images/ui/counter_8_white.png")),
        }


        self.logo_dict = {
            "A1": (QPixmap("src/images/set_logo/geneticapex.png"), QPixmap("src/images/tags/A1_black.png")),
            "P-A": (QPixmap("src/images/set_logo/promo-a.png"), QPixmap("src/images/tags/P-A_black.png")),
            "P-B": (QPixmap("src/images/set_logo/promo-b.png"), QPixmap("src/images/tags/P-B_black.png")),
            "A1a": (QPixmap("src/images/set_logo/mythicalisland.png"), QPixmap("src/images/tags/A1a_black.png")),
            "A2": (QPixmap("src/images/set_logo/space-timesmackdown.png"), QPixmap("src/images/tags/A2_black.png")),
            "A2a": (QPixmap("src/images/set_logo/triumphantlight.png"), QPixmap("src/images/tags/A2a_black.png")),
            "A2b": (QPixmap("src/images/set_logo/shiningrevelry.png"), QPixmap("src/images/tags/A2b_black.png")),
            "A3": (QPixmap("src/images/set_logo/celestialguardians.png"), QPixmap("src/images/tags/A3_black.png")),
            "A3a": (QPixmap("src/images/set_logo/extradimensionalcrisis.png"), QPixmap("src/images/tags/A3a_black.png")),
            "A3b": (QPixmap("src/images/set_logo/eeveegrove.png"), QPixmap("src/images/tags/A3b_black.png")),
            "A4": (QPixmap("src/images/set_logo/wisdomofseaandsky.png"), QPixmap("src/images/tags/A4_black.png")),
            "A4a": (QPixmap("src/images/set_logo/secludedsprings.png"), QPixmap("src/images/tags/A4a_black.png")),
            "A4b": (QPixmap("src/images/set_logo/deluxepackex.png"), QPixmap("src/images/tags/A4b_black.png")),
            "B1": (QPixmap("src/images/set_logo/megarising.png"), QPixmap("src/images/tags/B1_black.png")),
            "B1a": (QPixmap("src/images/set_logo/crimsonblaze.png"), QPixmap("src/images/tags/B1a_black.png")),
            "B2": (QPixmap("src/images/set_logo/fantasticalparade.png"), QPixmap("src/images/tags/B2_black.png")),
            "B2a": (QPixmap("src/images/set_logo/paldeanwonders.png"), QPixmap("src/images/tags/B2a_black.png")),
            
        }

        self.rarity_dict = {
            "1 Diamond": QPixmap("src/images/rarities/diamond1.png"),
            "2 Diamond": QPixmap("src/images/rarities/diamond2.png"),
            "3 Diamond": QPixmap("src/images/rarities/diamond3.png"),
            "4 Diamond": QPixmap("src/images/rarities/diamond4.png"),
            "1 Star": QPixmap("src/images/rarities/star1.png"),
            "2 Star": QPixmap("src/images/rarities/star2.png"),
            "3 Star": QPixmap("src/images/rarities/star3.png"),
            "1 Shiny": QPixmap("src/images/rarities/shiny1.png"),
            "2 Shiny": QPixmap("src/images/rarities/shiny2.png"),
            "Crown": QPixmap("src/images/rarities/crown.png"),
            "None": (QPixmap("src/images/rarities/none_black.png"), QPixmap("src/images/rarities/none_white.png"))
        }

        self.card_type_dict = {
            "Basic": QPixmap("src/images/card_data/basic_logo.png"),
            "Stage 1": QPixmap("src/images/card_data/stage1_logo.png"),
            "Stage 2": QPixmap("src/images/card_data/stage2_logo.png"),
            "Supporter": QPixmap("src/images/card_data/supporter_logo.png"),
            "Item": QPixmap("src/images/card_data/item_logo.png"),
            "Tool": QPixmap("src/images/card_data/tool_logo.png"),
            "Stadium": QPixmap("src/images/card_data/stadium_logo.png"),
        }

        self.type_dict = {
            "Colorless": QPixmap("src/images/card_data/energy_colorless.png"),
            "Grass": QPixmap("src/images/card_data/energy_grass.png"),
            "Fire": QPixmap("src/images/card_data/energy_fire.png"),
            "Water": QPixmap("src/images/card_data/energy_water.png"),
            "Lightning": QPixmap("src/images/card_data/energy_lightning.png"),
            "Psychic": QPixmap("src/images/card_data/energy_psychic.png"),
            "Fighting": QPixmap("src/images/card_data/energy_fighting.png"),
            "Darkness": QPixmap("src/images/card_data/energy_darkness.png"),
            "Metal": QPixmap("src/images/card_data/energy_metal.png"),
            "Dragon": QPixmap("src/images/card_data/energy_dragon.png")
        }


        self.energy_dict = {
            "C": "src/images/card_data/energy_colorless.png",
            "G": "src/images/card_data/energy_grass.png",
            "R": "src/images/card_data/energy_fire.png",
            "W": "src/images/card_data/energy_water.png",
            "L": "src/images/card_data/energy_lightning.png",
            "P": "src/images/card_data/energy_psychic.png",
            "F": "src/images/card_data/energy_fighting.png",
            "D": "src/images/card_data/energy_darkness.png",
            "M": "src/images/card_data/energy_metal.png",
            "DR": "src/images/card_data/energy_dragon.png",
            "0": "src/images/card_data/no_energy.png"
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

            self._reply.errorOccurred.connect(lambda e: print("Network error:", e)) # type: ignore

            self._reply.finished.connect(self.image_loaded) # type: ignore
        else:
            self.grab_local()
            

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
    
