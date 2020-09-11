# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 05:28:20 2020

@author: jgonz
"""

import random
import dates as date
import datetime
import time
import process
import pandas as pd

def undo(db):
    start = time.time()
    sqllist = list()
    sqllist.append("DELETE FROM `labevents` where charttime > '2019-12-31'")
    sqllist.append("DELETE FROM `obs` where date_created > '2020-07-31 23:59:59'")
    sqllist.append("DELETE FROM `encounter_provider` where date_created > '2020-07-31 23:59:59'")
    sqllist.append("DELETE FROM `encounter` where patient_id > 10 and encounter_datetime > '2019-12-31 23:59:59'")
    sqllist.append("DELETE FROM visit where patient_id > 10 and date_started > '2019-12-31 23:59:59'")
    sqllist.append("UPDATE `person` SET dead = 0, death_date = Null, cause_of_death = Null, changed_by = Null, date_changed = Null where cause_of_death = 20672 or cause_of_death = 20673")

    for sql in sqllist:
        db.getOpenMRScursor().execute(sql)
        db.oCommit()
        
    end = time.time()
    print("Total time: ", (end - start)/60, " mins.")
        
def doctorOrNurse(provider):      
    if provider[0] == "N":
        encounter_role_id = 2
    else:
        encounter_role_id = 1
    return encounter_role_id 

def flagBloodTest(val):
    if val < 0.9:
        flag = "Patient doesn't have CoVid-19"
    elif val >= 0.9 and val <= 1.1:
        flag = "Borderline case for CoVid-19"
    else:
        flag = "Positive case for CoVid-19"
    return flag
        
def getProviders(db):
    sql_get_providers = ('SELECT provider_id, name as identification from provider where provider_id > 31')
    df_providers = pd.read_sql(sql_get_providers, db.getOpenMRSconnection())
    providers = process.providers(df_providers)
    return providers
    
def casesVisits(db, indexCases, cases, resultCase):
    visit = list()
    for person in indexCases:
        case = cases[person]
        room = 2
        
        dicttime = {"Positive":case.getDiagDate(), "Suspicious":case.getDiagDate(), "Recovery":case.getLastEncounter(), "Healthy":case.getLastEncounter()}
        admittime = dicttime[resultCase]
        dischtime = date.incubation(1, admittime)
        
        conceptid = {"Positive":20672, "Suspicious":20673, "Recovery":20674, "Healthy":20674}
        concept_id = conceptid[resultCase]
        
        val_visit = (person, 1, admittime, dischtime, concept_id, room, 1, datetime.datetime.now())       
        visit.append(val_visit)
        
    sql_visit = "INSERT INTO visit (patient_id, visit_type_id, date_started, date_stopped, indication_concept_id, location_id, creator, date_created, uuid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,uuid())"
    db.getOpenMRScursor().executemany(sql_visit, visit)
    last_visit_id = db.getOpenMRScursor().lastrowid
    db.oCommit()
    return last_visit_id 
    
def casesEncounter(db, indexCases, cases, visitid, status):
    encounter = list()
    etype = 5
    room = 2
    for personid in indexCases:
        case = cases[personid]
        
        dicttime = {'Positive':case.getDiagDate(), 'Suspicious':case.getDiagDate(), 'Recovery':case.getLastEncounter(), 'Healthy':case.getLastEncounter()}
        admittime = dicttime[status]
        
        val_encounter = (etype, personid, room, 1, admittime, 1, datetime.datetime.now(), visitid)
        encounter.append(val_encounter)
        visitid += 1
    sql_encounter = "INSERT INTO encounter (encounter_type, patient_id, location_id, form_id, encounter_datetime, creator, date_created, visit_id, uuid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,uuid())"
    db.getOpenMRScursor().executemany(sql_encounter, encounter)
    last_encounter_id = db.getOpenMRScursor().lastrowid
    db.oCommit()
    return last_encounter_id
    
def positiveCasesObs(db, activeCases, cases, encounterid, providers):
    ecnounter_provider = list()
    obs = list()
    labresults = list()
    random.seed(13)
    for personid in activeCases:
        case = cases[personid]
        provider_id = random.randint(32, 59)
        provider = providers[provider_id]
        encounter_role_id = doctorOrNurse(provider)
        
        val_e_provider = (encounterid, provider_id, encounter_role_id, 1,datetime.datetime.now())        
        ecnounter_provider.append(val_e_provider)
    
        #------------------------------------------------------------------
        #OBS---------------------------------------------------------------
        #------------------------------------------------------------------
        room = 2
        concept_id = 20672
        diag = "Patient has CoVid-19"
        val_obs = (personid, concept_id, encounterid, case.getDiagDate(), room, diag, 1, datetime.datetime.now())  
        obs.append(val_obs)
        
        #LAB
        i = random.randint(1,2)
        if i == 1:
            #PCR
            val = 1
            itemid = random.randint(51560,51561)
            valueuom = "%"
            flag = "Patient has CoVid-19"
            val = (personid, encounterid, itemid, case.getDiagDate(), str(val), val, valueuom, flag)
            labresults.append(val)
        else:
            #Blood Test
            valIgG = round(random.uniform(0.9, 10.0), 1)
            valIgM = round(random.uniform(0.9, 10.0), 1)
            valueuom = "g/L"
            flagIgG = flagBloodTest(valIgG)
            flagIgM = flagBloodTest(valIgM)
            itemidIgG = 51557
            itemidIgM = 51558
            val = (personid, encounterid, itemidIgG, case.getDiagDate(), str(valIgG), valIgG, valueuom, flagIgG)
            labresults.append(val)
            val = (personid, encounterid, itemidIgM, case.getDiagDate(), str(valIgM), valIgM, valueuom, flagIgM)
            labresults.append(val)
        encounterid += 1
        
        
    sql_encounter_provider = "INSERT INTO encounter_provider (encounter_id, provider_id, encounter_role_id, creator, date_created, uuid) VALUES (%s,%s,%s,%s,%s,uuid())"
    db.getOpenMRScursor().executemany(sql_encounter_provider, ecnounter_provider)
    db.oCommit()
    
    sql_obs = "INSERT INTO obs (person_id, concept_id, encounter_id, obs_datetime, location_id, comments, creator, date_created, uuid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,uuid())"
    db.getOpenMRScursor().executemany(sql_obs, obs)
    db.oCommit()
    
    sql_lab = "INSERT INTO labevents (patient_id, encounter_id, item_id, charttime, value, valuenum, valueuom, flag) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    db.getOpenMRScursor().executemany(sql_lab, labresults)
    db.oCommit()

def recoveryCasesObs(db, recoveryCases, cases, encounterid, providers, status):
    ecnounter_provider = list()
    obs = list()
    labresults = list()
    random.seed(13)
    for personid in recoveryCases:
        case = cases[personid]
        provider_id = random.randint(32, 59)
        provider = providers[provider_id]
        encounter_role_id = doctorOrNurse(provider)
        
        val_e_provider = (encounterid, provider_id, encounter_role_id, 1,datetime.datetime.now())        
        ecnounter_provider.append(val_e_provider)
    
        #------------------------------------------------------------------
        #OBS---------------------------------------------------------------
        #------------------------------------------------------------------
        room = 2
        concept_id = 20674
        dictDiag = {"Recovery":"Patient no logner has CoVid-19", "Healthy":"Patient doesn't have CoVid-19", "History":"Patient no logner has CoVid-19"}
        diag = dictDiag[status]
        val_obs = (personid, concept_id, encounterid, case.getLastEncounter(), room, diag, 1, datetime.datetime.now())  
        obs.append(val_obs)
        
        #PCR
        val = 0
        itemid = random.randint(51560,51561)
        valueuom = "%"
        flag = "Patient doesn't have CoVid-19"
        val = (personid, encounterid, itemid, case.getLastEncounter(), str(val), val, valueuom, flag)
        labresults.append(val)
        
        #LAB
        i = random.randint(1,2)
        if i == 1:
            #Blood Test
            if status == "Healthy":
                valIgG = round(random.uniform(0.0, 1.1), 1)
                valIgM = round(random.uniform(0.0, 1.1), 1)
            else:
                valIgG = round(random.uniform(0.9, 10.0), 1)
                valIgM = round(random.uniform(0.9, 10.0), 1)
            valueuom = "g/L"
            flagIgG = flagBloodTest(valIgG)
            flagIgM = flagBloodTest(valIgM)
            itemidIgG = 51557
            itemidIgM = 51558
            val = (personid, encounterid, itemidIgG, case.getLastEncounter(), str(valIgG), valIgG, valueuom, flagIgG)
            labresults.append(val)
            val = (personid, encounterid, itemidIgM, case.getLastEncounter(), str(valIgM), valIgM, valueuom, flagIgM)
            labresults.append(val)
        encounterid += 1
        
        
    sql_encounter_provider = "INSERT INTO encounter_provider (encounter_id, provider_id, encounter_role_id, creator, date_created, uuid) VALUES (%s,%s,%s,%s,%s,uuid())"
    db.getOpenMRScursor().executemany(sql_encounter_provider, ecnounter_provider)
    db.oCommit()
    
    sql_obs = "INSERT INTO obs (person_id, concept_id, encounter_id, obs_datetime, location_id, comments, creator, date_created, uuid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,uuid())"
    db.getOpenMRScursor().executemany(sql_obs, obs)
    db.oCommit()
    
    sql_lab = "INSERT INTO labevents (patient_id, encounter_id, item_id, charttime, value, valuenum, valueuom, flag) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    db.getOpenMRScursor().executemany(sql_lab, labresults)
    db.oCommit()

def suspiciousObs(db, indexCases, cases, encounterid, providers):
    ecnounter_provider = list()
    obs = list()
    random.seed(13)
    for personid in indexCases:
        case = cases[personid]
        provider_id = random.randint(32, 59)
        provider = providers[provider_id]
        encounter_role_id = doctorOrNurse(provider)
        
        val_e_provider = (encounterid, provider_id, encounter_role_id, 1,datetime.datetime.now())        
        ecnounter_provider.append(val_e_provider)
    
        #------------------------------------------------------------------
        #OBS---------------------------------------------------------------
        #------------------------------------------------------------------
        room = 2
        concept_id = 20673
        diag = "It is unclear if patient has CoVid-19"
        val_obs = (personid, concept_id, encounterid, case.getDiagDate(), room, diag, 1, datetime.datetime.now())  
        obs.append(val_obs)
        encounterid += 1
        
    sql_encounter_provider = "INSERT INTO encounter_provider (encounter_id, provider_id, encounter_role_id, creator, date_created, uuid) VALUES (%s,%s,%s,%s,%s,uuid())"
    db.getOpenMRScursor().executemany(sql_encounter_provider, ecnounter_provider)
    db.oCommit()
    
    sql_obs = "INSERT INTO obs (person_id, concept_id, encounter_id, obs_datetime, location_id, comments, creator, date_created, uuid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,uuid())"
    db.getOpenMRScursor().executemany(sql_obs, obs)
    db.oCommit()
        
    

def positiveCases(db, activeCases, cases):
    last_visit_id  = casesVisits(db, activeCases, cases, "Positive")
    last_encounter_id = casesEncounter(db, activeCases, cases, last_visit_id, "Positive")
    providers = getProviders(db)
    positiveCasesObs(db, activeCases, cases, last_encounter_id, providers)
    
def suspiciousCases(db, suspiciousCases, cases):
    last_visit_id  = casesVisits(db, suspiciousCases, cases, "Suspicious")
    last_encounter_id = casesEncounter(db, suspiciousCases, cases, last_visit_id, "Suspicious")
    providers = getProviders(db)
    suspiciousObs(db, suspiciousCases, cases, last_encounter_id, providers)
    
def deceasedPatients(db, deceasedPatients, cases, confirmation):
    for personid in deceasedPatients:
        case = cases[personid]
        deadDate = case.getDeadDate()
        if confirmation == True:
            cod = 20672
        else:
            cod = 20673
        sql = "UPDATE person SET dead = 1, death_date = '" + str(deadDate) + "', cause_of_death = " + str(cod) + ", changed_by = 1, date_changed = '" + str(datetime.datetime.now()) + "' WHERE person_id  = " + str(personid) + ";"
        db.getOpenMRScursor().execute(sql)
        db.oCommit()
    
def recoveryCases(db, recoveryCases, cases):
    last_visit_id  = casesVisits(db, recoveryCases, cases, "Recovery")
    last_encounter_id = casesEncounter(db, recoveryCases, cases, last_visit_id, "Recovery")
    providers = getProviders(db)
    recoveryCasesObs(db, recoveryCases, cases, last_encounter_id, providers, "Recovery")
    
def healthyCases(db, healthyCases, cases, status = "Healthy"):
    last_visit_id  = casesVisits(db, healthyCases, cases, "Healthy")
    last_encounter_id = casesEncounter(db, healthyCases, cases, last_visit_id, "Healthy")
    providers = getProviders(db)
    recoveryCasesObs(db, healthyCases, cases, last_encounter_id, providers, status)