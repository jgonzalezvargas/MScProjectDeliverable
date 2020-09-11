# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 00:14:50 2020

@author: jgonz
"""
from sqlalchemy import create_engine
import pymysql
import mysql.connector
import pandas as pd

class ConnectionDataW:
    openmrs = create_engine('mysql+pymysql://root:pass@127.0.0.1/openmrs', pool_recycle=3600)
    dbConnectionOpenMRS = openmrs.connect()
    
    mimic = create_engine('mysql+pymysql://root:pass@127.0.0.1/mimic', pool_recycle=3600)
    dbConnectionMimic = mimic.connect()
    
    openmrs = mysql.connector.connect(user='root', password='pass',
                                  host='127.0.0.1',
                                  database='openmrs')
    
    mimic = mysql.connector.connect(user='root', password='pass',
                                  host='127.0.0.1',
                                  database='mimic')
    
    openmrscursor = openmrs.cursor(buffered=True)
    mimiccursor = mimic.cursor()
    
    def getOpenMRScursor(self):
        return self.openmrscursor
    
    def getMimicCursor(self):
        return self.mimiccursor
    
    def getOpenMRSconnection(self):
        return self.dbConnectionOpenMRS
    
    def getMimicConnection(self):
        return self.dbConnectionMimic
    
    def getOpenMRSdb(self):
        return self.openmrs
    
    def getMimicDB(self):
        return self.mimic
    
    def patientData(self):
        sql_get_patient_data = ('''SELECT pat.SUBJECT_ID, pat.GENDER, pat.DOB, pat.DOD, pat.EXPIRE_FLAG,
                            adm.HADM_ID, adm.ADMITTIME, adm.DISCHTIME,adm.ADMISSION_TYPE, adm.ADMISSION_LOCATION,
                            diag.ICD9_CODE,
                            diagnoses.LONG_TITLE
                            
                            FROM `patients` as pat
                            INNER JOIN admissions as adm ON (pat.SUBJECT_ID = adm.SUBJECT_ID)
                            INNER JOIN diagnoses_icd as diag ON (adm.SUBJECT_ID = diag.SUBJECT_ID AND adm.HADM_ID = diag.HADM_ID)
                            INNER JOIN d_icd_diagnoses as diagnoses ON (diagnoses.ICD9_CODE = diag.ICD9_CODE)
                            
                            GROUP BY 
                            pat.SUBJECT_ID, pat.GENDER, pat.DOB, pat.DOD, 
                            adm.HADM_ID, adm.ADMITTIME, adm.DISCHTIME,adm.ADMISSION_TYPE, adm.ADMISSION_LOCATION,
                            diag.ICD9_CODE,
                            diagnoses.LONG_TITLE
                            
                            order by pat.subject_id, adm.HADM_ID, diag.ICD9_CODE''')  
        
        df_patient_data = pd.read_sql(sql_get_patient_data, self.getMimicConnection())
        return df_patient_data 
    
    def getLabevets(self):
        sql = '''SELECT ROW_ID, SUBJECT_ID, HADM_ID, ITEMID, CHARTTIME, VALUE, VALUENUM, VALUEUOM, FLAG from labevents
                order by SUBJECT_ID, HADM_ID'''
        df_lab = pd.read_sql(sql, self.getMimicConnection())
        return df_lab
    
    def oCommit(self):
        self.openmrs.commit()
        
        
        
    
    