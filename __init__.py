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
from qgis.core import QgsFeatureRequest
from qgis.utils import iface


def classFactory(iface):
    return NanChecker(iface)


class NanChecker:
    def __init__(self, iface):
        self.iface = iface

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

    def an(self):
        try:
            self.iface.activeLayer().beforeCommitChanges.disconnect()
        except:
            pass
        self.iface.activeLayer().beforeCommitChanges.connect( lambda: self.beforeCommitChanges(self.iface.activeLayer()) )
        
        try:
            self.iface.activeLayer().committedFeaturesAdded.disconnect()
        except:
            pass
        self.iface.activeLayer().afterCommitChanges.connect( lambda: self.afterCommitChanges(self.iface.activeLayer()) )        

    
    def aus(self):
        try:
            self.iface.activeLayer().beforeCommitChanges.disconnect()
        except:
            pass
     
    def check(self): 
        for f in self.iface.activeLayer().getFeatures():
            if self.has_nan_vertices(f):
                QMessageBox.warning(None, 'Null vertices', 'Found null vertices in feature {}'.format(f.id()))
            if self.has_null_geometry(f):
                QMessageBox.warning(None, 'Null geometry', 'Found null geometry in feature {}'.format(f.id()))
    
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
        print("commis")
        for f in layer.getFeatures():
            if self.has_nan_vertices(f):
                self.errors_after_commit+=1
                QMessageBox.warning(None, 'Null vertices after commit', 'Found null vertices in feature {}'.format(f.id()))
            if self.has_null_geometry(f):
                self.errors_after_commit+=1
                QMessageBox.warning(None, 'Null geometry after commit', 'Found null geometry in feature {}'.format(f.id()))
        print("errors in selected or edit buffer: {}. after commit: {}".format(self.errors_before_commit, self.errors_after_commit))
    def beforeCommitChanges(self,layer):
        self.errors_before_commit=0
        self.errors_after_commit=0
        for f in layer.getSelectedFeatures():
            if self.has_nan_vertices(f):
                self.errors_before_commit+=1
                QMessageBox.warning(None, 'Null vertices', 'Found null vertices in feature {}'.format(f.id()))
            if self.has_null_geometry(f):
                self.errors_before_commit+=1
                QMessageBox.warning(None, 'Null geometry', 'Found null geometry in feature {}'.format(f.id()))

        buffer = layer.editBuffer()
        if buffer:
            ids = set(buffer.addedFeatures().keys())
            ids = ids.union(set(buffer.changedGeometries().keys()))
            for f in layer.getFeatures(QgsFeatureRequest().setFilterFids(list(ids))):
                if self.has_nan_vertices(f):
                    self.errors_before_commit+=1
                    QMessageBox.warning(None, 'Null vertices', 'Found null vertices in feature {}'.format(f.id()))
                if self.has_null_geometry(f):
                    self.errors_before_commit+=1
                    QMessageBox.warning(None, 'Null geometry', 'Found null geometry in feature {}'.format(f.id()))
