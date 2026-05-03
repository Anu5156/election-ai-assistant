import sys
import os
sys.path.append(os.getcwd())
try:
    from app.services.maps_service import load_stations, calculate_distance
    print("SUCCESS: Imports work locally.")
    print(f"load_stations: {load_stations}")
    print(f"calculate_distance: {calculate_distance}")
except Exception as e:
    print(f"FAILURE: {e}")
    import traceback
    traceback.print_exc()
