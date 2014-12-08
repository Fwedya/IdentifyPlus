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

import numbers

from urlparse import urlparse, parse_qs

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyQt4 import QtDeclarative

from qgis.core import *
from qgis.gui import *

from GdalTools.tools import GdalTools_utils

from ui_attributestable import Ui_AttributesTable
from ui_attributestablewithimages import Ui_AttributesTableWithImages
from ui_identifyplusresultsbase_new import Ui_IdentifyPlusResultsNew

from image_gallery import ImageGallery
from image_gallery.ngwImageAPI import *
from identifyplusutils import getImageByURL, gdallocationinfoXMLOutputProcessing

from ngwapi import ngwapi

def _parseQgsLayerSource(qgsLayer):
        """
            wfs:        http://demo.nextgis.ru/ngw/resource/1311/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=rukluobninsk4wfs&SRSNAME=EPSG:3857&username=administrator&password=admin
            geojson:    http://administrator:admin@demo.nextgis.ru/ngw/resource/1316/geojson/
        """
        baseURL = ""
        ngw_username = ""
        ngw_password = ""
        resourceID = 0
            
        o = urlparse(qgsLayer.source())
        m = re.search('^/\w+/resource/\d+/',o.path)
        if m is None:
            return None
        
        # o.path is '/<ngw service name>/resource/<resource id>/.......'
        # m.group() is '/<ngw service name>/resource/<resource id>/'
        basePathStructure = m.group().strip('/').split('/')
        baseURL = o.scheme + '://' + o.netloc + '/' + basePathStructure[0]
        resourceID = int(basePathStructure[2])

        requestAttrs = parse_qs(o.query)
        if qgsLayer.providerType() == u'WFS':
            if requestAttrs.has_key(u'username'):
                ngw_username = requestAttrs.get(u'username')[0]
            if requestAttrs.has_key(u'password'):
                ngw_password = requestAttrs.get(u'password')[0]
        elif qgsLayer.providerType() == u'ogr':
            if o.netloc.find('@') != -1:
                auth_data = o.netloc.split('@')[0]
                ngw_username = auth_data.split(':')[0]
                ngw_password = auth_data.split(':')[1]
        else:
            return None
        
        additionAttrs = {}
        if requestAttrs.get(u'TYPENAME') is not None:
            additionAttrs.update({u'LayerName': requestAttrs[u'TYPENAME'][0]})
            
        additionAttrs.update({u'auth':(ngw_username, ngw_password)})
        
        return (ngwapi.getNGWResource(baseURL, resourceID, (ngw_username, ngw_password)), additionAttrs)
        
class ExtendedFeature(QObject):
    def __init__(self, qgsMapCanvas, qgsMapLayer, qgsFeature):
        QObject.__init__(self)
        self._canvas = qgsMapCanvas
        self._layer = qgsMapLayer
        self._feature = qgsFeature
        
        self._attrs = dict()

        attrs = qgsFeature.attributes()
        fields = qgsFeature.fields().toList()
        for i in xrange(len(attrs)):
            self._attrs[fields[i].name()] = attrs[i]
            
        self._attrs.update(self._getDerivedAttrs())
        
        
    @property
    def layer(self):
        return self._layer
    
    @property
    def id(self):
        return self._feature.id()
    
    @property
    def attributes(self):
        return self._attrs
    
    def _getDerivedAttrs(self):
        if self._layer is None:
          return None
    
        calc = QgsDistanceArea()
    
        calc.setEllipsoidalMode(self._canvas.hasCrsTransformEnabled())
        calc.setEllipsoid(QgsProject.instance().readEntry("Measure", "/Ellipsoid", GEO_NONE)[0])
        calc.setSourceCrs(self._layer.crs().srsid())
    
        attrs = dict()
    
        if self._layer.geometryType() == QGis.Line:
          dist = calc.measure(self._feature.geometry())
          dist, myDisplayUnits = self.__convertUnits(calc, dist, False)
          res = calc.textUnit(dist, 3, myDisplayUnits, False)
          attrs[self.tr("Length")] = res
    
          if self._feature.geometry().wkbType() in [QGis.WKBLineString, QGis.WKBLineString25D]:
            pnt = self._canvas.mapRenderer().layerToMapCoordinates(self._layer, self._feature.geometry().asPolyline()[0])
            res = QLocale.system().toString(pnt.x(), 'g', 10)
            attrs[self.tr("firstX")] = res
            res = QLocale.system().toString(pnt.y(), 'g', 10)
            attrs[self.tr("firstY")] = res
    
            pnt = self._canvas.mapRenderer().layerToMapCoordinates(self._layer, self._feature.geometry().asPolyline()[len(self._feature.geometry().asPolyline()) - 1])
            res = QLocale.system().toString(pnt.x(), 'g', 10)
            attrs[self.tr("lastX")] = res
            res = QLocale.system().toString(pnt.y(), 'g', 10)
            attrs[self.tr("lastY")] = res
        
        elif self._layer.geometryType() == QGis.Polygon:
          area = calc.measure(self._feature.geometry())
          perimeter = calc.measurePerimeter(self._feature.geometry())
          area, myDisplayUnits = self.__convertUnits(calc, area, True)
          res = calc.textUnit(area, 3, myDisplayUnits, True)
          attrs[self.tr("Area")] = res
    
          perimeter, myDisplayUnits = self.__convertUnits(calc, perimeter, False)
          res = calc.textUnit(perimeter, 3, myDisplayUnits, False)
          attrs[self.tr("Perimeter")] = res
        
        elif self._layer.geometryType() == QGis.Point and self._feature.geometry().wkbType() in [QGis.WKBPoint, QGis.WKBPoint25D]:
          pnt = self._canvas.mapRenderer().layerToMapCoordinates(self._layer, self._feature.geometry().asPoint())
          res = QLocale.system().toString(pnt.x(), 'g', 10)
          attrs[self.tr("X")] = res
          res = QLocale.system().toString(pnt.y(), 'g', 10)
          attrs[self.tr("Y")] = res
    
        return attrs
    
    def __convertUnits(self, calc, measure, isArea):
        myUnits = self._canvas.mapUnits()
        settings = QSettings("QGIS", "QGIS")
        displayUnits = QGis.fromLiteral(settings.value("/qgis/measure/displayunits", QGis.toLiteral(QGis.Meters)))
        measure, myUnits = calc.convertMeasurement(measure, myUnits, displayUnits, isArea)
        return (measure, myUnits)

class Obj1Widget(QWidget, Ui_AttributesTable):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.tblAttributes.verticalHeader().setResizeMode(QHeaderView.ResizeToContents);
        #self.tblAttributes.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents);
        #self.tblAttributes.horizontalHeader().setResizeMode(1, QHeaderView.Interactive)
    def takeControl(self, extendedFeature):
        attrs = {}
        if isinstance(extendedFeature, ExtendedFeature):
            attrs = extendedFeature.attributes
        elif isinstance(extendedFeature, dict):
            attrs = extendedFeature
            
        self.tblAttributes.clear()
        self.tblAttributes.setHorizontalHeaderLabels([self.tr("Name"), self.tr("Value")])
        self.tblAttributes.setRowCount(len(attrs))
        self.tblAttributes.setColumnCount(2)
        
        row = 0
        for fieldName, fieldValue in attrs.items():
            item = QTableWidgetItem(fieldName)
            self.tblAttributes.setItem(row, 0, item )
            
            if isinstance(fieldValue, QPyNullVariant):
                item = QTableWidgetItem("NULL")
                
            elif isinstance(fieldValue, QVariant):
                item = QTableWidgetItem(attrs[i].toString())
                
            else:
              if isinstance(fieldValue, numbers.Number):
                item = QTableWidgetItem(str(fieldValue))
              else:
                item = QTableWidgetItem(fieldValue)
            
            self.tblAttributes.setItem(row, 1, item )
            row += 1
            
        #self.tblAttributes.resizeRowsToContents()
        #self.tblAttributes.resizeColumnsToContents()
        
class Obj2Widget(QWidget, Ui_AttributesTableWithImages):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.attributesView = Obj1Widget(self)
        
        self.vlAtributesViewContainer.addWidget(self.attributesView)
        
        self.imgAPI = NGWImageAPI()
        
        self.btnLoadPhoto.clicked.connect(self.addPhotos)
        self.btnSaveAllPhotos.clicked.connect(self.downloadPhotos)
        #
        #  Add image Gallery
        #
        self.ig = ImageGallery.ImageGallery(QUrl('qrc:/image_gallery/ImageGallery.qml'), self.tr("No photos") )
        
        self.ig.onDownloadImage.connect(self.downloadPhoto)
        self.ig.onDeleteImage.connect(self.deletePhoto)
        
        self.ig.setResizeMode(QtDeclarative.QDeclarativeView.SizeRootObjectToView)
        self.ig.setGeometry(100, 100, 400, 240)
        self.vlImageGaleryContainer.addWidget(self.ig)
        
        self.ig.setDataProvider(self.imgAPI)
        
        settings = QSettings();
        self.tabWidget.setCurrentIndex( settings.value("identifyplus/atrrsWithImages/currentTabIndex", 1, type=int) )
        self.tabWidget.currentChanged.connect(self.saveTabState)
    
    def saveTabState(self, tabIndex):
        settings = QSettings();
        settings.setValue("identifyplus/atrrsWithImages/currentTabIndex", tabIndex)
        
    def takeControl(self, qgsFeature):
        self.attributesView.takeControl(qgsFeature)
        
        try:
            res = _parseQgsLayerSource(qgsFeature.layer)
            
            ngwResource = None
            if res is not None:
                (ngwResource, addAttrs) = res
            
            if isinstance(ngwResource, ngwapi.NGWResourceWFS):
                resourceId4identify = ngwResource.getLayerResourceIDByKeyname(addAttrs[u'LayerName'])
                ngwResource4identify = ngwapi.getNGWResource(ngwResource.baseURL, resourceId4identify, addAttrs[u'auth'])
                self.ig.loadImages(ngw_resource = ngwResource4identify, feature_id = qgsFeature.id+1, auth = addAttrs[u'auth'])
                
            elif isinstance(ngwResource, ngwapi.NGWResourceVectorLayer):
                self.ig.loadImages(ngw_resource = ngwResource, feature_id = qgsFeature.id, auth = addAttrs[u'auth'])
            else:
                self.tabWidget.setTabEnabled(1, False)
                return
        except ImageGallery.ImageGalleryError as err:
            QgsMessageLog.logMessage(self.tr("Load images error") + ":\n" + str(err), u'IdentifyPlus', QgsMessageLog.CRITICAL)
        except ngwapi.NGWAPIError as err:
            QgsMessageLog.logMessage(self.tr("Get NGWw resource error") + ":\n" + str(err), u'IdentifyPlus', QgsMessageLog.CRITICAL)

    @pyqtSlot(QObject)
    def downloadPhoto(self, image):
        settings = QSettings("Photos", "identifyplus")
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
          img = getImageByURL(image.url, None)
          img.save(fName)
        except ImageGallery.ImageGalleryError as err:
          self.showMessage(self.tr("Download photo error.<br>") + err.msg)
    
        settings.setValue("/lastPhotoDir", QFileInfo(fName).absolutePath())
    
    def deletePhoto(self):
        self.showMessage(self.tr("The delete photo operation is not available"))

    def downloadPhotos(self):
        settings = QSettings("Photos", "identifyplus")
        lastDir = settings.value( "/lastPhotoDir", "." )
    
        dirName = QFileDialog.getExistingDirectory(self,
                                                   self.tr("Select directory"),
                                                   lastDir,
                                                   QFileDialog.ShowDirsOnly
                                                  )
        if dirName == "":
          return

        try:
          for image_info in self.ig.getAllImagesInfo():
            img = getImageByURL(image_info["url"], None)
            img.save("%s/%s.png" % (dirName, image_info["id"]))
          
        except ImageGallery.ImageGalleryError as err:
          self.showMessage(self.tr("Download photo error.<br>") + err.msg)
          
        settings.setValue("/lastPhotoDir", QFileInfo(dirName).absolutePath())
  
    def addPhotos(self):
        self.showMessage(self.tr("The add photo operation is not available"))
    
    def showMessage(self, message):
        msgViewer = QgsMessageViewer(self)
        msgViewer.setTitle(self.tr("IdentifyPlus message") )
        msgViewer.setCheckBoxVisible(False)
        msgViewer.setMessageAsHtml(message)
        msgViewer.showMessage()
    
class IdentifyPlusResultsNew(QWidget, Ui_IdentifyPlusResultsNew):
    def __init__(self, tool, canvas, parent):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.canvas = canvas
        self.tool = tool
        
        self.objectView = None
        self.objects = []
        
        self.currentObjectIndex = 0;
        self.btnFirstRecord.clicked.connect(self.firstRecord)
        self.btnLastRecord.clicked.connect(self.lastRecord)
        self.btnNextRecord.clicked.connect(self.nextRecord)
        self.btnPrevRecord.clicked.connect(self.prevRecord)
        
        self.lblFeatures.setText(self.tr("No features"))
        
        self.btnFirstRecord.setEnabled(False)
        self.btnLastRecord.setEnabled(False)
        self.btnNextRecord.setEnabled(False)
        self.btnPrevRecord.setEnabled(False)
        
    def firstRecord(self):
        self.currentObjectIndex = 0
        self._loadFeatureAttributes()
        
    def lastRecord(self):
        self.currentObjectIndex = len(self.objects) - 1
        self._loadFeatureAttributes()
        
    def nextRecord(self):
        self.currentObjectIndex += 1
        if self.currentObjectIndex >= len(self.objects):
          self.currentObjectIndex = 0

        self._loadFeatureAttributes()

    def prevRecord(self):
        self.currentObjectIndex = self.currentObjectIndex - 1
        if self.currentObjectIndex < 0:
          self.currentObjectIndex = len(self.objects) - 1
    
        self._loadFeatureAttributes()
    
    def _loadFeatureAttributes(self):
        self.lblFeatures.setText(self.tr("Feature %s from %s") % (self.currentObjectIndex + 1, len(self.objects)))
        self.objectView.takeControl(self.objects[self.currentObjectIndex])
        
    def identify(self, qgsMapLayer, x, y):
        self.objects = []
        self.currentObjectIndex = 0;
        
        if self.objectView is not None:
            self.loObjectContainer.removeWidget(self.objectView)
            self.objectView.close()
        
        if qgsMapLayer.type() == QgsMapLayer.RasterLayer:
            self.objectView = Obj1Widget(self)
            self._initRasterLayer(qgsMapLayer, x, y)
            
        elif qgsMapLayer.type() == QgsMapLayer.VectorLayer:
            try:
                res = _parseQgsLayerSource(qgsMapLayer)
                if res is not None:
                    self.objectView  = Obj2Widget(self)
                else:
                    self.objectView  = Obj1Widget(self)
            except ngwapi.NGWAPIError as err:
                QgsMessageLog.logMessage(self.tr("Get NGWw resource error") + ":\n" + str(err), u'IdentifyPlus', QgsMessageLog.CRITICAL)
                self.objectView  = Obj1Widget(self)
            
            self._initVectorLayer(qgsMapLayer, x, y)
        else:
            QgsMessageLog.logMessage(self.tr("Unknown layer type"), u'IdentifyPlus', QgsMessageLog.WARNING)
            
        if len(self.objects) != 0:
            self._loadFeatureAttributes()
            self.loObjectContainer.addWidget(self.objectView)
            self.btnFirstRecord.setEnabled(True)
            self.btnLastRecord.setEnabled(True)
            self.btnNextRecord.setEnabled(True)
            self.btnPrevRecord.setEnabled(True)
        else:
            self.lblFeatures.setText(self.tr("No features"))
            self.btnFirstRecord.setEnabled(False)
            self.btnLastRecord.setEnabled(False)
            self.btnNextRecord.setEnabled(False)
            self.btnPrevRecord.setEnabled(False)
        
        if len(self.objects) == 0:
            QgsMessageLog.logMessage(self.tr("Objects not found"), u'IdentifyPlus', QgsMessageLog.WARNING)
            
        return len(self.objects) > 0
    
    def _initRasterLayer(self, qgsMapLayer, x, y):
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        
        #Use gdalocationinfo utility
        process = QProcess()
        GdalTools_utils.setProcessEnvironment(process)
    
        process.start("gdallocationinfo", ["-xml","-b", "1" ,"-geoloc", qgsMapLayer.source(), str(point.x()), str(point.y())], QIODevice.ReadOnly)
        
        finishWaitSuccess = process.waitForFinished(5000) # wait 5 sec
        
        if not finishWaitSuccess:
            QgsMessageLog.logMessage(self.tr("Wait for gdallocationinfo more then 5 sec <br/>"), u'IdentifyPlus', QgsMessageLog.CRITICAL)
            return
        
        if(process.exitCode() != 0):
            err_msg = str(process.readAllStandardError())
            if err_msg == '':
                err_msg = str(process.readAllStandardOutput())
            
            #QMessageBox.warning(self,
            #              self.tr("Location info request fail"),
            #              self.tr("gdallocationinfo return error status<br/>"+err_msg)
            #             )
            #self.lastIdentifyErrorMsg = self.tr("gdallocationinfo return error status<br/>" + err_msg)
            QgsMessageLog.logMessage(self.tr("gdallocationinfo return error status<br/>") + ":\n" + err_msg, u'IdentifyPlus', QgsMessageLog.CRITICAL)
        else:
            data = str(process.readAllStandardOutput());
            
            res = gdallocationinfoXMLOutputProcessing(data)
            
            if res[0] != None:
               # QMessageBox.warning(self,
               #           self.tr("Location info request fail"),
               #           self.tr("Parsing gdallocationinfo request error<br/>" + res[1])
               #          )
               #self.lastIdentifyErrorMsg = self.tr("Parsing gdallocationinfo request error<br/>" + res[1])
               QgsMessageLog.logMessage(self.tr("Parsing gdallocationinfo request error<br/>") + ":\n" + res[1] + "\n" + data, u'IdentifyPlus', QgsMessageLog.CRITICAL)
            else:
                for f in res[1]:
                    self.objects.append(f)
        
    def _initVectorLayer(self, qgsMapLayer, x, y):
        # load identify radius from settings
        settings = QSettings()
        identifyValue = float(settings.value("/Map/searchRadiusMM", QGis.DEFAULT_IDENTIFY_RADIUS))
    
        if identifyValue <= 0.0:
          identifyValue = QGis.DEFAULT_IDENTIFY_RADIUS

        pointFrom = self.canvas.getCoordinateTransform().toMapCoordinates(
            x - identifyValue * self.canvas.PdmWidthMM, 
            y + identifyValue * self.canvas.PdmHeightMM)
            
        pointTo = self.canvas.getCoordinateTransform().toMapCoordinates(
            x + identifyValue * self.canvas.PdmWidthMM, 
            y - identifyValue * self.canvas.PdmHeightMM)
        
        featureCount = 0
        featureList = []
        try:
          #searchRadius = self.canvas.extent().width() * (identifyValue / 100.0)
          r = QgsRectangle()
          r.setXMinimum(pointFrom.x())
          r.setXMaximum(pointTo.x())
          r.setYMinimum(pointFrom.y())
          r.setYMaximum(pointTo.y())
    
          r = self.tool.toLayerCoordinates(qgsMapLayer, r)
    
          rq = QgsFeatureRequest()
          rq.setFilterRect(r)
          rq.setFlags(QgsFeatureRequest.ExactIntersect)
          for f in qgsMapLayer.getFeatures(rq):
            featureList.append(QgsFeature(f))
        except QgsCsException as cse:
          QgsMessageLog.logMessage(self.tr("Caught CRS exception") + ":\n" + cse.what(), u'IdentifyPlus', QgsMessageLog.CRITICAL)
        
        myFilter = False
    
        #renderer = qgsMapLayer.rendererV2() # неизвестность
    
        qgsVersion = int(unicode(QGis.QGIS_VERSION_INT))
        
        
        #if renderer is not None and (renderer.capabilities() | QgsFeatureRendererV2.ScaleDependent):
        #  if qgsVersion < 20200 and qgsVersion > 10900:
        #    renderer.startRender( self.canvas.mapRenderer().rendererContext(), qgsMapLayer)
        #  elif qgsVersion >= 20300:
        #    renderer.startRender( self.canvas.mapRenderer().rendererContext(), qgsMapLayer.pendingFields())
        #  else:
        #    renderer.startRender( self.canvas.mapRenderer().rendererContext(), qgsMapLayer)
            
        #  myFilter = renderer.capabilities() and QgsFeatureRendererV2.Filter
    
        for f in featureList:
        #    if myFilter and not renderer.willRenderFeature(f): # какие-то фичи отсеивают
        #        continue
            featureCount += 1
            self.objects.append(ExtendedFeature(self.canvas, qgsMapLayer, f))
            
        #if renderer is not None and (renderer.capabilities() | QgsFeatureRendererV2.ScaleDependent):
        #  renderer.stopRender(self.canvas.mapRenderer().rendererContext())

class IdentifyPlusResultsDialog(QDialog):
    def __init__(self, tool, canvas, plugin):
        QDialog.__init__(self, None)
        self.hbloResultContainer = QHBoxLayout()
        self.setLayout(self.hbloResultContainer)
        self.setWindowTitle(self.tr("IdentifyPlus"))
        
        self.wResults = IdentifyPlusResultsNew(tool, canvas, self)
        
        
        self.hbloResultContainer.addWidget(self.wResults)
        
    def identify(self, qgsMapLayer, x, y):
        return self.wResults.identify(qgsMapLayer, x, y)


class IdentifyPlusResultsDock(QDockWidget):
    def __init__(self, tool, canvas, plugin):
        QDockWidget.__init__(self, None)
        self.setWindowTitle(self.tr("IdentifyPlus"))
        
        self.wResults = IdentifyPlusResultsNew(tool, canvas, self)
        self.setWidget(self.wResults)

        self.setWidget(self.wResults)
        
        self.tool = tool
        self.tool.used.connect(self.mapToolProcess)
        
    def mapToolProcess(self, qgsMapLayer, x, y):
        self.setEnabled(False)
        
        if not self.isVisible():
            self.setVisible(True)
        
        self.wResults.identify(qgsMapLayer, x, y)
        
        self.setEnabled(True)
        