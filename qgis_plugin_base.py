# -*- coding: utf-8 -*-
#******************************************************************************
#
# qgis_plugin_base
# ---------------------------------------------------------
# Base Class for qgis plugins
#
# Author:   Alexander Lisovenko, alexander.lisovenko@nextgis.ru
# *****************************************************************************
# Copyright (c) 2015-2016. NextGIS, info@nextgis.com
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
#*****************************************************************************

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import (
    QgsMessageLog, Qgis
)


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if Singleton not in cls._instances:
             cls._instances[Singleton] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[Singleton]


class Plugin(metaclass=Singleton):
    def __init__(self, iface, pluginName):
        self._iface = iface
        self._name = pluginName

        self.__actions = []

    def plPrint(self, msg, level=Qgis.Info):
        QgsMessageLog.logMessage(
            msg,
            self._name,
            level
        )

    def addAction(self, name, iconSrc):
        action = QAction(name, self._iface.mainWindow())
        action.setIcon(QIcon(iconSrc))

        self.__actions.append(action)
        index = len(self.__actions) - 1

        self._iface.addPluginToMenu(self._name, self.__actions[index])
        self._iface.addToolBarIcon(self.__actions[index])

        return self.__actions[index]

    def delAllActions(self):
        for action in self.__actions:
            self._iface.removeToolBarIcon(action)
            self._iface.removePluginMenu(self._name, action)

    def getPluginName(self):
        return self._name