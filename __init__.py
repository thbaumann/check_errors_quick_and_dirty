# encoding: utf-8
#-----------------------------------------------------------
# Copyright (C) based on the minimal plugin from 2015 Martin Dobias
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

from PyQt5.QtWidgets import QAction, QMessageBox
import math
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsFeatureRequest, QgsMessageLog,Qgis
from qgis.utils import iface


def classFactory(iface):
    return NanChecker(iface)


class NanChecker:
    def __init__(self, iface):
        self.iface = iface
        self.ueberwachte_layer=[]

    def initGui(self):
        self.action = QAction(u'An!', self.iface.mainWindow())
        self.action.triggered.connect(self.an)
        self.iface.addToolBarIcon(self.action)
        self.action2 = QAction(u'Aus!', self.iface.mainWindow())
        self.action2.triggered.connect(self.aus)
        self.iface.addToolBarIcon(self.action2)
        self.action3 = QAction(u'Check!', self.iface.mainWindow())
        self.action3.triggered.connect(self.check)
        self.iface.addToolBarIcon(self.action3)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action
        self.iface.removeToolBarIcon(self.action2)
        del self.action2
        self.iface.removeToolBarIcon(self.action3)
        del self.action3
        
    def get_active_layer_name(self):
        try:
            layername=self.iface.activeLayer().name()
            return layername
        except:
            QMessageBox.warning(None, 'Hinweis', "Fehler. Bitte Suppport kontaktieren.")

    def an(self):
        layername=self.get_active_layer_name()
        if layername:
            if layername in self.ueberwachte_layer:
                QgsMessageLog.logMessage("Ueberwachung ist schon aktiv fuer Layer {}".format(layername), 'Fehlersuche', level=Qgis.Info)
                QMessageBox.warning(None, 'Hinweis', "Ueberwachung ist schon aktiv fuer Layer {}".format(layername))
            else:
                QgsMessageLog.logMessage("Ueberwachung ist an fuer folgende Layer: {}".format(self.iface.activeLayer().name()), 'Fehlersuche', level=Qgis.Info)

                self.iface.activeLayer().beforeCommitChanges.connect( lambda: self.beforeCommitChanges(self.iface.activeLayer()) )
                
                self.iface.activeLayer().afterCommitChanges.connect( lambda: self.afterCommitChanges(self.iface.activeLayer()) ) 
                self.ueberwachte_layer.append(self.iface.activeLayer().name())
                self.alle_layer=','.join(self.ueberwachte_layer)
                QgsMessageLog.logMessage("Ueberwachung an fuer folgende Layer: {}".format(self.alle_layer), 'Fehlersuche', level=Qgis.Info)
        else:
            QMessageBox.warning(None, 'Hinweis', "Fehler. Kein Layer ermittelt.")

    
    def aus(self):
        layername=self.get_active_layer_name()
        if layername in self.ueberwachte_layer:
            self.ueberwachte_layer.remove(self.iface.activeLayer().name())
            self.alle_layer=','.join(self.ueberwachte_layer)
            QgsMessageLog.logMessage("Ueberwachung aus fuer Layer: {}".format(self.iface.activeLayer().name()), 'Fehlersuche', level=Qgis.Info)
            QgsMessageLog.logMessage("Ueberwachung ist jetzt noch an fuer folgende Layer: {}".format(self.alle_layer), 'Fehlersuche', level=Qgis.Info)
            try:
                self.iface.activeLayer().beforeCommitChanges.disconnect(self.iface.activeLayer())
                self.iface.activeLayer().committedFeaturesAdded.disconnect(self.iface.activeLayer())
            except:
                pass
        else:
            QgsMessageLog.logMessage("Ueberwachung ist nicht aktiv fuer Layer {}".format(layername), 'Fehlersuche', level=Qgis.Info)
            QMessageBox.warning(None, 'Hinweis', "Ueberwachung ist nicht aktiv fuer Layer {}".format(layername))
        
     
    def check(self): 
        for f in self.iface.activeLayer().getFeatures():
            if self.has_nan_vertices(f):
                QMessageBox.warning(None, 'NaN-Vertex gefunden', 'Bitte beim Support melden. Id ist {}'.format(f.id()))
            if self.has_null_geometry(f):
                QMessageBox.warning(None, 'Nullgeometrie gefunden', 'Unbedingt gleich bereinigen. Suche nach Ausdruck: $id= {}'.format(f.id()))
    
    def has_nan_vertices(self, feature):
        geometry = feature.geometry()
        for v in geometry.vertices():
            if math.isnan(v.x()) or math.isnan(v.y()):
                return True
        return False
    def has_null_geometry(self, feature):
        geometry = feature.geometry()
        if geometry.isNull():
            return True
        return False
                
    def afterCommitChanges(self,layer):
        for f in layer.getFeatures():
            if self.has_nan_vertices(f):
                self.errors_after_commit+=1
                QMessageBox.warning(None, 'NaN-Vertex gefunden', 'Bitte beim Support melden. Id ist {}'.format(f.id()))
            if self.has_null_geometry(f):
                self.errors_after_commit+=1
                QMessageBox.warning(None, 'Nullgeometrie gefunden', 'Unbedingt gleich bereinigen. Suche nach Ausdruck: $id= {}'.format(f.id()))
        # You can optionally pass a 'tag' and a 'level' parameters
        QgsMessageLog.logMessage("errors in selected or edit buffer: {}. after commit: {}".format(self.errors_before_commit, self.errors_after_commit), 'Fehlersuche', level=Qgis.Info)

    def beforeCommitChanges(self,layer):
        self.errors_before_commit=0
        self.errors_after_commit=0
        if len(iface.activeLayer().selectedFeatures())>0:
            layer_iterator = layer.getSelectedFeatures()
        else:
            layer_iterator = layer.getFeatures()
        for f in layer_iterator:
            if self.has_nan_vertices(f):
                self.errors_before_commit+=1
                QMessageBox.warning(None, 'NaN-Vertex gefunden', 'Bitte beim Support melden. Id ist {}'.format(f.id()))
            if self.has_null_geometry(f):
                self.errors_before_commit+=1
                QMessageBox.warning(None, 'Nullgeometrie gefunden', 'Unbedingt gleich bereinigen. Suche nach Ausdruck: $id= {}'.format(f.id()))
        
        del layer_iterator
        
        buffer = layer.editBuffer()
        if buffer:
            ids = set(buffer.addedFeatures().keys())
            ids = ids.union(set(buffer.changedGeometries().keys()))
            for f in layer.getFeatures(QgsFeatureRequest().setFilterFids(list(ids))):
                if self.has_nan_vertices(f):
                    self.errors_before_commit+=1
                    QMessageBox.warning(None, 'NaN-Vertex gefunden', 'Bitte beim Support melden. Id ist {}'.format(f.id()))
                if self.has_null_geometry(f):
                    self.errors_before_commit+=1
                    QMessageBox.warning(None, 'Nullgeometrie gefunden', 'Unbedingt gleich bereinigen. Suche nach Ausdruck: $id= {}'.format(f.id()))
