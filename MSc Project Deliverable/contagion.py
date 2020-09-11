# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 15:55:39 2020

@author: jgonz
"""

import pandas as pd
import datetime
import time
import random

import dates as date
from Connection.connectionWamp import ConnectionDataW

from covidCaseClass import covidCase
from coronavirusPatient import covidPatient

import contagionQueries as cq

CD = ConnectionDataW()
    
def checkLen(activeCases, suspiciousCases, healthyPeople, victims, unusedpatients, coVidCases):
    print("Active Cases:               ", len(activeCases))
    print("Suspicious Cases:           ", len(suspiciousCases))
    print("Healthy Cases:              ", len(healthyPeople))
    print("Deceased:                   ", len(victims))
    print("Unknown Cases:              ", len(unusedpatients))
    print("Total Coronavirus Cases:    ", len(coVidCases))
    print()
    
def preprocessData(df):
    patients = {}
    c = 0
    for index, row in df.iterrows():
        newpatient = covidPatient(row.person_id, row.icd, row.distance, row.latitude, row.longitude, row.score, row.age)
        patients[row.person_id] = newpatient
        c+=1
        
    return patients

def getJanuaryDate():
    i = random.randint(24, 31)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    Jdate = "2020-01-" + str(i) + " " + str(hour) + ":" + str(minute) + ":00"
    J = date.parse_date(Jdate)
    return J

def getFebruaryDate():
    i = random.randint(1, 29)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    Fdate = "2020-02-" + str(i) + " " + str(hour) + ":" + str(minute) + ":00"
    F = date.parse_date(Fdate)
    return F

def getMarchDate():
    i = random.randint(1, 31)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    Mdate = "2020-03-" + str(i) + " " + str(hour) + ":" + str(minute) + ":00"
    M = date.parse_date(Mdate)
    return M

def getAprilDate():
    i = random.randint(1, 30)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    Adate = "2020-04-" + str(i) + " " + str(hour) + ":" + str(minute) + ":00"
    A = date.parse_date(Adate)
    return A

def getMayDate():
    i = random.randint(1, 31)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    Mdate = "2020-05-" + str(i) + " " + str(hour) + ":" + str(minute) + ":00"
    M = date.parse_date(Mdate)
    return M

def getJuneDate():
    i = random.randint(1, 30)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    Jdate = "2020-06-" + str(i) + " " + str(hour) + ":" + str(minute) + ":00"
    J = date.parse_date(Jdate)
    return J

def getMonthDate(month):
    if month == "January":
        caseDate = getJanuaryDate()
    elif month == "February":
        caseDate = getFebruaryDate()
    elif month == "March":
        caseDate = getMarchDate()
    elif month == "April":
        caseDate = getAprilDate()
    elif month == "May":
        caseDate = getMayDate()
    elif month == "June":
        caseDate = getJuneDate()
    return caseDate
        
def positiveCases(activeCases, suspiciousCases, cases, month, maxCases, healthyPeople, coVidCases, unusedpatients):
    positiveCases = 0
    usedpatients = list()
    
    poscases = list()
    suscases = list()
    healthcases = list()
    for pat in unusedpatients:
        i = random.randint(0,100)
        patient = unusedpatients[pat]
        
        caseDate = getMonthDate(month)
        
        if i < patient.score:
            case = covidCase(patient.personid, "confirmed", patient.icd, patient.age)
            case.setDiagDate(caseDate)
            cases[patient.personid] = case
            positiveCases += 1
            activeCases.append(patient.personid)
            poscases.append(patient.personid)
            coVidCases.append(patient.personid)
            
        elif (month == "January") or  (month == "February") or (month == "March"):
            case = covidCase(patient.personid, "suspicious", patient.icd, patient.getAge())
            cases[patient.personid] = case
            case.setDiagDate(caseDate)
            suspiciousCases.append(patient.personid)
            suscases.append(patient.personid)
            
        else:
            case = covidCase(patient.personid, "healthy", patient.icd, patient.getAge())
            cases[patient.personid] = case
            case.setDiagDate(caseDate)
            healthyPeople.append(patient.personid)
            healthcases.append(patient.personid)
            
        usedpatients.append(patient.personid)
        if positiveCases > maxCases:
            break
    for patient in usedpatients:
        del unusedpatients[patient]
    del usedpatients
        
    cq.positiveCases(CD, poscases, cases)
    cq.suspiciousCases(CD, suscases, cases)
    cq.healthyCases(CD, healthcases, cases)
    
    return [activeCases, suspiciousCases, cases, unusedpatients, healthyPeople, coVidCases]

def deceased(indexCases, cases, minDays, maxDays, maxCases, victims, coVidCases, inputList = "confirmed"):
    deceased = 0
    toremove = list()
    for person in indexCases:
        i = random.randint(0,100)
        if i < 2 + (2 * cases[person].getICD()) + (cases[person].getAge()):
            cases[person].changeStatus("deceased")
            
            incubationDays = random.randint(minDays, maxDays)
            deadDate = date.incubation(incubationDays, cases[person].getDiagDate())
            cases[person].setDeadDate(deadDate)
            
            deceased += 1
            toremove.append(person)
            victims.append(person)
            
            if inputList == "suspicious":
                coVidCases.append(person)
        if deceased > maxCases - 1: 
            break
    
    status = {"confirmed": True, "suspicious": False}
    cq.deceasedPatients(CD, toremove, cases, status[inputList])
    for person in toremove:
        indexCases.remove(person)
    del toremove
    return [indexCases, cases, victims, coVidCases]

def unconfirmedDeath(unusedpatients, cases, month, maxCases, victims, coVidCases):
    sudden = 0
    usedpatients = list()
    for pat in unusedpatients:
        patient = unusedpatients[pat]
        i = random.randint(0,100)
        if i < 2 + (2 * patient.icd) + (patient.getAge()):
            if patient.personid not in cases:
                
                caseDate = getMonthDate(month)
                
                case = covidCase(patient.personid, "unconfirmed", patient.icd, patient.getAge(), caseDate)
                cases[patient.personid] = case
                sudden += 1
                usedpatients.append(patient.personid)
                victims.append(patient.personid)
                coVidCases.append(patient.personid)
        if sudden > maxCases - 1:
            break
    cq.deceasedPatients(CD, usedpatients, cases, False)
    for patient in usedpatients:
        del unusedpatients[patient]
    del usedpatients
    return [unusedpatients, cases, victims, coVidCases]

def recoveryCases(healthyPeople, activeCases, cases, forced, minDays, maxDays, maxCases, maxForced = 100):
    recoveries = 0
    toremove = list()
    for person in activeCases:
        i = random.randint(forced, maxForced)
        if cases[person].getStatus() == "confirmed":
            if i > 2 + (2 * cases[person].getICD()) + (cases[person].getAge()):
                cases[person].changeStatus("recovered")
                days = random.randint(minDays, maxDays)
                recoveryDate = date.incubation(days, cases[person].getLastEncounter())
                cases[person].setLastEncounter(recoveryDate)
                
                recoveries += 1
                toremove.append(person)
                healthyPeople.append(person)
        if recoveries > maxCases - 1:
            break
    cq.recoveryCases(CD, toremove, cases)
    for person in toremove:
        activeCases.remove(person)
    del toremove
    return [activeCases, cases, healthyPeople]

def testingHealthyPeople(healthyPeople, maxCases, cases):
    healthy = list()
    history = list()
    for i in range(maxCases):
        a = random.randint(0, len(healthyPeople)-1)
        personid = healthyPeople[a]
        case = cases[personid]
        if case.getStatus() == "healthy":
            healthy.append(personid)
        else:
            history.append(personid)
    cq.healthyCases(CD, healthy, cases)
    cq.healthyCases(CD, history, cases, "History")

def clearSuspicion(healthyPeople, suspiciousCases, maxDeads, cases, victims, coVidCases):
    deceased = 0
    healthy = list()
    dead = list()
    for person in suspiciousCases:
        i = random.randint(0, 100)
        if i < (2 + (2 * cases[person].getICD()) + (cases[person].getAge())) and deceased <= maxDeads:
            cases[person].changeStatus("deceased")
                
            incubationDays = random.randint(10, 20)
            deadDate = date.incubation(incubationDays, cases[person].getLastEncounter())
            cases[person].setDeadDate(deadDate)
            
            deceased += 1
            dead.append(person)
            victims.append(person)
            coVidCases.append(person)
        else:
            cases[person].changeStatus("healthy")
            days = random.randint(10, 20)
            recoveryDate = date.incubation(days, cases[person].getLastEncounter())
            cases[person].setLastEncounter(recoveryDate)
            
            healthy.append(person)
            healthyPeople.append(person)
    
    cq.deceasedPatients(CD, dead, cases, False)
    for person in dead:
        suspiciousCases.remove(person)
        
    cq.healthyCases(CD, healthy, cases)        
    for person in healthy:
        suspiciousCases.remove(person)
    
    del dead
    del healthy
    return [healthyPeople, suspiciousCases, cases, victims, coVidCases]

def unknownCases(healthyPeople, unusedpatients, maxCases, month, cases):
    healthcases = list()
    ncases = 0
    for pat in unusedpatients:
        patient = unusedpatients[pat]
        caseDate = getMonthDate(month)
        
        case = covidCase(patient.personid, "healthy", patient.icd, patient.getAge())
        cases[patient.personid] = case
        case.setDiagDate(caseDate)
        healthyPeople.append(patient.personid)
        healthcases.append(patient.personid)
            
        ncases += 1
        if ncases > maxCases:
            break
    cq.healthyCases(CD, healthcases, cases)
    for patient in healthcases:
        del unusedpatients[patient]
    del healthcases
    
    return [unusedpatients, healthyPeople]


def simulation():
    start = time.time()
    
    random.seed(13)
    
    sql = """SELECT address.person_id, count(DISTINCT obs.concept_id) as icd, 
                SQRT((address.latitude - 30.617740) * (address.latitude - 30.617740) + (address.longitude  - 114.261612) * (address.longitude  - 114.261612))*100000 as distance,
                address.latitude, address.longitude,
    
                ((((((((DATEDIFF('2020-08-02', p.birthdate) / 365.25) + (count(DISTINCT obs.concept_id))) / ((SQRT((address.latitude - 30.617740) * (address.latitude - 30.617740) + (address.longitude  - 114.261612) * (address.longitude  - 114.261612)))*100000))/(0.18/075))/77)/0.73)*100)*2)  as score,
                
                (DATEDIFF('2020-08-02', p.birthdate) / 365.25) as age
    
                FROM `person_address` as address
                INNER JOIN `person` as p on (p.person_id = address.person_id)
                INNER JOIN encounter on (encounter.patient_id = address.person_id)
                INNER JOIN obs ON (encounter.encounter_id = obs.encounter_id AND address.person_id = obs.person_id)
                
                WHERE p.dead = 0 AND p.person_id > 100000
    
                group by address.person_id
    
                order by score desc, distance asc, icd desc, address.person_id"""
                
                
    result = pd.read_sql(sql, CD.getOpenMRSconnection())
    
    print("got query")
    
    unusedpatients = preprocessData(result)
    del result
    
    activeCases = list()
    suspiciousCases = list()
    healthyPeople = list()
    victims = list()
    coVidCases = list()
    cases = {}
    
    #JANUARY
    #5806      cases -> 100
    #204      deaths -> 4
    #141  recoveries -> 2
    Jantime = time.time()
    month = "January"
    print(month)
    
    ####POSITIVE CASES
    data = positiveCases(activeCases, suspiciousCases, cases, month, 100, healthyPeople, coVidCases, unusedpatients)
    activeCases = data[0]
    suspiciousCases = data[1]
    cases = data[2]
    unusedpatients = data[3]
    healthyPeople = data[4]
    coVidCases = data[5]
    del data
    
    ####DECEASED
    data = deceased(activeCases, cases, 1, 5, 3, victims, coVidCases)
    activeCases = data[0]
    cases = data[1]
    victims = data[2]
    coVidCases = data[3]
    del data
     
    data = unconfirmedDeath(unusedpatients, cases, month, 1, victims, coVidCases)
    unusedpatients = data[0]
    cases = data[1]
    victims = data[2]
    coVidCases = data[3]
    del data
    
    ####RECOVERIES
    data = recoveryCases(healthyPeople, activeCases, cases, 0, 1, 3, 2)
    activeCases = data[0]
    cases = data[1]
    healthyPeople = data[2]
    del data
            
    checkLen(activeCases, suspiciousCases, healthyPeople, victims, unusedpatients, coVidCases)
    #Deal with leftovers before the next month
    data = recoveryCases(healthyPeople, activeCases, cases, 85, 10, 30, 1000)
    activeCases = data[0]
    cases = data[1]
    healthyPeople = data[2]
    del data
    
    data = deceased(suspiciousCases, cases, 10, 20, 5, victims, coVidCases, "suspicious")
    suspiciousCases = data[0]
    cases = data[1]
    victims = data[2]
    coVidCases = data[3]
    del data
    
    data = clearSuspicion(healthyPeople, suspiciousCases, 5, cases, victims, coVidCases)
    healthyPeople = data[0]
    suspiciousCases = data[1]
    cases = data[2]
    victims = data[3]
    coVidCases  = data[4]
    del data
    
    #FEBRUARY
    #60531 new cases    -> 1043
    #2523  new deaths   -> 50  (10 prev month, 20 confirmed, 20 unconfirmed)
    #28852 recoveries   -> 492 - (100 - 3 - 2 - 10)
    Febtime = time.time()
    month = "February"
    print(month)
    
    data = positiveCases(activeCases, suspiciousCases, cases, month, 1043, healthyPeople, coVidCases, unusedpatients)
    activeCases = data[0]
    suspiciousCases = data[1]
    cases = data[2]
    unusedpatients = data[3]
    healthyPeople = data[4]
    coVidCases = data[5]
    del data
    
    data = deceased(activeCases, cases, 1, 5, 20, victims, coVidCases)
    activeCases = data[0]
    cases = data[1]
    victims = data[2]
    coVidCases = data[3]
    del data
    
    data = unconfirmedDeath(unusedpatients, cases, month, 20, victims, coVidCases)
    unusedpatients = data[0]
    cases = data[1]
    victims = data[2]
    coVidCases = data[3]
    del data
    
    data = recoveryCases(healthyPeople, activeCases, cases, 0, 1, 3, 300)
    activeCases = data[0]
    cases = data[1]
    healthyPeople = data[2]
    del data
    
    checkLen(activeCases, suspiciousCases, healthyPeople, victims, unusedpatients, coVidCases)
    
    #Deal with leftovers before the next month
    data = recoveryCases(healthyPeople, activeCases, cases, 85, 10, 30, 1000)
    activeCases = data[0]
    cases = data[1]
    healthyPeople = data[2]
    del data
    
    data = deceased(suspiciousCases, cases, 10, 20, 10, victims, coVidCases, "suspicious")
    suspiciousCases = data[0]
    cases = data[1]
    victims = data[2]
    coVidCases = data[3]
    del data
    
    data = clearSuspicion(healthyPeople, suspiciousCases, 5, cases, victims, coVidCases)
    healthyPeople = data[0]
    suspiciousCases = data[1]
    cases = data[2]
    victims = data[3]
    coVidCases = data[4]
    del data
    
    #MARCH
    #1464 new cases     -> 30
    #460 new deaths     -> 10
    #34160 recoveries   -> 589
    Martime = time.time()
    month = "March"
    print(month)
    
    data = positiveCases(activeCases, suspiciousCases, cases, month, 30, healthyPeople, coVidCases, unusedpatients)
    activeCases = data[0]
    suspiciousCases = data[1]
    cases = data[2]
    unusedpatients = data[3]
    healthyPeople = data[4]
    coVidCases = data[5]
    del data
    
    data = deceased(activeCases, cases, 1, 5, 2, victims, coVidCases)
    activeCases = data[0]
    cases = data[1]
    victims = data[2]
    coVidCases = data[3]
    del data
    
    data = unconfirmedDeath(unusedpatients, cases, month, 1, victims, coVidCases)
    unusedpatients = data[0]
    cases = data[1]
    victims = data[2]
    coVidCases = data[3]
    del data
    
    data = recoveryCases(healthyPeople, activeCases, cases, 0, 1, 3, 300)
    activeCases = data[0]
    cases = data[1]
    healthyPeople = data[2]
    del data
    
    checkLen(activeCases, suspiciousCases, healthyPeople, victims, unusedpatients, coVidCases)
    
    #Deal with leftovers before the next month
    data = recoveryCases(healthyPeople, activeCases, cases, 85, 10, 30, 1000)
    activeCases = data[0]
    cases = data[1]
    healthyPeople = data[2]
    del data
    
    data = deceased(suspiciousCases, cases, 10, 20, 2, victims, coVidCases, "suspicious")
    suspiciousCases = data[0]
    cases = data[1]
    victims = data[2]
    coVidCases = data[3]
    del data
    
    data = clearSuspicion(healthyPeople, suspiciousCases, 1, cases, victims, coVidCases)
    healthyPeople = data[0]
    suspiciousCases = data[1]
    cases = data[2]
    victims = data[3]
    coVidCases = data[4]
    del data
    
    #APRIL
    #327 new cases      -> 6
    #1325 new deaths    -> 23
    #463 recoveries     -> 8
    Aprtime = time.time()
    month = "April"
    print(month)
    
    testingHealthyPeople(healthyPeople, 200, cases)
    data = unknownCases(healthyPeople, unusedpatients, 200, month, cases)
    unusedpatients = data[0]
    healthyPeople = data[1]
    del data
    
    data = positiveCases(activeCases, suspiciousCases, cases, month, 6, healthyPeople, coVidCases, unusedpatients)
    activeCases = data[0]
    suspiciousCases = data[1]
    cases = data[2]
    unusedpatients = data[3]
    healthyPeople = data[4]
    coVidCases = data[5]
    del data
    
    data = deceased(activeCases, cases, 1, 5, 15, victims, coVidCases)
    activeCases = data[0]
    cases = data[1]
    victims = data[2]
    coVidCases = data[3]
    del data
    
    data = unconfirmedDeath(unusedpatients, cases, month, 1, victims, coVidCases)
    unusedpatients = data[0]
    cases = data[1]
    victims = data[2]
    coVidCases = data[3]
    del data
    
    data = recoveryCases(healthyPeople, activeCases, cases, 0, 1, 12, 300)
    activeCases = data[0]
    cases = data[1]
    healthyPeople = data[2]
    del data
    
    checkLen(activeCases, suspiciousCases, healthyPeople, victims, unusedpatients, coVidCases)
    
    #Deal with leftovers before the next month
    data = recoveryCases(healthyPeople, activeCases, cases, 85, 10, 30, 1000)
    activeCases = data[0]
    cases = data[1]
    healthyPeople = data[2]
    del data
    
    data = deceased(suspiciousCases, cases, 10, 20, 2, victims, coVidCases, "suspicious")
    suspiciousCases = data[0]
    cases = data[1]
    victims = data[2]
    coVidCases = data[3]
    del data
    
    data = clearSuspicion(healthyPeople, suspiciousCases, 1, cases, victims, coVidCases)
    healthyPeople = data[0]
    suspiciousCases = data[1]
    cases = data[2]
    victims = data[3]
    coVidCases = data[4]
    del data
    
    #MAY
    #7 New cases        -> 1
    #0 New deaths       -> 0
    #4 recoveries       -> X/2
    Maytime = time.time()
    month = "May"
    print(month)
    
    testingHealthyPeople(healthyPeople,int( len(healthyPeople)*2/3), cases)
    data = unknownCases(healthyPeople, unusedpatients, int(len(unusedpatients)*2/3), month, cases)
    unusedpatients = data[0]
    healthyPeople = data[1]
    del data
    
    data = positiveCases(activeCases, suspiciousCases, cases, month, 1, healthyPeople, coVidCases, unusedpatients)
    activeCases = data[0]
    suspiciousCases = data[1]
    cases = data[2]
    unusedpatients = data[3]
    healthyPeople = data[4]
    coVidCases = data[5]
    del data
    
    data = recoveryCases(healthyPeople, activeCases, cases, 0, 1, 12, len(activeCases)/2)
    activeCases = data[0]
    cases = data[1]
    healthyPeople = data[2]
    del data
    
    checkLen(activeCases, suspiciousCases, healthyPeople, victims, unusedpatients, coVidCases)
    
    #JUNE
    #0 new cases
    #0 new deaths
    #3 Recoveries
    Juntime = time.time()
    month = "June"
    print(month)
    
    testingHealthyPeople(healthyPeople, int(len(healthyPeople)*2/3), cases)        
    data = unknownCases(healthyPeople, unusedpatients, int(len(unusedpatients)), month, cases)
    unusedpatients = data[0]
    healthyPeople = data[1]
    del data
    
    data = recoveryCases(healthyPeople, activeCases, cases, 200, 10, 30, 1000, 200)
    activeCases = data[0]
    cases = data[1]
    healthyPeople = data[2]
    del data
    
    checkLen(activeCases, suspiciousCases, healthyPeople, victims, unusedpatients, coVidCases)
    
    CD.getOpenMRSconnection().close()
    
    endtime = time.time()
                
    
    print("Start time:        ", (Jantime - start)/60, " mins.")
    print("January time:      ", (Febtime - Jantime)/60, " mins.")
    print("February time:     ", (Martime - Febtime)/60, " mins.")
    print("March time:        ", (Aprtime - Martime)/60, " mins.")
    print("April time:        ", (Maytime - Aprtime)/60, " mins.")
    print("May time:          ", (Juntime - Maytime)/60, " mins.")
    print("June time:         ", (endtime - Juntime)/60, " mins.")