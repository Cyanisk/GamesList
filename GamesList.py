import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from MainWindow import Ui_MainWindow


class GamesList(QMainWindow):
    
    def __init__(self):
        super().__init__()

        # Setup main window
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('Games List')
        
        # Read in consoles and games
        file = open("Games.txt")
        consoles = file.readline()[:-2].split("$")
        temp = file.readlines()
        gameslist = [game[:-2].split("$") for game in temp]
        
        self.ui.tableView.model().data(gameslist)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = GamesList()
    widget.show()
    app.exec_()