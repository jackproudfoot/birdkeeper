import click
import datetime
from shutil import copyfile
from dateutil import parser
import pathlib
import geojson
import json
from metadata.extract import extract_metadata, organize_media
from metadata.util import get_metadata_file
import requests
from urllib.parse import urljoin
import os
from tabulate import tabulate
from metadata.util import sample_frames

'''
Create plan for importing media from external disk
'''
def import_plan(media_path, harddrive_path, pilot, debug = False):
    new_flights, unsorted_media, unparsed_media = organize_media(media_path, debug)

    harddrive_dir = pathlib.Path(harddrive_path)

    # Scan for existing flights on those days
    for date in new_flights.keys():
        existing_flights = get_existing_flights(harddrive_dir.joinpath(date))

        new_flights[date] = new_flights[date] + existing_flights 


    plan = {
        'flight': [],
        'media': []
    }
    
    # Sort flights by start time and import files
    for date, date_flights in new_flights.items():
        sorted_flights = sorted(date_flights, key=lambda d: d['start'] if isinstance(d['start'], datetime.datetime) else parser.parse(d['start']))

        for index, flight in enumerate(sorted_flights[::-1]):
            flight_num = len(sorted_flights) - index

            new_flight_dir = harddrive_dir.joinpath(date).joinpath("Flight {}".format(flight_num))

            # Existing flight
            if 'current_flight_num' in flight:
                current_flight_num = int(flight['current_flight_num'])

                # New flight num doesn't match current flight num
                if flight_num != current_flight_num:
                    
                    current_path = harddrive_dir.joinpath(date).joinpath("Flight {}".format(current_flight_num))
                    plan_item = {
                        'flight_num': flight_num,
                        'type': 'rename_flight',
                        'current_flight_num': current_flight_num,
                        'current_path': current_path,
                        'new_path': new_flight_dir
                    }
                    plan['flight'].append(plan_item)


            # New flight
            else:
                plan_item = {
                    'flight_num': flight_num,
                    'type': 'create_flight',
                    'flight_metadata': {k: str(flight[k]) for k in ('run_id', 'start', 'end', 'drone_id')},
                    'new_path': new_flight_dir
                }
                plan_item['flight_metadata']['pilot'] = pilot
                plan['flight'].append(plan_item)

                # Add import media plans for flight media
                for media in flight['media']:
                    media_plan_item = {}
                    media_plan_item['type'] = 'import_media'
                    media_plan_item['current_path'] = media
                    media_plan_item['new_path'] = new_flight_dir.joinpath(media.name)
                    media_plan_item['run_id'] = plan_item['flight_metadata']['run_id']
                    media_plan_item['time'] = plan_item['flight_metadata']['start']
                    plan['media'].append(media_plan_item)
                

    
    # Create plan item for unsorted media
    for unsorted_image in unsorted_media:
        plan_item = {}
        plan_item['type'] = 'import_media'

        plan_item['current_path'] = unsorted_image

        image_metadata_path = get_metadata_file(unsorted_image)
                
        with open(image_metadata_path, 'r') as image_metadata_file:
            image_metadata = json.load(image_metadata_file)

            date_parts = image_metadata['DateTime'].split(" ")[0].split(':')

        plan_item['new_path'] = harddrive_dir.joinpath('{}-{}-{}'.format(date_parts[1], date_parts[2], date_parts[0][2:4])).joinpath('unsorted').joinpath(unsorted_image.name)

        plan['media'].append(plan_item)


    # Create plan item for unparsed media
    for unparsed in unparsed_media:
        plan_item = {}
        plan_item['type'] = 'import_media'
        plan_item['skip_metadata'] = True
        plan_item['current_path'] = unparsed
        plan_item['new_path'] = harddrive_dir.joinpath('unparsed').joinpath(unparsed.name)

        plan['media'].append(plan_item)

    return plan


def import_media(plan, drone, debug = False):

    # dict to store database uids for flights
    database_uids = {}

    # Do one pass over flight plans to rename existing flights to prevent accidental overwriting
    # First pass for existing flights

    sorted_flight_plans = sorted(plan['flight'], reverse=True, key=lambda d: int(d['flight_num']))

    for flight_import_plan in sorted_flight_plans:
        if flight_import_plan['type'] == 'rename_flight':
            current_path = flight_import_plan['current_path']

            current_path.rename(flight_import_plan['new_path'])

    # Second pass for new flights
    for flight_import_plan in sorted_flight_plans:
        if flight_import_plan['type'] == 'create_flight':
            new_path = flight_import_plan['new_path']

            try:
                new_path.mkdir(parents=True, exist_ok=False)
            except FileExistsError:
                print('Could not create new Flight {} ({}) since folder already exists.'.format(flight_import_plan['flight_num'], new_path))
                exit(1)

            # Create flight metadata file

            flight_metadata = flight_import_plan['flight_metadata']

            with open(new_path.joinpath('metadata.json'), 'w') as f:
                    json.dump(flight_metadata, f)

            # Upload flight metadata to metadata database

            res = requests.post(f"{os.environ.get('API_URL')}/flight", json={
                'run_id': flight_metadata['run_id'],
                'drone_name': drone,
                'drone_id': flight_metadata['drone_id'],
                'pilot_name': flight_metadata['pilot'],
                'start': flight_metadata['start'],
                'end': flight_metadata['end']
            })

            if (res.status_code != 200 and res.status_code != 201):
                click.echo(click.style('Error: {}'.format(res.text), fg='red'))
                exit(1)

            # track mapping of run_id => flight_uid from database
            database_uids[flight_metadata['run_id']] = json.loads(res.text)['flight_uid']



    # Import plan media

    for media_import_plan in plan['media']:
        current_path = media_import_plan['current_path']
        new_path = media_import_plan['new_path']

        new_path.parent.mkdir(exist_ok=True)

        copyfile(current_path, new_path)

        # Import media metadata
        if 'skip_metadata' not in media_import_plan or not media_import_plan['skip_metadata']:
            current_metadata_path = get_metadata_file(current_path)
            new_metadata_path = get_metadata_file(new_path)

            new_metadata_path.parent.mkdir(parents=True, exist_ok=True)

            copyfile(current_metadata_path, new_metadata_path)

            # Upload media metadata to metadata database
            flight_uid = database_uids[media_import_plan['run_id']]

            
            media_type = pathlib.Path(new_path).suffix.lower()[1:]

            with open(new_metadata_path, 'r') as media_metadata_fd:
                media_metadata = json.load(media_metadata_fd)
                
                # Create geojson data from media
                geometry = None
                if media_type == 'jpg':
                    lat_raw = media_metadata['GPSInfo']['GPSLatitude']
                    long_raw = media_metadata['GPSInfo']['GPSLongitude']

                    lat = lat_raw[0] + lat_raw[1] / 60 + lat_raw[2] / 3600
                    long = -long_raw[0] + long_raw[1] / 60 + long_raw[2] / 3600

                    lat *= -1 if media_metadata['GPSInfo']['GPSLatitudeRef'] == 'S' else 1
                    long *= -1 if media_metadata['GPSInfo']['GPSLatitudeRef'] == 'W' else 1

                    altitude = media_metadata['GPSInfo']['GPSAltitude']

                    geometry = geojson.Point((long, lat, altitude))
                elif media_type == 'mp4':
                    frames = sample_frames(media_metadata['frame'])

                    points = []

                    for frame in frames:
                        frame_metadata = frame['metadata']

                        if 'location' in frame_metadata:
                            points.append((frame_metadata['location']['longitude'], frame_metadata['location']['latitude'], frame_metadata['location']['altitude']))

                    geometry = geojson.LineString(points)

            
            # Upload metadata and geojson representation to database
            res = requests.post(f"{os.environ.get('API_URL')}/flight/media", json={
                'flight_uid': flight_uid,
                'media_data': {
                    'file': str(new_path),
                    'type': media_type,
                    'geometry': geometry,
                    'datetime_recorded': media_import_plan['time']
                }
            })

            if (res.status_code != 200 and res.status_code != 201):
                click.echo(click.style('Error uploading media metadata [{}]: {}'.format(new_metadata_path, res.text), fg='red'))




    # Format tabular output

    # runs_table = [
    #     [ run['run_id'], run['start'], run['end'], tabulate([
    #         [media_path.name] for media_path in run['media']
    #     ], tablefmt="plain")
    #     ]
    #     for run in sorted_runs
    # ]

    # colored_headers = ['\u001b[36m{}\u001b[0m'.format(header) for header in ['Run ID', 'Start Time', 'Approx. End Time', 'Media']]

    # print(tabulate(runs_table, headers=colored_headers, tablefmt="simple_grid"))

    # # Unsorted images
    # if len(unsorted_images) > 0:
    #     colored_headers = ['\u001b[31m{}\u001b[0m'.format(header) for header in ['Unsorted Images (Not Imported)']]
    #     print(tabulate([[image] for image in unsorted_images], headers=colored_headers, tablefmt='simple_grid'))

    # # Media that failed to parse
    # if  len(unparsed_media) > 0:
    #     colored_headers = ['\u001b[31m{}\u001b[0m'.format(header) for header in ['Media Failed to Parse (Not Imported)']]
    #     print(tabulate([[video] for video in unparsed_media], headers=colored_headers, tablefmt='simple_grid'))

    

'''
Scans the provided drone path and determines the next flight index to use
Drone day path must be in format */Drone Name/MM-DD-YY
'''
def get_existing_flights(drone_day_path):
    parent_dir = pathlib.Path(drone_day_path)

    # If parent directory doesn't exist, return empty array
    if not parent_dir.exists():
        return []

    # Get existing flight directories
    existing_flights = sorted(parent_dir.glob('Flight *'))

    flights = []

    # Load start time from general flight metadata file
    for flight_dir in existing_flights:
        metadata_filepath = flight_dir.joinpath('metadata.json')

        with open(metadata_filepath, 'r') as f:
            metadata = json.load(f)
            metadata['current_flight_num'] = flight_dir.name.split(' ')[1]
            flights.append(metadata)
    
    return flights