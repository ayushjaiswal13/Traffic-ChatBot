import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY") 
origin = "IIT Hyderabad"
destination = "Hitech City, Hyderabad"

url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&departure_time=now&key={API_KEY}"

response = requests.get(url)
data = response.json()

if data["status"] == "OK":
    route = data["routes"][0]["legs"][0]
    duration = route["duration"]["text"]
    traffic_duration = route.get("duration_in_traffic", {}).get("text", duration)
    print(f"Duration (without traffic): {duration}")
    print(f"Estimated with traffic: {traffic_duration}")
else:
    print("API Error:", data["status"])
