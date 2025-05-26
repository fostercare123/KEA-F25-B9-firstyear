import sqlite3
import random
import time
from datetime import datetime, timezone

# Define sensor IDs to simulate for (e.g., 1 to 3)
sensor_ids = [1, 2, 3]

# Example ratings for simulation
air_quality_ratings = ['Excellent', 'Good', 'Average', 'Poor']
tvoc_ratings = ['Low', 'Moderate', 'High']

def insert_simulated_reading(sensor_id, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht):
    try:
        db_path = 'sensordata.db'
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        c.execute("""
            INSERT INTO environment (esp_id, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (sensor_id, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht, timestamp))
        conn.commit()
        print(f"Data inserted for sensor {sensor_id} at {timestamp}")
    except sqlite3.Error as e:
        print(f"Error inserting data into database: {e}")
    finally:
        conn.close()

def simulate_sensor_data():
    try:
        while True:
            print("Simulation loop running...")
            for sensor_id in sensor_ids:
                # Generate random simulated sensor values.
                Aqi = round(random.uniform(0.5, 2.0), 1)
                Tvoc = round(random.uniform(30, 100), 1)
                Eco2 = round(random.uniform(400, 1000), 1)
                Rhens = round(random.uniform(0.1, 0.3), 2)
                Eco2rating = random.choice(air_quality_ratings)
                Tvocrating = random.choice(tvoc_ratings)
                Tempens = round(random.uniform(270, 280), 2)
                Tempaht = round(random.uniform(20, 30), 2)
                Rhaht = round(random.uniform(30, 70), 2)
                
                # Insert the simulated reading.
                print(f"Simulating data for sensor {sensor_id}")
                insert_simulated_reading(sensor_id, Aqi, Tvoc, Eco2, Rhens, Eco2rating, Tvocrating, Tempens, Tempaht, Rhaht)
                print(f"Simulated sensor {sensor_id} reading at {datetime.now()}")
            time.sleep(10)  # Wait 10 seconds before the next round.
    except KeyboardInterrupt:
        print("Simulation stopped by user.")

def start_simulation():
    simulate_sensor_data()

if __name__ == '__main__':
    start_simulation()