
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
###################################################
# create engine to hawaii.sqlite
###################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement=Base.classes.measurement
Station=Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Route Setup
#################################################
@app.route("/")
def welcome():
    return(
        f"Welcome to Climate API!<br/>"
        f"Available Routes : <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"

    )


@app.route("/api/v1.0/precipitation")
def precipite():
    """Return a JSON list of precipitations for last 12 months from the dataset."""
    #create the session 
    session = Session(engine)
    # Find the most recent date in the data set.
    recent_date=session.query(measurement.date).order_by(measurement.date.desc()).first()
    # Design a query to retrieve the last 12 months of precipitation data 
    cdate=dt.datetime.strptime(recent_date.date,  "%Y-%m-%d")
    query_date=(cdate - dt.timedelta(days=365))
    # Perform a query to retrieve the data and precipitation scores
    result=session.query(measurement.date, measurement.prcp ).\
        filter(measurement.date > query_date).\
        group_by(measurement.date).all()
    session.close()
    #Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    all_precipitation=[]
    for date, prcp in result:
        precipitate_dict={}
        precipitate_dict[date]= prcp
        all_precipitation.append(precipitate_dict)
       
    return jsonify(all_precipitation)  


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    #create the session 
    session = Session(engine)

    #Query stations
    stations = session.query(Station.station, Station.name,
        Station.latitude, Station.longitude, Station.elevation).all()

    session.close()
    all_stations=[]
    for station, name, latitude, longitude, elevation in stations:
        station_dict={}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """ Return a JSON list of temperature observations (TOBS) for the previous year."""
     #create the session 
    session = Session(engine)
    #Find last year of data
    recent_date=session.query(measurement.date).order_by(measurement.date.desc()).first()
    cdate=dt.datetime.strptime(recent_date.date,  "%Y-%m-%d")
    date_year_earlier=(cdate - dt.timedelta(days=365))
    # Design a query to find the most active stations 
    same_station=session.query(measurement.station,\
        func.count(measurement.station)).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).all()
    most_active_station=same_station[0][0]
    active_last_year=session.query(measurement.date, measurement.tobs ).\
        filter(measurement.station == most_active_station).\
        filter(measurement.date >= date_year_earlier ).\
        order_by(measurement.tobs.desc()).\
        all()

    session.close()
    all_temp=[]
    for date, temp in active_last_year:
        temp_dict = {}
        temp_dict[date]= temp
        all_temp.append(temp_dict)
    return jsonify(all_temp)

if __name__ == "__main__":
    app.run(debug=True)