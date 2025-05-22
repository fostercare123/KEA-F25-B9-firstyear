import DB
import base64 # Graphs

from matplotlib.figure import Figure
from io import BytesIO # Graphs and stuff


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

def create_graph(datarow, datarow2 = 0, minuts = 5):
    print("----------------------------------")
    print(f"Create Graph Function is running")
    # Fetch recent data from database
    recent_data = DB.fetch_temps_last_x_minutes(minuts)
    # This ^ function returns a list of all types of readings the last x minuttes
    # Check to make sure things don't go south, in case no readings are returned
    if not recent_data:
        print(f"if not recent_data: was run :(")
        return None
    
    # Time stuff - DONT TOUCH!
    # One row looks like:
    # (id, timestamp, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht)
    # [(57, '2025-05-18 09:52:51', 2.0, 196.0, 688.0, 0.1953125, 'Good - Average', 'Unhealthy', 276.0063, 27.41, 51.39)]
    # row[4] says that we want the fith element (timestamp) in the recent_data pull from the SQLite database
    # The timestamp looks like this:
    # '2025-12-31 17:59:30'
    # [-8] slices the last 8 charaters from the timestamp string, which gives us:
    #  17:59:30'
    
    times = [row[1][-8:] for row in recent_data]  # Only show HH:MM:SS
    print(times)
    # Row[3] says that we want the forth element:
    # (id, temperature, humidity, earthhumidity, timestamp)
    # datarow is the data to be extrated from our recent_data pull from DB
    # (id, timestamp, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht)
    #  0 , 1        , 2  , 3   , 4   , 5    , 6         , 7         , 8      , 9      , 10
    
    values = [row[datarow] for row in recent_data]  # value
    if datarow2 != 0:
        values2 = [row[datarow2] for row in recent_data] # Value 2
    
    # print(recent_data)

    fig = Figure(figsize=(12, 6))  # Width=3 inches, Height=1 inch
    # Axix X
    ax = fig.subplots()
    # Rotate x-axis labels
    ax.tick_params(axis='x', rotation=45)
    # First line
    ax.plot(times, values,label= str(datanames.get(datarow)))

    # Second optinal line if datarow 2 != 0 is true
    title = datanames.get(datarow)
    if datarow2 != 0:
        ax.plot(times, values2, label= str(datanames.get(datarow2)))
        title += " & " + datanames.get(datarow2)
    
    ax.set_title(f"{title} (Last {minuts} Minutes)")
    ax.set_ylabel("Values")
    ax.set_xlabel("Time")
    ax.set_xticks(times[::10]) # Says that every ::n x titel is shown. Change n
    ax.legend() # Box with info and stuff
    ax.grid(True)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode("ascii")
    #print(f"Trying to print image - Hoping for the best...")
    #print(image_base64)
    print("----------------------------------")
    return image_base64