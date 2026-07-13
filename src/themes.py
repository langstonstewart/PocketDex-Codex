class Themes:
    def __init__(self):
        self.light_theme = """
            QWidget {
                background-color: white;
                color: #1E1E1E;
            }
            QLabel[class="header1"] {
                font-size: 75px; margin: 3px; color: #1E1E1E;
            }

            QLabel[class="header_title"] {
                font-size: 40px; margin: 3px; color: #1E1E1E;
            }

            QLabel[class="dex_header_title"] {
                font-size: 64px; margin: 3px; color: #1E1E1E;
            }

            QLabel[class="header2"] {
                font-size: 24px; margin: 3px; color: #1E1E1E;
            }

            QLabel[class="dex_num_header"] {
                font-size: 24px; margin: 3px; color: #9ca3af;
            }

            QLabel[class="header3"] {
                font-size: 30px; margin: 3px; color: #1E1E1E;
            }
            QLabel[class="small_header"] {
                font-size: 16px; margin: 3px; color: #1E1E1E;
            }

            QLabel[class="red_ability_header"] {
                font-size: 24px; margin: 3px; color: #e31a21;
            }

            QLabel[class="purple_ability_header"] {
                font-size: 24px; margin: 3px; color: #444db2;
            }

            QLabel[class="green_ability_header"] {
                font-size: 24px; margin: 3px; color: #00863f;
            }

            QLabel[class="lime_ability_header"] {
                font-size: 24px; margin: 3px; color: #93c42d;
            }

            QLabel[class="theta_header"] {
                font-size: 24px; margin: 3px; color: white;
            }

            QLabel[class="Card_Label"] {
                border-radius: 10px; 
            }

             QLabel[class="Link_Label"] {
                font-size: 25px; 
                margin: 3px;
                color: #4f4e4e;
            }
            QLabel[class="Link_Label"]:hover {
                font-size: 25px; 
                margin: 0px; 
                color: #828181;
            }

            QLabel[class="header4"] {
                font-size: 20px;
                color: #1E1E1E; 
                margin: 3px; 
                background-color: #ebebeb; 
                border: 3px solid #1E1E1E; 
                border-radius: 20px; 
                padding: 5px; 
                padding-left: 25px; 
                padding-right: 25px;
            }

            QLabel[class="type_header"] {
                font-size: 20px;
                color: white; 
                margin: 3px; 
                background-color: #575757; 
                border-radius: 20px; 
                padding: 5px; 
                padding-left: 15px; 
                padding-right: 15px;
            }

            QLabel[class="type_header"][poke_type="bug"] { background-color: #92a212; }

            QLabel[class="type_header"][poke_type="dark"] { background-color: #4f3f3d; }

            QLabel[class="type_header"][poke_type="dragon"] { background-color: #4f60e2; }

            QLabel[class="type_header"][poke_type="electric"] { background-color: #fac100; }
            
            QLabel[class="type_header"][poke_type="fairy"] { background-color: #ef70ef; }

            QLabel[class="type_header"][poke_type="fighting"] { background-color: #ff8100; }

            QLabel[class="type_header"][poke_type="fire"] { background-color: #e72324; }

            QLabel[class="type_header"][poke_type="flying"] { background-color: #82baef; }

            QLabel[class="type_header"][poke_type="ghost"] { background-color: #703f70; }

            QLabel[class="type_header"][poke_type="grass"] { background-color: #3da224; }

            QLabel[class="type_header"][poke_type="ground"] { background-color: #92501b; }

            QLabel[class="type_header"][poke_type="ice"] { background-color: #3dd9ff; }

            QLabel[class="type_header"][poke_type="normal"] { background-color: #a0a2a0; }

            QLabel[class="type_header"][poke_type="poison"] { background-color: #923fcc; }

            QLabel[class="type_header"][poke_type="psychic"] { background-color: #ef3f7a; }

            QLabel[class="type_header"][poke_type="rock"] { background-color: #b0aa82; }

            QLabel[class="type_header"][poke_type="steel"] { background-color: #60a2b9; }

            QLabel[class="type_header"][poke_type="water"] { background-color: #2481ef; }

            QLabel[class="type_header"][gender="male"] { background-color: #2481ef; }

            QLabel[class="type_header"][gender="female"] { background-color: #ef3f7a; }

            QLabel[class="type_header"][gender="genderless"] { color: #1E1E1E; background-color: #ebebeb; }

            QLabel[class="dex_text"] {
                font-size: 20px;
                color: white; 
                margin: 3px; 
                background-color: #ebebeb; 
                border-radius: 20px; 
                padding: 5px; 
                padding-left: 15px; 
                padding-right: 15px;
            }

            QLabel[class="Set_Tag"] {
                font-size: 35px;
                color: #1E1E1E; 
                margin: 3px; 
                background-color: #ebebeb; 
                border: 3px solid gray; 
                border-radius: 20px; 
                padding: 5px;
                padding-left: 15px; 
                padding-right: 15px;
            }

            QPushButton[class="Main_Button"] {
                font-size: 20px;
                color: #1E1E1E; 
                margin: 3px; 
                background-color: #ebebeb; 
                border: 3px #ebebeb; 
                border-radius: 15px; 
                padding: 5px;
                padding-left: 15px; 
                padding-right: 15px;
            }
            QPushButton[class="Main_Button"]:hover {
                background-color: #f5f5f5
            }
            QPushButton[class="Main_Button"]:pressed {
                background-color: #ebebeb
            }

            QToolButton[class="Main_Button"] {
                font-size: 20px;
                color: #1E1E1E; 
                margin: 3px; 
                background-color: #ebebeb; 
                border: 3px #ebebeb; 
                border-radius: 15px; 
                padding: 5px;
                padding-left: 15px; 
                padding-right: 15px;
            }
            QToolButton[class="Main_Button"]:hover {
                background-color: #f5f5f5
            }
            QToolButton[class="Main_Button"]:pressed {
                background-color: #ebebeb
            }

            QToolButton[class="Dex_Button_D"] {
                font-size: 20px;
                color: #1E1E1E; 
                margin: 3px; 
                background-color: #ebebeb; 
                border: 3px #ebebeb; 
                border-radius: 15px; 
                padding: 5px;
                padding-left: 15px; 
                padding-right: 15px;
            }
            QToolButton[class="Dex_Button_D"]:hover {
                background-color: #ebebeb
            }
            QToolButton[class="Dex_Button_D"]:pressed {
                background-color: #ebebeb
            }
            

            

            QToolButton[class="Dex_Button"] {
                font-size: 20px;
                color: #1E1E1E; 
                margin: 3px; 
                background-color: #ebebeb; 
                border: 3px #ebebeb; 
                border-radius: 15px; 
                padding: 5px;
                padding-left: 15px; 
                padding-right: 15px;
            }
            QToolButton[class="Dex_Button"]:hover {
                background-color: #f5f5f5
            }
            QToolButton[class="Dex_Button"]:pressed {
                background-color: #ebebeb
            }


            QPushButton[class="Card_Button"] {
                font-size: 40px;
                color: #1E1E1E; 
                margin: 3px; 
                background-color: #ebebeb; 
                border: 3px #ebebeb; 
                border-radius: 15px; 
                padding: 5px;
                padding-left: 15px; 
                padding-right: 15px;
            }
            QPushButton[class="Card_Button"]:hover {
                background-color: #f5f5f5
            }
            QPushButton[class="Card_Button"]:pressed {
                background-color: #ebebeb
            }

            QLabel[class="dex_text_icon"] {
                font-size: 20px;
                color: #1E1E1E; 
                margin: 3px; 
                background-color: #ebebeb; 
                border-radius: 20px; 
                padding: 5px; 
                padding-left: 15px; 
                padding-right: 15px;
            }

            QLabel[class="dex_text"] {
                font-size: 20px;
                color: #1E1E1E; 
                margin: 3px; 
                background-color: #ebebeb; 
                border-radius: 15px; 
                padding: 5px; 
                padding-left: 15px; 
                padding-right: 15px;
            }

            QPushButton[class="Setting_Button"] {
                font-size: 20px;
                color: #1E1E1E; 
                margin: 3px; 
                background-color: #ebebeb; 
                border: 3px solid gray; 
                border-radius: 15px; 
                padding: 5px;
                padding-left: 5px; 
                padding-right: 5px;
            }
            QPushButton[class="Setting_Button"]:hover {
                background-color: #f5f5f5
            }
            QPushButton[class="Setting_Button"]:pressed {
                background-color: #ebebeb
            }

            QTableView[class="Data_Chart"] {
                font-size: 16px;
                color: #1E1E1E;
                background-color: #ebebeb;
                border: 5px solid #808080;
                gridline-color: transparent
            }
            QTableView[class="Data_Chart"]::item:alternate {
                background-color: #dbdbdb;
            }

            QHeaderView::section {
                font-size: 18px;
                color: #1E1E1E;
                background-color: #bcbcbc;
                border: none;
            }

            QLineEdit {
                background-color: #ffffff;
                color: #1f2937;
                border: 2px solid #575757;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 18px;
                selection-background-color: #a5b4fc;
            }

            QLineEdit:focus {
                border: 2px solid #575757;
                background-color: #f9fafb;
            }
           
            QLineEdit[text=""] {
                color: #9ca3af;
            }
            
        """

        self.dark_theme = """
            QWidget {
                background-color: #1E1E1E;
                color: white;
            }

            QLabel[class="header1"] {
                font-size: 75px; margin: 3px; color: white;
            }

            QLabel[class="header_title"] {
                font-size: 40px; margin: 3px; color: white;
            }

            QLabel[class="dex_header_title"] {
                font-size: 64px; margin: 3px; color: white;
            }

            QLabel[class="header2"] {
                font-size: 24px; margin: 3px; color: white;
            }

            QLabel[class="dex_num_header"] {
                font-size: 24px; margin: 3px; color: #3d3d3d;
            }
            
            QLabel[class="header3"] {
                font-size: 30px; margin: 3px; color: white;
            }
            QLabel[class="small_header"] {
                font-size: 16px; margin: 3px; color: white;
            }

            QLabel[class="red_ability_header"] {
                font-size: 24px; margin: 3px; color: #e31a21;
            }
            
            QLabel[class="purple_ability_header"] {
                font-size: 24px; margin: 3px; color: #444db2;
            }

            QLabel[class="green_ability_header"] {
                font-size: 24px; margin: 3px; color: #00863f;
            }

            QLabel[class="lime_ability_header"] {
                font-size: 24px; margin: 3px; color: #93c42d;
            }

            QLabel[class="theta_header"] {
                font-size: 24px; margin: 3px; color: white;
            }

            QLabel[class="Card_Label"] {
                border-radius: 10px;
            }

            QLabel[class="Link_Label"] {
                font-size: 25px; 
                margin: 3px;
                color: #e0faff;
            }
            QLabel[class="Link_Label"]:hover {
                font-size: 25px; 
                margin: 0px; 
                color: white;
            }

            QLabel[class="header4"] {
                font-size: 20px;
                color: white; 
                margin: 3px; 
                background-color: #575757; 
                border: 3px solid white; 
                border-radius: 20px; 
                padding: 5px; 
                padding-left: 25px; 
                padding-right: 25px;
            }

            QLabel[class="type_header"] {
                font-size: 20px;
                color: white; 
                margin: 3px; 
                background-color: #575757; 
                border-radius: 20px; 
                padding: 5px; 
                padding-left: 15px; 
                padding-right: 15px;
            }

            QLabel[class="type_header"][poke_type="bug"] { background-color: #92a212; }

            QLabel[class="type_header"][poke_type="dark"] { background-color: #4f3f3d; }

            QLabel[class="type_header"][poke_type="dragon"] { background-color: #4f60e2; }

            QLabel[class="type_header"][poke_type="electric"] { background-color: #fac100; }
            
            QLabel[class="type_header"][poke_type="fairy"] { background-color: #ef70ef; }

            QLabel[class="type_header"][poke_type="fighting"] { background-color: #ff8100; }

            QLabel[class="type_header"][poke_type="fire"] { background-color: #e72324; }

            QLabel[class="type_header"][poke_type="flying"] { background-color: #82baef; }

            QLabel[class="type_header"][poke_type="ghost"] { background-color: #703f70; }

            QLabel[class="type_header"][poke_type="grass"] { background-color: #3da224; }

            QLabel[class="type_header"][poke_type="ground"] { background-color: #92501b; }

            QLabel[class="type_header"][poke_type="ice"] { background-color: #3dd9ff; }

            QLabel[class="type_header"][poke_type="normal"] { background-color: #a0a2a0; }

            QLabel[class="type_header"][poke_type="poison"] { background-color: #923fcc; }

            QLabel[class="type_header"][poke_type="psychic"] { background-color: #ef3f7a; }

            QLabel[class="type_header"][poke_type="rock"] { background-color: #b0aa82; }

            QLabel[class="type_header"][poke_type="steel"] { background-color: #60a2b9; }

            QLabel[class="type_header"][poke_type="water"] { background-color: #2481ef; }
            
            QLabel[class="type_header"][gender="male"] { background-color: #2481ef; }

            QLabel[class="type_header"][gender="female"] { background-color: #ef3f7a; }

            QLabel[class="type_header"][gender="genderless"] { background-color: #3d3d3d; }

            QLabel[class="dex_text"] {
                font-size: 20px;
                color: white; 
                margin: 3px; 
                background-color: #3d3d3d; 
                border-radius: 15px; 
                padding: 5px; 
                padding-left: 15px; 
                padding-right: 15px;
            }

            QLabel[class="dex_text_icon"] {
                font-size: 20px;
                color: white; 
                margin: 3px; 
                background-color: #3d3d3d; 
                border-radius: 20px; 
                padding: 5px; 
                padding-left: 15px; 
                padding-right: 15px;
            }

            QLabel[class="Set_Tag"] {
                font-size: 35px;
                color: white; 
                margin: 5px; 
                background-color: #1E1E1E; 
                border: 4px solid white; 
                border-radius: 20px; 
                padding: 5px;
                padding-left: 15px; 
                padding-right: 15px;
            }

            QPushButton[class="Main_Button"] {
                font-size: 20px;
                color: white; 
                margin: 3px; 
                background-color: #3d3d3d; 
                border-radius: 15px; 
                padding: 5px;
                padding-left: 15px; 
                padding-right: 15px;
            }
            QPushButton[class="Main_Button"]:hover {
                background-color: #747474
            }
            QPushButton[class="Main_Button"]:pressed {
                background-color: #3d3d3d
            }

            QToolButton[class="Main_Button"] {
                font-size: 20px;
                color: white; 
                margin: 3px; 
                background-color: #3d3d3d; 
                border-radius: 15px; 
                padding: 5px;
                padding-left: 15px; 
                padding-right: 15px;
            }
            QToolButton[class="Main_Button"]:hover {
                background-color: #747474
            }
            QToolButton[class="Main_Button"]:pressed {
                background-color: #3d3d3d
            }

            QToolButton[class="Dex_Button_D"] {
                font-size: 20px;
                color: #1E1E1E; 
                margin: 3px; 
                background-color: #3d3d3d; 
                border: 3px #3d3d3d; 
                border-radius: 15px; 
                padding: 5px;
                padding-left: 15px; 
                padding-right: 15px;
            }
            QToolButton[class="Dex_Button_D"]:hover {
                background-color: #3d3d3d
            }
            QToolButton[class="Dex_Button_D"]:pressed {
                background-color: #3d3d3d
            }


            QPushButton[class="Card_Button"] {
                font-size: 40px;
                color: white; 
                margin: 3px; 
                background-color: #575757; 
                border-radius: 15px; 
                padding: 5px;
                padding-left: 15px; 
                padding-right: 15px;
            }
            QPushButton[class="Card_Button"]:hover {
                background-color: #747474
            }
            QPushButton[class="Card_Button"]:pressed {
                background-color: #575757
            }
            QPushButton[class="Setting_Button"] {
                font-size: 20px;
                color: white; 
                margin: 3px; 
                background-color: #575757; 
                border: 3px solid #2c2c2c; 
                border-radius: 15px; 
                padding: 5px;
                padding-left: 5px; 
                padding-right: 5px;
            }
            QPushButton[class="Setting_Button"]:hover {
                background-color: #747474
            }
            QPushButton[class="Setting_Button"]:pressed {
                background-color: #575757
            }
            QTableView[class="Data_Chart"] {
                font-size: 16px;
                color: #1E1E1E;
                background-color: #585858;
                border: 5px solid #2b2b2b;
                gridline-color: transparent
            }
            QTableView[class="Data_Chart"]::item:alternate {
                background-color: #464646;
            }
            QHeaderView::section {
                font-size: 18px;
                color: #1E1E1E;
                background-color: #363636;
                border: none;
            }

            QLineEdit {
                background-color: #2c2c2c;
                color: #575757;
                border: 2px solid #2c2c2c;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 18px;
                selection-background-color: #a5b4fc;
            }

            QLineEdit:focus {
                border: 2px solid #474747;
                background-color: #474747;
            }
           
            QLineEdit[text=""] {
                color: #b0b0b0;
            }

                    """