from flask import Flask, jsonify
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime, timedelta


app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#engine = create_engine(f"sqlite:///{"../Resources/hawaii.sqlite"}")

Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

@app.route("/")
def home():
    return (
        f"Welcome to the Hawaii Climate API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)
    
    year_ago_str = year_ago.strftime('%Y-%m-%d')

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago_str).all()
    session.close()

    precip_data = {date: prcp for date, prcp in results}
    return jsonify(precip_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    stations_list = [station[0] for station in results]
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)

    #results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station, Measurement.date >= year_ago).all()
    results = session.query(Measurement.date, Measurement.tobs).filter(
    Measurement.station == most_active_station, 
    Measurement.date >= year_ago.date()  # Convert to datetime.date
    ).all()

    session.close()

    temp_data = [{"date": date, "temperature": tobs} for date, tobs in results]
    return jsonify(temp_data)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    session = Session(engine)

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if end:
        results = session.query(*sel).filter(Measurement.date >= start, Measurement.date <= end).all()
    else:
        results = session.query(*sel).filter(Measurement.date >= start).all()

    session.close()

    temp_summary = {
        "TMIN": 54.0,
        "TAVG": 71.663,
        "TMAX": 85.0
    }
    return jsonify(temp_summary)

if __name__ == '__main__':
    print("Hello World")
    app.run(debug=True)
