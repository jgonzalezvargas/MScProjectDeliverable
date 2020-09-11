# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 00:00:50 2020

@author: jgonz
"""
import datetime
import random
from dates import getNewDate

class patient:
    def __init__(self, sid, g, dateofbirth, dateofdead, dead, adm):
        self.subject_id = sid
        self.gender = g
        self.dob = dateofbirth
        self.dod = dateofdead
        self.flag = dead
        self.maxadm = adm
        
    def updateAdm(self, adm):
        if adm > self.maxadm:
            self.maxadm = adm
            
    def changeDate(self, y):
        if self.dod is not None:
            self.dod = getNewDate(y,self.dod)
        if self.getDoB() < datetime.datetime.strptime(str('2000-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S'):
            y = y + random.randint(90, 100)
        self.dob = getNewDate(y,self.getmaxadm())
            
    def getDoB(self):
        return self.dob
    
    def getmaxadm(self):
        return self.maxadm
    
    def getGender(self):
        return self.gender
    
    def getDoD(self):
        return self.dod
    
    def getFlag(self):
        return self.flag