# CMSC828D A4: Evaluating Dashboard Performance

Name: David Wang

Email: dwang248@umd.edu

### Introduction  
#### _Fatal Police Shootings in the United States (2015-2020)_  
The original dataset is comprised of fatal police shootings in U.S. that occurred between January 2015 and June 2020. You will be interacting with a generated dataset of 10,000 tuples that uses the same attributes and distribution based on the original dataset. The data contains basic information about the people who were killed and factors relating the shooting event. For my dashboard, I decided to specifically focus on a person's race, gender, and age group, as well as the date it took place, where it occurred, signs of mental illness, if the suspect was fleeing, and if there was a body camera present to record the incident.    

### Pre-requisite  
Make sure you have pip3, python3, and psql installed. Additionally, we have assumed that you have created the user `cmsc828d` and have the database `a3database`.

### POSTGRESQL
We assume that the user `cmsc828d` has ___superuser___ privilege. If not, please run the following command into your PostgreSQL server as admin:
```
ALTER USER cmsc828d WITH SUPERUSER;
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

### Notes
1. If you have any additional feedback on any part of this process (i.e. setting up the interface, interacting with the vis, etc.) , please include it in the last prompt on the google form labeled: "_Please provide any additional feedback here_"
2. **All tasks are to be performed on the A3 dashboard**. I will not be asking you to make observations on the A2 dashboard, but it is included in the setup so that you may interact with it if you are interested. 
   * You can access the A2 dashboard interface by visiting the page: http://127.0.0.1:8000/a2
   * If you have any feedback after interacting with both the A3 and A2 dashboards, please include it in the last prompt on the form as well.
3. For your convenience, there are buttons at the top right of the screen that can record when you start and end each task. _This information is important to understand how long each task took, so **please use these controls during the evaluation**._
  
### Tasks
Please fill out the following form to complete tasks and provide feedback: [[Form Link]](https://forms.gle/SLpYdX4v64Tan9bX9)<br>  
You will be asked to **perform 4 tasks** and **upload a user log file (logs.txt)** at the end of the evaluation.
