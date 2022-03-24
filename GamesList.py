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
#TODO: Commit when Enter is pressed in lineEdit
#TODO: Notify user that Title is taken
#TODO: Disallow empty Titles and usage of $
#TODO: Pokemon Unite sortering??


def reduce_title(t):
        excl = ["a", "by", "in", "of", "the"]
        t_list = t.lower().split(" ")
        return " ".join(list(filter(lambda a:a not in excl, t_list)))
    

class TableModel(QtCore.QAbstractTableModel):
    
    def __init__(self, fileName, data, status_dict):
        super(TableModel, self).__init__()
        self.fileName = fileName
        self._data = data
        self.status_dict = status_dict
    
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
            
            # Check that title doesn't already exist
            if value[0] in self._data.Title.values:
                return False
            
            # I have no clue about the values used below - it seems that they
            # don't do anything but must be valid...
            self.beginInsertRows(QModelIndex(), 0, 0)
            
            # Fix some values
            if value[3] == "No score":
                value[3] = -1
            value[3] = float(value[3])
            
            value.append(reduce_title(value[0]))
            value.append(self.status_dict[value[1]])
            print(value)
            
            # Find the place where the new value goes
            row = pd.DataFrame([value], columns=self._data.columns)
            temp = self._data[(self._data["categorized"] <= value[5]) &
                              (self._data["reduced"] <= value[4])]
            if temp.empty:
                self._data = pd.concat([row, self._data]).reset_index(drop=True)
            else:
                idx = temp.index[-1] + 1
                self._data = pd.concat([self._data.iloc[:idx], row, self._data.iloc[idx:]]).reset_index(drop=True)
            
            # Save the data
            self._data.to_csv(self.fileName, sep="$", header=True, index=False)
            
            self.endInsertRows()
            return True
        return False
    
    def updateData(self, index, value, role):
        if role == Qt.EditRole:
            
            row = index.row()
            
            # Check that title doesn't already exist among the other objects
            if (value[0] in self._data.Title.values[:row-1]) | \
                (value[0] in self._data.Title.values[row+1:]):
                return False
            
            # Remove the row, then insert the update as a new row
            self.beginRemoveRows(QModelIndex(), 0, 0)
            self._data = self._data.drop(row, axis=0)
            self.endRemoveRows()
            
            return self.setData(QModelIndex(), value, role)
        
        return False
    
    def deleteData(self, index, role):
        if role == Qt.EditRole:
            
            self.beginRemoveRows(QModelIndex(), 0, 0)
            
            self._data = self._data.drop(index.row(), axis=0).reset_index(drop=True)
            
            # Save the data
            self._data.to_csv(self.fileName, sep="$", header=True, index=False)
            
            self.endRemoveRows()
            
            return True
        
        return False
        

class BetterProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, status):
        QtCore.QSortFilterProxyModel.__init__(self)
        self.score_dict = {"":-1,"10.0":10.0,"9.5":9.5,"9.0":9.0,
                           "8.5":8.5,"8.0":8.0,"7.5":7.5,"7.0":7.0,"6.5":6.5,
                           "6.0":6.0,"5.5":5.5,"5.0":5.0,"4.5":4.5,"4.0":4.0,
                           "3.5":3.5,"3.0":3.0,"2.5":2.5,"2.0":2.0,"1.5":1.5,
                           "1.0":1.0,"0.5":0.5,"0.0":0.0}
     
        
    def lessThan(self, left, right):
        lval = left.data()
        rval = right.data()
        if left.column() == 0:  # Sort by Title
            lval = left.sibling(left.row(), 4).data()
            rval = right.sibling(right.row(), 4).data()
        elif left.column() == 1:  # Sort by Status (or Title if tie)
            lval = left.sibling(left.row(), 5).data()
            rval = right.sibling(right.row(), 5).data()
            if lval == rval:
                lval = left.sibling(left.row(), 4).data()
                rval = right.sibling(right.row(), 4).data()
        elif left.column() == 2:  # Sort by Console (or Title if tie)
            if lval == rval:
                lval = left.sibling(left.row(), 4).data()
                rval = right.sibling(right.row(), 4).data()
        elif left.column() == 3:  # Sort by Score (or Title if tie)
            lval = self.score_dict[left.data()]
            rval = self.score_dict[right.data()]
            if lval == rval:
                lval = left.sibling(left.row(), 4).data()
                rval = right.sibling(right.row(), 4).data()
        return lval < rval


class GamesList(QMainWindow):
    
    def __init__(self):
        super().__init__()

        # Setup main window
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('Games List')
        
        # Get data
        self.fileName = "Games.txt"
        data = pd.read_csv(self.fileName, sep = "$")
        self.status = [c[:-1] for c in open("Status.txt").readlines()]
        status_dict = dict(zip(self.status, list(range(len(self.status)))))
        self.consoles = [c[:-1] for c in open("Consoles.txt").readlines()]
        self.scores = ["No score","10.0","9.5","9.0","8.5",
                       "8.0","7.5","7.0","6.5","6.0","5.5",
                       "5.0","4.5","4.0","3.5","3.0","2.5",
                       "2.0","1.5","1.0","0.5","0.0"]
        
        # Create helper columns
        data["reduced"] = data["Title"].apply(reduce_title)
        data["categorized"] = data["Status"].replace(status_dict)
        
        # Set up QTableView
        self.tableModel = TableModel(self.fileName, data, status_dict)
        self.proxyModel = BetterProxyModel(self.status)
        self.proxyModel.setSourceModel(self.tableModel)
        self.ui.tableView.setModel(self.proxyModel)
        self.ui.tableView.setColumnWidth(0, 327)
        self.ui.tableView.setColumnWidth(1, 95)
        self.ui.tableView.setColumnWidth(2, 95)
        self.ui.tableView.setColumnWidth(3, 50)
        self.ui.tableView.hideColumn(5)
        self.ui.tableView.hideColumn(4)
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
    
    def addGame(self):
        title = self.dialog.ui.lineEdit_title.text()
        status = self.dialog.ui.comboBox_status.currentText()
        console = self.dialog.ui.comboBox_console.currentText()
        score = self.dialog.ui.comboBox_score.currentText()
        
        if self.tableModel.setData(QModelIndex(), [title, status, console, score], Qt.EditRole):
            self.dialog.close()
        else:
            print("noooo")
        
    
    # ----- Edit Dialog Functions -----
    
    def openEditDialog(self):
        if not self.ui.tableView.selectionModel().hasSelection():
            return
        
        row_elems = self.ui.tableView.selectionModel().selection().indexes()
        self.dialog = QtWidgets.QDialog()
        self.dialog.ui = editGameDialog()
        self.dialog.ui.setupUi(self.dialog)
        
        # Populate fields
        self.dialog.ui.lineEdit_title.setText(row_elems[0].data())
        self.dialog.ui.comboBox_status.addItems(self.status)
        self.dialog.ui.comboBox_status.setCurrentText(row_elems[1].data())
        self.dialog.ui.comboBox_console.addItems(self.consoles)
        self.dialog.ui.comboBox_console.setCurrentText(row_elems[2].data())
        self.dialog.ui.comboBox_score.addItems(self.scores)
        self.dialog.ui.comboBox_score.setCurrentText(row_elems[3].data())
        self.dialog.ui.button_cancel.clicked.connect(self.dialog.close)
        self.dialog.ui.button_delete.clicked.connect(self.deleteGame)
        self.dialog.ui.button_update.clicked.connect(self.updateGame)
        self.dialog.exec_()
    
    def deleteGame(self):
        row = self.ui.tableView.selectionModel().selection()
        if self.tableModel.deleteData(row.indexes()[0], Qt.EditRole):
            self.dialog.close()
        else:
            print("noooo")
    
    def updateGame(self):
        row = self.ui.tableView.selectionModel().selection()
        title = self.dialog.ui.lineEdit_title.text()
        status = self.dialog.ui.comboBox_status.currentText()
        console = self.dialog.ui.comboBox_console.currentText()
        score = self.dialog.ui.comboBox_score.currentText()
        if self.tableModel.updateData(row.indexes()[0], [title, status, console, score], Qt.EditRole):
            self.dialog.close()
        else:
            print("noooo")
    
    
    def openConsoleDialog(self):
        print(self.consoles)
    
    def clearSearch(self):
        self.ui.lineEdit_search.clear()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = GamesList()
    widget.show()
    app.exec_()