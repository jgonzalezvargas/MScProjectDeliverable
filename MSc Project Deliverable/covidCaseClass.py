# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 20:59:42 2020

@author: jgonz
"""

class covidCase:
    def __init__(self, pid, status, icd, age, dDate = None):
        self.personid = pid
        self.status = status
        self.icd = icd
        self.lastEncounter = None
        self.deadDate = dDate
        self.diagDate = None
        self.age = age
        
    def getAge(self):
        return self.age
        
    def getICD(self):
        return self.icd
    
    def setDiagDate(self, date):
        self.diagDate = date
        self.lastEncounter = date
        
    def setDeadDate(self, date):
        self.deadDate = date
        
    def getDeadDate(self):
        return self.deadDate
    
    def changeStatus(self, status):
        self.status = status
        if self.status == "confirmed":
            self.history = True
        
    def getStatus(self):
        return self.status
    
    def getDiagDate(self):
        return self.diagDate
    
    def getLastEncounter(self):
        return self.lastEncounter
    
    def setLastEncounter(self, date):
        self.lastEncounter = date
        