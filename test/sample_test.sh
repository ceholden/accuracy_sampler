#!/bin/bash

../script/sample_map.py -v \
    --size 110 --allocation "10, 10, 10, 50, 10, 10, 10" \
    --mask 0 --ndv 255 \
    --raster test.gtif --vector test.shp \
    --seed 10000 \
    stratified LC_20050101_coded

../script/sample_map.py -v \
    --size 110 \
    --mask 0 --ndv 255 \
    --raster test.gtif --vector test.shp \
    --seed 10000 \
    simple LC_20050101_coded
