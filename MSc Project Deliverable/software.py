# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 15:40:32 2020

@author: jgonz
"""

print("Hello, what would you like to do?")
print("1: Data Migration")
print("2: CoVid-19 Simulation")
print("3: Undo Simulation")
print("4: Exit")

val = input()

while(True):
    if val == "1":
        try:
            import improvedVersion as m
            print("Starting Migration")
            m.dataMigration()
        except:
            print("I'm sorry, something is wrong")
        break
    elif val == "2":
        try:
            import contagion as c
            print("Starting Simulation")
            c.simulation()
        except:
            print("I'm sorry, something is wrong")
        break
    elif val == "3":
        try:
            import contagionQueries as cq
            from Connection.connectionWamp import ConnectionDataW
            db = ConnectionDataW()
            print("Undoing Simulation")
            cq.undo(db)
        except:
            print("I'm sorry, something is wrong")
        break
    elif val == "4":
        break
    else:
        print("Invalid input, please try again")
print("Thank you for using this software.")
    