# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 03:43:50 2020

@author: jgonz
"""

class covidPatient:
    def __init__(self, pid, icd, distance, latitude, longitude, score, age):
        self.personid = pid
        self.icd = icd
        self.distance = distance
        self.latitude = latitude
        self.longitude = longitude
        self.score = score
        self.age = age
        
    def getPatientID(self):
        return self.personid
    
    def getICD(self):
        return self.icd
    
    def getScore(self):
        return self.score
    
    def getAge(self):
        return self.age