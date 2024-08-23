from nemo_to_gpx import nemo_to_gpx, remove_middle_east_false_points
from datetime import datetime, timezone

# Define the time window
start_date = datetime(2022, 10, 27, 6, 30, tzinfo=timezone.utc)
# UTC departure time from Oléron
end_date = datetime(2024, 8, 17, 14, 0, tzinfo=timezone.utc)#datetime.now(timezone.utc)

# Define the output gpx file name
file_name = "heremoana_track.gpx"

# Define the time in minutes between 2 successive waypoints
delta_time_minutes = 10

# Generate the raw gpx file
new_name = file_name.split(sep=".")[0]
raw_file_name = f"{new_name}_raw.gpx"
nemo_to_gpx(start_date, end_date, delta_time_minutes, raw_file_name)

# Post-process the gpx file to remove erroneous points in Middle-Est (beacon problem)
remove_middle_east_false_points(raw_file_name, file_name)
