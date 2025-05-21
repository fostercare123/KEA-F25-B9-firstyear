from machine import I2C, Pin
from ens160 import ENS160
from ahtx0 import AHT20
import time

# Initialize I2C – adjust pins as needed
i2c = I2C(0, scl=Pin(26), sda=Pin(25), freq=100000)  # Change pins if needed

# Initialize sensors
ens = ENS160(i2c)
aht = AHT20(i2c)

while True:
    # Read AHT21 values
    temp_aht = aht.temperature
    rh_aht = aht.relative_humidity

    # Update ENS160 environmental data (optional, not shown in your driver)
    # Normally you'd feed temp/humidity to ENS160 if supported
    
    # Read ENS160 values
    aqi, tvoc, eco2, temp_ens, rh_ens, eco2_rating, tvoc_rating = ens.read_air_quality()

    # Print readings
    print(f"AHT21 Temp: {temp_aht:.2f}°C, RH: {rh_aht:.2f}%")
    print(f"ENS160 AQI: {aqi}, TVOC: {tvoc} ppb, eCO2: {eco2} ppm")
    print(f"ENS160 Rating: eCO2 -> {eco2_rating}, TVOC -> {tvoc_rating}")
    print("-----")
    time.sleep(3)
