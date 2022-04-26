import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
import pandas as pd
from MainWindow import Ui_MainWindow
from AddGameDialog import Ui_Dialog as addGameDialog
from EditGameDialog import Ui_Dialog as editGameDialog
from EditConsolesDialog import Ui_Dialog as editConsolesDialog


def reduce_title(t):
    # Words that are commonly disregarded from sorting
    excl = ["a", "by", "in", "of", "the"]
    t_list = t.lower().split(" ")
    return " ".join(list(filter(lambda a:a not in excl, t_list)))
    

class TableModel(QtCore.QAbstractTableModel):
    
    def __init__(self, fileName, data, status_dict):
        super(TableModel, self).__init__()
        self.fileName = fileName
        self._backend_data = data  # The data that is imported/exported/edited
        self._data = data  # The representation of the data after applying sorting (used by tableView)
        self.status_dict = status_dict
        self.current_filter = ""
        self.sort_column = 1
        self.sort_order = 0  # 0 = ascending, 1 = descending
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            
            value = self._data.iloc[index.row()][index.column()]
            if value == -1:  # Display a score of -1 (no score) as an empty string
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
                return str(self._data.index[section] + 1)  # 1-indexed for normies
    
    # Adding a row
    def setData(self, index, value, role):
        if role == Qt.EditRole:
            
            # Check validity of title
            if value[0] in self._backend_data["Title"].values:
                return "\"" + value[0] + "\" already exists."
            if value[0].strip() == "":
                return "Enter a title."
            if "$" in value[0]:
                return "The symbol \"$\" is reserved."
            
            # Convert selected score to a float
            if value[3] == "No score":
                value[3] = -1
            value[3] = float(value[3])
            
            # Add hidden representations of title and status (used for sorting)
            value.append(reduce_title(value[0]))
            value.append(self.status_dict[value[1]])
            
            # Make a new row and find the row that comes before the new row
            row = pd.DataFrame([value], columns=self._backend_data.columns)
            before1 = self._backend_data["categorized"] < value[5]
            before2 = (self._backend_data["categorized"] == value[5]) & \
                      (self._backend_data["reduced"] <= value[4])
            temp = self._backend_data[before1 | before2]
            
            # Sandwich the new row in between the rows that come before (if any) and after
            if temp.empty:
                self._backend_data = pd.concat([row, self._backend_data]).reset_index(drop=True)
            else:
                idx = temp.index[-1] + 1
                self._backend_data = pd.concat([self._backend_data.iloc[:idx], row, 
                                                self._backend_data.iloc[idx:]]).reset_index(drop=True)
            
            # Update the tableView (maintain current sorting)
            self.filterSortData()
            
            # Save the data
            self._backend_data.to_csv(self.fileName, sep="$", header=True, index=False)
            
            return ""
        return "Something went wrong."
    
    def updateData(self, index, value, role):
        if role == Qt.EditRole:
            
            # Convert tableView index to _backend_data index
            row = self._data.index[index.row()]
            
            # Check that title doesn't already exist among the other objects
            if (value[0] in self._backend_data.Title.values[:row-1]) | \
                (value[0] in self._backend_data.Title.values[row+1:]):
                return "\"" + value[0] + "\" already exists."
            if value[0].strip() == "":
                return "Enter a title."
            if "$" in value[0]:
                return "The symbol \"$\" is reserved."
            
            # Delete the row, then insert the updated row
            self._backend_data = self._backend_data.drop(row, axis=0)
            return self.setData(QModelIndex(), value, role)
        
        return "Something went wrong."
    
    def deleteData(self, index, role):
        if role == Qt.EditRole:
            
            # Convert tableView index to _backend_data index
            row = self._data.index[index.row()]
            
            # Delete the row and update the tableView (maintain current sorting)
            self._backend_data = self._backend_data.drop(row, axis=0).reset_index(drop=True)
            self.filterSortData()
            
            # Save the data
            self._backend_data.to_csv(self.fileName, sep="$", header=True, index=False)
            
            return ""
        
        return "Something went wrong"
    
    def filterSortData(self, text=None, column=-1, order=-1):
        # If an argument is unspecified, use the current choice
        if text == None:
            text = self.current_filter
        if column == -1:
            column = self.sort_column
        if order == -1:
            order = self.sort_order
        
        self.current_filter = text
        self.sort_column = column
        self.sort_order = order
        
        ascending = (order == 0)
        by = ""
        
        # If column != 0, the rows are sorted secondarily by reduced title (always ascending)
        if column == 0: 
            by = 'reduced'
        elif column == 1:
            by = ['categorized', 'reduced']
            ascending = [ascending, True]
        elif column == 2:
            by = ['Console', 'reduced']
            ascending = [ascending, True]
        elif column == 3:
            by = ['Score', 'reduced']
            ascending = [ascending, True]
        
        # Declare that the displayed data is about to change, then do it
        self.beginResetModel()
        temp = self._backend_data[self._backend_data['Title'].str.lower().str.contains(text.lower())]
        temp = temp.sort_values(by=by, ascending=ascending)
        self._data = temp
        self.endResetModel()
    
    def isConsoleUsed(self, console):
        return console in self._backend_data["Console"].values
    
    def renameConsole(self, old, new):
        # Replace the old console with the new
        self._backend_data["Console"] = self._backend_data["Console"].replace({old:new})
        
        # Update the tableView
        self.filterSortData()
            
        # Save the data
        self._backend_data.to_csv(self.fileName, sep="$", header=True, index=False)
        

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
        
        # Create hidden representations of title and status (used for sorting)
        data["reduced"] = data["Title"].apply(reduce_title)
        data["categorized"] = data["Status"].replace(status_dict)
        
        # Set up QTableView
        self.tableModel = TableModel(self.fileName, data, status_dict)
        self.ui.tableView.setModel(self.tableModel)
        self.ui.tableView.setColumnWidth(0, 327)
        self.ui.tableView.setColumnWidth(1, 95)
        self.ui.tableView.setColumnWidth(2, 95)
        self.ui.tableView.setColumnWidth(3, 50)
        self.ui.tableView.horizontalHeader().setSectionResizeMode(2) # Disable header drag
        self.ui.tableView.verticalHeader().setSectionResizeMode(2)
        self.ui.tableView.hideColumn(5)
        self.ui.tableView.hideColumn(4)
        self.ui.tableView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ui.tableView.setSelectionBehavior(1) # Select whole row
        self.ui.tableView.setSelectionMode(1) # Only one selection at a time
        self.ui.tableView.setSortingEnabled(True)
        self.ui.tableView.sortByColumn(1, Qt.AscendingOrder)
        self.ui.tableView.horizontalHeader().sortIndicatorChanged.connect(self.headerTriggered)
        
        # Define button behaviour
        self.ui.button_add.clicked.connect(self.openAddDialog)
        self.ui.button_edit.clicked.connect(self.openEditDialog)
        self.ui.button_consoles.clicked.connect(self.openConsoleDialog)
        self.ui.button_clear.clicked.connect(self.clearSearch)
        
        # Search bar
        self.ui.lineEdit_search.textChanged.connect(self.applyFilter)
    
    
    # ----- Column Sorting Functions -----
    
    def headerTriggered(self, column=-1, order=-1):
        self.tableModel.filterSortData(column=column, order=order)
        
    
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
        self.dialog.ui.button_cancel.setAutoDefault(False)
        self.dialog.ui.button_add.setAutoDefault(True)
        self.dialog.exec_()
    
    def addGame(self):
        title = self.dialog.ui.lineEdit_title.text()
        status = self.dialog.ui.comboBox_status.currentText()
        console = self.dialog.ui.comboBox_console.currentText()
        score = self.dialog.ui.comboBox_score.currentText()
        
        result = self.tableModel.setData(QModelIndex(), [title, status, console, score], Qt.EditRole)
        if result == "":
            self.dialog.close()
        else:
            message = QMessageBox(text = result)
            message.setWindowTitle("Error")
            message.exec()
       
    
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
        
        # Add events
        self.dialog.ui.button_cancel.clicked.connect(self.dialog.close)
        self.dialog.ui.button_delete.clicked.connect(self.deleteGame)
        self.dialog.ui.button_update.clicked.connect(self.updateGame)
        
        # Make the update button the default selected button
        self.dialog.ui.button_cancel.setAutoDefault(False)
        self.dialog.ui.button_delete.setAutoDefault(False)
        self.dialog.ui.button_update.setAutoDefault(True)
        
        self.dialog.exec_()
    
    def deleteGame(self):
        row = self.ui.tableView.selectionModel().selection().indexes()[0]
        
        result = self.tableModel.deleteData(row, Qt.EditRole)
        if result == "":
            self.dialog.close()
        else:
            message = QMessageBox(text = result)
            message.setWindowTitle("Error")
            message.exec()
    
    def updateGame(self):
        row = self.ui.tableView.selectionModel().selection().indexes()[0]
        
        title = self.dialog.ui.lineEdit_title.text()
        status = self.dialog.ui.comboBox_status.currentText()
        console = self.dialog.ui.comboBox_console.currentText()
        score = self.dialog.ui.comboBox_score.currentText()
        
        result = self.tableModel.updateData(row, [title, status, console, score], Qt.EditRole)
        if result == "":
            self.dialog.close()
        else:
            message = QMessageBox(text = result)
            message.setWindowTitle("Error")
            message.exec()
    
    
    # ----- Console Dialog Functions -----
    
    def openConsoleDialog(self):
        self.dialog = QtWidgets.QDialog()
        self.dialog.ui = editConsolesDialog()
        self.dialog.ui.setupUi(self.dialog)
        
        # Populate fields
        options = ['New console'] + self.consoles
        self.dialog.ui.comboBox.addItems(options)
        self.dialog.ui.comboBox.setCurrentText(options[0])
        self.dialog.ui.lineEdit.setText(options[0])
        
        # Add events
        self.dialog.ui.comboBox.currentIndexChanged.connect(self.consoleDialogIndexChanged)
        self.dialog.ui.button_cancel.clicked.connect(self.dialog.close)
        self.dialog.ui.button_delete.clicked.connect(self.deleteConsole)
        self.dialog.ui.button_update.clicked.connect(self.updateConsole)
        
        # Make the update button the default selected button
        self.dialog.ui.button_cancel.setAutoDefault(False)
        self.dialog.ui.button_delete.setAutoDefault(False)
        self.dialog.ui.button_update.setAutoDefault(True)
        self.dialog.exec_()
    
    def consoleDialogIndexChanged(self):
        self.dialog.ui.lineEdit.setText(self.dialog.ui.comboBox.currentText())
        if self.dialog.ui.comboBox.currentIndex() == 0:
            self.dialog.ui.button_delete.setEnabled(False)
            self.dialog.ui.button_update.setText("Add console")
        else:
            self.dialog.ui.button_delete.setEnabled(True)
            self.dialog.ui.button_update.setText("Update console")
    
    def deleteConsole(self):
        console = self.dialog.ui.comboBox.currentText()
        if self.tableModel.isConsoleUsed(console):
            message = QMessageBox(text = "The selected console is still\n used by a game entry")
            message.setWindowTitle("Error")
            message.exec()
        else:
            self.consoles.remove(console)
            with open('Consoles.txt', 'w') as f:
                for c in self.consoles:
                    f.write(c)
                    f.write('\n')
            self.dialog.close()
    
    def updateConsole(self):
        console = self.dialog.ui.lineEdit.text()
        index = self.dialog.ui.comboBox.currentIndex()
        if index == 0:
            if console in self.consoles:
                message = QMessageBox(text = (console + " already exists"))
                message.setWindowTitle("Error")
                message.exec()
            else:
                self.consoles = sorted(self.consoles + [console])
                with open('Consoles.txt', 'w') as f:
                    for c in self.consoles:
                        f.write(c)
                        f.write('\n')
                self.dialog.close()
        else:
            self.tableModel.renameConsole(self.consoles[index-1], console)
            self.consoles[index-1] = console
            with open('Consoles.txt', 'w') as f:
                for c in self.consoles:
                    f.write(c)
                    f.write('\n')
            self.dialog.close()
            
    
    
    # ----- Search Functions -----
    
    def clearSearch(self):
        # Clear search field and reload displayed data
        self.ui.lineEdit_search.clear()
        self.tableModel.filterSortData(text="")
    
    def applyFilter(self, text):
        self.tableModel.filterSortData(text=text)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = GamesList()
    widget.show()
    app.exec_()