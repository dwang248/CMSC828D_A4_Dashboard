import csv
try:
    import simplejson as json
except ImportError:
    import json
from flask import Flask,request,Response,render_template
import psycopg2 # use this package to work with postgresql
from us_state_abbrev import abbrevUSState
import datetime


total = 7
startYear = 0
endYear = 0

# Connects to the server
def getConnection():
  conn = psycopg2.connect(host="localhost", port = 5432, database="a2database", user="cmsc828d", password="password")
  cur = conn.cursor()
  return (cur,conn)

# Gets all the attributes from the movies dataset
def getAttributes(cur):
  cur.execute("Select * FROM hud LIMIT 0")
  colNames = [desc[0] for desc in cur.description]
  return colNames

def getAveragePerState(cur, column, range):
  if range is None:
    cur.execute("SELECT SUM(avg_{0} * count / sum), avg_attributes.property_state FROM avg_attributes LEFT JOIN (SELECT SUM(count), property_state FROM \
      avg_attributes GROUP BY property_state ORDER BY property_state) AS a ON a.property_state = avg_attributes.property_state GROUP BY \
      avg_attributes.property_state ORDER BY avg_attributes.property_state".format(column))
  else:
    cur.execute("SELECT SUM(avg_{0} * count / sum), avg_attributes.property_state FROM avg_attributes LEFT JOIN (SELECT SUM(count), property_state FROM \
      avg_attributes WHERE year >= '{1}' and year <= '{2}' GROUP BY property_state ORDER BY property_state) AS a ON a.property_state = avg_attributes.property_state \
      WHERE year >= '{1}' and year <= '{2}' GROUP BY avg_attributes.property_state ORDER BY avg_attributes.property_state;".format(column, range[0], range[1]))
  data = cur.fetchall()
  return data

# Creates a table of the average column per year
def getNationalAverageByYear(cur, column, range):
  if range is None:
    cur.execute("SELECT avg_attributes.year, SUM(avg_{0} * count / sum) FROM avg_attributes LEFT JOIN (SELECT SUM(count), year FROM \
      avg_attributes GROUP BY year ORDER BY year) AS a ON a.year = avg_attributes.year GROUP BY avg_attributes.year ORDER BY avg_attributes.year".format(column))
  else:
    cur.execute("SELECT avg_attributes.year, SUM(avg_{0} * count / sum) FROM avg_attributes LEFT JOIN (SELECT SUM(count), year FROM \
      avg_attributes WHERE year >= '{1}' and year <= '{2}' GROUP BY year ORDER BY year) AS a ON a.year = avg_attributes.year \
      WHERE avg_attributes.year >= '{1}' and avg_attributes.year <= '{2}' GROUP BY avg_attributes.year ORDER BY avg_attributes.year".format(column, range[0], range[1]))
  
  data = cur.fetchall()
  return data

#  Merged getting the bin counts and national averages per year in one query
def getCountAndAveragePerYear(cur, column, range):
  if range is None:
    cur.execute("SELECT avg_attributes.year, SUM(count), SUM(avg_{0} * count / sum) FROM avg_attributes LEFT JOIN (SELECT SUM(count), year FROM \
      avg_attributes GROUP BY year ORDER BY year) AS a ON a.year = avg_attributes.year GROUP BY avg_attributes.year ORDER BY avg_attributes.year".format(column))
  else:
    cur.execute("SELECT avg_attributes.year, SUM(count), SUM(avg_{0} * count / sum) FROM avg_attributes LEFT JOIN (SELECT SUM(count), year FROM \
      avg_attributes WHERE year >= '{1}' and year <= '{2}' GROUP BY year ORDER BY year) AS a ON a.year = avg_attributes.year \
      WHERE avg_attributes.year >= '{1}' and avg_attributes.year <= '{2}' GROUP BY avg_attributes.year ORDER BY avg_attributes.year".format(column, range[0], range[1]))

  # SELECT year, COUNT(*), AVG(interest_rate) FROM hud GROUP BY year ORDER BY year
  # SELECT year, COUNT(*), avg_interest_rate FROM avg_attributes GROUP BY year ORDER BY year
  # SELECT avg_attributes.year, SUM(count), SUM(avg_interest_rate * count / sum) FROM avg_attributes LEFT JOIN 
  # (SELECT SUM(count), year FROM avg_attributes GROUP BY year ORDER BY year) AS a ON a.year = avg_attributes.year GROUP BY avg_attributes.year ORDER BY avg_attributes.year

  data = cur.fetchall()
  return data

def getYears(cur):
  cur.execute("SELECT MIN(year) FROM hud")
  min = cur.fetchall()[0][0]
  cur.execute("SELECT MAX(year) FROM hud")
  max = cur.fetchall()[0][0]
  return min,max

def computeColorRanges(mn,mx,total):
  step = float((mx-mn)/total)
  ranges = []
  rangeLabels = []
  prev = float(mn)

  for i in range(total):
    start = abbreviateNumber(prev)
    end = abbreviateNumber(prev + step)
    rangeLabels.append(end + " - " + start)
    ranges.append(prev)
    prev += step
  ranges.sort()
  rangeLabels.reverse()
  return ranges, rangeLabels

def abbreviateNumber(num):
  abbrev = ['', 'K', 'M']
  magnitude = 0
  while abs(num) >= 1000:
      magnitude += 1
      num /= 1000.0
  return '%.2f%s' % (num, abbrev[magnitude])

def formatTable(table):
  tableUpdate = {}
  tableUpdateAbbrev = {}
  for i in range(len(table)):
    table[i] = list(table[i])
    table[i][0] = float(table[i][0])
    table[i][1] = abbrevUSState[table[i][1]]
      
    tableUpdate["{0}".format(table[i][1])] = table[i][0]
    tableUpdateAbbrev["{0}".format(table[i][1])] = abbreviateNumber(table[i][0])
  
  return tableUpdate, tableUpdateAbbrev

conn = psycopg2.connect(host="localhost", port = 5432, database="a2database", user="cmsc828d", password="password")
cur = conn.cursor()
cur.execute("DROP MATERIALIZED VIEW IF EXISTS avg_attributes")
cur.execute("DROP TABLE IF EXISTS hud")
cur.execute("""CREATE TABLE IF NOT EXISTS hud (hud_project_number integer, premise_id integer, 
property_name text, property_street text, property_city text, property_state text, property_zip text, 
units integer, initial_endorsement_date date, final_endorsement_date text, original_mortgage_amount decimal,
first_payment_date date, maturity_date date, term_in_months integer, interest_rate decimal, 
current_principal_and_interest decimal, amortized_principal_balance decimal, holder_name text,
holder_city text, holder_state text, servicer_name text, servicer_city text, servicer_state text, 
section_of_act_code text, soa_category text, te varchar(2), tc varchar(2), year int)""")

with open('hudmortgages.csv', 'r') as f:
  reader = csv.reader(f)
  next(reader)
  for row in reader:
    row[10] = row[10].replace(',', '')
    row[15] = row[15].replace(',', '')
    row[16] = row[16].replace(',', '')
    date = datetime.datetime.strptime(row[8], '%m/%d/%Y')
    row.append(date.year)

    cur.execute("INSERT INTO hud VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", row)

conn.commit()
cur.close()
conn.close()


app = Flask(__name__)

# Renders the page
# Creates the movie table in the database
@app.route('/')
def renderPage():

  conn = psycopg2.connect(host="localhost", port = 5432, database="a2database", user="cmsc828d", password="password")
  cur = conn.cursor()

  cur.execute("CREATE MATERIALIZED VIEW IF NOT EXISTS avg_attributes AS SELECT AVG(interest_rate) avg_interest_rate, AVG(original_mortgage_amount) avg_original_mortgage_amount, \
    AVG(current_principal_and_interest) avg_current_principal_and_interest, AVG(amortized_principal_balance) avg_amortized_principal_balance, \
    property_state, year, count(*) FROM hud GROUP BY property_state, year ORDER BY property_state")
  
  cur.execute("CREATE INDEX IF NOT EXISTS state_id ON avg_attributes(property_state)")
  cur.execute("CREATE INDEX IF NOT EXISTS year_id ON avg_attributes(year)")

  conn.commit()

  cur.close()
  conn.close()

  return render_template("index.html")

# Update map and line when changing attribute
@app.route('/update-attribute/', methods = ["GET", "POST"])
def updateAttribute():
  data = request.get_json()
  column = data['column']
  years = data['years'].split("-")

  if years[0] is startYear and years[1] is endYear:
    years = None

  cur, conn = getConnection()
  avgValPerState = getAveragePerState(cur, column, years)
  maxValPerState = float(max(avgValPerState)[0])
  minValPerState = float(min(avgValPerState)[0])
  rangesPerState = computeColorRanges(maxValPerState, minValPerState, total)
  

  # Gets a table of national averages by year
  avgNationalByYear = getNationalAverageByYear(cur, column, years)
  # Gets the minimum value of avgNationalByYear
  minNationalByYear = float(min(avgNationalByYear, key=lambda x:x[1])[1])
  # Gets the maximum value of avgNationalByYear
  maxNationalByYear = float(max(avgNationalByYear, key=lambda x:x[1])[1])
  # Gets the national average of a column 
  avgNational = float(sum(map(lambda x: x[1], avgNationalByYear)) / len(avgNationalByYear))

  cur.close()
  conn.close()

  states, statesAbbrevNum = formatTable(avgValPerState)

  nationalAverageByYearFormatted = []
  for i in range(len(avgNationalByYear)):
    nationalAverageByYearFormatted.append({"year": avgNationalByYear[i][0], "average": float(avgNationalByYear[i][1]),
     "averageAbbrev": abbreviateNumber(float(avgNationalByYear[i][1]))})
  

  respData = {"averagesPerState": states, "averagesPerStateAbbrev": statesAbbrevNum, "rangesPerState": rangesPerState[0],
  "rangesPerStateLabels": rangesPerState[1], "nationalAverageByYearFormatted": nationalAverageByYearFormatted,
  "minNationalByYear": minNationalByYear, "maxNationalByYear": maxNationalByYear, "avgNational": avgNational}
  resp = Response(response=json.dumps(respData), status=200, mimetype='application/json')
  h = resp.headers
  h['Access-Control-Allow-Origin'] = "*"
  return resp

#  Create all three visualizations
@app.route('/visualizations/', methods = ["GET", "POST"])
def visualizations():
  #  Get start and end years
  data = request.get_json()
  valRange = data["yearsRange"]
  column = data['column']

  if valRange[0] is startYear and valRange[1] is endYear:
    valRange = None

  cur, conn = getConnection()
  binCountData = getCountAndAveragePerYear(cur, column, valRange)
  minBinCount = float(min(binCountData, key=lambda x:x[1])[1])
  maxBinCount = float(max(binCountData, key=lambda x:x[1])[1])

  # Gets a table of national averages by year
  avgNationalByYear = [(year, attr) for year, count, attr in binCountData]
  # Gets the minimum value of avgNationalByYear
  minNationalByYear = float(min(avgNationalByYear, key=lambda x:x[1])[1])
  # Gets the maximum value of avgNationalByYear
  maxNationalByYear = float(max(avgNationalByYear, key=lambda x:x[1])[1])
  # Gets the national average of a column 
  avgNational = float(sum(map(lambda x: x[1], avgNationalByYear)) / len(avgNationalByYear))

  # Gets a table of the averages for all states
  avgValPerState = getAveragePerState(cur, column, valRange)
  # Max value compared to all states
  maxValPerState = float(max(avgValPerState)[0])
  # Min value compared to all states
  minValPerState = float(min(avgValPerState)[0])

  cur.close()
  conn.close()

  binCountYears = []
  for i in range(len(binCountData)):
    binCountYears.append({"year": binCountData[i][0], "count": float(binCountData[i][1])})

  rangesPerState = computeColorRanges(maxValPerState, minValPerState, total)
  states, statesAbbrevNum = formatTable(avgValPerState)

  nationalAverageByYearFormatted = []
  for i in range(len(avgNationalByYear)):
    nationalAverageByYearFormatted.append({"year": avgNationalByYear[i][0], "average": float(avgNationalByYear[i][1]),
     "averageAbbrev": abbreviateNumber(float(avgNationalByYear[i][1]))})

  respData = {"binCountYears": binCountYears, "minBinCount": minBinCount, "maxBinCount": maxBinCount,
  "averagesPerState": states, "averagesPerStateAbbrev": statesAbbrevNum, "rangesPerState": rangesPerState[0],
  "rangesPerStateLabels": rangesPerState[1], "nationalAverageByYearFormatted": nationalAverageByYearFormatted,
  "minNationalByYear": minNationalByYear, "maxNationalByYear": maxNationalByYear, "avgNational": avgNational}

  resp = Response(response=json.dumps(respData), status=200, mimetype='application/json')
  h = resp.headers
  h['Access-Control-Allow-Origin'] = "*"
  return resp

@app.route('/get-year-range/', methods = ["GET"])
def getYearRange():
  cur, conn = getConnection()
  yearRange = list(getYears(cur))

  cur.close()
  conn.close()

  global starYear
  global endYear

  starYear = yearRange[0]
  endYear = yearRange[1]

  respData = {"yearRange": yearRange}
  resp = Response(response=json.dumps(respData), status=200, mimetype='application/json')
  h = resp.headers
  h['Access-Control-Allow-Origin'] = "*"
  return resp

if __name__ == "__main__":
  app.run(debug=True,port=8000)
