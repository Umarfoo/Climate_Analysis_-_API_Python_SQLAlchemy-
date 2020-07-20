# Importing necassary dependencies
import datetime as dt
import numpy as np
import pandas as pd

# Importing sqlalchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Importing flask and jsonify
from flask import Flask, jsonify

# Creating connection to database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Setting up base and reflecting the tables
Base = automap_base()
Base.prepare(engine, reflect = True)

# Defining tables separately
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask set
app = Flask(__name__)

# List all routes that are available.
@app.route('/')
def welcome():
    return(f"Welcome to the API<br/><br/>"
           f"<h1> Available Routes </h1><br/>"
           f"/api/v1.0/precipitation<br/><br/>"
           f"/api/v1.0/stations<br/><br/>"
           f"/api/v1.0/&lt;start&gt;<br/>"
           f"<start> input format YYYY-MM-DD<br/><br/>"
           f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
           f"<start> & <end> input format YYYY-MM-DD<br/>"
    )

# Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary.

@app.route('/api/v1.0/precipitation')
def prcp():
    # Starting session
    session = Session(engine)
    
    # Running queries
    all_data = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()
    
    # Closing session
    session.close()
    
    all_dates_prcp = []
    for pdate, pr in all_data:
        prcp_dict = {}
        prcp_dict[pdate] = pr
        
        # Appending list with dictionary results
        all_dates_prcp.append(prcp_dict)
    
    return jsonify(all_dates_prcp)

# Return a JSON list of stations from the dataset.

@app.route('/api/v1.0/stations')
def stat():
    # Starting session
    session = Session(engine)
    
    # Query for listing all the station names and their ID
    station_query = session.query(Station.station, Station.name).group_by(Station.station).all()
    
    # Closing session
    session.close()
    
    # Creating Json Dict
    all_station = []
    for id, name in station_query:
        stat_dict = {}
        stat_dict[id] = name
        
        all_station.append(stat_dict)
        
    return jsonify(all_station)

# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route('/api/v1.0/tobs')
def tobs():
    # Starting session
    session = Session(engine)
    
    # Finding last year date
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = (dt.datetime.strptime(last_date[0],'%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    
    # Finding most active station and setting it in a variable
    act_stat = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    # Most active station
    pop_stat = act_stat[0][0]
    
    # Temperature data for most popular station
    temp_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).filter_by(station = pop_stat).order_by(Measurement.date).all()

    # Closing session
    session.close()
    
    # Creating Json Dict
    pop_station = []
    for tdate, temp in temp_data:
        temp_dict = {}
        temp_dict[f'Temperature on {tdate} at {pop_stat} Station'] = temp 
        
        pop_station.append(temp_dict)
        
    return jsonify(pop_station)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

@app.route('/api/v1.0/<start>')
def start(start):
    # Setting start date
    start_date = start
    
    # Starting session
    session = Session(engine)
    
    # Running query and grouping_by date
    result_start = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).group_by(Measurement.date).all()
    
    # Closing session
    session.close()
    
    # Creating Json Dict
    final_result = []
    for sdate, s_min, s_max, s_avg in result_start:
        min_max_dict = {}
        min_max_dict["DATE"] = sdate
        min_max_dict["Min Temperature"] = s_min
        min_max_dict["Max Temperature"] = s_max
        min_max_dict["Average Temperature"] = round((s_avg),1)
        
        final_result.append(min_max_dict)
    
    
    return jsonify(final_result)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    
    # Setting start date
    s_date = start
    e_date = end
    
    # Starting session
    session = Session(engine)
    
     # Running query and grouping_by date
    result_se = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= s_date).filter(Measurement.date <= e_date).group_by(Measurement.date).all()
    
     # Closing session
    session.close()
    
    # Creating Json Dict
    f_result = []
    for sedate, se_min, se_max, se_avg in result_se:
        min_max_dict = {}
        min_max_dict["DATE"] = sedate
        min_max_dict["Min Temperature"] = se_min
        min_max_dict["Max Temperature"] = se_max
        min_max_dict["Average Temperature"] = round((se_avg),1)
        
        f_result.append(min_max_dict)
    
    
    return jsonify(f_result)


if __name__ == '__main__':
    app.run(debug = False)