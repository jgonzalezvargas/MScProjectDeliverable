# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 00:01:50 2020

@author: jgonz
"""
import datetime
#import time
import random
from dateutil.relativedelta import relativedelta

maxyear = datetime.datetime.now().year - 1

def generateYearDif(maxadm):
    randomyears = random.randint(0, 10)
    dif = maxadm.year - maxyear + randomyears
    return dif

def getNewDate(y, oldDate):
    newDate = oldDate - relativedelta(years=y)
    return newDate

def incubation(d, originalDate):
    newDate = originalDate + relativedelta(days=d)
    return newDate

def parse_date(d):
    return datetime.datetime.strptime(str(d), '%Y-%m-%d %H:%M:%S')

def parse_date_lab(d):
    a = str(d)
    a = a[:-9]
    return datetime.datetime.strptime(str(a), '%Y-%m-%d')
    