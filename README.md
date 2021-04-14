# CMSC828D A4: Evaluating Dashboard Performance

Name: David Wang

Email: dwang248@umd.edu

### Introduction  
#### _Insured Multifamily Mortgages (1970-2014)_  
The dataset used was from the Housing and Urban Development (HUD) department contaiining data related to mortgages for multifamily insured properties from 1970 to 2014.    

### Prerequisite  
Make sure you have pip3, python3, and psql installed. Additionally, we have assumed that you have created the user `cmsc828d` and have the database `a3database`. If you do not please run the following commands into your PostgreSQL server as admin:
```
CREATE USER cmsc828d;
CREATE DATABASE a3database;
```

### POSTGRESQL
We assume that the user `cmsc828d` has ___superuser___ privilege. If not, please run the following command into your PostgreSQL server as admin:
```
ALTER USER cmsc828d WITH SUPERUSER;
```

Also, ensure that the following is true on your PostgreSQL:
```
Host: localhost
Port: 5432
```

### Python Packages
Ensure that the following python packages are installed:
csv, random, datetime, simplejson, json, flask, and psycopg2

### Launching the Interface
Run the following to start up the dashboard:
```
python3 server.py
```

Now, open the web page http://127.0.0.1:8000/ with any browser to run the dashboard.
  
### Evaluation Survey
Please fill out the following form to complete tasks and provide feedback: [[Link]](https://forms.gle/SLpYdX4v64Tan9bX9)

You will be asked to upload a user log at the end of the survey. To do so will require you to right click within the console window and selecting "save as" in the menu ([instructions here](https://support.shortpoint.com/support/solutions/articles/1000222881-save-google-chrome-browser-s-console-file))
