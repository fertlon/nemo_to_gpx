import requests
from datetime import datetime, timedelta
from gpxpy import gpx
import json


def datetime_to_api_str(datetime):
    """

    :param datetime: date at the datetime format
    :return: date at the string format used in CLS's API
    """
    # Format should be: '2022-10-13_11:02:37.380000000'
    out_date_str = f'{datetime.year:04d}-{datetime.month:02d}-{datetime.day:02d}_' \
                   f'{datetime.hour:02d}:{datetime.minute:02d}:{datetime.second:02d}.' \
                   f'{datetime.microsecond}'
    return out_date_str


def load_api_param(param_file_path):
    """

    :param param_file_path: parameter file (json)
    :return: id and password to be used for the API request
    """
    with open(param_file_path, "r") as file:
        param_data = json.load(file)
        return param_data['id'], param_data['pwd']


def main():
    # Define the time window
    start_oleron = datetime(2022, 10, 27, 6, 30)  # UTC departure time from Oléron
    arrival_lacorona = datetime(2022, 10, 31, 13, 15)  # UTC arrival time in La Coroña

    start_date = start_oleron  # end_date - timedelta(hours=3)
    end_date = arrival_lacorona  # datetime.utcnow()

    # Convert the dates to the API date format
    end_date_str = datetime_to_api_str(end_date)
    start_date_str = datetime_to_api_str(start_date)
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

    if data['data']:
        n_points = len(data['data'])
        print(f'Number of points: {n_points}')
        # Creating a new gpx file
        gpx_data = gpx.GPX()
        # Create first track in our GPX
        gpx_track = gpx.GPXTrack()
        gpx_data.tracks.append(gpx_track)
        # Create first segment in our GPX track
        gpx_segment = gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        # Create points
        for it_response in data['data']:
            this_date = datetime.strptime(it_response['locDate'], "%Y-%m-%d_%H:%M:%S")
            if start_date <= this_date <= end_date:
                gpx_segment.points.append(
                    gpx.GPXTrackPoint(longitude=it_response['loc'][0],
                                      latitude=it_response['loc'][1],
                                      elevation=0,
                                      time=this_date,
                                      comment=f"SOG: {it_response['speed']}, COG: {it_response['heading']}"))
        # Define gpx output file
        gpx_file = 'Oleron_LaCorona.gpx'
        with open(gpx_file, 'w') as f:
            f.write(gpx_data.to_xml())
        print(f'Created GPX file {gpx_file}')


if __name__ == "__main__":
    main()
