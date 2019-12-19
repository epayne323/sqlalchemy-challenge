import numpy as np
import os
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

app.route("/")
def welcome():
    """List all available api routes."""
    return \
    (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"<br/>"
        f"NOTE: please enter <start> and <end> dates as YYYY-MM-DD"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return amount of precipitation over the past year"""

    # initialize session
    session = Session(bind=engine)
    # Calculate the date 1 year ago from the last data point in the database
    maxdate = session.query(func.max(Measurement.date))
    mdsplit = maxdate.scalar().split("-")
    prevyear = dt.date(int(mdsplit[0]), int(mdsplit[1]), int(mdsplit[2])) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    prevyearmeasurements = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>prevyear)

    # store query results in dictionary
    precipitation = {row[0]: row[1] for row in prevyearmeasurements}

    # close the session to end the communication with the database
    session.close()

    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""

    session = Session(bind=engine)

    # Query all stations
    stations = session.query(Station).all()

    # close the session to end the communication with the database
    session.close()

    # store query results in dictionary
    all_stations = []
    for station in stations:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of all temperature observatons for last year of measurements"""

    session = Session(bind=engine)

    maxdate = session.query(func.max(Measurement.date))
    mdsplit = maxdate.scalar().split("-")
    prevyear = dt.date(int(mdsplit[0]), int(mdsplit[1]), int(mdsplit[2])) - dt.timedelta(days=365)

    # query previous year's measurements
    prevyearmeasurements = session.query(Measurement.station, Measurement.tobs, Station.name).\
        filter(Measurement.station == Station.station, Measurement.date>prevyear)

    # close the session to end the communication with the database
    session.close()

    # store query results in dictionary
    all_temps = []
    for tobs in prevyearmeasurements:
        temp_dict = {}
        temp_dict["station"] = tobs[0]
        temp_dict["temp"] = tobs[1]
        temp_dict["name"] = tobs[2]
        all_temps.append(temp_dict)

    return jsonify(all_temps)


@app.route("/api/v1.0/<start>")
def tempstart(start):
    """Return temperature statistics for dates greater than and equal to the start date"""

    session = Session(bind=engine)

    # the start date variable is expected to be in the format YYYY-MM-DD. split it into parts, cast those
    # parts as ints as arguments to a date object for use in the query
    ssplit = start.split("-")
    datestart = dt.date(int(ssplit[0]),int(ssplit[1]),int(ssplit[2]))

    # query tmax, tmin, and tavg from the given start date
    tmax = session.query(func.max(Measurement.tobs)).filter(Measurement.date>=datestart).scalar()
    tmin = session.query(func.min(Measurement.tobs)).filter(Measurement.date>=datestart).scalar()
    tavg = round(session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=datestart).scalar(), 1)

    # close the session to end the communication with the database
    session.close()

    return \
    (
        f"Temperature statistics starting from {start}:</br>"
        "</br>"
        f"Maximum Temperature: {tmax} °F</br>"
        f"Minimum Temperature: {tmin} °F</br>"
        f"Average Temperature: {tavg} °F"
    )

@app.route("/api/v1.0/<start>/<end>")
def tempstartend(start, end):
    """Return temperature statistics for dates between the start and end date inclusive"""

    session = Session(bind=engine)

    # turn the date variables into date objects for querying
    ssplit = start.split("-")
    datestart = dt.date(int(ssplit[0]),int(ssplit[1]),int(ssplit[2]))
    esplit = end.split("-")
    dateend = dt.date(int(esplit[0]),int(esplit[1]),int(esplit[2]))

    # query tmax, tmin, and tavg from the given start date
    tmax = session.query(func.max(Measurement.tobs)).filter(Measurement.date>=datestart, \
        Measurement.date<=dateend).scalar()
    tmin = session.query(func.min(Measurement.tobs)).filter(Measurement.date>=datestart, \
        Measurement.date<=dateend).scalar()
    tavg = round(session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=datestart, \
        Measurement.date<=dateend).scalar(),1)

    # close the session to end the communication with the database
    session.close()

    return \
    (
        f"Temperature statistics starting from {start} and ending {end}:</br>"
        "</br>"
        f"Maximum Temperature: {tmax} °F</br>"
        f"Minimum Temperature: {tmin} °F</br>"
        f"Average Temperature: {tavg} °F"
    )

if __name__ == "__main__":
    app.run(debug=True)