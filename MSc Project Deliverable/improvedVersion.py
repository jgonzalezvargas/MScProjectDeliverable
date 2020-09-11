# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 02:33:47 2020

@author: jgonz
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 00:00:21 2020

@author: jgonz
"""

import pandas as pd
import datetime
import time
import random

from patient import patient
import dates as date
import process
from ec import exceptions_conditions
from Connection.connectionWamp import ConnectionDataW
from addAdresses import addAddress
from addPatients import addPatient
from ChineseNames.generateNames import CNnames

import itemvalues

CD = ConnectionDataW()

country = 'CN'
namesGenerator = CNnames()


def whatTimeIsItRightNow():
    print(datetime.datetime.fromtimestamp(time.time()).isoformat())

whatTimeIsItRightNow()

def addPatients(df):
    person = list()
    added_patient = list()
    patientList = {}
    patient_years = {}
    for index, row in df.iterrows():
        sid = row.SUBJECT_ID
        admittime = date.parse_date(row.ADMITTIME)
        #Create patient
        if sid not in added_patient:
            dob = date.parse_date(row.DOB)
            if row.EXPIRE_FLAG == 1:
                dod = date.parse_date(row.DOD)
            else:
                dod = None
            pat = patient(sid, row.GENDER, dob, dod, row.EXPIRE_FLAG, admittime)
            patientList[sid] = pat
            added_patient.append(sid)
        else:
            patientList[sid].updateAdm(admittime)
        
    ##########################################
    for sid in patientList:
        maxdate = patientList[sid].getmaxadm()
        yeardif = date.generateYearDif(maxdate)
        patient_years[sid] = yeardif
        patientList[sid].changeDate(yeardif)
        val = (patientList[sid].getGender(), patientList[sid].getDoB(), patientList[sid].getFlag(), patientList[sid].getDoD(), 1, datetime.datetime.now())
        person.append(val)
    returndata = [person, added_patient, patient_years]
    return returndata

def map_ids(listofids, lastid):
    mapofid = {}
    newid = lastid #- len(listofids) + 1
    for k in listofids:
        mapofid[k] = newid
        newid += 1
    return mapofid
      
def patients_to_obs(df, concepts, providers, namesGenerator):
    person_name = list()
    patient = list()
    patient_identifier = list()
    visit = list()
    encounter = list()
    ecnounter_provider = list()
    obs = list()

    identifier = 900
    
    ###########################################################################
    ######################ADDING#PERSONS#######################################
    ###########################################################################
    print("Persons")
    whatTimeIsItRightNow()
    time_addindg_patients_start = time.time()

    retdata = addPatients(df)
    person = retdata[0]
    added_patient = retdata[1]
    pat_year = retdata[2]
    
    sql_person = "INSERT INTO person(gender,birthdate,dead, death_date,creator,date_created, uuid) VALUES (%s, %s, %s, %s, %s, %s, uuid())"
    CD.getOpenMRScursor().executemany(sql_person, person)
    CD.oCommit()
    #added_people = openmrscursor.rowcount
    last_person_id = CD.getOpenMRScursor().lastrowid
    print("Last Person ID: ", last_person_id, " Added Patients: ", len(added_patient))
    
    subjectid_to_personid = map_ids(added_patient, last_person_id)
    time_addindg_patients_end = time.time()
    time_addindg_patients = (time_addindg_patients_end - time_addindg_patients_start)/60
    
    ###########################################################################
    ####################ADDRESSES##############################################
    ###########################################################################
    addressTimeS = time.time()
    addAddress(subjectid_to_personid, CD, country)
    addressTimeE = time.time()
    addressTime = (addressTimeE - addressTimeS)/60
    
    
    ###########################################################################
    ############PATIENT#PATIENTID#NAME#VISIT###################################
    ###########################################################################
    print("Patient, Patient identifier & visit")
    whatTimeIsItRightNow()
    time_addindg_patients_name_visit_start = time.time()
    
    added_admissions = list()
    added_patient = list()
    
    for index, row in df.iterrows():
        if row.SUBJECT_ID not in added_patient:
            addedpatientdata = addPatient(row, added_patient, subjectid_to_personid, patient, identifier, patient_identifier, person_name, namesGenerator, country)
            #print(addedpatientdata)
            patient = addedpatientdata['patient']
            identifier = addedpatientdata['identifier']
            patient_identifier = addedpatientdata['patientIdentifier']
            person_name = addedpatientdata['personName']
            added_patient = addedpatientdata['addedPatient']
        
        
        #VISITS
        if row.HADM_ID not in added_admissions and row.ICD9_CODE not in exceptions_conditions:
            if row.ADMISSION_LOCATION == "EMERGENCY ROOM ADMIT":
                room = 2
            elif row.ADMISSION_LOCATION == "CLINIC REFERRAL/PREMATURE":
                room = 3
            elif row.ADMISSION_LOCATION == "PHYS REFERRAL/NORMAL DELI":
                room = 4
            elif row.ADMISSION_LOCATION == "TRANSFER FROM HOSP/EXTRAM":
                room = 5
            else:
                room = 6
                
            admittimep = date.parse_date(row.ADMITTIME)
            dischtimep = date.parse_date(row.DISCHTIME)
            
            admittime = date.getNewDate(pat_year[row.SUBJECT_ID], admittimep)
            dischtime = date.getNewDate(pat_year[row.SUBJECT_ID], dischtimep)
    
            concept_id = concepts[row.ICD9_CODE]
            val_visit = (subjectid_to_personid[row.SUBJECT_ID], 1, admittime, dischtime, concept_id, room, 1, datetime.datetime.now())       
            visit.append(val_visit)
            
            added_admissions.append(row.HADM_ID)
        
    whatTimeIsItRightNow()        
    sql_pat = "INSERT INTO  patient (patient_id, date_created, creator) VALUES (%s, %s, %s)"
    #print(patient)
    CD.getOpenMRScursor().executemany(sql_pat, patient)
    CD.oCommit()
    
    whatTimeIsItRightNow()
    sql_pat_id = "INSERT INTO  patient_identifier (patient_id, identifier, identifier_type, date_created, creator, location_id, uuid) VALUES (%s,%s, %s, %s, %s, %s, uuid())"
    CD.getOpenMRScursor().executemany(sql_pat_id, patient_identifier)
    CD.oCommit()
    
    whatTimeIsItRightNow()
    sql_names = "INSERT INTO person_name (person_id, prefix, given_name, middle_name, family_name, creator, date_created, uuid) VALUES (%s,%s,%s,%s,%s,%s,%s,uuid())"
    CD.getOpenMRScursor().executemany(sql_names, person_name)
    CD.oCommit()

    whatTimeIsItRightNow()
    sql_visit = "INSERT INTO visit (patient_id, visit_type_id, date_started, date_stopped, indication_concept_id, location_id, creator, date_created, uuid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,uuid())"
    CD.getOpenMRScursor().executemany(sql_visit, visit)
    last_visit_id = CD.getOpenMRScursor().lastrowid
    CD.oCommit()
    
    admid_to_visitid = map_ids(added_admissions, last_visit_id)
    
    time_addindg_patients_name_visit_end = time.time()
    time_addindg_patients_name_visit = (time_addindg_patients_name_visit_end - time_addindg_patients_name_visit_start)/60
    
    
    ###########################################################################
    ##################ENCOUNTERS###############################################
    ###########################################################################
    print("Encounters")
    whatTimeIsItRightNow()
    time_addindg_encounters_start = time.time()
    
    
    added_encounters = list()
    for index, row in df.iterrows():
        if row.HADM_ID not in added_encounters and row.ICD9_CODE not in exceptions_conditions:
            #These two can be sent to a function
            if row.ADMISSION_LOCATION == "Emergency":
                etype = 5
            elif row.ADMISSION_LOCATION == "Elective":
                etype = 6
            else:
                etype = 7
                
            if row.ADMISSION_LOCATION == "EMERGENCY ROOM ADMIT":
                    room = 2
            elif row.ADMISSION_LOCATION == "CLINIC REFERRAL/PREMATURE":
                room = 3
            elif row.ADMISSION_LOCATION == "PHYS REFERRAL/NORMAL DELI":
                room = 4
            elif row.ADMISSION_LOCATION == "TRANSFER FROM HOSP/EXTRAM":
                room = 5
            else:
                room = 6
                
            admittimep = date.parse_date(row.ADMITTIME)
            admittime = date.getNewDate(pat_year[row.SUBJECT_ID], admittimep)
            
            val_encounter = (etype, subjectid_to_personid[row.SUBJECT_ID], room, 1, admittime, 1, datetime.datetime.now(), admid_to_visitid[row.HADM_ID])
            encounter.append(val_encounter)
            
            added_encounters.append(row.HADM_ID)

    whatTimeIsItRightNow()
    sql_encounter = "INSERT INTO encounter (encounter_type, patient_id, location_id, form_id, encounter_datetime, creator, date_created, visit_id, uuid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,uuid())"
    CD.getOpenMRScursor().executemany(sql_encounter, encounter)
    last_encounter_id = CD.getOpenMRScursor().lastrowid
    CD.oCommit()
    
    admid_to_enocunter_id = map_ids(added_encounters, last_encounter_id)
    time_addindg_encounters_end = time.time()
    time_addindg_encounters = (time_addindg_encounters_end - time_addindg_encounters_start)/60
    
    
    ###########################################################################
    ##############PROVIDER#OBS#################################################
    ###########################################################################
    print("Providers & Obs")
    
    print()
    #print(admid_to_enocunter_id)
    print()
    whatTimeIsItRightNow()
    time_addindg_providers_obs_start = time.time()
    
    for index, row in df.iterrows():
        if row.ICD9_CODE not in exceptions_conditions:
            provider_id = random.randint(32, 59)
            
            provider = providers[provider_id]
            if provider[0] == "N":
                encounter_role_id = 2
            else:
                encounter_role_id = 1
            
            #encounter_role_id = random.randint(1, 2)
            val_e_provider = (admid_to_enocunter_id[row.HADM_ID], provider_id, encounter_role_id, 1,datetime.datetime.now())        
            ecnounter_provider.append(val_e_provider)

            #------------------------------------------------------------------
            #OBS---------------------------------------------------------------
            #------------------------------------------------------------------
            if row.ADMISSION_LOCATION == "EMERGENCY ROOM ADMIT":
                    room = 2
            elif row.ADMISSION_LOCATION == "CLINIC REFERRAL/PREMATURE":
                room = 3
            elif row.ADMISSION_LOCATION == "PHYS REFERRAL/NORMAL DELI":
                room = 4
            elif row.ADMISSION_LOCATION == "TRANSFER FROM HOSP/EXTRAM":
                room = 5
            else:
                room = 6
            concept_id = concepts[row.ICD9_CODE]
            val_obs = (subjectid_to_personid[row.SUBJECT_ID], concept_id, admid_to_enocunter_id[row.HADM_ID], datetime.datetime.now(), room, row.LONG_TITLE, 1, datetime.datetime.now())  
            obs.append(val_obs)
            
    whatTimeIsItRightNow()
    sql_encounter_provider = "INSERT INTO encounter_provider (encounter_id, provider_id, encounter_role_id, creator, date_created, uuid) VALUES (%s,%s,%s,%s,%s,uuid())"
    CD.getOpenMRScursor().executemany(sql_encounter_provider, ecnounter_provider)
    CD.oCommit()
    
    whatTimeIsItRightNow()
    sql_obs = "INSERT INTO obs (person_id, concept_id, encounter_id, obs_datetime, location_id, comments, creator, date_created, uuid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,uuid())"
    CD.getOpenMRScursor().executemany(sql_obs, obs)
    CD.oCommit()
    time_addindg_providers_obs_end = time.time()
    time_addindg_providers_obs = (time_addindg_providers_obs_end - time_addindg_providers_obs_start)/60
    
    data = {}
    data['patients'] = time_addindg_patients
    data['pataddress'] = addressTime
    data['patnames'] = time_addindg_patients_name_visit
    data['encoutners'] = time_addindg_encounters
    data['providers'] = time_addindg_providers_obs
    data['subjecttoperson'] = subjectid_to_personid
    data['admtoencounter'] = admid_to_enocunter_id
    data['patientsyears'] = pat_year
    #data = [time_addindg_patients, time_addindg_patients_name_visit, time_addindg_encounters, time_addindg_providers_obs, subjectid_to_personid, admid_to_enocunter_id, pat_year]
    
    return data

def value_flag(valuenum, minval, maxval):
    if valuenum < minval:
        return "low"
    elif valuenum > maxval:
        return "high"
    else:
        return "normal"
    
def def_flag(itemid, valuenum, flag):
    #test, loinc, itemid, min-max
    #wbc, 26464-8, 51300, 4-10
    #rbc, 789-8, 51279, 4.5 - 6.2
    #hemoglobin, 718-7, 50811 51222, 14 - 18
    #hematocrit, 4544-3, 51221, 40 - 54
    #mcv, 787-2, 51250, 80 - 96
    #mch, 785-6, 51248, 26 - 34
    #mchc, 786-4, 51249, 32 - 38
    #PlateletCount, 777-3, 51265, 150 - 450
    if itemid in itemvalues.itemval:
        val = value_flag(valuenum, itemvalues.itemval[itemid][0], itemvalues.itemval[itemid][1])
    else:
        val = "normal"
    if val == "low":
        flag = "abnormal low"
    elif val == "high":
        flag = "abnormal high"
    
    return flag

def lab_data(df, personiddic, admdic, pat_year):
    lab_start = time.time()
    whatTimeIsItRightNow()
    get_id_sql = "SELECT max(id) FROM labevents"
    CD.getOpenMRScursor().execute(get_id_sql)
    result = CD.getOpenMRScursor().fetchone()
    last_row = result[0]
    
    lab_events = open("labtxt.csv","w")
    
    lab_time_iter_s = time.time()
    for index, row in df.iterrows():
        #0-> row_id, 1-> subject_id, 2-> hadm_id, 3-> itemid, 4-> charttime, 5-> value, 6-> valuenum, 7-> valueuom, 8-> flag
        if row.SUBJECT_ID in personiddic and row.HADM_ID in admdic:
            charttimep = date.parse_date(row.CHARTTIME)
            charttime = date.getNewDate(pat_year[row.SUBJECT_ID], charttimep)
            
            flag = def_flag(row.ITEMID, row.VALUENUM, row.FLAG)
            
            last_row += 1
            
            labs = str(last_row) + str(";") + str(personiddic[row.SUBJECT_ID]) + str(";") + str(admdic[row.HADM_ID]) + str(";") + str(int(row.ITEMID)) + str(";") + str(charttime) + str(";") + str(row.VALUE) + str(";")  + str(row.VALUENUM) + str(";") + str(row.VALUEUOM) + str(";") + str(flag)
            lab_events.write(labs)
            lab_events.write("\n")
    lab_time_iter_e = time.time()
    
    print("LAST ROW: ", labs)
    
    sql_lab = """LOAD DATA INFILE 'c:/users/jgonz/documents/myproject/NewVersion/labtxt.csv' INTO TABLE labevents FIELDS
                TERMINATED BY ';' 
                ENCLOSED BY '"' 
                LINES TERMINATED BY '\r\n';"""
    print("loading Lab Data")
    CD.getOpenMRScursor().execute(sql_lab)
    CD.oCommit()
    
    whatTimeIsItRightNow()
    lab_end = time.time()
    lab_time = (lab_end - lab_start)/60
    lab_iter_time = (lab_time_iter_e - lab_time_iter_s)/60
    lab_file_time = (lab_end - lab_time_iter_e)/60
    data_time = [lab_time, lab_iter_time, lab_file_time]
    return data_time  
    
def dataMigration():
    start_time = time.time()
    
    sql_get_concepts = ('SELECT concept_id, short_name from concept')
    df_concepts = pd.read_sql(sql_get_concepts, CD.getOpenMRSconnection())
    concepts = process.concepts(df_concepts)
    
    
    sql_get_providers = ('SELECT provider_id, name as identification from provider where provider_id > 31')
    df_providers = pd.read_sql(sql_get_providers, CD.getOpenMRSconnection())
    providers = process.providers(df_providers)
    
    print("Getting patient  data")
    tp = time.time()
    df_patient_data = CD.patientData()
    time_query = time.time()
    
    pat_to_obs = patients_to_obs(df_patient_data, concepts, providers)
    te = time.time()
    time_creating_patients_time = (te - tp)/60
    
    print("Getting lab data")
    whatTimeIsItRightNow()
    df_lab_data = CD.getLabevets()
    CD.getMimicConnection().close()
    ta = time.time()
    time_querying_lab = (ta-te)/60
    
    subject_to_id = pat_to_obs['subjecttoperson']
    hadm_to_id = pat_to_obs['admtoencounter']
    
    lab_time = lab_data(df_lab_data, subject_to_id, hadm_to_id, pat_to_obs['patientsyears'])
    
    CD.getOpenMRSconnection().close()
    
    end_time = time.time()
    
    
    print("Total Time:                                            ", (end_time - start_time)/60, " mins.")
    print("Time to start:                                         ", (tp - start_time)/60, " mins.")
    print("Time persons query:                                    ", (time_query - tp)/60, " mins.")
    print("Time creating persons:                                 ", pat_to_obs['patients'], " mins.")
    print("Time creating persons addresses:                       ", pat_to_obs['pataddress'], " mins.")
    print("Time creating patients, identifiers, names and visits: ", pat_to_obs['patnames'], " mins.")
    print("Time creating encounters:                              ", pat_to_obs['encoutners'], " mins.")
    print("Time creating providers and obs:                       ", pat_to_obs['providers'], " mins.")
    print("Total time creating patients:                          ", time_creating_patients_time, " mins.")
    print("Time reading lab data csv:                             ", time_querying_lab, " mins.")
    print("Time creating lab:                                     ", lab_time[0], " mins.")
    print("Time iterating lab data:                               ", lab_time[1], " mins.")
    print("Time inserting lab data:                               ", lab_time[2], " mins.")