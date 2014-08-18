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

    # Information about class_map
    class_map = None
    classes = None
    class_count = None
    class_freq = None
    class_proportion = None

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

    def __init__(self, class_map, n_samples, nodata=None):
        """ Initializse with some number of samples in the design

        Args:
          class_map (ndarray):      a NumPy 2D array of the classification map
          n_samples (int):          number of samples
          nodata (int, optional):   NoData value for the map
        """
        self.class_map = class_map
        self.n_samples = n_samples
        self.nodata = nodata

        # Extra properties from class_map
        self.process_class_map()

    def process_class_map(self):
        """ Extra properties from class_map

        Extracts the:
            - classes
            - number of classes
            - class frequency
            - class proportion of total map

        """
        # Get classes and total number of valid pixels
        if isinstance(self.nodata, (list, np.ndarray)):
            # Get values not matching anything in self.nodata
            unmasked = self.class_map != self.nodata[0]
            for nodata in self.nodata[1:]:
                unmasked = np.logical_and(unmasked,
                                          self.class_map != nodata)

            self.classes = np.unique(self.class_map[unmasked])
            n_valid_pixels = unmasked.sum()
        elif isinstance(self.nodata, int):
            self.classes = np.unique(
                self.class_map[self.class_map != self.nodata])
            n_valid_pixels = (self.class_map != self.nodata).sum()
        else:
            self.classes = np.unique(self.class_map)
            n_valid_pixels = self.class_map.size

        # Number of classes
        self.class_count = self.classes.size

        # Get class frequency
        self.class_freq = np.zeros(self.classes.size)
        for i, c in enumerate(self.classes):
            self.class_freq[i] = (self.class_map == c).sum()

        # Get class proportion
        self.class_proportion = (self.class_freq.astype(np.float32) /
                                 n_valid_pixels)

    @abc.abstractmethod
    def sample_map(self, seed=None):
        """ Perform a stratified random sample on the map

        Args:
          seed (int, optional):     specify seed for RNG

        Returns:
          samples (ndarray):        Samples for each strata
        """
        pass

    def allocate(self, n_samples, allocation=None):
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
        super(self.__class__, self).__init__()

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
        s = "A stratified random probability sample of {n} samples for " \
            "{c} classes".format(n=self.n_samples,
                                 c=self.class_count)
        return s

    def __init__(self, class_map, n_samples, nodata=None):
        """ Initializse with some number of samples in the design

        Args:
          class_map (ndarray):      a NumPy 2D array of the classification map
          n_samples (int):          number of samples
          nodata (int, optional):   NoData value for the map
        """
        super(self.__class__, self).__init__(
            class_map, n_samples, nodata)

        # Allocate our samples initially
        self.allocate(self._allocation_prop)

    def allocate(self, allocation):
        """ Allocate number of samples to map categories based on type

        Args:
            allocation_type (int):  code corresponding to allocation_str

        """
        if self.n_samples < self.class_count:
            raise ValueError('Number of samples cannot be less than number'
                             ' of classes')

        if allocation == self._allocation_prop:
            logger.info('Allocating samples proportional to area')
            self._allocate_prop()
        elif allocation == self._allocation_equal:
            logger.info('Allocating samples to all strata equally')
            self._allocate_equal()
        elif allocation == self._allocation_user:
            logger.warning('No allocation method user specified allocation')

    def _allocate_prop(self):
        """ Allocation samples proportional to area

        Number of samples allocated will be rounded up or down, with any
        remainder allocated to last class.

        """
        self.samples = np.zeros(self.class_count, dtype=np.uint32)

        # Keep counter to make sure we have samples left to allocate
        remaining = self.n_samples

        for i, prop in enumerate(self.class_proportion):
            n = round(self.n_samples * prop)

            if n > remaining:
                n = remaining

            remaining -= n

            self.samples[i] = n

        assert self.samples.sum() == self.n_samples, \
            "Error in proportional allocation"

    def _allocate_equal(self):
        """ Allocate samples equally across all strata

        If number of samples is not evenly divisible by the number of classes,
        then extra samples are allocated to the first classes.

        """
        # How many samples per class?
        n_per = int(self.n_samples / self.class_count)

        # Allocate base amount
        self.samples = np.ones(self.class_count, dtype=np.uint32) * n_per

        # Allocate extra
        remaining = self.n_samples % self.class_count
        if remaining != 0:
            for i in range(remaining):
                self.samples[i] += 1

        assert self.samples.sum() == self.n_samples, \
            "Error in equal allocation"

    def sample_map(self, n_samples, seed=None):
        """ Perform a stratified random sample on the map

        Args:
          n_samples (int):          number of samples
          seed (int, optional):     specify seed for RNG

        Returns:
          samples (ndarray):        Samples for each strata
        """
        pass



