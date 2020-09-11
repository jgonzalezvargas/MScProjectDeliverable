# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 08:40:04 2020

@author: jgonz
"""
import random
from shapely.geometry import Polygon, Point

def random_points_within(poly, num_points, seed = None):
    if seed:
        random.seed(seed)
    min_x, min_y, max_x, max_y = poly.bounds

    points = []

    while len(points) < num_points:
        random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
        if (random_point.within(poly)):
            points.append(random_point)

    return points