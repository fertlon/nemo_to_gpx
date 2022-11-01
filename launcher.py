from nemo_to_gpx import nemo_to_gpx
from datetime import datetime

# Define the output gpx file name
file_name = "output.gpx"
# Define the time window
start_date = datetime(2022, 10, 27, 6, 30)  # UTC departure time from Oléron
end_date = datetime.utcnow()

nemo_to_gpx(start_date, end_date, file_name)
