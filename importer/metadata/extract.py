from dateutil import parser
import datetime
import subprocess
import pathlib
import json

from PIL import Image, TiffImagePlugin, ExifTags

def extract_metadata(media_file, metadata_path = None, debug = False):
    filetype = pathlib.Path(media_file).suffix.lower()

    if (filetype == '.mp4'):
        extract_video_metadata(media_file, metadata_path, debug)
    elif (filetype == '.jpg'):
        extract_photo_metadata(media_file, metadata_path, debug)
    else:
        print('Error media format (%s) not supported.' % filetype)

def extract_photo_metadata(photo_file, metadata_path = None, debug = False):
    print('Extracting metadata from image ({})'.format(photo_file))

    # Open image using Pillow library
    image = Image.open(photo_file)

    exif = {}

    # Parse exif data and make it serializeable
    for k, v in image._getexif().items():
        if k in ExifTags.TAGS:
            if isinstance(v, TiffImagePlugin.IFDRational):
                v = float(v)
            elif isinstance(v, tuple):
                v = tuple(float(t) if isinstance(t, TiffImagePlugin.IFDRational) else t for t in v)
            elif isinstance(v, bytes):
                v = v.decode(errors="replace")
            exif[ExifTags.TAGS[k]] = v

    # Parse GPS info if included in the image
    if 'GPSInfo' in exif.keys():
        # Add proper gps tags and make values serializeable
        old_gps_info = exif['GPSInfo']
        exif['GPSInfo'] = {}

        for k, v in old_gps_info.items():
            if isinstance(v, TiffImagePlugin.IFDRational):
                v = float(v)
            elif isinstance(v, tuple):
                v = tuple(float(t) if isinstance(t, TiffImagePlugin.IFDRational) else t for t in v)
            elif isinstance(v, bytes):
                v = v.decode(errors="replace")
            exif['GPSInfo'][ExifTags.GPSTAGS.get(k, k)] = v

    image.close()

    print('Metadata extracted!')

    if debug:
        print(json.dumps(exif, indent=2))


    # Set metadata path
    photo_path = pathlib.Path(photo_file)
    metadata_dir = photo_path.parent

    if (metadata_path != None):
        metadata_dir = pathlib.Path(metadata_path).resolve()
    metadata_dir.mkdir(parents=True, exist_ok=True)

    # Save image exif metadata to .json file
    metadata_file = metadata_dir.joinpath(photo_path.name).with_suffix(photo_path.suffix + '.json')
    with open(metadata_file, 'w') as f:
        json.dump(exif, f, indent=2)

'''
Run docker container containing vmeta-extract tool to extract frame metadata from videos
https://github.com/Parrot-Developers/libvideo-metadata
'''
def extract_video_metadata(video_file, metadata_path = None, debug = False):
    # Get relative path to script from current working directory
    script = pathlib.Path(__file__).parent.joinpath('extract.sh').relative_to(pathlib.Path.cwd())

    # Separate the path into the directory and file
    video_path = pathlib.PurePath(video_file)
    dir = video_path.parent.as_posix()
    vid = video_path.name

    print('Extracting metadata from video ({}) in ({})'.format(vid, dir))

    try:
        proc = subprocess.run(['sh', './{}'.format(script), dir, vid], stdout=subprocess.PIPE, check=True)

        if debug:
            print(proc.stdout.decode())

    except subprocess.CalledProcessError as err:
        raise Exception('Failed to extract frame metadata from {}'.format(video_path))

    # Move metadata file if metadata path set
    if (metadata_path != None):
        metadata_dir = pathlib.Path(metadata_path).resolve()
        metadata_dir.mkdir(parents=True, exist_ok=True)

        metadata_file = pathlib.Path(video_path.with_suffix(video_path.suffix + '.json'))
        metadata_file.rename(metadata_dir.joinpath(metadata_file.name))

    print('Metadata extracted!')


def organize_media(media_path, debug = False):
    media_dir = pathlib.Path(media_path)

    # Initialize metadata dir
    metadata_dir = media_dir.joinpath('metadata')
    metadata_dir.mkdir(parents=True, exist_ok=True)

    # Get list of videos and images to import
    videos = sorted(media_dir.glob('*.MP4'))
    images = sorted(media_dir.glob('*.JPG'))

    # Media that was unable to be parsed
    unparsed_media = []

    # Extract runs from metadata
    runs = {}
    for video in videos:
        # Get path to metadata file
        video_metadata_file = metadata_dir.joinpath(video.name).with_suffix(video.suffix + '.json')

        # If metadata doesn't exist, extract it
        if (not video_metadata_file.exists()):
            try:
                extract_metadata(video, metadata_path=metadata_dir, debug=debug)
            except Exception:
                unparsed_media.append(video)
                continue

        # Load metadata from file
        with open(video_metadata_file, 'r') as f:
            video_metadata = json.load(f)
        
        # Get run
        run_id = video_metadata['session']['run_id']

        # Calculate video recording end time
        media_time = parser.parse(video_metadata['session']['media_date'])
        media_end_delta = datetime.timedelta(microseconds=video_metadata['frame'][-1]['time'])
        media_end = media_time + media_end_delta

        # Create new run if it doesn't exist
        if run_id not in runs.keys():
            start_time = parser.parse(video_metadata['session']['run_date'])

            runs[run_id] = {
                'run_id': run_id,
                'start': start_time,
                'end': media_end,
                'media': [video],
                'drone_id': video_metadata['session']['friendly_name']
            }
        
        else:
            # Add video to media list
            runs[run_id]['media'].append(video)

        # Update ending time if video ends later
        if (media_end > runs[run_id]['end']):
            runs[run_id]['end'] = media_end
    
    # Sort the runs by time
    sorted_runs = sorted(runs.values(), key=lambda d: d['start'])

    unsorted_images = []

    # Add images to runs
    for image in images:
        # Get path to metadata file
        image_metadata_file = metadata_dir.joinpath(image.name).with_suffix(image.suffix + '.json')

        # If metadata doesn't exist, extract it
        if (not image_metadata_file.exists()):
            extract_metadata(image, metadata_path=metadata_dir, debug=debug)

        # Load metadata from file
        with open(image_metadata_file, 'r') as f:
            image_metadata = json.load(f)

        # Extract the time image was taken
        raw_datetime_parts = image_metadata['DateTime'].split(" ")
        raw_datetime_parts[0] = raw_datetime_parts[0].replace(":", "-")


        image_time = parser.parse(raw_datetime_parts[0] + 'T' + raw_datetime_parts[1] + image_metadata['OffsetTime'])

        # Add image to run
        image_sorted = False
        for run in sorted_runs:
            if (image_time >= run['start'] and image_time <= run['end']):
                run['media'].append(image)
                image_sorted = True
                break

        if not image_sorted:
            unsorted_images.append(image)
            
            if debug:
                print('\u001b[31mCould not automatically sort image: {} at time: {}\u001b[0m'.format(image.name, image_time))

    # Organize runs by date
    dateruns = {}

    # Organize imported runs into dict by start date
    for run in sorted_runs:
        datestring = run['start'].strftime('%m-%d-%y')

        if not datestring in dateruns.keys():
            dateruns[datestring] = []

        dateruns[datestring].append(run)

    return (dateruns, unsorted_images, unparsed_media)
    