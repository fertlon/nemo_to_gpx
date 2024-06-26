import requests
from datetime import datetime, timezone
import pytz
from gpxpy import gpx, parse
import json


def datetime_to_api_str(date: datetime):
    """

    This function writes a date from the datetime format to the str format used in CLS API.

    :param date: date at the datetime format
    :return: date at the string format used in CLS API
    """
    # Format should be: '2022-10-13_11:02:37.380000000'
    out_date_str = (
        f"{date.year:04d}-{date.month:02d}-{date.day:02d}_"
        f"{date.hour:02d}:{date.minute:02d}:{date.second:02d}."
        f"{date.microsecond}"
    )
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
        return param_data["id"], param_data["pwd"]


def nemo_to_gpx(
    start_date: datetime,
    end_date: datetime,
    delta_time_minutes: int = 0,
    file_name: str = "output.gpx",
):
    """

    This function creates a gpx file with all the positions of the NEMO beacon in a given time window.

    :param start_date: start date at the datetime format
    :param end_date: end date at the datetime format
    :param delta_time_minutes : step in minutes between 2 points in the GPX file
    :param file_name: output relative file name (.gpx)
    :return: none
    """

    # Paris datetime
    paris_tz = pytz.timezone("Europe/Paris")

    # Convert the dates to the API date format
    start_date_str = datetime_to_api_str(start_date)
    end_date_str = datetime_to_api_str(end_date)
    print(f"Start date: {start_date_str}")
    print(f"End date: {end_date_str}")

    # Load API username and password
    param_file = "param.json"
    api_id, api_pwd = load_api_param(param_file)

    # Launch the API request
    request_str = f"https://fishweb-nemo.cls.fr/uda/resources/positions?application=umv&login={api_id}&password={api_pwd}&orderBy=locDate&fields=heading%2Cspeed%2CmobileId%2Cloc%2ClocDate%2Cnature%2Csource%2CmobileName%2CmobileMmsi%2CqualityOverall%2CmobileCountryCode%2CmobileType%2CradarEchoId%2CmobileImo%2CmobileCallSign&from={start_date_str}&to={end_date_str}&dateType=creation&mode=default"
    print(f"\nLaunching following API request:\n{request_str}")
    response = requests.get(request_str)
    print("\nAPI request downloaded !")
    data = response.json()
    # Create GPX file
    if data["data"]:
        n_points = len(data["data"])
        print(f"Number of points from the API: {n_points}")
        # Creating a new gpx file
        gpx_data = gpx.GPX()
        # Create first track in our GPX
        gpx_track = gpx.GPXTrack()
        gpx_data.tracks.append(gpx_track)
        # Create first segment in our GPX track
        gpx_segment = gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        # Create points
        this_last_date = datetime.strptime(
            data["data"][0]["locDate"], "%Y-%m-%d_%H:%M:%S"
        ).replace(tzinfo=timezone.utc)
        # Initialize the number of points in the GPX file
        n_points_out = 0
        # Initialize the average speed
        speed_average = 0
        # Initialize the number of points used to average the data
        n_points_average = 0
        for it_response in data["data"]:
            this_date = datetime.strptime(
                it_response["locDate"], "%Y-%m-%d_%H:%M:%S"
            ).replace(tzinfo=timezone.utc)
            try:
                this_sog = it_response["speed"]
            except:
                print(f"{this_date}: no SOG, replaced by 0")
                this_sog = 0
            try:
                this_cog = it_response["heading"]
            except:
                print(f"{this_date}: no COG, replaced by 0")
                this_cog = 0
            if (
                (this_date - this_last_date).total_seconds() / 60 > delta_time_minutes
            ) or it_response == data["data"][-1]:
                # Keep only points that respect the input delta time and the last point
                if (
                    start_date <= this_date <= end_date
                ):  # Keep only points in the investigated time window
                    longitude_mod_360 = (it_response["loc"][0]) % 360
                    gpx_segment.points.append(
                        gpx.GPXTrackPoint(
                            longitude=longitude_mod_360,
                            latitude=it_response["loc"][1],
                            elevation=0,
                            time=this_date,
                            name=f"Date: {this_date} UTC, SOG: {this_sog}, "
                            f"COG: {this_cog}",
                        )
                    )
                    this_last_date = this_date
                    n_points_out += 1
                    # Add speed to average if different from 0
                    if this_sog != 0:
                        speed_average += float(this_sog)
                        n_points_average += 1
            # Add a waypoint to the last waypoint
            if it_response == data["data"][-1]:
                # Write the date in Paris time for the last waypoint that will be displayed on the map
                this_date_paris_tz_str = (
                    this_date.replace(tzinfo=timezone.utc)
                    .astimezone(paris_tz)
                    .strftime("%d-%m-%Y %H:%M")
                )
                print(f"\nLast known position: {this_date} UTC")
                print(f"Last known COG: {this_cog}°")
                print(f"Last known SOG: {this_sog} kt")
                last_wp = gpx.GPXWaypoint(
                    longitude=it_response["loc"][0],
                    latitude=it_response["loc"][1],
                    elevation=0,
                    time=this_date,
                    name=f"Date: {this_date_paris_tz_str}, {this_sog} kt",
                )
                gpx_data.waypoints.append(last_wp)

        # Define gpx output file
        with open(file_name, "w") as f:
            f.write(gpx_data.to_xml())
        print(f'\nCreated GPX file "{file_name}" with {n_points_out} points')

        # Print average speed in kts (*1,945 => Pourquoi ce coef et non pas 1,852 ? sur fishweb-nemo, la vitesse est
        # en noeuds, alors que la vitesse renvoyée est dans une unité inconnue, donc coef trouvé empiriquement... )
        speed_average = (speed_average / n_points_average) * 1.945
        format_speed = "{:.1f}".format(speed_average)
        print(f"Average speed = {format_speed} kts")

        # Print total distance in nautical miles
        total_dist_nm = gpx_track.length_2d() / 1852
        format_total_dist = "{:.0f}".format(total_dist_nm)
        print(f"Total distance = {format_total_dist} nm")


def remove_middle_east_false_points(file_name_input: str, file_name_postpro: str):
    """

    This function removes some erroneous points in Middle-East, that are due to a problem with the beacon

    :param file_name_input: input file name in str
    :param file_name_postpro: output file name in str
    :return: none
    """
    # Load input gpx file
    gpx_file = open(file_name_input, "r")
    gpx_old = parse(gpx_file)
    # Create a new empty gpx file
    gpx_new = gpx.GPX()
    # Create first track in our GPX
    gpx_track = gpx.GPXTrack()
    gpx_new.tracks.append(gpx_track)
    # Create first segment in our GPX track
    gpx_segment = gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    # Add a waypoint to the last waypoint
    gpx_new.waypoints.append(gpx_old.waypoints[0])
    # Keep only non-erroneous points
    n_dis_pts = 0
    print("\nStart post-processing...")
    for track in gpx_old.tracks:
        for segment in track.segments:
            for point in segment.points:
                if (abs(point.latitude - 33.81825) < 0.1) & (
                    abs(point.longitude - 35.4908) < 0.1
                ):
                    n_dis_pts += 1
                elif (abs(point.latitude - 31.6561) < 0.1) & (
                    abs(point.longitude - 34.53845) < 0.1
                ):
                    n_dis_pts += 1
                else:
                    gpx_segment.points.append(point)

    print(f"{n_dis_pts} discarded points")
    # Define output gpx output file
    with open(file_name_postpro, "w") as f:
        f.write(gpx_new.to_xml())
    print(f'Created GPX file "{file_name_postpro}"')

    # Print total distance in nautical miles
    total_dist_nm = gpx_track.length_2d() / 1852
    format_total_dist = "{:.0f}".format(total_dist_nm)
    print(f"Total distance = {format_total_dist} nm")
