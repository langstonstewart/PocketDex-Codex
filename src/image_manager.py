from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QUrl, QSize
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest


class ImageManager:

    def __init__(self):

        self.theme_icon = (QPixmap("src/images/ui/sun.png"), QPixmap("src/images/ui/moon.png"))
        self.codex_icon = (QPixmap("src/images/ui/codex.png"), QPixmap("src/images/ui/codex.png"))
        self.codex_icon_mini = (QPixmap("src/images/ui/logo_icon.png"), QPixmap("src/images/ui/logo_icon.png"))
        self.arrow_icon = (QPixmap("src/images/ui/back_black.png"), QPixmap("src/images/ui/back_white.png"))
        self.plus_icon = (QPixmap("src/images/ui/plus_black.png"), QPixmap("src/images/ui/plus_white.png"))
        self.minus_icon = (QPixmap("src/images/ui/minus_black.png"), QPixmap("src/images/ui/minus_white.png"))
        self.info_icon = (QPixmap("src/images/ui/info_black.png"), QPixmap("src/images/ui/info_white.png"))
        self.github_icon = (QPixmap("src/images/links/github_icon_dark.png"), QPixmap("src/images/links/github_icon_light.png"))
        self.ltcg_icon = (QPixmap("src/images/links/ltcg_icon_dark.png"), QPixmap("src/images/links/ltcg_icon_light.png"))
        self.pz_icon = (QPixmap("src/images/links/pz_icon_dark.png"), QPixmap("src/images/links/pz_icon_light.png"))
        self.serebii_icon = (QPixmap("src/images/links/serebii_icon_dark.png"), QPixmap("src/images/links/serebii_icon_light.png"))


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
            "Crown": QPixmap("src/images/rarities/crown.png")
        }


IM_manager = QNetworkAccessManager()
R_manager = QNetworkRequest

class ImageLabel(QLabel):
    
    def __init__(self, url, card_id, fp, cache=False, size=QSize(245, 337)):
        super().__init__()
        self.card_id = card_id
        self.filepath = fp
        self.cache = cache
        
        self.target_size = size
        self.setFixedSize(size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.fp = f"{self.filepath}\\{self.card_id}.png"

        if cache:
            request = R_manager(QUrl(url))
            self.reply = IM_manager.get(request)

            self.reply.finished.connect(self.image_loaded) # type: ignore
        else:
            self.grab_local()
            

    def image_loaded(self):
        
        pixmap = QPixmap()
        pixmap.loadFromData(self.reply.readAll()) # type: ignore
        scaled = pixmap.scaled(
            self.target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)
        scaled.save(self.fp, "PNG")
    
        self.reply.deleteLater() # type: ignore

    def grab_local(self):

        # print(f"pulling from local files.. {self.fp}")
        pixmap = QPixmap(self.fp)
        scaled = pixmap.scaled(
            self.target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)
    