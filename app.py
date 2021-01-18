
# Dependencies
import numpy as np
import pandas as pd 

import datetime as dt
from datetime import timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the existing datebase into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session from python app to database
session = Session(engine)

# Flask setup
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>" 
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    "Returns precipitation from the last 12 months of data in the dataset"
    
    # Getting the last date in the dataset and creating a variable for the query date
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - timedelta(days=366)
    query_date = dt.datetime.strftime(year_ago, "%Y-%m-%d")

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > query_date).all()
    
    # Dictionary to hold results
    precip = {date: prcp for date, prcp in results}
    return jsonify(precip)

@app.route('/api/v1.0/stations')
def stations():
    '''Returns a list of all stations in the dataset'''
    results = session.query(Station.station, Station.name).all()

    # Convert list of tuples to list
    stations = {name: station for name, station in results}

    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def temp_obvs():

    # Getting the last date in the dataset and creating a variable for the query date
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - timedelta(days=366)
    query_date = dt.datetime.strftime(year_ago, "%Y-%m-%d")

    # Finding which station is most active
    active_stations = session.query(Station.name, Station.id, func.count(Measurement.id,)).\
                    filter(Station.station == Measurement.station).\
                    group_by(Station.name, Station.id).\
                    order_by(func.count(Measurement.id).desc()).all()
    
    most_active_station = active_stations[0][1]

    # Query database
    results = session.query(Measurement.tobs).\
            filter(Station.station == Measurement.station).\
            filter(Measurement.date >= query_date).all()

    temps = list(np.ravel(results))

    return jsonify(temps)

@app.route('/api/v1.0/temp/<start>')
@app.route('/api/v1.0/temp/<start>/<end>')
def trip_stats(start=None, end=None):
    '''Returns trip minimum temp, trip average temp, and trip max temp'''

    # Options for queries with and without an end date
    if not end:
        trip_min = session.query(func.min(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
        
        trip_min = list(np.ravel(trip_min))

        trip_avg = session.query(func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

        trip_avg = list(np.ravel(trip_avg))

        trip_max = session.query(func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

        trip_max = list(np.ravel(trip_max))
        
        return jsonify(f"Lowest Temp: {trip_min}, Average Temp: {trip_avg}, Highest Temp: {trip_max}")
    
    trip_min = session.query(func.min(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()
    
    trip_min = list(np.ravel(trip_min))

    trip_avg = session.query(func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()
    
    trip_avg = list(np.ravel(trip_avg))

    trip_max = session.query(func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()
    
    trip_max = list(np.ravel(trip_max))

    return jsonify(f"Lowest Temp: {trip_min}, Average Temp: {trip_avg}, Highest Temp: {trip_max}")
    





if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=False)