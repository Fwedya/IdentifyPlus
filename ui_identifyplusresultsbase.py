# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'identifyplusresultsbase.ui'
#
# Created: Tue Feb 11 13:19:47 2014
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_IdentifyPlusResults(object):
    def setupUi(self, IdentifyPlusResults):
        IdentifyPlusResults.setObjectName(_fromUtf8("IdentifyPlusResults"))
        IdentifyPlusResults.resize(569, 529)
        self.verticalLayout_5 = QtGui.QVBoxLayout(IdentifyPlusResults)
        self.verticalLayout_5.setSpacing(2)
        self.verticalLayout_5.setMargin(10)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setMargin(10)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.lblFeatures = QtGui.QLabel(IdentifyPlusResults)
        self.lblFeatures.setObjectName(_fromUtf8("lblFeatures"))
        self.verticalLayout_4.addWidget(self.lblFeatures)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnFirstRecord = QtGui.QToolButton(IdentifyPlusResults)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/first.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnFirstRecord.setIcon(icon)
        self.btnFirstRecord.setObjectName(_fromUtf8("btnFirstRecord"))
        self.horizontalLayout.addWidget(self.btnFirstRecord)
        self.btnPrevRecord = QtGui.QToolButton(IdentifyPlusResults)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/previous.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnPrevRecord.setIcon(icon1)
        self.btnPrevRecord.setObjectName(_fromUtf8("btnPrevRecord"))
        self.horizontalLayout.addWidget(self.btnPrevRecord)
        self.btnNextRecord = QtGui.QToolButton(IdentifyPlusResults)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/next.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnNextRecord.setIcon(icon2)
        self.btnNextRecord.setObjectName(_fromUtf8("btnNextRecord"))
        self.horizontalLayout.addWidget(self.btnNextRecord)
        self.btnLastRecord = QtGui.QToolButton(IdentifyPlusResults)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/last.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnLastRecord.setIcon(icon3)
        self.btnLastRecord.setObjectName(_fromUtf8("btnLastRecord"))
        self.horizontalLayout.addWidget(self.btnLastRecord)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.verticalLayout_5.addLayout(self.verticalLayout_4)
        self.tabWidget = QtGui.QTabWidget(IdentifyPlusResults)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tblAttributes = QtGui.QTableWidget(self.tab)
        self.tblAttributes.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tblAttributes.setAlternatingRowColors(True)
        self.tblAttributes.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblAttributes.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblAttributes.setObjectName(_fromUtf8("tblAttributes"))
        self.tblAttributes.setColumnCount(2)
        self.tblAttributes.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tblAttributes.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tblAttributes.setHorizontalHeaderItem(1, item)
        self.tblAttributes.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.tblAttributes)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setMargin(5)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.galleryWidget = QtGui.QWidget(self.tab_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.galleryWidget.sizePolicy().hasHeightForWidth())
        self.galleryWidget.setSizePolicy(sizePolicy)
        self.galleryWidget.setObjectName(_fromUtf8("galleryWidget"))
        self.verticalLayout_2.addWidget(self.galleryWidget)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.btnLoadPhoto = QtGui.QToolButton(self.tab_2)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/add.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnLoadPhoto.setIcon(icon4)
        self.btnLoadPhoto.setIconSize(QtCore.QSize(24, 24))
        self.btnLoadPhoto.setObjectName(_fromUtf8("btnLoadPhoto"))
        self.horizontalLayout_4.addWidget(self.btnLoadPhoto)
        self.btnSaveAllPhotos = QtGui.QToolButton(self.tab_2)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/download.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnSaveAllPhotos.setIcon(icon5)
        self.btnSaveAllPhotos.setIconSize(QtCore.QSize(24, 24))
        self.btnSaveAllPhotos.setObjectName(_fromUtf8("btnSaveAllPhotos"))
        self.horizontalLayout_4.addWidget(self.btnSaveAllPhotos)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.verticalLayout_5.addWidget(self.tabWidget)

        self.retranslateUi(IdentifyPlusResults)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(IdentifyPlusResults)

    def retranslateUi(self, IdentifyPlusResults):
        IdentifyPlusResults.setWindowTitle(_translate("IdentifyPlusResults", "Identify results", None))
        self.lblFeatures.setText(_translate("IdentifyPlusResults", "TextLabel", None))
        self.btnFirstRecord.setToolTip(_translate("IdentifyPlusResults", "First feature", None))
        self.btnFirstRecord.setText(_translate("IdentifyPlusResults", "...", None))
        self.btnPrevRecord.setToolTip(_translate("IdentifyPlusResults", "Previous feature", None))
        self.btnPrevRecord.setText(_translate("IdentifyPlusResults", "...", None))
        self.btnNextRecord.setToolTip(_translate("IdentifyPlusResults", "Next feature", None))
        self.btnNextRecord.setText(_translate("IdentifyPlusResults", "...", None))
        self.btnLastRecord.setToolTip(_translate("IdentifyPlusResults", "Last feature", None))
        self.btnLastRecord.setText(_translate("IdentifyPlusResults", "...", None))
        item = self.tblAttributes.horizontalHeaderItem(0)
        item.setText(_translate("IdentifyPlusResults", "Name", None))
        item = self.tblAttributes.horizontalHeaderItem(1)
        item.setText(_translate("IdentifyPlusResults", "Value", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("IdentifyPlusResults", "Attributes", None))
        self.btnLoadPhoto.setToolTip(_translate("IdentifyPlusResults", "Load photo to database", None))
        self.btnLoadPhoto.setText(_translate("IdentifyPlusResults", "...", None))
        self.btnSaveAllPhotos.setToolTip(_translate("IdentifyPlusResults", "Save all photos to disk", None))
        self.btnSaveAllPhotos.setText(_translate("IdentifyPlusResults", "...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("IdentifyPlusResults", "Image", None))

import resources_rc
