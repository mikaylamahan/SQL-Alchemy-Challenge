import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#create session
session = Session(engine)

#setup Flask
app = Flask(__name__)

#create a homepage
@app.route("/")
def home():
    """Lists all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

#define variable used in pandas to figure out the most recent date

highest_date= (session.query(func.max(Measurement.date)))

#recreate the precpitation query used in pandas

@app.route("/api/v1.0/precipitaton")
def precipitation():
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date> highest_date)
                      .order_by(Measurement.date)
                      .all())

#make date the key and prcp the value in the dictionary  
  
    prcp_data = []
    for result in results:
        prcp_dict = {result.date: result.prcp, "Station": result.station}
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)

#listing all stations in the dataset

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

#query for the dates and temperature observations from a year from the last data point

@app.route("/api/v1.0/temperature")
def temperature():
    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > highest_date)
                      .order_by(Measurement.date)
                      .all())

#return in list instead of dict

    temp_data = []
    temp_data.append(results)

    return jsonify(temp_data)


#date data pull

@app.route('/api/v1.0/datesearch/<startdate>')
def start(startdate):
    date_info_list = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*date_info_list)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startdate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Minimum Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["Maximum Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route('/api/v1.0/datesearch/<startdate>/<enddate>')
def startend(startdate, enddate):
    date_info_list = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

#make sure to filter inclusive

    results =  (session.query(*date_info_list)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startdate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= enddate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Minimum Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["Maximum Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__home__":
    app.run(debug=True)

