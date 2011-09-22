# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created: Tue Jan 25 00:49:05 2011
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(265, 141)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label_track_src = QtGui.QLabel(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_track_src.sizePolicy().hasHeightForWidth())
        self.label_track_src.setSizePolicy(sizePolicy)
        self.label_track_src.setObjectName("label_track_src")
        self.gridLayout.addWidget(self.label_track_src, 0, 0, 1, 1)
        self.label_track_wrapper = QtGui.QLabel(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_track_wrapper.sizePolicy().hasHeightForWidth())
        self.label_track_wrapper.setSizePolicy(sizePolicy)
        self.label_track_wrapper.setObjectName("label_track_wrapper")
        self.gridLayout.addWidget(self.label_track_wrapper, 1, 0, 1, 1)
        self.comboBox_what2add = QtGui.QComboBox(Dialog)
        self.comboBox_what2add.setObjectName("comboBox_what2add")
        self.comboBox_what2add.addItem("")
        self.comboBox_what2add.addItem("")
        self.gridLayout.addWidget(self.comboBox_what2add, 2, 0, 1, 1)
        self.playlist_chooser = QtGui.QComboBox(Dialog)
        self.playlist_chooser.setObjectName("playlist_chooser")
        self.gridLayout.addWidget(self.playlist_chooser, 2, 1, 1, 1)
        self.lineEdit = QtGui.QLineEdit(Dialog)
        self.lineEdit.setEnabled(True)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 3, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label_track_src.setText(QtGui.QApplication.translate("Dialog", "track source", None, QtGui.QApplication.UnicodeUTF8))
        self.label_track_wrapper.setText(QtGui.QApplication.translate("Dialog", "track wrapper", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_what2add.setItemText(0, QtGui.QApplication.translate("Dialog", "add track", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_what2add.setItemText(1, QtGui.QApplication.translate("Dialog", "add all tracks", None, QtGui.QApplication.UnicodeUTF8))

