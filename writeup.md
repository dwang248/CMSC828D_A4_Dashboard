--------------------------------------------------------------------------------
David Wang
dwang248@terpmail.umd.edu
--------------------------------------------------------------------------------


To Connect To POSTGRESQL
--------------------------------------------------------------------------------
Host: localhost
Port: 5432
Database: a2database
User: cmsc828d
Password: password

Note: Password required to access the database
Note: I did not use a .sql file. All sql commands are run in server.py
--------------------------------------------------------------------------------


To Run the Server
--------------------------------------------------------------------------------
Version of python used: Python 3.7.6
Ensure that csv, random, datetime, simplejson, json, flask, and psycopg2 are imported
Run python3 server.py

server.py uses hudmortgages.csv to run startup the visualizations. 
When running server.py, it will insert the rows in the csv into postgresql.
This may take some time given a large number of rows. 

In order to update the visualizations with newly randomly generated rows from
randomizer.py, you need to stop running server.py, and then start running 
it again. At the startup of server.py, it will read hudmortgages.csv and insert
the rows in the csv into PostgreSQL. As a result, if you updated hudmortgages.csv
such running randomizer.py, you need to restart server.py, which can be done by 
stopping the code run with CTRL-C and then running: python3 server.py.

--------------------------------------------------------------------------------


To Run the Randomizer
--------------------------------------------------------------------------------
The original dataset is in hudmortgagesOriginal.csv. randomizer.py takes the
original dataset and randomizes it into hudmortgages.csv. It outputs duplicates from the
a csv and placed them into hudmortgages.csv. randomizer.py retains the distribution of the 
original dataset. hudmortgages.csv initially contains 10,000 rows of data randomly generated 
from hudmortgagesOriginal.csv. As an example, to create a randomized hud mortgages 
dataset with 100,000 rows, run:

python randomizer.py hudmortgagesOriginal.csv 100000

The purpose of storing the randomized dataset into hudmortgages.csv is to 
allow for easier toggling between A2 and A3. When comparing the performance 
of the generated dataset from randomizer.py, copy and paste hudmortgages.csv
into the A2 file, and it should create the visualizations using the randomized
dataset.  
--------------------------------------------------------------------------------


Interface Reminder
--------------------------------------------------------------------------------
The dataset used was from the Housing and Urban Development (HUD) department.
It contained data related to mortgages for multifamily insured properties.
The data is from 1970 to 2014. The application has three visualizations. 
The first visualizations is a histogram that looks at the total number of 
mortgages. The second visualization is a line chart. This details the national 
average of attributes from the data set. The last visualization is a heatmap of
the United States. This looks at the average for a specific attribute for each
state. The user is able to select different attributes to display using buttons.
This will change the visualizations for the line chart and the heat map. The user
may also click on a state in the heapmap to zoom into it. The user
can also hover over each visualization to view additional details. 
--------------------------------------------------------------------------------


Rational
--------------------------------------------------------------------------------
In reducing the server response time, I first implemented various optimization algorithms. 
I noticed a lag time between the updates of visualizations. For instance, there was a 
noticeable time difference between when the bar graph updated and when the line chart updated. 
The reason for this was because the front end would send separate POST requests for different visualizations. 
As a result, I combined all combined queries for each interaction, resulting in the removal of the lag time.
When updating the range slider, the front end would receive a POST request that would update all three 
visualizations at the same time. 
 
Leis et al. discussed how cardinality estimators typically produce large errors which may cause 
unsatisfactory query performance on query engines that relies too heavily on such estimates. 
They found this to be the case in Postgresql. As a result, I want to use fewer queries as it can improve 
performance. This is why I re-used existing query results. As an example, when asking for the number of 
mortgages for each year, the server would receive a table of the bin counts for each year. From this 
query result, the server can compute the minimum and maximum bin count. Instead of computing the minimum 
and maximum bin counts through a query, the server uses the table the query returned to calculate relevant 
information. I did the same when receiving tables for the national average of a given attribute and the 
average of a given attribute by state.
 
I also batched queries together. Previously, obtaining the bin counts by year for the histogram and 
obtaining the national averages for the line chart were separate queries. The server now batches 
those queries together such that it would query for both bin counts and national averages 
together returning a table that contains the year, the bin counts, and the national averages. 
 
I considered implementing speculative query execution to optimize the system. I considered executing 
queries for each attribute and storing the resulting information on the server. This would then allow 
for a quick response time when interacting with the buttons. For example, when clicking on the “Original 
Mortgage Amount” button, the line chart and choropleth map would quickly update as the query was already 
precomputed. However, I would have to store 8 tables since there were 4 attributes with 2 visualizations each. 
I believed I was storing too much data on the server. I also did not think that such an implementation would be 
that effective in optimizing the system. Updating the range slider would make the tables relating to the choropleth 
map useless as the map outputs the averages of a state between a time range. This means that it would require querying 
for map data every time the user interacts with the range slider. That is why I chose not to implement speculative 
query execution.
 
Previously, in order to get the year of a row, PostgreSQL would have to compute DATETRUNC on the attribute 
"initial_endorsement_date". I thought that this was adding unnecessary computation to each query. 
When updating the range slider, queries would have to compute DATETRUNC on 
the attribute “initial_endorsement_date” to get the year. I updated it such that a column would be added to the 
dataset on PostgreSQL with the year removing the DATETRUNC computation; though this does add precomputation time. 

The textbook Database Systems: The Complete Handbook described indexes as a data structure that make it efficient 
to find tuples that have a fixed value. Indexes can be particularly useful for queries which an attribute is compared 
with a constant. From this, I implemented indexes in order to improves efficiency. All queries on the server are 
comparing the year attribute with the values from the range slider, specifically through the use of the WHERE clause. 
As a result, I indexed the dataset using the year attribute. Additionally, for the choropleth map, the queries used to 
output the visualization uses the property state attribute using the GROUP BY  and ORDER BY clause. Indexing based on 
property state would provide additional optimization as PostgreSQL does not need to use a sort the result explicitly 
and can instead use indexes to sort the result. The textbook Database Systems mentioned that indexing can be time 
consuming for insertions, deletions, and updates; however, such operations do not occur when interacting with the visualizations. 
 
The textbook Database Systems: The Complete Handbook also described how materialized views can provide efficiency 
as commonly used queries are stored in the database. The textbook mentioned that maintenance of a materialized 
view can be costly if their are frequent changes to the base tables. Though, the base tables for mortgages will 
not be updated when interacting with the visualizations. Materialized views will be time-consuming during 
precomputation, but it would allow faster query execution during online computation. I implemented a materialized 
view that computes the averages of each attribute grouped by property state and year. Essentially, the rows are 
binned by property state and year.It also computes the number of rows in the group. From this, all queries 
use the materialized view to compute their results for the visualizations. Average attribute values are used 
in the line chart and the choropleth map. Using the materialized view allows for such a computation to occur 
less often than previously allowing for better system response time. Additionally, the indexes are on the 
materialized view allowing for improved efficiency.

I considered using partitioning in order to improve performance. I tried implementing range partitioning based on year. 
This was in order to use parallelism to improve efficiency. However, when testing the performance of such an 
implementation, I noticed little to no improvement. There may be several reasons as to why this occurred. 
From the article, Architecture of a Database System, it details how good partitioning of the data is required 
for good performance. It is possible that the partitioning of the data was not good enough. From the histogram 
visualization, it can be seen that the data is heavily skewed to the right. It is possible that not accounting 
for such a skewed distribution did not allow for good performance. As a result, range partitioning were not 
used to optimize the system.

The article, Architecture of a Database System, also greatly discussed how parallelism could be used 
to improve performance as seen in the shared-nothing parallel system and the shared-disk parallel system. 
I attempted to achieve parallelism through the use of parallel queries as well as adding more parallel workers. 
Such an implementation did not provide any improvements. The article explains how the query optimizer needs 
to do a good job partitioning the workload. It might be that the query optimizer was inefficient in managing 
parallelism. It may also be because of the limitations of hardware in that only one machine, my laptop, 
was used in processing the data. 
--------------------------------------------------------------------------------


Overview of Development Process
--------------------------------------------------------------------------------
The development of my application took approximately 25 hours in total. I first 
began with the implementation of optimization algorithms including re-using 
query results and batching queries together. I also spent time improving upon the
html and server requests for less time lag between updating each visualization. This
took around 12 hours to complete. Next, implemented the optimization structures 
including indexes and materialized views. This took the most amount of time as I spent
a significant amount of time testing to determine whether other structures would improve
response time. I implmented structures such as partitions and tested to see if they 
improved performance. I would spend several hours comparing the performance of when
the data structure was implemented and when it wasn't.
--------------------------------------------------------------------------------