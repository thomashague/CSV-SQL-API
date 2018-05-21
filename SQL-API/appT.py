#################################################
# Depedencies
#################################################

# Data analysis imports
import datetime as dt 
import numpy as np 
import pandas as pd

# SQL and database imports
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Flask for web API functioning and jsonify for json file handling
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Connect to the file-based database, hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement 
Station = Base.classes.station 

# Create the session link from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Default route user will navigate to. Shows other routes 
@app.route("/")
def hello():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Avalable Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    """Return the precipitation data for the last year"""
    
    # Calulate the date 1 year ago from today
    prev_year = dt.date.today() - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    
    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""

    # Query for the stations
    results = session.query(Station.station).all()

    # Unravel results into a 1D array and convert to a list  - why unravel???
    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations (tobs) for previous year."""

    # Get the date from 1 year ago
    prev_year = dt.date.today() - dt.timedelta(days=365)

    # Query for the temperature observationsfor the last year
    tobs = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(tobs))

    return jsonify(temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>") 
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""  

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
   
    if not end:
        # return for dates greater than the start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)


# Ability to run the flask app from this file
if __name__ == '__main__':
    app.run()