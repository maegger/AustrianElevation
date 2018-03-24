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

def classFactory(iface):
    from .AustrianElevation import AustrianElevation
    return AustrianElevation(iface)
