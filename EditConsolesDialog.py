# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EditConsolesDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(372, 150)
        Dialog.setMinimumSize(QtCore.QSize(372, 150))
        Dialog.setMaximumSize(QtCore.QSize(372, 150))
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 11, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.comboBox = QtWidgets.QComboBox(Dialog)
        self.comboBox.setObjectName("comboBox")
        self.verticalLayout.addWidget(self.comboBox)
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        spacerItem1 = QtWidgets.QSpacerItem(20, 12, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.button_cancel = QtWidgets.QPushButton(Dialog)
        self.button_cancel.setMinimumSize(QtCore.QSize(90, 0))
        self.button_cancel.setObjectName("button_cancel")
        self.horizontalLayout_3.addWidget(self.button_cancel)
        self.button_delete = QtWidgets.QPushButton(Dialog)
        self.button_delete.setEnabled(False)
        self.button_delete.setMinimumSize(QtCore.QSize(115, 0))
        self.button_delete.setCheckable(False)
        self.button_delete.setObjectName("button_delete")
        self.horizontalLayout_3.addWidget(self.button_delete)
        self.button_update = QtWidgets.QPushButton(Dialog)
        self.button_update.setObjectName("button_update")
        self.horizontalLayout_3.addWidget(self.button_update)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.button_cancel.setText(_translate("Dialog", "Cancel"))
        self.button_delete.setText(_translate("Dialog", "Delete Console"))
        self.button_update.setText(_translate("Dialog", "Add console"))
