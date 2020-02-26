#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 11:41:13 2020

@author: roopareddynagilla
"""

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from datetime import date
from datetime import datetime
from datetime import timedelta as dtd


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Base.classes.keys()

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
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
        f"/api/v1.0/precipitation:<br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/<start> <br/>"
        f"/api/v1.0/<start>/<end> <br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Convert the query results to a Dictionary using date as the key and prcp as the value"""
    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()
    dictionary = {}
    # Convert tuples into dictionary
    def Convert(tup, di):
        for a, b in tup: 
            di.setdefault(a, []).append(b) 
        return di
    #all_names = list(np.ravel(results))
    Convert(results, dictionary)
    
    #Return the JSON representation of your dictionary
    return jsonify(dictionary)

@app.route("/api/v1.0/stations")
def stationList():
    session = Session(engine)
    """Return a list of all stations"""
    station_list = session.query(Station.station).all()
    session.close()    
    all_stations = list(np.ravel(station_list))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobsLastYear():
    session = Session(engine)
    """Return a the latest date"""
    tobs_last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    session.close() 
    last_date = list(np.ravel(tobs_last_date))
    
    import datetime as dt
    for item in last_date:
        Dyear, Dmon, Ddate = item.split('-')
        latest_date = dt.date(int(Dyear),int(Dmon),int(Ddate))

    year_ago = latest_date - dt.timedelta(days=365)
    
    session = Session(engine)
    temperature_obs = session.query(Measurement.tobs).filter(Measurement.date >= year_ago).order_by(Measurement.date.desc()).all()
    temperature_obs_list = list(np.ravel(temperature_obs))
    return jsonify(temperature_obs_list)

@app.route("/api/v1.0/<start>")
def tempStatsWithStartDate(start):
    def calc_temps(start, end_date):
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = session.query(func.max(Measurement.date)).all()[0][0]
            return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    enddate = session.query(func.max(Measurement.date)).all()[0][0]
    temps = calc_temps(start, enddate)
    temp_stats_list = list(np.ravel(temps))
    return jsonify(temp_stats_list)

@app.route("/api/v1.0/<start>/<end>")
def tempStatsWithStartDateAndEndDate(start, end):
    def calc_temps_se(start, end):
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temps_se = calc_temps_se(start, end)
    temp_stats_list_se = list(np.ravel(temps_se))
    return jsonify(temp_stats_list_se)

if __name__ == '__main__':
    app.run(debug=True)
