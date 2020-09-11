# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 00:49:56 2020

@author: jgonz
"""
import random
import datetime
import names
from ChileanNames.generateNames import CLnames
from ChineseNames.generateNames import CNnames

def USnames(g):
    if g == 'F':
        fname = names.get_first_name(gender='female')      
        prefix = "Mrs."
    else:
        fname = names.get_first_name(gender='male')
        prefix = "Mr."
    lname = names.get_last_name()
    mname = names.get_first_name()
    mname = mname[:1]
    
    data = {}
    data['prefix'] = prefix
    data['fname'] = fname
    data['mname'] = mname
    data['lname'] = lname
    return data

def CLname(g, CL):
    if g == 'F':
        fname = CL.generateName('female')      
        prefix = "Mrs."
    else:
        fname = CL.generateName('male')
        prefix = "Mr." 
    mname = CL.generateName()
    lname = CL.generateSurname()
    mname = mname[:1]
    
    data = {}
    data['prefix'] = prefix
    data['fname'] = fname
    data['mname'] = mname
    data['lname'] = lname
    return data

def CNname(g, CN):
    if g == 'F':
        fname = CN.generateName("female")      
        prefix = "Mrs."
    else:
        fname = CN.generateName("male")
        prefix = "Mr."   
    lname = CN.generateSurname()
    mname = CN.generateName()
    mname = mname[:1]
    
    data = {}
    data['prefix'] = prefix
    data['fname'] = fname
    data['mname'] = mname
    data['lname'] = lname
    return data
    
    
def addPatient(row, added_patient, subjectid_to_personid, patient, identifier, patient_identifier, person_name, namesGenerator, country = "US"):
    
    #PATIENT
    val_pat = (subjectid_to_personid[row.SUBJECT_ID], datetime.datetime.now(), 1)
    patient.append(val_pat)
    #PATIENT ID
    val_pat_id = (subjectid_to_personid[row.SUBJECT_ID], identifier, 2, datetime.datetime.now(),1,1)
    identifier += 1 
    patient_identifier.append(val_pat_id)
    #PERSON NAME
    if country == 'US':
        personName = USnames(row.GENDER)
    elif country == 'CL':
        personName = CLname(row.GENDER, namesGenerator)
    elif country == 'CN':
        personName = CNname(row.GENDER, namesGenerator)
    else:
        personName = USnames(row.GENDER)
    
    prefix = personName['prefix']
    fname = personName['fname']
    mname = personName['mname']
    lname = personName['lname']
    
    
    val_name = (subjectid_to_personid[row.SUBJECT_ID], prefix, fname, mname, lname, 1, datetime.datetime.now())    
    person_name.append(val_name)
    added_patient.append(row.SUBJECT_ID)
        
    data = {}
    data['patient'] = patient
    data['identifier'] = identifier
    data['patientIdentifier'] = patient_identifier
    data['personName'] = person_name
    data['addedPatient'] = added_patient
    
    return data
        