# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime, timedelta


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model

# reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
app = Flask(__name__)

#################################################
# Flask Setup
#################################################


#################################################
# Flask Routes
#################################################
def home():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prcp_data = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    return jsonify(dict(prcp_data))


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_data = session.query(Station.station).all()
    session.close()
    return jsonify([station[0] for station in station_data])


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]
    most_recent_date = datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - timedelta(days=365)
    most_active_station = (
        session.query(Measurement.station)
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .first()[0]
    )
    tobs_data = (
        session.query(Measurement.date, Measurement.tobs)
        .filter(Measurement.station == most_active_station)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )
    session.close()
    return jsonify(dict(tobs_data))


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end=None):
    session = Session(engine)
    if end is None:
        data = (
            session.query(
                func.min(Measurement.tobs),
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs),
            )
            .filter(Measurement.date >= start)
            .all()
        )
    else:
        data = (
            session.query(
                func.min(Measurement.tobs),
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs),
            )
            .filter(Measurement.date >= start)
            .filter(Measurement.date <= end)
            .all()
        )
    session.close()
    return jsonify(data[0])


if __name__ == "__main__":
    app.run(debug=True)
