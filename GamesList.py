import sys
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
import pandas as pd
from MainWindow import Ui_MainWindow
from AddGameDialog import Ui_Dialog as addGameDialog
from EditGameDialog import Ui_Dialog as editGameDialog

#TODO: Store data from TableView
#TODO: Button functionality
#TODO: Pop-up menus
#TODO: Search
#TODO: Column sort


class TableModel(QtCore.QAbstractTableModel):
    
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            
            value = self._data.iloc[index.row()][index.column()]
            if value == -1:
                value = ""
            return str(value)
    
    def rowCount(self, index):
        return self._data.shape[0]
    
    def columnCount(self, index):
        return self._data.shape[1]
    
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.columns[section]
            if orientation == Qt.Vertical:
                return str(self._data.index[section] + 1)


class GamesList(QMainWindow):
    
    def __init__(self):
        super().__init__()

        # Setup main window
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('Games List')
        
        # Read in consoles and games
        data = pd.read_csv("Games.txt", sep = "$")
        consoles = pd.read_csv("Consoles.txt")
        
        # Set up QTableView
        self.tableModel = TableModel(data)
        self.ui.tableView.setModel(self.tableModel)
        self.ui.tableView.setColumnWidth(0, 327)
        self.ui.tableView.setColumnWidth(1, 95)
        self.ui.tableView.setColumnWidth(2, 95)
        self.ui.tableView.setColumnWidth(3, 50)
        self.ui.tableView.setSelectionBehavior(1) # Select whole row
        self.ui.tableView.setSelectionMode(1) # Only one selection at a time
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = GamesList()
    widget.show()
    app.exec_()