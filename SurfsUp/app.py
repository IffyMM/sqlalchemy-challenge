# Import the dependencies.


import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import pandas as pd
from flask import Flask, jsonify


# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()


#################################################
# Database Setup
#################################################

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement=Base.classes.measurement
Station=Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################

app=Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return(
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/+start_date<br/>"
        f"/api/v1.0/+start_date/+end_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print('Server received request for "Precipitation" page...')
    recent_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago=dt.date(2017,8,23)-dt.timedelta(days=365)
    data=session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=one_year_ago).all()
    precipitation_data=[]
    for date, prcp in data:
        precipitation_dict={}
        precipitation_dict["date"]=date
        precipitation_dict["prcp"]=prcp
        precipitation_data.append(precipitation_dict)
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    print('Server received request for "Stations" page...')
    stations=session.query(Station.station).all()
    stations=list(np.ravel(stations))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    print('Server received request for "Temperature" page...')
    one_year_ago=dt.date(2017,8,23)-dt.timedelta(days=365)
    active_stations = session.query(Measurement.station, func.count(Measurement.id)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).\
        desc()).\
            all()
    most_active_station=active_stations[0][0]
    observed_data=session.query(Measurement.tobs).\
    filter(Measurement.station==most_active_station).\
        filter(Measurement.date>=one_year_ago).\
            all()
    observed_data=list(np.ravel(observed_data))
    return jsonify(observed_data)

@app.route("/api/v1.0/<start>")
def startDate(start):
    print('Server received request for "Start Date" page...')
    query=session.query(Measurement.tobs).filter(Measurement.date>=start).all()
    df=pd.DataFrame(query)
    tmin=df.min()
    tmax=df.max()
    tavg=df.mean()
    data=[tmin,tmax,tavg]
    data=list(np.ravel(data))
    return jsonify(data)

@app.route("/api/v1.0/<start>/<end>")
def startDateEndDate(start,end):
    print('Server received request for "Start Date and End Date" page...')
    query=session.query(Measurement.tobs).filter(Measurement.date>=start).filter(Measurement.date<=end).all()
    df=pd.DataFrame(query)
    tmin=df.min()
    tmax=df.max()
    tavg=df.mean()
    data=[tmin,tmax,tavg]
    data=list(np.ravel(data))
    return jsonify(data)



if __name__ == "__main__":
    app.run(debug=True)