# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AustrianElevation
                                 A QGIS plugin
 Display elevation value of specified position on QGIS.  
 Using Austrian Elevation Service by Manfred Egger.  
                              -------------------
        begin                : 2018-03-24
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Yasunori Kirimoto
        email                : contact@day-journal.com
        license              : GNU General Public License v2.0
 ***************************************************************************/
"""

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from qgis.core import *
from qgis.gui import *

from .resources import *
from .AustrianElevation_dialog import AustrianElevationDialog

import os.path
import os
import sys
import codecs
import urllib.request, urllib.error, urllib.parse
import json

class AustrianElevation:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.dlg = AustrianElevationDialog()
        self.dlg.hide()  
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'AustrianElevation_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        self.actions = []
        self.menu = self.tr(u'&AustrianElevation')
        self.toolbar = self.iface.addToolBar(u'AustrianElevation')
        self.toolbar.setObjectName(u'AustrianElevation')
    def tr(self, message):
        return QCoreApplication.translate('AustrianElevation', message)
    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)
        self.actions.append(action)
        return action
    def initGui(self):
        icon_path = ':/plugins/AustrianElevation/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'AustrianElevation'),
            callback=self.run,
            parent=self.iface.mainWindow())
    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&AustrianElevation'),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar
    def run(self):
        self.toolClick = QgsMapToolClick(self.iface, self.canvas, self.dlg)
        self.canvas.setMapTool(self.toolClick)
class QgsMapToolClick(QgsMapTool):
    def __init__(self, iface, canvas, dlg):
        QgsMapTool.__init__(self, canvas)
        self.iface = iface
        self.canvas = canvas
        self.dlg = dlg
    def canvasPressEvent(self, mouseEvent):
        self.dlg.show()
        dPos = mouseEvent.pos()
        mPosBefore = self.toMapCoordinates(dPos)
        destcrs = self.iface.mapCanvas().mapSettings().destinationCrs()
        Tf = QgsCoordinateTransform(destcrs,QgsCoordinateReferenceSystem(3857), QgsProject.instance())
        mPos = Tf.transform(mPosBefore)
        x = mPos.x()
        y = mPos.y()
        mod_x_path = x % 20000;
        path_x = x - mod_x_path;
        database = int(path_x );
        mod_y = y % 10;
        raster_y = y - mod_y;
        mod_x = x % 10;
        raster_x = int(x - mod_x);
        file = "https://raw.githubusercontent.com/maegger/"+str(database)+"/master/"+str(int(raster_y))+".txt"
        try:
            ret = urllib.request.urlopen(file)
            self.dlg.label.setText("No Data")
            if ret.code == 200:
                data = urllib.request.urlopen(file)
                for line in data:
                    x_wert = line.decode('utf-8').strip().split(' ', 1 )[0]      
                    if str(x_wert) == str(raster_x):
                        elevationall = " " + line.decode('utf-8').strip().split(' ', 1 )[1]
                        elevationtext = ""
                        self.dlg.label.setText(elevationall + "m")
                        break
        except Exception:
            self.dlg.label.setText("No Data")    
        self.dlg.show()
           