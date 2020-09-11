# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 00:36:59 2020

@author: jgonz
"""
import random
import geopy
from shapely.geometry import Polygon
from Locations import poligons
from Locations import randomPoints
from geopy.geocoders import Nominatim
import datetime
from addresscsv import addressesCSV

def countryUnknown(pat_id):
    addressList = list()
    points = randomPoints.random_points_within(poligons.polyCL, len(pat_id))
    
    i = 0
    for subject_id in pat_id:
        lat = points[i].x
        long = points[i].y
        pat_address = (pat_id[subject_id], 1, 
                       str("This is my address"), 
                       str("This is my address pt 2"), 
                       str("This is my city"), str("This is my state"), 0, str("This is my country"), 
                       lat, long, datetime.datetime.now(), 1, datetime.datetime.now())
        addressList.append(pat_address)
        i += 1
    return addressList

def country_CL(pat_id, locator):
    addressList = list()
    points = randomPoints.random_points_within(poligons.polyCL, len(pat_id))
    
    i = 0
    for subject_id in pat_id:
        lat = points[i].x
        long = points[i].y
        coordinates = str(lat) + str(", ") + str(long)
        location = locator.reverse(coordinates)
        l = location.raw
        
        pat_address = (pat_id[subject_id], 1, 
                       str(location.address), 
                       str("Santiago"), 
                       str("Santiago"), str(l['address']['state']), 0, str(l['address']['country']), 
                       lat, long, datetime.datetime.now(), 1, datetime.datetime.now())
        addressList.append(pat_address)
        i += 1
    return addressList
    

def country_CN(pat_id, locator):
    addressList = list()
    addressList = list()
    points = randomPoints.random_points_within(poligons.polyCN, len(pat_id))
    
    address = addressesCSV()
    address.loadCSV()
    
    i = 0
    for subject_id in pat_id:
        lat = points[i].x
        long = points[i].y
        
        patient_address = address.randomAddress()
        
        pat_address = (pat_id[subject_id], 1, str(patient_address['address1']), str(patient_address['address2']), str(patient_address['city']), str(patient_address['state']), 0, str(patient_address['country']), lat, long, datetime.datetime.now(), 1, datetime.datetime.now())
        addressList.append(pat_address)
        i += 1
    return addressList

def addAddress(pat_id, CD, country = "CN"):
    locator = Nominatim(user_agent="myGeocoder")
    
    if country == "CN":
        addressList = country_CN(pat_id, locator)
        
    if country == "CL":
        addressList = country_CL(pat_id, locator)
        
    if country == "Unknown":
        addressList = countryUnknown(pat_id)
    
    
    sql_visit = "INSERT INTO person_address (person_id, preferred, address1, address2, city_village, state_province, postal_code, country, latitude, longitude, start_date, creator, date_created, uuid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,uuid())"
    CD.getOpenMRScursor().executemany(sql_visit, addressList)
    CD.oCommit()