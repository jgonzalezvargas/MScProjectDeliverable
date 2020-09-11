# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 14:51:40 2020

@author: jgonz
"""
import random
import io
import pandas as pd
from geopy.geocoders import Nominatim
from Locations import poligons
from Locations import randomPoints
import time

class addressesCSV:
    def __init__(self, seed = None):
        if seed:
            random.seed(seed)
        print("address")
    
    def createFile(self):
        points = randomPoints.random_points_within(poligons.polyCN, 3600)
        locator = Nominatim(user_agent="myGeocoder")
        wuhanAddresses = open("wuhanAddresses.csv","w",encoding="utf-8")
        
        row = str('address1') + str(";") + str('address2') + str(";") + str('city') + str(";") + str('state') + str(";") + str('postcode') + str(";") + str('country')
        wuhanAddresses.write(row)
        wuhanAddresses.write("\n")
        
        for i in range(len(points)):
            lat = points[i].x
            long = points[i].y
            coordinates = str(lat) + str(", ") + str(long)
            location = locator.reverse(coordinates)
            l = location.raw
            address1 = str(location.address)
            print(address1)
            try:
                address2 = str(l['address']['state_district'])
            except:
                address2 = str('武汉市')
            try:
                city = str(l['address']['city'])
            except:
                city = str('关东街道')
            try:
                state = str(l['address']['state'])
            except:
                state = str('湖北省')
                
            try:
                postcode = str(l['address']['postcode'])
            except:
                postcode = str('430050')
                
            try:
                country = str(l['address']['country'])
            except:
                country = str('country')
                
            row = address1 + str(";") + address2 + str(";") + city + str(";") + state + str(";") + postcode + str(";") + country
            print(row)
            wuhanAddresses.write(row)
            wuhanAddresses.write("\n")
            time.sleep(1)
                    
            
    def loadCSV(self):
        df_addresses = pd.read_csv('wuhanAddresses.csv', delimiter = ';')
        addresses= []
        for index, row in df_addresses.iterrows():
            address = {}
            address['address1'] = row.address1
            address['address2'] = row.address2
            address['city'] = row.city
            address['state'] = row.state
            address['postcode'] = row.postcode
            address['country'] = row.country
            addresses.append(address)
        self.addressLists = addresses
    
    def getAddresses(self):
        return self.addressLists
    
    def randomAddress(self):
        maxnum = len(self.addressLists) -1
        i = random.randint(0, maxnum)
        return self.addressLists[i]
    
        