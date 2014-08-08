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
from __future__ import division

import logging
import os

from PyQt4 import QtCore
from PyQt4 import QtGui

import qgis.core

from ui_sampler import Ui_AccuracyAssessSampler as Ui_Dialog

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.DEBUG,
                    datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)



# GUI class
class SamplerDialog(QtGui.QDialog, Ui_Dialog):

    # Initialize map related variables
    map_filename = os.getcwd()
    map_band = 1
    map_mask_val = [255]

    # Initialize sample variables
    total_sample_size = 0

    design = 0
    _sample_designs = ['simple_random', 'stratified_random']
    _sample_designs_has_allocation = [False, True]

    # Initialize map dataset variables
    _map_ds = None
    _map = None
    _map_size = 1

    _map_values = None
    _map_values_display = None
    _map_value_descriptions = None
    _map_value_percents = None

    def __init__(self, iface):
        QtGui.QDialog.__init__(self)

        self.iface = iface

        self.setupUi(self)
        self.setup_gui()

    def setup_gui(self):
        """ Finish setting up GUI """
        # Map open and handling
        self.edit_fname.setText(self.map_filename)
        self.spin_band.setValue(self.map_band)
        self.edit_maskval.setText(list_repr(self.map_mask_val))

        self.but_browse.clicked.connect(self.find_map)

    @QtCore.pyqtSlot()
    def find_map(self):
        """ Open file browse to find a map """
        # Setup QFileDialog
        _map_filename = self.map_filename if os.path.isdir(self.map_filename) \
            else os.path.dirname(self.map_filename)
        map_filename = str(QtGui.QFileDialog.getOpenFileName(self,
                                                             'Locate map',
                                                             _map_filename))
        self.edit_fname.setText(map_filename)

        self.gui_output_onoff(onoff=False)

# Utility methods
    def gui_reset_map(self, map_filename=None, map_band=None):
        """ Reset some GUI elements """
        if not map_filename:
            map_filename = self.map_filename
        if not map_band:
            map_band = self.map_band

        self.edit_fname.setText(map_filename)
        self.spin_band.setValue(map_band)

    def gui_output_onoff(self, onoff=True):
        """ Turn on/off buttons since we've loaded/changed map """
        self.but_raster_browse.setEnabled(onoff)
        self.cbox_save_raster.setEnabled(onoff)
        self.edit_raster_fname.setEnabled(onoff)
        self.combo_raster_format.setEnabled(onoff)

        self.but_vector_browse.setEnabled(onoff)
        self.cbox_save_vector.setEnabled(onoff)
        self.edit_vector_fname.setEnabled(onoff)
        self.combo_vector_format.setEnabled(onoff)

    def unload(self):
        """ Disconnect signals and delete resources """
        pass

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window = SamplerDialog(app)
    window.show()
    sys.exit(app.exec_())
