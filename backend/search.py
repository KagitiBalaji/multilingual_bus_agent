import json
import os
from fuzzywuzzy import fuzz

# Load bus data from JSON
def load_bus_data():
    data_path = os.path.join(os.path.dirname(__file__), "data", "bus_timings.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

bus_data = load_bus_data()

# Improved search function with fuzzy matching
def find_buses(destination_query):
    destination_query = destination_query.lower()
    best_match = None
    highest_score = 0
    
    for bus in bus_data:
        # Calculate match score
        score = fuzz.token_set_ratio(destination_query, bus["route"].lower())
        if score > highest_score:
            highest_score = score
            best_match = bus
    
    # Return best match if above threshold
    if best_match and highest_score > 60:
        return {
            "route": best_match["route"],
            "departure_times": best_match["departure_times"],
            "bus_type": best_match["bus_type"]
        }
    return None