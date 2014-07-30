# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AccuracySampler

 Plugin for generating random samples from maps for accuracy assessment
                             -------------------
        begin                : 2014-07-30
        copyright            : (C) 2014 by Chris Holden
        email                : ceholden@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os

from PyQt4 import QtCore
from PyQt4 import QtGui

from qgis.core import *

# Initialize Qt resources from file resources.py
import resources_rc

# Import dialog window
from sampler_dialog import SamplerDialog


class AccuracySampler(object):

    def __init__(self, iface):
        # Save reference to QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QtCore.QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n',
                                  'accuracy_sampler_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QtCore.QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QtCore.QCoreApplication.installTranslator(self.translator)

        # Create dialog
        self.dialog = SamplerDialog(self.iface)

    def initGui(self):
        """ Create toolbar item for plugin """
        self.show_dialog_action = QtGui.QAction(QtGui.QIcon(
            ':/plugins/accuracy_sampler/icon.png'),
            'Sample Map for Accuracy Assessment',
            self.iface.mainWindow())
        self.show_dialog_action.triggered.connect(self.show_dialog)
        self.iface.addToolBarIcon(self.show_dialog_action)

    def show_dialog(self):
        """ Show sampler dialog window """
        self.dialog.show()

    def unload(self):
        """ Shutdown by removing icons and disconnecting signals """
        # Remove toolbar icons
        self.iface.removeToolBarIcon(self.show_dialog_action)

        # Disconnect signals
        self.show_dialog_action.triggered.disconnect()

        # Unload resources
        self.dialog.unload()
        self.dialog.close()
        self.dialog = None

    def run(self):
        """ Run plugin """
        # Show dialog
        self.dialog.show()
        # Run dialog event loop
        result = self.dialog.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            pass
