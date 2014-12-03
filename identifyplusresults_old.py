# -*- coding: utf-8 -*-

#******************************************************************************
#
# IdentifyPlus
# ---------------------------------------------------------
# Extended identify tool. Supports displaying and modifying photos
#
# Copyright (C) 2012-2013 NextGIS (info@nextgis.org)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/licenses/>. You can also obtain it by writing
# to the Free Software Foundation, 51 Franklin Street, Suite 500 Boston,
# MA 02110-1335 USA.
#
#******************************************************************************

import sys
import re
import requests
import abc
import numbers
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyQt4 import QtCore, QtGui, Qt, QtDeclarative

from qgis.core import *
from qgis.gui import *

from GdalTools.tools import GdalTools_utils

from ui_identifyplusresultsbase import Ui_IdentifyPlusResults
from ui_attributestable import Ui_AttributesTable
from ui_attributestablewithimages import Ui_AttributesTableWithImages
from ui_identifyplusresultsbase_new import Ui_IdentifyPlusResultsNew

from image_gallery import ImageGallery
from image_gallery.ngwImageAPI import *
from identifyplusutils import getImageByURL, gdallocationinfoXMLOutputProcessing

API_PORT = ":8888"

DISABLED_FIELDS = ["FID", "ogc_fid", "gid", "osm_id"]

from PyQt4 import uic

class IdentifyPlusResults(QDialog, Ui_IdentifyPlusResults):
  def __init__(self, canvas, parent):
    QDialog.__init__(self, parent)
    self.setupUi(self)

    self.canvas = canvas
    self.proxy = None
    
    self.features = []
    self.currentFeature = 0
    
    self.requestPhotos = True

    self.tabWidget.setCurrentIndex(0)

    self.btnFirstRecord.clicked.connect(self.firstRecord)
    self.btnLastRecord.clicked.connect(self.lastRecord)
    self.btnNextRecord.clicked.connect(self.nextRecord)
    self.btnPrevRecord.clicked.connect(self.prevRecord)

    self.btnLoadPhoto.clicked.connect(self.addPhotos)
    self.btnSaveAllPhotos.clicked.connect(self.downloadPhotos)

    #
    #  Add image Gallery
    #
    self.ig = ImageGallery.ImageGallery(QtCore.QUrl('qrc:/image_gallery/ImageGallery.qml'), self.tr("No photos") )
    
    self.ig.onDownloadImage.connect(self.downloadPhoto)
    self.ig.onDeleteImage.connect(self.deletePhoto)
    
    self.ig.setResizeMode(QtDeclarative.QDeclarativeView.SizeRootObjectToView)
    self.ig.setGeometry(100, 100, 400, 240)
    self.galleryLayout = QtGui.QHBoxLayout()
    self.galleryLayout.addWidget(self.ig)
    self.galleryWidget.setLayout(self.galleryLayout)

    self.__setupProxy()

  def addFeature(self, feature):
    self.features.append(feature)

  def loadAttributes(self, fid):
    f = self.features[fid]
    attrs = f.attributes()

    derived = self.getDerivedAttrs(f)

    self.tblAttributes.clear()
    self.tblAttributes.setHorizontalHeaderLabels([self.tr("Name"), self.tr("Value")])
    self.tblAttributes.setRowCount(len(attrs) + len(derived))
    self.tblAttributes.setColumnCount(2)

    row = 0
    for k, v in derived.iteritems():
      item = QTableWidgetItem(k)
      self.tblAttributes.setItem(row, 0, item )

      item = QTableWidgetItem(unicode(v))
      self.tblAttributes.setItem(row, 1, item )
      row += 1
    
    for i in xrange(len(attrs)):
      fieldName = self.layer.attributeDisplayName(i)

      if fieldName in DISABLED_FIELDS:
        self.tblAttributes.removeRow(self.tblAttributes.rowCount() - 1)
        continue

      item = QTableWidgetItem(fieldName)
      self.tblAttributes.setItem(row, 0, item )
      
      if isinstance(attrs[i], QPyNullVariant):
          item = QTableWidgetItem("NULL")
          
      elif isinstance(attrs[i], QVariant):
          item = QTableWidgetItem(attrs[i].toString ())
          
      else:
        if isinstance(attrs[i], numbers.Number):
          item = QTableWidgetItem(str(attrs[i]))
        else:
          item = QTableWidgetItem(attrs[i])
      
      self.tblAttributes.setItem(row, 1, item )
      row += 1

    self.tblAttributes.resizeRowsToContents()
    self.tblAttributes.resizeColumnsToContents()
    self.tblAttributes.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)

    self.lblFeatures.setText(self.tr("Feature %s from %s") % (fid + 1, len(self.features)))

    # load photos
    if self.requestPhotos:
      self.getPhotos(fid)

  def getPhotos(self, fid):
    featureId = self.features[fid].id()
    layerName = self.__getLayerName()
    
    try:
      self.ig.loadImages(layer_name = layerName, feature_id = featureId)
    except ImageGallery.ImageGalleryError as err:
      self.showMessage(self.tr("Load photos error.<br>") + err.msg)
      self.togglePhotoTab(False)
  
  def addPhotos(self):
    settings = QSettings("Krasnogorsk", "identifyplus")
    lastDir = settings.value( "/lastPhotoDir", "." )

    formats = ["*.%s" % unicode( format ).lower() for format in QImageReader.supportedImageFormats()]
    fNames = QFileDialog.getOpenFileNames(self,
                                        self.tr("Open image"),
                                        lastDir,
                                        self.tr("Image files (%s)" % " ".join(formats))
                                       )
    
    featureId = self.features[self.currentFeature].id()
    layerName = self.__getLayerName()
    
    try:
      for fName in fNames:
        self.ig.addImage(image_path = unicode(QFileInfo(fName).absoluteFilePath()), layer_name = layerName, feature_id = featureId)
      
      if fNames != []:
        settings.setValue("/lastPhotoDir", QFileInfo(fNames[0]).absolutePath())
        
    except ImageGallery.ImageGalleryError as err:
      self.showMessage(self.tr("Add photo error.<br>") + err.msg)
      
    
  def firstRecord(self):
    self.currentFeature = 0
    self.currentPhoto = 0
    self.loadAttributes(self.currentFeature)

  def lastRecord(self):
    self.currentFeature = len(self.features) - 1
    self.currentPhoto = 0
    self.loadAttributes(self.currentFeature)

  def nextRecord(self):
    self.currentFeature += 1
    if self.currentFeature >= len(self.features):
      self.currentFeature = 0

    self.currentPhoto = 0
    self.loadAttributes(self.currentFeature)

  def prevRecord(self):
    self.currentFeature = self.currentFeature - 1
    if self.currentFeature < 0:
      self.currentFeature = len(self.features) - 1

    self.currentPhoto = 0
    self.loadAttributes(self.currentFeature)
  
  @QtCore.pyqtSlot(QtCore.QObject)
  def deletePhoto(self, image):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle(self.tr("Delete confirmation"))
    msgBox.setText(self.tr("Are you sure you want to delete this photo?"))
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No);
    msgBox.setDefaultButton(QMessageBox.Yes);
  
    status = msgBox.exec_()
    
    if status == QMessageBox.Yes:
      self.ig.deleteImage(image)
    
  @QtCore.pyqtSlot(QtCore.QObject)
  def downloadPhoto(self, image):
    settings = QSettings("Krasnogorsk", "identifyplus")
    lastDir = settings.value( "/lastPhotoDir", "." )

    fName = QFileDialog.getSaveFileName(self,
                                        self.tr("Save image"),
                                        lastDir,
                                        self.tr("PNG files (*.png)")
                                       )
    if fName == "":
      return

    if not fName.lower().endswith(".png"):
      fName += ".png"
    
    try:
      img = getImageByURL(image.url, self.proxy)
      img.save(fName)
    except ImageGallery.ImageGalleryError as err:
      self.showMessage(self.tr("Download photo error.<br>") + err.msg)

    settings.setValue("/lastPhotoDir", QFileInfo(fName).absolutePath())

  def downloadPhotos(self):
    settings = QSettings("Krasnogorsk", "identifyplus")
    lastDir = settings.value( "/lastPhotoDir", "." )

    dirName = QFileDialog.getExistingDirectory(self,
                                               self.tr("Select directory"),
                                               lastDir,
                                               QFileDialog.ShowDirsOnly
                                              )
    if dirName == "":
      return

    #
    #  TODO Р±РѕР»РµРµ РґРµС‚Р°Р»СЊРЅР°СЏ РёРЅС„РѕСЂРјР°С†РёСЏ Рѕ СЃРѕС…СЂРѕРЅСЏРµРјС‹С… РёР·РѕР±СЂР°Р¶РµРЅРёСЏС…
    #
    try:
      for image_info in self.ig.getAllImagesInfo():
        img = getImageByURL(image_info["url"], self.proxy)
        img.save("%s/%s.png" % (dirName, image_info["id"]))
      
    except ImageGallery.ImageGalleryError as err:
      self.showMessage(self.tr("Download photo error.<br>") + err.msg)
      
    settings.setValue("/lastPhotoDir", QFileInfo(dirName).absolutePath())
    
  def clear(self):
    self.features = []
    self.photos = None
    self.currentFeature = 0
    self.currentPhoto = 0
    self.tblAttributes.clear()

  def show(self, layer):
    
    self.layer = layer

    self.ellipsoid = QgsProject.instance().readEntry("Measure", "/Ellipsoid", GEO_NONE)[0]

    if self.layer.providerType() not in ["postgres"]:
      self.togglePhotoTab(False)
    else:
      self.togglePhotoTab(True)

    if not self.__canEditLayer():
      self.toggleEditButtons(False)
    else:
      self.toggleEditButtons(True)

    if self.layer.providerType() in ["postgres"]:
      host = "http://" + unicode(self.__getDBHost()) + API_PORT
      
      header = None
      userName, password = self.__getCredentials()
      if userName is not None and password is not None:
        header = {"X-Role" : unicode(userName), "X-Password" : unicode(password)}
      else:
        self.toggleEditButtons(False)
        
      """
        Add data provider to Image Gallery
      """    
      self.ig.setDataProvider(KrasnogorskImageAPI(host, self.proxy, header))
    

    self.loadAttributes(self.currentFeature)
    
    QDialog.show(self)
    self.raise_()

  def togglePhotoTab(self, enable):
    self.requestPhotos = enable
    self.tabWidget.setTabEnabled(1, enable)

  def toggleEditButtons(self, enable):
    self.btnLoadPhoto.setEnabled(enable)

  def showMessage(self, message):
    msgViewer = QgsMessageViewer(self)
    msgViewer.setTitle(self.tr("IdentifyPlus message") )
    msgViewer.setCheckBoxVisible(False)
    msgViewer.setMessageAsHtml(message)
    msgViewer.showMessage()

  def getDerivedAttrs(self, feature):
    if self.layer is None:
      return None

    calc = QgsDistanceArea()

    calc.setEllipsoidalMode(self.canvas.hasCrsTransformEnabled())
    calc.setEllipsoid(self.ellipsoid)
    calc.setSourceCrs(self.layer.crs().srsid())

    attrs = dict()

    if self.layer.geometryType() == QGis.Line:
      dist = calc.measure(feature.geometry())
      dist, myDisplayUnits = self.__convertUnits(calc, dist, False)
      res = calc.textUnit(dist, 3, myDisplayUnits, False)
      attrs[self.tr("Length")] = res

      if feature.geometry().wkbType() in [QGis.WKBLineString, QGis.WKBLineString25D]:
        pnt = self.canvas.mapRenderer().layerToMapCoordinates(self.layer, feature.geometry().asPolyline()[0])
        res = QLocale.system().toString(pnt.x(), 'g', 10)
        attrs[self.tr("firstX")] = res
        res = QLocale.system().toString(pnt.y(), 'g', 10)
        attrs[self.tr("firstY")] = res

        pnt = self.canvas.mapRenderer().layerToMapCoordinates(self.layer, feature.geometry().asPolyline()[len(feature.geometry().asPolyline()) - 1])
        res = QLocale.system().toString(pnt.x(), 'g', 10)
        attrs[self.tr("lastX")] = res
        res = QLocale.system().toString(pnt.y(), 'g', 10)
        attrs[self.tr("lastY")] = res
    
    elif self.layer.geometryType() == QGis.Polygon:
      area = calc.measure(feature.geometry())
      perimeter = calc.measurePerimeter(feature.geometry())
      area, myDisplayUnits = self.__convertUnits(calc, area, True)
      res = calc.textUnit(area, 3, myDisplayUnits, True)
      attrs[self.tr("Area")] = res

      perimeter, myDisplayUnits = self.__convertUnits(calc, perimeter, False)
      res = calc.textUnit(perimeter, 3, myDisplayUnits, False)
      attrs[self.tr("Perimeter")] = res
    
    elif self.layer.geometryType() == QGis.Point and feature.geometry().wkbType() in [QGis.WKBPoint, QGis.WKBPoint25D]:
      pnt = self.canvas.mapRenderer().layerToMapCoordinates(self.layer, feature.geometry().asPoint())
      res = QLocale.system().toString(pnt.x(), 'g', 10)
      attrs[self.tr("X")] = res
      res = QLocale.system().toString(pnt.y(), 'g', 10)
      attrs[self.tr("Y")] = res

    return attrs

  def __setupProxy(self):
    settings = QSettings()
    if bool(settings.value("/proxyEnabled", False)):
      proxyType = settings.value("/proxyType", "Default proxy")
      proxyHost = settings.value("/proxyHost", "")
      proxyPost = int(settings.value("/proxyPort", 0))
      proxyUser = settings.value("/proxyUser", "")
      proxyPass = settings.value("/proxyPassword", "")

      # setup proxy
      connectionString = "http://%s:%s@%s:%s" % (proxyUser, proxyPass, proxyHost, proxyPort)
      self.proxy = {"http" : conectionString}
  
  def __getLayerName(self):
    if self.layer is None:
      return ""

    metadata = self.layer.source().split(" ")
    regex = re.compile("^table=.*")
    pos = metadata.index([m.group(0) for l in metadata for m in [regex.search(l)] if m][0])
    tmp = metadata[pos]
    pos = tmp.find(".")
    return tmp[pos + 2:-1]

  def __getDBHost(self):
    if self.layer is None:
      return ""

    metadata = self.layer.source().split(" ")
    regex = re.compile("^host=.*")
    pos = metadata.index([m.group(0) for l in metadata for m in [regex.search(l)] if m][0])
    tmp = metadata[pos]
    pos = tmp.find("=")
    return tmp[pos + 1:]

  def __getCredentials(self):
    if self.layer is None:
      return (None, None)

    metadata = self.layer.source().split(" ")
    regex = re.compile("^user=.*")
    pos = metadata.index([m.group(0) for l in metadata for m in [regex.search(l)] if m][0])
    tmp = metadata[pos]
    pos = tmp.find("=")
    userName = tmp[pos + 2:-1]

    regex = re.compile("^password=.*")
    pos = metadata.index([m.group(0) for l in metadata for m in [regex.search(l)] if m][0])
    tmp = metadata[pos]
    pos = tmp.find("=")
    password = tmp[pos + 2:-1]

    if userName == "" or password == "":
      regex = re.compile("^dbname=.*")
      pos = metadata.index([m.group(0) for l in metadata for m in [regex.search(l)] if m][0])
      dbname = metadata[pos]

      regex = re.compile("^host=.*")
      pos = metadata.index([m.group(0) for l in metadata for m in [regex.search(l)] if m][0])
      host = metadata[pos]

      regex = re.compile("^port=.*")
      pos = metadata.index([m.group(0) for l in metadata for m in [regex.search(l)] if m][0])
      port = metadata[pos]

      regex = re.compile("^sslmode=.*")
      pos = metadata.index([m.group(0) for l in metadata for m in [regex.search(l)] if m][0])
      ssl = metadata[pos]

      realm = "%s %s %s %s" % (dbname, host, port, sslmode)

      res, userName, password = QgsCredentials.instance().get(realm, userName, password)
      if userName == "" or password == "":
        print "Can't get user credentials"
        return (None, None)

      QgsCredentials.instance().put(realm, userName, password)

    return (userName, password)

  def __canEditLayer(self):
    if self.layer is None:
      return False

    canChangeAttributes = self.layer.dataProvider().capabilities() & QgsVectorDataProvider.ChangeAttributeValues

    return canChangeAttributes and not self.layer.isReadOnly()

  def __convertUnits(self, calc, measure, isArea):
    myUnits = self.canvas.mapUnits()
    settings = QSettings("QGIS", "QGIS")
    displayUnits = QGis.fromLiteral(settings.value("/qgis/measure/displayunits", QGis.toLiteral(QGis.Meters)))
    measure, myUnits = calc.convertMeasurement(measure, myUnits, displayUnits, isArea)
    return (measure, myUnits)