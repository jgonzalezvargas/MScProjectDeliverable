# MSc Project Deliverable
Deliverable for my MSc Project, University of Leeds 2019/2020

# Requirements
A MySQL database is required, with user as root, password as pass and hosted in 127.0.0.1 with a OpenMRS database. The user is invited to install OpenMRS, but it is not required, only its database is. One of the deliverables are my credentials for a databae in AWS, this one works, it just needs to be downloaded and mounted.

# Running
The file software.py is the main file to run. In console, it will ask what to do, the options are:
1. Data Migration
2. CoVid-19 Simulation
3. Undo Simulation
4. Exit

# Data Migration
Data migrations requires some tables from MIMIC-III database. Since special access is required to access that database, I cannnot upload it here. However, the code is here if it is needed to see something

# CoVid-19 Simulation
Simulates the spread of Coronavirus  upon the database population. In order to work it requieres the dabase to have patients. The data contained in the AWS database mentioned earlier works. The data in said database already has the pandemic simulated.

# Undo Simulation
Reverts the simulation, so it can be run again. The simulation can run wihtout it being previously undone, but undoing it and doing it again guarantees obtaining the same results.

For more information on how the code works, the user is invited to read the MSc project report.
