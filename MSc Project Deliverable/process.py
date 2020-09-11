# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 00:33:20 2020

@author: jgonz
"""

def providers(df):
    providers_dictionary = {}
    for index, row in df.iterrows():
        providers_dictionary[row.provider_id] = row.identification
    return providers_dictionary

def concepts(df):
    concept_dictionary = {}
    for index, row in df.iterrows():
        concept_dictionary[row.short_name] = row.concept_id
    return concept_dictionary