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


class SamplerDialog(QtGui.QDialog, Ui_Dialog):

    def __init__(self, iface):
        QtGui.QDialog.__init__(self)

        self.iface = iface

        self.setupUi(self)

    def unload(self):
        """ Disconnect signals and delete resources """
        pass

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window = SamplerDialog(app)
    window.show()
    sys.exit(app.exec_())
