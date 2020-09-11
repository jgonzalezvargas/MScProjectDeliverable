# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 23:45:56 2020

@author: jgonz
"""

import pandas as pd
from random import random 
from random import randint
import numpy as np



class CNnames:
    def __init__(self):
        self.surname = list()
        self.surnameFrequency = list()
        
        self.namesM = list()
        self.namesF = list()
        
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
        df = pd.read_csv(r'ChineseNames\table-2.csv')
        for index, row in df.iterrows():
            self.surname.append(row.Name)
            self.surnameFrequency.append(row['% of pop.'][:-1])
        
    def initiateNames(self):
        df = pd.read_excel(r'ChineseNames\9800ChineseNamesnamegender.xlsx')
        for index, row in df.iterrows():
            if row['性别'] == '男':
                self.namesM.append(row['姓名'][0])
            else:
                self.namesF.append(row['姓名'][0])
            
    def getSurname(self):
        return self.surname
    
    def getSurnameFrequency(self):
        return self.surnameFrequency
    
    def getNameM(self):
        return self.namesM
    
    def getNameF(self):
        return self.namesF
    
    def generateName(self, gender = 'male'):
        if gender == 'male':
            x = randint(0,len(self.getNameM()) -1)
            return self.getNameM()[x]
        else:
            x = randint(0,len(self.getNameF()) -1)
            return self.getNameF()[x]
    
    def generateSurname(self):
        return self.weighted_choice(self.getSurname(), self.getSurnameFrequency())
    
    def generateFullName(self, gender):
        return self.generateName(gender) + str(" ") + self.generateName(gender) + str(" ") + self.generateSurname()