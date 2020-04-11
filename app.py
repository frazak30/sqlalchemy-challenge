# import Dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
stat = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Create an app, being sure to pass __name__
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route('/api/v1.0/<start>')
def get_t_start(start):
    session = Session(engine)
    query_result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    session.close()
    tobsall = []
    for min,avg,max in query_result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)
    return jsonify(tobsall)

@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start,stop):
    session = Session(engine)
    query_result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= stop).all()
    session.close()
    tobsall = []
    for min,avg,max in query_result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)
    return jsonify(tobsall)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    last_12 = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    query_date = dt.date(last_12.year -1, last_12.month, last_12.day)
    data_and_precipitation_scores = [measurement.date,measurement.tobs]
    queryresult = session.query(*data_and_precipitation_scores).filter(measurement.date >= query_date).all()
    session.close()
    tobsall = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)
    return jsonify(tobsall)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    data_and_precipitation_scores = [stat.station,stat.name,stat.latitude,stat.longitude,stat.elevation]
    query_result = session.query(*data_and_precipitation_scores).all()
    session.close()
    stations = []
    for station,name,lat,lon,el in query_result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)
    return jsonify(stations)

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    data_and_precipitation_scores = [measurement.date,measurement.prcp]
    queryresult = session.query(*data_and_precipitation_scores).all()
    session.close()
    precipitation = []
    for date, prcp in queryresult:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        precipitation.append(precipitation_dict)
    return jsonify(precipitation)
if __name__ == '__main__':
    app.run(debug=True)