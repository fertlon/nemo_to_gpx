from nemo_to_gpx import nemo_to_gpx
from datetime import datetime, timezone

# Define the time window
start_date = datetime(2022, 10, 27, 6, 30, tzinfo=timezone.utc)  # UTC departure time from Oléron
end_date = datetime.now(timezone.utc)

# Define the output gpx file name
file_name = "heremoana_track.gpx"

# Define the time in minutes between 2 successive waypoints
delta_time_minutes = 10

# Generate the gpx file
nemo_to_gpx(start_date, end_date, delta_time_minutes, file_name)
