from nemo_to_gpx import nemo_to_gpx
from datetime import datetime

# Define the time window
start_date = datetime(2022, 10, 27, 6, 30)  # UTC departure time from Oléron
end_date = datetime.utcnow()

# Define the output gpx file name
file_name = "heremoana_track.gpx"

# Define the time in seconds between 2 successive waypoints
delta_time_seconds = 55

# Generate the gpx file
nemo_to_gpx(start_date, end_date, delta_time_seconds, file_name)
