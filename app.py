#Import Dependencies 
import numpy as np 

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session 
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

import datetime as dt

#######################################
# Database Setup
#######################################
engine=create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station=Base.classes.station

#Create session link from Python to DB
session=Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #Docstring
    """Return a list of precipitation data over 12 months"""
    # Query to find last 12 months of precipitation
    #Find dates
    last_date= session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date=last_date[0]
    year_ago=dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=366)

    #Perform query to find precipitation data 
    precipitation_results=session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=year_ago).all()
    precipitation_dict=dict(precipitation_results)

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    #Docstring
    """Return a list of Stations"""
    #Query stations
    station_results=session.query(Measurement.station).group_by(Measurement.station).all()
    station_list=list(np.ravel(station_results))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    #Docstring
    """Return a list Temperature Observations for the previous year."""
    #Find dates
    latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest_date=latest_date[0]
    year_ago=dt.datetime.strptime(latest_date,"%Y-%m-%d") - dt.timedelta(days=366)

    #Query Tobs
    tobs_results= session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>=year_ago).all()

    tobs_list=list(np.ravel(tobs_results))

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    #Docstring
    """Return a list of the minimum temperature, the average temperature, and the max temperature for dates greater than or equal to a date provided"""
    start_date=session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date>=start).group_by(Measurement.date).all()
    start_list=list(np.ravel(start_date))

    return jsonify(start_list)
    

@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start, end):
    #Docstring
    """Return a list of minimum temperature, the average temperature, and the max temperature for a time period between two dates"""
    
    start_end_list = []
    start_end_dates=session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date>=start).filter(Measurement.date<= end).group_by(Measurement.date).all()
    
    for date, min, avg, max in start_end_dates:
        dict = {}
        dict["Date"]=date
        dict["Min"]=min
        dict["Max"]=max
        dict["Avg"]=avg
        start_end_list.append(dict)
        
    return jsonify(start_end_list)
        

if __name__ == '__main__':
    app.run(debug=True)

