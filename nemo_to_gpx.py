import requests
from datetime import datetime
from gpxpy import gpx
import json
from functions_for_cartography import distance_gps


def datetime_to_api_str(date: datetime):
    """

    This function writes a date from the datetime format to the str format used in CLS API.

    :param date: date at the datetime format
    :return: date at the string format used in CLS API
    """
    # Format should be: '2022-10-13_11:02:37.380000000'
    out_date_str = f'{date.year:04d}-{date.month:02d}-{date.day:02d}_' \
                   f'{date.hour:02d}:{date.minute:02d}:{date.second:02d}.' \
                   f'{date.microsecond}'
    return out_date_str


def load_api_param(param_file_path: str):
    """

    This function loads the parameter file "param.json" which contains the id and the password needed for the API
    request.

    :param param_file_path: parameter file relative path (json)
    :return: id and password to be used for the API request
    """
    with open(param_file_path, "r") as file:
        param_data = json.load(file)
        return param_data['id'], param_data['pwd']


def nemo_to_gpx(start_date: datetime, end_date: datetime, delta_time_minutes: int = 0, file_name: str = 'output.gpx'):
    """

    This function creates a gpx file with all the positions of the NEMO beacon in a given time window.

    :param start_date: start date at the datetime format
    :param end_date: end date at the datetime format
    :param file_name: output relative file name (.gpx)
    :param delta_time_minutes : step in minutes between 2 points in the GPX file
    :return: none
    """
    # Convert the dates to the API date format
    start_date_str = datetime_to_api_str(start_date)
    end_date_str = datetime_to_api_str(end_date)
    print(f"Start date: {start_date_str}")
    print(f"End date: {end_date_str}")

    # Load API username and password
    param_file = 'param.json'
    api_id, api_pwd = load_api_param(param_file)

    # Launch the API request
    response = requests.get(
        'https://fishweb-nemo.cls.fr/uda/resources/positions?' +
        f'application=umv&login={api_id}&password={api_pwd}&orderBy=locDate&fields=heading' +
        '%2Cspeed%2CmobileId%2Cloc%2ClocDate%2Cnature%2Csource%2CmobileName%2CmobileMmsi%' +
        '2CqualityOverall%2CmobileCountryCode%2CmobileType%2CradarEchoId%2CmobileImo%2CmobileCallSign&' +
        f'from={start_date_str}&to={end_date_str}&dateType=creation&mode=default')
    data = response.json()
    # Create GPX file
    if data['data']:
        n_points = len(data['data'])
        print(f'Number of points from the API: {n_points}')
        # Creating a new gpx file
        gpx_data = gpx.GPX()
        # Create first track in our GPX
        gpx_track = gpx.GPXTrack()
        gpx_data.tracks.append(gpx_track)
        # Create first segment in our GPX track
        gpx_segment = gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        # Create points
        this_last_date = datetime.strptime(data['data'][0]['locDate'], "%Y-%m-%d_%H:%M:%S")
        # Initialize the number of points in the GPX file
        n_points_out = 0
        # Initialize the average speed
        speed_average = 0
        # Initialize the number of points used to average the data
        n_points_average = 0
        n_index = 0
        total_dist = 0
        lat_a = 0
        long_a = 0
        for it_response in data['data']:
            this_date = datetime.strptime(it_response['locDate'], "%Y-%m-%d_%H:%M:%S")
            if (this_date - this_last_date).total_seconds() / 60 > delta_time_minutes:
                if start_date <= this_date <= end_date:  # Keep only points in the investigated time window
                    gpx_segment.points.append(
                        gpx.GPXTrackPoint(longitude=it_response['loc'][0],
                                          latitude=it_response['loc'][1],
                                          elevation=0,
                                          time=this_date,
                                          name=f"Date: {this_date} UTC, SOG: {it_response['speed']}, "
                                               f"COG: {it_response['heading']}"))
                    this_last_date = this_date
                    n_points_out += 1

                    # Add speed to average if different from 0
                    if float(it_response['speed']) != 0:
                        speed_average += float(it_response['speed'])
                        n_points_average += 1

            # Add a waypoint to the last waypoint
            if it_response == data['data'][-1]:
                print(f'\nLast known position: {this_date}')
                last_wp = gpx.GPXWaypoint(longitude=it_response['loc'][0],
                                          latitude=it_response['loc'][1],
                                          elevation=0,
                                          time=this_date,
                                          name=f"Date: {this_date} UTC, SOG: {it_response['speed']}, "
                                               f"COG: {it_response['heading']}")
                gpx_data.waypoints.append(last_wp)
            # Compute total distance and speed
            long_b = it_response['loc'][0]
            lat_b = it_response['loc'][1]
            # Compute distance between two last points after first point
            if n_index > 2 and float(it_response['speed']) != 0 and not (long_a == long_b and lat_a == lat_b):
                dist = distance_gps(lat_a, long_a, lat_b, long_b) / 1852
                total_dist += dist

            n_index += 1
            long_a = it_response['loc'][0]
            lat_a = it_response['loc'][1]
        # Define gpx output file
        with open(file_name, 'w') as f:
            f.write(gpx_data.to_xml())
        print(f'Created GPX file "{file_name}" with {n_points_out} points')

        # Print average speed in kts (*1,945 => Pourquoi ce coef et non pas 1,852 ? sur fishweb-nemo, la vitesse est
        # en noeuds, alors que la vitesse renvoyée est dans une unité inconnue, donc coef trouvé empiriquement... )
        speed_average = (speed_average / n_points_average) * 1.945
        format_speed = "{:.2f}".format(speed_average)
        print(f'Average speed = {format_speed} kts')

        # Print total distance in nautical miles
        format_total_dist = "{:.1f}".format(total_dist)
        print(f'Total distance = {format_total_dist} nmi')
