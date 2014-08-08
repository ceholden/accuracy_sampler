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

from itertools import izip
import logging
import os

from osgeo import gdal
import numpy as np

from PyQt4 import QtCore
from PyQt4 import QtGui

import qgis.core

from ui_sampler import Ui_AccuracyAssessSampler as Ui_Dialog

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.DEBUG,
                    datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

gdal.UseExceptions()
gdal.AllRegister()


# Utilities for handling QLineEdit with lists
def list_repr(l):
    """ custom string repr for a list or numpy array using commas """
    # handle 2d arrays
    if isinstance(l, np.ndarray):
        if len(l.shape) > 1:
            l = l[0]

    return ', '.join(map(repr, l))


def str2list(s, dtype):
    """ return list parsed from space, or comma, separated string """
    l = [_s for _s in s.replace(',', ' ').split(' ') if _s != '']
    return map(dtype, l)


# GUI class
class SamplerDialog(QtGui.QDialog, Ui_Dialog):

    # Initialize map related variables
    map_filename = os.getcwd()
    map_band = 1
    map_mask_val = [255]

    # Initialize sample variables
    total_sample_size = 0

    _alloc_strat = 0
    _alloc_strat_buttons = ['rbut_alloc_prop',
                            'rbut_alloc_spec',
                            'rbut_alloc_equal']

    design = 1
    _sample_designs_buttons = ['rbut_type_simple', 'rbut_type_strat']
    _sample_designs_allocation = [None,
                                  ('_alloc_strat', '_alloc_strat_buttons')]
    _sample_designs_pages = ['page_simple', 'page_stratified']

    # Initialize map dataset variables
    _map_ds = None
    _map = None
    _map_size = 1

    _map_values = None
    _map_value_display = None
    _map_value_descriptions = None
    _map_value_percent = None

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
        self.but_loadmap.clicked.connect(self.load_map)

        ### Allocation
        # Check default design and change page
        rbutton = getattr(self, self._sample_designs_buttons[self.design])
        rbutton.setChecked(True)

        page = getattr(self, self._sample_designs_pages[self.design])
        self.stack_design.setCurrentWidget(page)

        allocation = self._sample_designs_allocation[self.design]
        if allocation:
            allocation_type = getattr(self, allocation[0])
            rbutton = getattr(self, allocation[1])
            rbutton = getattr(self, rbutton[allocation_type])

        rbutton.setChecked(True)

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

    @QtCore.pyqtSlot()
    def load_map(self):
        """ Try loading map """
        # Test specified filename and map properties
        map_filename = str(self.edit_fname.text())
        map_band = self.spin_band.value()

        # Try opening with GDAL
        try:
            self._map_ds = gdal.Open(map_filename, gdal.GA_ReadOnly)
        except:
            self.gui_reset_map()
            # TODO - QGIS message bar error
            logger.error('Cannot load map image {m}'.
                         format(m=map_filename))
            return
        else:
            if not self._map_ds:
                logger.error('Cannot load map image {m}'.
                             format(m=map_filename))
                return
            self.map_filename = map_filename
            logger.debug('Opened map dataset')

        # If we can open file, try opening band specified
        n_bands = self._map_ds.RasterCount
        if map_band > n_bands:
            logger.error('Cannot load map band {b} (image has {n})'.
                         format(b=map_band, n=n_bands))
            self.gui_reset_map()
            return

        self.map_band = map_band

        # Read in band
        self._map = self._map_ds.GetRasterBand(self.map_band).ReadAsArray()
        self.gui_output_onoff()
        logger.debug('Opened map')

        self.process_map_table()

    @QtCore.pyqtSlot()
    def process_map_table(self):
        """ Process map for allocation table """
        # Set map values and categories for table
        self.get_map_categories()
        # Calculate percentages of map for each category
        self.get_map_percents()

        # Clear table
        self.table_allocation.clear()

        self.table_allocation.setHorizontalHeaderLabels(
            ['Map Value', 'Description', 'Map Percent', 'Sample Allocation']
        )

        # Populate table
        self.table_allocation.setRowCount(len(self._map_value_display))

        for row, (val, desc, percent) in \
            enumerate(izip(self._map_value_display,
                           self._map_value_descriptions,
                           self._map_value_percent)):

            _val = QtGui.QTableWidgetItem(str(val))
            _val.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignVCenter)

            _desc = QtGui.QTableWidgetItem(desc)
            _desc.setTextAlignment(QtCore.Qt.AlignHCenter |
                                   QtCore.Qt.AlignVCenter)

            _percent = QtGui.QTableWidgetItem(str(percent))
            _percent.setTextAlignment(QtCore.Qt.AlignHCenter |
                                      QtCore.Qt.AlignVCenter)

            _alloc = QtGui.QTableWidgetItem('0')
            _alloc.setTextAlignment(QtCore.Qt.AlignHCenter |
                                    QtCore.Qt.AlignVCenter)
            _alloc.setFlags(_alloc.flags() | QtCore.Qt.ItemIsEditable)

            self.table_allocation.setItem(row, 0, _val)
            self.table_allocation.setItem(row, 1, _desc)
            self.table_allocation.setItem(row, 2, _percent)
            self.table_allocation.setItem(row, 3, _alloc)

        logger.debug('Populated table')


    def get_map_categories(self):
        """ Read the map image and find map categories """
        # Get unique values
        logger.debug('Reading in map values')
        unique_values = np.unique(self._map)
        self._map_values = unique_values.copy()

        # Get categories names
        logger.debug('Checking for map category names')
        band = self._map_ds.GetRasterBand(self.map_band)
        categories = band.GetCategoryNames()

        # Set to defaults if the map doesn't have names
        if not categories:
            logger.debug('No category names found')
            logger.debug('Setting default category names')
            self._map_value_descriptions = []
            for i, u in enumerate(unique_values):
                self._map_value_descriptions.append('Class {i}'.format(i=i))
        else:
            # Test to make sure we have descriptions for all unique values
            logger.debug('Trying to use category names from map')

            # If same size, keep values and proceed
            if len(unique_values) == len(categories):
                logger.debug('Map categories provided are suitable')
                self._map_values = unique_values
                self._map_value_descriptions = np.array(categories)
            # If more categories than values, append blank unique values
            elif len(unique_values) < len(categories):
                logger.debug('Map provides categories than unique values')

                # Check if categories' length encompasses unique value
                encompass = all([uv in range(len(categories))
                                 for uv in unique_values])

                if encompass:
                    # If it would work to be sequential, just set unique as
                    #   range(len(categories))
                    # E.g., we have mask, water, land categories
                    #       we have 0, 2 unique values
                    #       we'll end up with mask 0, water 1, land 2
                    unique_values = np.array(range(len(categories)))
                else:
                    # Use unique values, but match categories with fill
                    unique_values = np.append(unique_values,
                                              [np.nan] * (len(categories) -
                                                          len(unique_values)
                                                          )
                                              )
            # If more values than categories, ignore categories
            else:
                logger.debug('More map values than categories')
                logger.debug('Ignoring categories')
                categories = ['Class ' + str(i) for i in range(unique_values)]

            self._map_value_descriptions = list(categories)

        self._map_value_display = unique_values.copy()

        print self._map_values
        print self._map_value_display
        print self._map_value_descriptions

        assert len(self._map_value_display) == len(self._map_value_descriptions), \
            'ooops! display values not same length as descriptions'

    def get_map_percents(self):
        """ Calculate map for each class """
        # Find mask
        logger.debug('Finding ')
        mask = np.ones_like(self._map)
        for val in self.map_mask_val:
            logger.debug('    masked value {v}'.format(v=val))
            mask *= self._map != val

        # Get total number of pixcels in image
        n_pix = mask.sum()
        logger.debug('Calculated unmasked size: {n}'.format(n=n_pix))

        # Find totals per class
        totals = np.zeros(len(self._map_value_display))
        for i, val in enumerate(self._map_value_display):
            totals[i] = (self._map == val).sum()

        # Find percents
        self._map_value_percent = totals / n_pix * 100.0

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
