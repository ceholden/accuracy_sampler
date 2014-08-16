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

import abc
import logging

import numpy as np

logger = logging.getLogger(__name__)


class SampleDesign(object):

    __metaclass__ = abc.ABCMeta

    # Samples from probability sample
    n_samples = None
    samples = None

    # Information on need for radio buttons
    has_allocation = False
    allocation = None
    allocation_str = None

    # Other information
    nodata = None
    seed = None

    def __repr__(self):
        return "A probability sample"

    def __init__(self, classmap, nodata=None):
        """ Initializse with some number of samples in the design

        Args:
          class_map (ndarray):      a NumPy 2D array of the classification map
          nodata (int, optional):   NoData value for the map
        """
        self.classmap = classmap
        self.nodata = nodata

        # Extra properties from classmap
        self.process_classmap()

    def process_classmap(self):
        """ Extra properties from classmap

        Extracts the:
            - number of classes
            - class frequency
            - class proportion of total map

        """

    @abc.abstractmethod
    def sample_map(self, seed=None):
        """ Perform a stratified random sample on the map

        Args:
          seed (int, optional):     specify seed for RNG

        Returns:
          samples (ndarray):        Samples for each strata
        """
        pass

    def allocate(self, n_samples, allocation):
        """ Allocate samples according to some strategy

        Args:
            allocation (int):       allocation type

        """
        pass


class SimpleRandomDesign(SampleDesign):

    def __repr__(self):
        return "A simple random probability sample"

    def __init__(self, n_samples):
        """ Initialize a simple random with some number of samples """
        super(SampleDesign, self).__init__()

        raise NotImplementedError

    def sample_map(self, n_samples, seed=None):
        """ Perform a stratified random sample on the map

        Args:
          n_samples (int):          number of samples
          seed (int, optional):     specify seed for RNG

        Returns:
          samples (ndarray):        Samples for each strata
        """
        pass


class StratifiedRandomSample(SampleDesign):

    # Allocation information
    has_allocation = True
    # Default to proportional to area allocation
    allocation = 0
    allocation_str = ['Proportional to area',
                      'Equal allocation',
                      'User specified']
    _allocation_prop = 0
    _allocation_equal = 1
    _allocation_user = 2

    def __repr__(self):
        return "A stratified random probability sample"

    def __init__(self, classmap, nodata=None):
        """ Initializse with some number of samples in the design

        Args:
          class_map (ndarray):      a NumPy 2D array of the classification map
          nodata (int, optional):   NoData value for the map
        """
        super(SampleDesign, self).__init__()

        # Allocate our samples initially
        self.allocate(self.allocation)

    def allocate(self, n_samples, allocation):
        """ Allocate number of samples to map categories based on type

        Args:
            n_samples (int):        number of samples
            allocation_type (int):  code corresponding to allocation_str

        """
        if n_samples < 1:
            raise ValueError('Number of samples cannot be less than 1')

        if allocation == self._allocation_prop:
            logger.info('Allocating samples proportional to area')
            self._allocate_prop()
        elif allocation == self._allocation_equal:
            logger.info('Allocating samples to all strata equally')
            self._allocate_equal()
        elif allocation == self._allocation_user:
            logger.warning('No allocation method user specified allocation')

    def _allocate_prop(self):
        """ Al

    def sample_map(self, n_samples, seed=None):
        """ Perform a stratified random sample on the map

        Args:
          n_samples (int):          number of samples
          seed (int, optional):     specify seed for RNG

        Returns:
          samples (ndarray):        Samples for each strata
        """
        pass



