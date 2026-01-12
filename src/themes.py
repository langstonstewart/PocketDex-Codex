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
            QLabel[class="header2"] {
                font-size: 25px; margin: 3px; color: #1E1E1E;
            }
            QLabel[class="header3"] {
                font-size: 30px; margin: 3px; color: #1E1E1E;
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
                color: #ebebeb; 
                margin: 3px; 
                background-color: #ebebeb; 
                border: 3px solid #1E1E1E; 
                border-radius: 20px; 
                padding: 5px; 
                padding-left: 25px; 
                padding-right: 25px;
            }
            QLabel[class="Completion_Label"] {
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
            
        """

        self.dark_theme = """
            QWidget {
                background-color: #1E1E1E;
                color: white;
            }
            QLabel[class="header1"] {
                font-size: 75px; margin: 3px; color: white;
            }
            QLabel[class="header2"] {
                font-size: 25px; margin: 3px; color: white;
            }
            QLabel[class="header3"] {
                font-size: 30px; margin: 3px; color: white;
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
            QLabel[class="Completion_Label"] {
                font-size: 35px;
                color: #1E1E1E; 
                margin: 3px; 
                background-color: #575757; 
                border: 3px solid #2c2c2c; 
                border-radius: 20px; 
                padding: 5px;
                padding-left: 15px; 
                padding-right: 15px;
            }
            QPushButton[class="Main_Button"] {
                font-size: 20px;
                color: white; 
                margin: 3px; 
                background-color: #575757; 
                border-radius: 15px; 
                padding: 5px;
                padding-left: 15px; 
                padding-right: 15px;
            }
            QPushButton[class="Main_Button"]:hover {
                background-color: #747474
            }
            QPushButton[class="Main_Button"]:pressed {
                background-color: #575757
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
                color: #1E1E1E; 
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
                    """