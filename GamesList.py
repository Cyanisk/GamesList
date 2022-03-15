import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QModelIndex, pyqtSignal, QSortFilterProxyModel
from PyQt5.QtWidgets import QApplication, QMainWindow
import pandas as pd
from MainWindow import Ui_MainWindow
from AddGameDialog import Ui_Dialog as addGameDialog
from EditGameDialog import Ui_Dialog as editGameDialog

#TODO: Store data from TableModel
#TODO: Button functionality
#TODO: Pop-up menus
#TODO: Search
#TODO: Column sort (ignore case, ignore "the")
#TODO: Commit when Enter is pressed in lineEdit


class TableModel(QtCore.QAbstractTableModel):
    
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
        self._sortBy = []
        self._sortDirection = []
    
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
        if role ==  Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.columns[section]
            if orientation == Qt.Vertical:
                return str(self._data.index[section] + 1)
            
    def setData(self, index, value, role):
        if role == Qt.EditRole:
            
            if value[0] in self._data.Title.values:
                return False
            
            # I have no clue about the values used below - it seems that they
            # don't do anything but must be valid...
            self.beginInsertRows(QModelIndex(), 0, 0)
            
            if value[3] == "No score":
                value[3] = -1
            self._data.loc[self._data.shape[0]] = value
            
            self.endInsertRows()
            return True
        return False
    
# =============================================================================
#     def sort(self, col, order=QtCore.Qt.AscendingOrder):
# 
#         # Storing persistent indexes
#         self.layoutAboutToBeChanged.emit()
#         oldIndexList = self.persistentIndexList()
#         oldIds = self._data.index.copy()
#         
#         print()
#     
#         # Sorting data
#         column = self._data.columns[col]
#         ascending = (order == QtCore.Qt.AscendingOrder)
#         if column in self._sortBy:
#             i = self._sortBy.index(column)
#             self._sortBy.pop(i)
#             self._sortDirection.pop(i)
#         self._sortBy.insert(0, column)
#         self._sortDirection.insert(0, ascending)
#         #self.updateDisplay()
#     
#         # Updating persistent indexes
#         newIds = self._data.index
#         newIndexList = []
#         for index in oldIndexList:
#             id = oldIds[index.row()]
#             newRow = newIds.get_loc(id)
#             newIndexList.append(self.index(newRow, index.column(), index.parent()))
#         self.changePersistentIndexList(oldIndexList, newIndexList)
#         self.layoutChanged.emit()
#         self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
#         
#     def sortSource(self, column order):
#         Q_D(check lige hvad det er)
#         if d.dynamic_sortfilter & d.proxy_sort_column == column & d.sort_order == order:
#             return
#         d.sort_order = order
#         d.proxy_sort_column = column
#         d.update_source_sort_column()
#         d.sort
# =============================================================================


class BetterProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self):
        QtCore.QSortFilterProxyModel.__init__(self)
        self.score_dict = {"":-1,"10.0":10.0,"9.5":9.5,"9.0":9.0,
                           "8.5":8.5,"8.0":8.0,"7.5":7.5,"7.0":7.0,"6.5":6.5,
                           "6.0":6.0,"5.5":5.5,"5.0":5.0,"4.5":4.5,"4.0":4.0,
                           "3.5":3.5,"3.0":3.0,"2.5":2.5,"2.0":2.0,"1.5":1.5,
                           "1.0":1.0,"0.5":0.5,"0.0":0.0}
    
    def lessThan(self, left, right):
        if left.column() == 0:
            return left.data() < right.data()
        
        if left.column() == 1:
            lval = left.data()
            rval = right.data()
            if lval == rval:
                lsib = left.sibling(left.row(), 0)
                rsib = right.sibling(right.row(), 0)
                return self.lessThan(lsib, rsib)
            return lval < rval
        
        if left.column() == 2:
            lval = left.data()
            rval = right.data()
            if lval == rval:
                lsib = left.sibling(left.row(), 1)
                rsib = right.sibling(right.row(), 1)
                return self.lessThan(lsib, rsib)
            return lval < rval
        
        if left.column() == 3:
            lval = self.score_dict[left.data()]
            rval = self.score_dict[right.data()]
            if lval == rval:
                lsib = left.sibling(left.row(), 1)
                rsib = right.sibling(right.row(), 1)
                return self.lessThan(lsib, rsib)
            return lval < rval
        
        return left > right


class GamesList(QMainWindow):
    
    def __init__(self):
        super().__init__()

        # Setup main window
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('Games List')
        
        # Get data
        self.data = pd.read_csv("Games.txt", sep = "$")
        #self.data = pd.read_csv("Games.txt", sep = "$")
        self.status = [c[:-1] for c in open("Status.txt").readlines()]
        self.consoles = [c[:-1] for c in open("Consoles.txt").readlines()]
        self.scores = ["No score","10.0","9.5","9.0","8.5",
                       "8.0","7.5","7.0","6.5","6.0","5.5",
                       "5.0","4.5","4.0","3.5","3.0","2.5",
                       "2.0","1.5","1.0","0.5","0.0"]
        
        # Set up QTableView
        self.tableModel = TableModel(self.data)
        self.proxyModel = BetterProxyModel()
        self.proxyModel.setSourceModel(self.tableModel)
        self.ui.tableView.setModel(self.proxyModel)
        self.ui.tableView.setColumnWidth(0, 327)
        self.ui.tableView.setColumnWidth(1, 95)
        self.ui.tableView.setColumnWidth(2, 95)
        self.ui.tableView.setColumnWidth(3, 50)
        self.ui.tableView.setSelectionBehavior(1) # Select whole row
        self.ui.tableView.setSelectionMode(1) # Only one selection at a time
        self.ui.tableView.setSortingEnabled(True)
        self.ui.tableView.sortByColumn(1, Qt.AscendingOrder)
        
        # Define button behaviour
        self.ui.button_add.clicked.connect(self.openAddDialog)
        self.ui.button_edit.clicked.connect(self.openEditDialog)
        self.ui.button_consoles.clicked.connect(self.openConsoleDialog)
        self.ui.button_clear.clicked.connect(self.clearSearch)
    
    
    # ----- Add Dialog Functions -----

    def openAddDialog(self):
        self.dialog = QtWidgets.QDialog()
        self.dialog.ui = addGameDialog()
        self.dialog.ui.setupUi(self.dialog)
        self.dialog.ui.comboBox_status.addItems(self.status)
        self.dialog.ui.comboBox_console.addItems(self.consoles)
        self.dialog.ui.comboBox_score.addItems(self.scores)
        self.dialog.ui.button_add.clicked.connect(self.addGame)
        self.dialog.ui.button_cancel.clicked.connect(self.dialog.close)
        self.dialog.exec_()
        #self.dialog.show()
    
    def addGame(self):
        title = self.dialog.ui.lineEdit_title.text()
        status = self.dialog.ui.comboBox_status.currentText()
        console = self.dialog.ui.comboBox_console.currentText()
        score = self.dialog.ui.comboBox_score.currentText()
        
        if self.tableModel.setData(QModelIndex(), [title, status, console, score], Qt.EditRole):
            self.dialog.close()
        else:
            print("noooo")
        
        #print(self.tableModel.flags(QModelIndex())[0])
        
        #if self.tableModel.addRow(title, status, console, score):
        #    self.dialog.close()
        #else:
        #    print("noooo")
        
    
    # ----- Edit Dialog Functions -----
    
    def openEditDialog(self):
        if not self.ui.tableView.selectionModel().hasSelection():
            return
        
        item = self.ui.tableView.selectionModel().selection()
        self.dialog = QtWidgets.QDialog()
        self.dialog.ui = editGameDialog()
        self.dialog.ui.setupUi(self.dialog)
        #self.dialog.ui.lineEdit_title =
        self.dialog.ui.comboBox_status.addItems(self.status)
        self.dialog.ui.comboBox_console.addItems(self.consoles)
        self.dialog.ui.comboBox_score.addItems(self.scores)
        #self.dialog.ui.button_update.clicked.connect(self.addGame)
        self.dialog.ui.button_cancel.clicked.connect(self.dialog.close)
        self.dialog.exec_()
    
    def openConsoleDialog(self):
        print(self.consoles)
    
    def clearSearch(self):
        self.ui.lineEdit_search.clear()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = GamesList()
    widget.show()
    app.exec_()