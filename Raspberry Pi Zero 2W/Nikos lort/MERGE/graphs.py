import sqlite3
import DB
import base64 # Graphs
from matplotlib.figure import Figure
from io import BytesIO # Graphs and stuff
from datetime import datetime, timedelta

# Dictionary for data name conversion
# (id, timestamp, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht)
#  0 , 1        , 2  , 3   , 4   , 5    , 6         , 7         , 8      , 9      , 10
datanames = {
    2: "AQI",               # Air Quality Index
    3: "TVOC (ppb)",          # Total Volatile organic componds, parts per billion
    4: "eCO2 (ppm)",          # Equvelant CO2 based on TVOC
    5: "Relative Humidity (%)", # Relative Humidity from ENS160
    6: "eCO2 rating",       # Rating for CO2
    7: "TVOC rating",       # Rating for TVOC
    8: "Temp (ENS160) (°)",     # Temp from ENS160
    9: "Temperature (%)",       # Temp from AHT
    10: "Humidity (°)",         #Humidity from AHT

}

def create_graph(datarow, datarow2=0, minuts=5):
    recent_data = DB.fetch_temps_last_x_minutes(minuts)
    if not recent_data:
        fig = Figure(figsize=(12, 6))
        ax = fig.subplots()
        ax.set_title("No data available")
        ax.set_ylabel("Values")
        ax.set_xlabel("Time")
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode("ascii")

    grouped_data = {}
    for row in recent_data:
        timestamp = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        interval_start = timestamp - timedelta(minutes=timestamp.minute % 5, seconds=timestamp.second, microseconds=timestamp.microsecond)
        if interval_start not in grouped_data:
            grouped_data[interval_start] = []
        grouped_data[interval_start].append(row)

    times = sorted(grouped_data.keys())
    values = [sum(row[datarow] for row in grouped_data[time]) / len(grouped_data[time]) for time in times]
    if datarow2 != 0:
        values2 = [sum(row[datarow2] for row in grouped_data[time]) / len(grouped_data[time]) for time in times]

    fig = Figure(figsize=(12, 6))
    ax = fig.subplots()
    ax.tick_params(axis='x', rotation=45)
    ax.plot([time.strftime('%H:%M') for time in times], values, label=str(datanames.get(datarow)))

    if datarow2 != 0:
        ax.plot([time.strftime('%H:%M') for time in times], values2, label=str(datanames.get(datarow2)))
        title = f"{datanames.get(datarow)} & {datanames.get(datarow2)}"
    else:
        title = datanames.get(datarow)

    ax.set_title(f"{title} (Last {minuts} Minutes)")
    ax.set_ylabel("Values")
    ax.set_xlabel("Time")
    ax.legend()
    ax.grid(True)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("ascii")

def create_combined_graph(datarow1, datarow2, minuts=5):
    recent_data = DB.fetch_temps_last_x_minutes(minuts)
    if not recent_data:
        return None

    times, values1, values2 = [], [], []
    for row in recent_data:
        times.append(row[1])
        values1.append(row[datarow1])
        values2.append(row[datarow2])

    fig = Figure(figsize=(12, 6))
    ax = fig.subplots()
    ax.plot(times, values1, label=datanames[datarow1])
    ax.plot(times, values2, label=datanames[datarow2])
    ax.set_title(f"{datanames[datarow1]} & {datanames[datarow2]} (Last {minuts} Minutes)")
    ax.legend()
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("ascii")