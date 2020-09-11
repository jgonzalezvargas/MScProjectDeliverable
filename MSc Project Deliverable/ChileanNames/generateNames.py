# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 16:51:47 2020

@author: jgonz
"""

import pandas as pd
from random import random 
import numpy as np


class CLnames:
    def __init__(self):
        self.surname = list()
        self.surnameFrequency = list()
        
        self.namesM = list()
        self.namesMFrequency = list()
        
        self.namesF = list()
        self.namesFFrequency = list()
        
        self.initiateSurnames()
        self.initiateNames()
        
    def weighted_choice(self, objects, weights):
        #https://www.python-course.eu/weighted_choice_and_sample.php
        """ returns randomly an element from the sequence of 'objects', 
            the likelihood of the objects is weighted according 
            to the sequence of 'weights', i.e. percentages."""
    
        weights = np.array(weights, dtype=np.float64)
        sum_of_weights = weights.sum()
        # standardization:
        np.multiply(weights, 1 / sum_of_weights, weights)
        weights = weights.cumsum()
        x = random()
        for i in range(len(weights)):
            if x < weights[i]:
                return objects[i]
        
    def initiateSurnames(self):
        df = pd.read_excel(r'ChileanSurnames.xlsx')
        for index, row in df.iterrows():
            self.surname.append(row.Surname)
            self.surnameFrequency.append(row.Incidence)
        
    def initiateNames(self):
        df = pd.read_csv(r'NombresM2019.csv', encoding='latin-1')
        for index, row in df.iterrows():
            self.namesM.append(row.Nombre)
            self.namesMFrequency.append(row.Total)
        #total = sum(df.Total)
        #self.weightsName= [ round(freq / total, 2) for freq in self.namesFrequency]
        df = pd.read_csv(r'NombresF2019.csv', encoding='latin-1')
        for index, row in df.iterrows():
            self.namesF.append(row.Nombre)
            self.namesFFrequency.append(row.Total)
    
    def getSurname(self):
        return self.surname
    
    def getSurnameFrequency(self):
        return self.surnameFrequency
    
    def getNameM(self):
        return self.namesM
    
    def getNameF(self):
        return self.namesF
    
    def getNameMFrequency(self):
        return self.namesMFrequency
    
    def getNameFFrequency(self):
        return self.namesFFrequency
    
    def generateName(self, gender = 'male'):
        if gender == 'male':
            return self.weighted_choice(self.getNameM(), self.getNameMFrequency())
        else:
            return self.weighted_choice(self.getNameF(), self.getNameFFrequency())
    
    def generateSurname(self):
        return self.weighted_choice(self.getSurname(), self.getSurnameFrequency())
    
    def generateFullName(self, gender):
        return self.generateName(gender) + str(" ") + self.generateName(gender) + str(" ") + self.generateSurname() + str(" ") + self.generateSurname()