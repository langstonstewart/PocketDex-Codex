import os
from PyQt6.QtCore import Qt, QObject
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
        self.pc_icon = (QPixmap(self.img("src/images/links/pkmn_cards_icon_dark.png")), QPixmap(self.img("src/images/links/pkmn_cards_icon_light.png")))
        self.export_icon = (QPixmap(self.img("src/images/ui/export_black.png")), QPixmap(self.img("src/images/ui/export_white.png")))
        self.import_icon = (QPixmap(self.img("src/images/ui/import_black.png")), QPixmap(self.img("src/images/ui/import_white.png")))
        self.shadow_add_icon = (QPixmap(self.img("src/images/ui/shadow_add_black.png")), QPixmap(self.img("src/images/ui/shadow_add_white.png")))
        self.shadow_minus_icon = (QPixmap(self.img("src/images/ui/shadow_minus_black.png")), QPixmap(self.img("src/images/ui/shadow_minus_white.png")))
        self.refresh_icon = (QPixmap(self.img("src/images/ui/refresh_black.png")), QPixmap(self.img("src/images/ui/refresh_white.png")))
        self.favorite_icon = (QPixmap(self.img("src/images/ui/heart_black.png")), QPixmap(self.img("src/images/ui/heart_white.png")), QPixmap(self.img("src/images/ui/heart_active.png")))
        self.heart_button_icon = (QPixmap(self.img("src/images/ui/heart_button_black.png")), QPixmap(self.img("src/images/ui/heart_button_white.png")))
        self.star_outline_icon = (self.img("src/images/ui/star_outline_dark.png"), self.img("src/images/ui/star_outline_light.png"))
        self.star_full_icon = (self.img("src/images/ui/star_full_dark.png"), self.img("src/images/ui/star_full_light.png"))
        self.f_tag = (QPixmap(self.img("src/images/tags/favorites_black.png")), QPixmap(self.img("src/images/tags/favorites_black.png")))
        self.paint_icon = (QPixmap(self.img("src/images/card_data/paint_black.png")), QPixmap(self.img("src/images/card_data/paint_white.png")))
        self.exit_icon = (QPixmap(self.img("src/images/ui/exit_black.png")), QPixmap(self.img("src/images/ui/exit_white.png")))
        self.pokeball_icon = (QPixmap(self.img("src/images/rarities/TCG/no_rarity_black.png")), QPixmap(self.img("src/images/rarities/TCG/no_rarity_white.png")))
        self.ex_icon = self.img("src/images/name_icons/ex_icon.png")
        self.tcgplayer_icon = (QPixmap(self.img("src/images/links/tcgplayer_icon_dark.png")), QPixmap(self.img("src/images/links/tcgplayer_icon_light.png")))
        self.cm_icon = (QPixmap(self.img("src/images/links/cardmarket_icon_dark.png")), QPixmap(self.img("src/images/links/cardmarket_icon_light.png")))

        self.pkdb_icon = (QPixmap(self.img("src/images/links/pkdb_icon_dark.png")), QPixmap(self.img("src/images/links/pkdb_icon_light.png")))

        self.d_art_icon = (QPixmap(self.img("src/images/links/d_art_icon_dark.png")), QPixmap(self.img("src/images/links/d_art_icon_light.png")))

        self.height_icon = (self.img("src/images/dex_type_icons/height_icon_dark.png"), self.img("src/images/dex_type_icons/height_icon_light.png"))
        self.weight_icon = (self.img("src/images/dex_type_icons/weight_icon_dark.png"), self.img("src/images/dex_type_icons/weight_icon_light.png"))
        self.entry_icon = (self.img("src/images/dex_type_icons/entry_icon_dark.png"), self.img("src/images/dex_type_icons/entry_icon_light.png"))

        self.sound_icon = (self.img("src/images/ui/sound_icon_dark.png"), self.img("src/images/ui/sound_icon_light.png"))

        self.arrow_up_icon = (QPixmap(self.img("src/images/ui/arrow_up_dark.png")), QPixmap(self.img("src/images/ui/arrow_up_light.png")))

        self.arrow_down_icon = (QPixmap(self.img("src/images/ui/arrow_down_dark.png")), QPixmap(self.img("src/images/ui/arrow_down_light.png")))

        self.dex_icon = (QPixmap(self.img("src/images/ui/pokedex_dark.png")), QPixmap(self.img("src/images/ui/pokedex_light.png")))
        
        self.gx_icon = self.img("src/images/name_icons/gx_icon.png")
        self.gx_tag_team_icon = self.img("src/images/name_icons/gx_tag_team_icon.png")
        self.tera_icon = QPixmap(self.img("src/images/card_data/tera_icon.png"))

        self.vstar_banner = QPixmap(self.img("src/images/name_icons/txt_tags/vstar_banner.png"))

        self.star_icon = self.img("src/images/name_icons/star_logo.png")
      
        self.dice_icon = (QPixmap(self.img("src/images/ui/dice_black.png")), QPixmap(self.img("src/images/ui/dice_white.png")))

        self.sort_icon = (QPixmap(self.img("src/images/ui/sort_black.png")), QPixmap(self.img("src/images/ui/sort_white.png")))

        self.trait_dict = {
            "\u03b1": QPixmap(self.img("src/images/card_data/traits/alpha_icon.png")),
            "\u03a9": QPixmap(self.img("src/images/card_data/traits/omega_icon.png")),
            "\u0394": QPixmap(self.img("src/images/card_data/traits/delta_icon.png")),
            "Delta": QPixmap(self.img("src/images/card_data/traits/delta_icon.png")),
            "\u03b8": QPixmap(self.img("src/images/card_data/traits/theta_icon.png")),
        }

        self.rarity_dict = {"TCG": [
                                            "Double Rare", # done
                                            "Common", # done
                                            "Rare", # done
                                            "Uncommon", # done
                                            "ACE SPEC Rare", # done
                                            "Illustration Rare", # done
                                            "Ultra Rare", # done
                                            "Special Illustration Rare", # done
                                            "Hyper Rare", # done
                                            "Shiny Rare", # done
                                            "Shiny Ultra Rare", # done
                                            "Promo", # done
                                            "Holo Rare V", # done
                                            "Holo Rare VSTAR", # done
                                            "Rare Holo", # done
                                            "Radiant Rare", # done
                                            "Holo Rare VMAX", # done
                                            "Rare Secret", # done
                                            "Trainer Gallery Holo Rare", # done
                                            "Trainer Gallery Holo Rare V", # done
                                            "Trainer Gallery Ultra Rare", # done
                                            "Trainer Gallery Secret Rare", # done
                                            "Rainbow Rare", # done
                                            "Trainer Gallery Holo Rare V or VMAX", # done
                                            "Special Full Art", # done
                                            "Amazing Rare", # done
                                            "Shiny Rare V or VMAX", # done
                                            "Rare Holo GX", # done
                                            "Rare Prism Star", # done
                                            "Rare Shiny GX", # done
                                            "Rare Shining", # done
                                            "Rare Holo EX", # done
                                            "Rare BREAK", # done
                                            "Rare Prime", # done
                                            "LEGEND", # done
                                            "Mega Hyper Rare", # done
                                            "Mega Attack Rare", # done
                                            "Black White Rare", #done
                                            "Rare Holo LV.X", #
                                            "Rare Holo ex", # done
                                            "Rare Holo Star" # done
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
        
        self.pokemon_rule_list = ['Mega-ex-Rule', 
                                'Mega-Evolution-Rule',
                                'ex-Rule',
                                'Ex-Rule',
                                'Tera-Rule',
                                'BREAK-Rule',
                                'V-Rule', 
                                'VSTAR-Rule',
                                'VMAX-Rule',
                                'V-UNION-Rule', 
                                'TAG-TEAM-Rule',
                                'GX-Rule', 
                                'Prism-Star-Rule', 
                                'Baby-Rule',
                                'Primal-Reversion-Rule',
                                'Dual-LEGEND-Rule', 
                                'LEGEND-Rule', 
                                'Level-Up-Rule', 
                                'Star-Rule', 
                                'Dual-Type-Rule']
        
        self.trainer_rule_list = ['Item-Rule', 
                                'Supporter-Rule',
                                'Tool-Rule',
                                'Tool-F-Rule',
                                'Stadium-Rule']
        
        self.region_dict = {'Kanto': (0, 151),
                            'Johto': (151, 251),
                            'Hoenn': (251, 386),
                            'Sinnoh': (386, 493),
                            'Unova': (493, 649),
                            'Kalos': (649, 721),
                            'Alola': (721, 809),
                            'Galar': (809, 905),
                            'Paldea': (905, 1025)}
        
        self.scrub_list = [
                            "Mega ",
                           "Origin Forme ",
                           "Paldean ",
                           "Hisuian ",
                           "Galarian ",
                           "Alolan ",
                           "Dusk Mane ",
                           "Dawn Wings ",
                           "White ",
                           "Black ",
                           "Fan ",
                           "Wash ",
                           "Mow ",
                           "Heat ",
                           "Frost ",
                           "Erika’s ",
                           "Blaine’s ",
                           "Brock’s ",
                           "Lt. Surge’s ",
                           "Misty’s ",
                           "Sabrina’s ",
                           "N’s ",
                           "Lillie’s ",
                           "Iono’s ",
                           "Larry’s ",
                           "Marnie’s ",
                           "Cynthia’s ",
                           "Team Rocket’s ",
                           "Steven’s ",
                           "Hop’s ",
                           "Ethan’s ",
                           "Arven’s ",
                           "Ash’s ",
                           "Imakuni?’s ",
                           "Team Magma’s ",
                           "Team Aqua’s ",
                           "Holon’s ",
                           "Rocket’s ",
                           "Koga’s ",
                           "Giovanni’s ",
                           "Dark ",
                           "Flying ",
                           "Surfing",
                           "Shining ",
                           " E4",
                           " GL",
                           " Normal Forme",
                           " Attack Forme",
                           " Defense Forme",
                           " Speed Forme",
                           " Rain Form",
                           " Snow-Cloud Form",
                           "Sunny Form",
                           " ex"
                           ]

        self.tag_dict  = {
            "-EX": self.img("src/images/name_icons/ex_legacy.png"),
            "BREAK": self.img("src/images/name_icons/break.png"),
            "V": self.img("src/images/name_icons/v_icon.png"),
            "VMAX": self.img("src/images/name_icons/v_max_icon.png"),
            "VSTAR": self.img("src/images/name_icons/v_star_icon.png"),
            "V-UNION": self.img("src/images/name_icons/v-union_icon.png"),
            "LV.X": self.img("src/images/name_icons/lv_x_logo.png"),
            "LEGEND": self.img("src/images/name_icons/legend.png"),
            "Prism Star": self.img("src/images/name_icons/prism_star.png"),
            "GX": self.img("src/images/name_icons/gx_icon.png"),
            "GX-TAG-TEAM": self.img("src/images/name_icons/gx_tag_team_icon.png"),
            "GX-UB": self.img("src/images/name_icons/gx_ub_icon.png"),
            "GX-UB-TAG-TEAM": self.img("src/images/name_icons/gx_ub_tag_team_icon.png")
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
            "Goldenrod Game Corner": QPixmap(self.img("src/images/card_data/stages/ggc_logo.png")),
            "Rocket's Secret Machine": QPixmap(self.img("src/images/card_data/stages/rsm_logo.png")),
            "Restored": QPixmap(self.img("src/images/card_data/stages/restored_logo.png")),
            "Basic": QPixmap(self.img("src/images/card_data/stages/basic_logo.png")),
            "Baby": QPixmap(self.img("src/images/card_data/stages/baby_logo.png")),
            "Stage 1": QPixmap(self.img("src/images/card_data/stages/stage1_logo.png")),
            "Stage 2": QPixmap(self.img("src/images/card_data/stages/stage2_logo.png")),
            "Supporter": QPixmap(self.img("src/images/card_data/stages/supporter_logo.png")),
            "Item": QPixmap(self.img("src/images/card_data/stages/item_logo.png")),
            "Tool": QPixmap(self.img("src/images/card_data/stages/tool_logo.png")),
            "Tool F": QPixmap(self.img("src/images/card_data/stages/tool_f_logo.png")),
            "Stadium": QPixmap(self.img("src/images/card_data/stages/stadium_logo.png")),
            "VMAX": QPixmap(self.img("src/images/card_data/stages/vmax_logo.png")),
            "VSTAR": QPixmap(self.img("src/images/card_data/stages/vstar_logo.png")),
            "V-UNION": QPixmap(self.img("src/images/card_data/stages/v-union_logo.png")),
            "Basic Energy": QPixmap(self.img("src/images/card_data/stages/energy_logo.png")),
            "Special Energy": QPixmap(self.img("src/images/card_data/stages/special_energy_logo.png")),
            "BREAK": QPixmap(self.img("src/images/card_data/stages/break_logo.png")),
            "Mega": QPixmap(self.img("src/images/card_data/stages/mega_logo.png")),
            "Level-Up": QPixmap(self.img("src/images/card_data/stages/level_up_logo.png")),
            "Technical Machine": QPixmap(self.img("src/images/card_data/stages/tm_logo.png")),
            "LEGEND": QPixmap(self.img("src/images/card_data/stages/legend_logo.png"))
        }

        self.ability_img_dict = {
            "Ability":  QPixmap(self.img("src/images/card_data/abilities/ability_banner.png")),
            "Poké-POWER":  QPixmap(self.img("src/images/card_data/abilities/pp_banner.png")),
            "Poké-BODY":  QPixmap(self.img("src/images/card_data/abilities/pb_banner.png")),
           

        }

        self.type_dict = {
            "Colorless": self.img("src/images/card_data/energy/energy_colorless.png"),
            "Grass": self.img("src/images/card_data/energy/energy_grass.png"),
            "Fire": self.img("src/images/card_data/energy/energy_fire.png"),
            "Water": self.img("src/images/card_data/energy/energy_water.png"),
            "Lightning": self.img("src/images/card_data/energy/energy_lightning.png"),
            "Psychic": self.img("src/images/card_data/energy/energy_psychic.png"),
            "Fighting": self.img("src/images/card_data/energy/energy_fighting.png"),
            "Darkness": self.img("src/images/card_data/energy/energy_darkness.png"),
            "Metal": self.img("src/images/card_data/energy/energy_metal.png"),
            "Dragon": self.img("src/images/card_data/energy/energy_dragon.png"),
            "Fairy": self.img("src/images/card_data/energy/energy_fairy.png"),
        }

        self.dex_type_dict = {
            "Bug": self.img("src/images/dex_type_icons/bug_icon_sv.png"),
            "Dark": self.img("src/images/dex_type_icons/dark_icon_sv.png"),
            "Dragon": self.img("src/images/dex_type_icons/dragon_icon_sv.png"),
            "Electric": self.img("src/images/dex_type_icons/electric_icon_sv.png"),
            "Fairy": self.img("src/images/dex_type_icons/fairy_icon_sv.png"),
            "Fighting": self.img("src/images/dex_type_icons/fighting_icon_sv.png"),
            "Fire": self.img("src/images/dex_type_icons/fire_icon_sv.png"),
            "Flying": self.img("src/images/dex_type_icons/flying_icon_sv.png"),
            "Ghost": self.img("src/images/dex_type_icons/ghost_icon_sv.png"),
            "Grass": self.img("src/images/dex_type_icons/grass_icon_sv.png"),
            "Ground": self.img("src/images/dex_type_icons/ground_icon_sv.png"),
            "Ice": self.img("src/images/dex_type_icons/ice_icon_sv.png"),
            "Normal": self.img("src/images/dex_type_icons/normal_icon_sv.png"),
            "Poison": self.img("src/images/dex_type_icons/poison_icon_sv.png"),
            "Psychic": self.img("src/images/dex_type_icons/psychic_icon_sv.png"),
            "Rock": self.img("src/images/dex_type_icons/rock_icon_sv.png"),
            "Steel": self.img("src/images/dex_type_icons/steel_icon_sv.png"),
            "Water": self.img("src/images/dex_type_icons/water_icon_sv.png")

        }

        self.gender_dict = {
            "Male": self.img("src/images/dex_type_icons/gender_male.png"),
            "Female": self.img("src/images/dex_type_icons/gender_female.png"),
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

        self.txt_tag_dict = {
            "Pokémon-GX": (self.img("src/images/name_icons/txt_tags/gx_txt_black.png"), self.img("src/images/name_icons/txt_tags/gx_txt_white.png"), '46', '17'),
            "-GX": (self.img("src/images/name_icons/txt_tags/gx_txt_black.png"), self.img("src/images/name_icons/txt_tags/gx_txt_white.png"), '46', '17'),
            "GX": (self.img("src/images/name_icons/txt_tags/gx_txt_black.png"), self.img("src/images/name_icons/txt_tags/gx_txt_white.png"), '46', '17'),
            "TAG TEAM": (self.img("src/images/name_icons/txt_tags/tag_team_black.png"), self.img("src/images/name_icons/txt_tags/tag_team_white.png"), '141', '17'),
            "[*]": (self.img("src/images/name_icons/txt_tags/prism_star_black.png"), self.img("src/images/name_icons/txt_tags/prism_star_white.png"), '12', '17'), # Prism Star
            "Pokémon-EX": (self.img("src/images/name_icons/txt_tags/ex_legacy_black.png"), self.img("src/images/name_icons/txt_tags/ex_legacy_white.png"), '45', '17'),
            "Pokémon ex": (self.img("src/images/name_icons/txt_tags/ex_black.png"), self.img("src/images/name_icons/txt_tags/ex_white.png"), '37', '17'),
            "Pokémon VMAX": (self.img("src/images/name_icons/txt_tags/vmax_black.png"), self.img("src/images/name_icons/txt_tags/vmax_white.png"), '63', '17'),
            "Pokémon VSTAR": (self.img("src/images/name_icons/txt_tags/vstar_black.png"), self.img("src/images/name_icons/txt_tags/vstar_white.png"), '58', '17'),
            "Pokémon V-UNION": (self.img("src/images/name_icons/txt_tags/v-union_black.png"), self.img("src/images/name_icons/txt_tags/v-union_white.png"), '88', '34'),
            "Pokémon V": (self.img("src/images/name_icons/txt_tags/v_black.png"), self.img("src/images/name_icons/txt_tags/v_white.png"), '15', '17'),
            "LV.X": (self.img("src/images/name_icons/txt_tags/lv.x_black.png"), self.img("src/images/name_icons/txt_tags/lv.x_white.png"), '60', '34'),
            "Pokémon Star": (self.img("src/images/name_icons/txt_tags/star_black.png"), self.img("src/images/name_icons/txt_tags/star_white.png"), '26', '17'),
            "LEGEND": (self.img("src/images/name_icons/txt_tags/legend_black.png"), self.img("src/images/name_icons/txt_tags/legend_white.png"), '103', '34'),
            "BREAK": (self.img("src/images/name_icons/txt_tags/break_black.png"), self.img("src/images/name_icons/txt_tags/break_white.png"), '72', '17'),
        }

        self.txt_tag_energy_dict = {
            "[C]": (self.img("src/images/name_icons/txt_tags/energy/colorless_black.png"), self.img("src/images/name_icons/txt_tags/energy/colorless_white.png")),
            "[G]": (self.img("src/images/name_icons/txt_tags/energy/grass_black.png"), self.img("src/images/name_icons/txt_tags/energy/grass_white.png")),
            "[R]": (self.img("src/images/name_icons/txt_tags/energy/fire_black.png"), self.img("src/images/name_icons/txt_tags/energy/fire_white.png")),
            "[W]": (self.img("src/images/name_icons/txt_tags/energy/water_black.png"), self.img("src/images/name_icons/txt_tags/energy/water_white.png")),
            "[L]": (self.img("src/images/name_icons/txt_tags/energy/lightning_black.png"), self.img("src/images/name_icons/txt_tags/energy/lightning_white.png")),
            "[P]": (self.img("src/images/name_icons/txt_tags/energy/psychic_black.png"), self.img("src/images/name_icons/txt_tags/energy/psychic_white.png")),
            "[F]": (self.img("src/images/name_icons/txt_tags/energy/fighting_black.png"), self.img("src/images/name_icons/txt_tags/energy/fighting_white.png")),
            "[D]": (self.img("src/images/name_icons/txt_tags/energy/darkness_black.png"), self.img("src/images/name_icons/txt_tags/energy/darkness_white.png")),
            "[M]": (self.img("src/images/name_icons/txt_tags/energy/metal_black.png"), self.img("src/images/name_icons/txt_tags/energy/metal_white.png")),
            "[DR]": (self.img("src/images/name_icons/txt_tags/energy/dragon_black.png"), self.img("src/images/name_icons/txt_tags/energy/dragon_white.png")),
            "[N]": (self.img("src/images/name_icons/txt_tags/energy/dragon_black.png"), self.img("src/images/name_icons/txt_tags/energy/dragon_white.png")),
            "[Y]": (self.img("src/images/name_icons/txt_tags/energy/fairy_black.png"), self.img("src/images/name_icons/txt_tags/energy/fairy_white.png")),
        }

        self.pocket_card_desc_dict = {
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
    cache_pixmap_set = pyqtSignal()
    
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
            self.is_pixmap = is_pixmap

    def load_from_cache(self):
        
        pixmap = QPixmap(self.is_pixmap) 
        scaled = pixmap.scaled(
        self.target_size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)
        self.cache_pixmap_set.emit()
        


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



class DexImage(QObject):

    image_fetched = pyqtSignal(str, QPixmap)

    _shared_network_manager = None

    def __init__(
        self,
        image_link: str,
        cache_dict: dict,
        network_manager: QNetworkAccessManager | None = None
    ):

        super().__init__()

        self.image_link = image_link
        self.cache_dict = cache_dict

        if network_manager is not None:
            self._network_manager = network_manager
        else:
            if DexImage._shared_network_manager is None:
                DexImage._shared_network_manager = QNetworkAccessManager()

            self._network_manager = DexImage._shared_network_manager

        self._reply: QNetworkReply | None = None

        if self.image_link not in self.cache_dict:
            self._start_fetch()

    def get_pixmap(self) -> QPixmap | None:

        if self.image_link in self.cache_dict:
            return self.cache_dict[self.image_link]

        return None

    def _start_fetch(self):

        if self._is_remote_url():
            self._fetch_remote_async()
        else:
            self._fetch_local_async()

    def _is_remote_url(self) -> bool:

        return (
            isinstance(self.image_link, str)
            and QUrl(self.image_link).scheme() in {"http", "https"}
        )

    def _fetch_remote_async(self):

        try:
            request = QNetworkRequest(QUrl(self.image_link))

            request.setRawHeader(
                b"User-Agent",
                b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                b"AppleWebKit/537.36 (KHTML, like Gecko) "
                b"Chrome/120.0 Safari/537.36"
            )

            request.setRawHeader(
                b"Accept",
                b"image/avif,image/webp,image/apng,image/*,*/*;q=0.8"
            )

            request.setRawHeader(
                b"Referer",
                b"https://pokemondb.net/"
            )

            self._reply = self._network_manager.get(request)

            if self._reply is None:
                print(f"Failed to create network request for {self.image_link}")
                return

            self._reply.finished.connect(self._on_remote_fetch_finished)  # type: ignore
            self._reply.errorOccurred.connect(self._on_fetch_error)  # type: ignore

        except Exception as e:
            print(f"Error starting remote fetch: {e}")

    def _fetch_local_async(self):

        try:
            if os.path.exists(self.image_link):
                pixmap = QPixmap(self.image_link)

                if not pixmap.isNull():
                    scaled = pixmap
                    self.cache_dict[self.image_link] = scaled
                    self.image_fetched.emit(self.image_link, scaled)

                else:
                    print(f"Failed to load local image: {self.image_link}")

            else:
                print(f"Local image file not found: {self.image_link}")

        except Exception as e:
            print(f"Error loading local image: {e}")

    def _on_remote_fetch_finished(self):

        reply = self._reply

        if reply is None or sip.isdeleted(reply):
            self._reply = None
            return

        try:
            if reply.error() == QNetworkReply.NetworkError.NoError:

                pixmap = QPixmap()
                pixmap.loadFromData(reply.readAll())  # type: ignore

                if not pixmap.isNull():
                    scaled = pixmap
                    self.cache_dict[self.image_link] = scaled
                    self.image_fetched.emit(self.image_link, scaled)

                else:
                    print(f"Failed to load pixmap from {self.image_link}")

            else:
                print(
                    f"Network error fetching {self.image_link}: "
                    f"{reply.errorString()}"
                )

        except Exception as e:
            print(f"Error processing fetched image: {e}")

        finally:
            if reply and not sip.isdeleted(reply):
                reply.deleteLater()  # type: ignore

            self._reply = None

    def _on_fetch_error(self):

        reply = self._reply

        if reply is None or sip.isdeleted(reply):
            self._reply = None
            return

        try:
            print(
                f"Network error fetching {self.image_link}: "
                f"{reply.errorString()}"
            )

        except Exception as e:
            print(f"Error handling fetch error: {e}")

        finally:
            if reply and not sip.isdeleted(reply):
                reply.deleteLater()  # type: ignore

            self._reply = None

    