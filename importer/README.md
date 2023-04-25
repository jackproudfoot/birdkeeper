# Duke Rainforest Xprize Drone Media Uploader 🦜


## Overview

This tool was born from a desire to have a standarized import process for media coming off of the drones during the xprize competitions. Doing the import and organization by hand took a significant amount of time which is one reason why we decided to build this tool. However, by controlling the media import process we also give ourselves the ability to automatically scrape the metadata from the media files and load that metadata in to a database for later processing. This opens up future oppurtunities for visualization and data processing that was simply not feasible from metadata scraped by hand.

## [Demo Video](https://drive.google.com/file/d/10Q2fOv8EPBd9so0ARPAX5ecKGAuOyCSu/view?usp=share_link)

[Drone Database Project: Overview, Current Status, and Next Steps](https://docs.google.com/document/d/1oMmx3iVq1pmT66SXy0jKGBCzmflcUfHFflUvewBOh3o/view)

## Components


### Drone Database API
First and foremost, the uploader script is dependent on the api designed to collect metadata from the drone media files and store it into a SQL database for later processing: [Aviary](../aviary/). Though the import standarization is nice, the automatic upload of the metadata is the real important piece of this work.

### Metadata extraction

We focused on the Parrot Anafi drones that are currently being used by the xprize team. These drones can collect two types of media during a flight: jpg images and mp4 videos. Into both types of media the Parrot embeds important metadata than we can extract. 

#### JPG Metadata
The metadata embedded in the jpg image files is the [standard EXIF](https://exifdata.com/) data format which is easy to extract. We're using [a python library](https://pillow.readthedocs.io/en/stable/reference/ExifTags.html) to extract this metadata for every imported image file.

Example jpg metadata
```json
{
  "GPSInfo": {
    "GPSVersionID": "\u0002\u0003\u0000\u0000",
    "GPSLatitudeRef": "N",
    "GPSLatitude": [
      10.0,
      25.0,
      49.5877554
    ],
    "GPSLongitudeRef": "W",
    "GPSLongitude": [
      84.0,
      0.0,
      23.7659492
    ],
    "GPSAltitudeRef": "\u0000",
    "GPSAltitude": 55.21138381958008,
    "GPSSatellites": "13"
  },
  "ResolutionUnit": 2,
  "ExifOffset": 243,
  "ImageDescription": "AnafiUSA 1.8.3",
  "Make": "Parrot",
  "Model": "AnafiUSA",
  "Software": "anafi-mark3-1.8.3",
  "Orientation": 1,
  "DateTime": "2022:06:12 10:55:36",
  "YCbCrPositioning": 1,
  "XResolution": 72.0,
  "YResolution": 72.0,
  "ExifVersion": "0231",
  "ComponentsConfiguration": "\u0001\u0002\u0003\u0000",
  "ShutterSpeedValue": 7.9071214452835274,
  "DateTimeOriginal": "2022:06:12 10:55:36",
  "DateTimeDigitized": "2022:06:12 10:55:36",
  "ApertureValue": 2.526068811667588,
  "ExposureBiasValue": 0.0,
  "MeteringMode": 2,
  "FlashPixVersion": "0100",
  "Flash": 0,
  "FocalLength": 4.0,
  "ColorSpace": 1,
  "ExifImageWidth": 2304,
  "LightSource": 0,
  "FocalPlaneXResolution": 16125.815687042843,
  "FocalPlaneYResolution": 16125.815687042843,
  "OffsetTime": "-04:00",
  "OffsetTimeOriginal": "-04:00",
  "OffsetTimeDigitized": "-04:00",
  "SubsecTime": "348",
  "SubsecTimeOriginal": "348",
  "SubsecTimeDigitized": "348",
  "ExifImageHeight": 1728,
  "FocalPlaneResolutionUnit": 3,
  "FileSource": "\u0003",
  "ExposureTime": 0.004166,
  "FNumber": 2.4,
  "SceneType": "\u0001",
  "ExposureProgram": 2,
  "ISOSpeedRatings": 118,
  "ExposureMode": 0,
  "SensitivityType": 3,
  "WhiteBalance": 0,
  "ISOSpeed": 118,
  "FocalLengthIn35mmFilm": 101,
  "SceneCaptureType": 0,
  "Contrast": 1,
  "Saturation": 1,
  "Sharpness": 1
}
```

#### MP4 Metadata
The metadata embedded in the mp4 video files is a proprietary format that we use the [Parrot pdraw tool](https://developer.parrot.com/docs/pdraw/video-metadata.html) to extract. Unfortunatly this tool is not the easiest to run and there is no great interface with Python. Previously we had installed the pdraw tool on an Ubuntu machine, however at the beginning of this semester we worked on containerizing the tool. By using Docker we can now easily setup and run the pdraw tool on almost any machine.

Example mp4 metadata
```json
{
  "session":{
    "friendly_name":"AnafiUSA-J000208",
    "maker":"Parrot",
    "model":"AnafiUSA",
    "model_id":"091e",
    "serial_number":"PI040505AA0J000208",
    "software_version":"1.8.2",
    "build_id":"anafi-mark3-1.8.2",
    "title":"Fri, 03 Jun 2022 12:27:04 -0400",
    "media_date":"2022-06-03T12:27:04-04:00",
    "run_date":"2022-06-03T12:27:03-04:00",
    "run_id":"068B5CD0EF78567104D7BB27CCF982DC",
    "boot_id":"B245666F7C98262FFF3B69D075F9BBD1",
    "video_mode":"standard"
  },
  "frame":[
    {
      "time":0,
      "metadata":{
        "drone_quat":{
          "w":0.96575927734375,
          "x":0.02191162109375,
          "y":0.011474609375,
          "z":-0.25811767578125
        },
        "ground_distance":0.514923095703125,
        "speed":{
          "north":0.0,
          "east":0.0,
          "down":0.0
        },
        "air_speed":-1.0,
        "frame_base_quat":{
          "w":0.96612548828125,
          "x":0.0,
          "y":0.0,
          "z":-0.2579345703125
        },
        "frame_quat":{
          "w":0.96612548828125,
          "x":0.0,
          "y":0.0,
          "z":-0.2579345703125
        },
        "exposure_time":1.03125,
        "gain":100,
        "awb_r_gain":2.312255859375,
        "awb_b_gain":1.268310546875,
        "picture_hfov":69.0,
        "picture_vfov":42.26953125,
        "link_goodput":12719,
        "link_quality":5,
        "wifi_rssi":-19,
        "battery_percentage":72,
        "animation":0,
        "state":"LANDED",
        "mode":"MANUAL",
        "frame_timestamp":40518804,
        "automation":{
          "followme_enabled":0,
          "lookatme_enabled":0,
          "angle_locked":0,
          "animation":"NONE"
        }
      }
    },
    ...,
    {
      "time":700700,
      "metadata":{
        "drone_quat":{
          "w":0.96575927734375,
          "x":0.0218505859375,
          "y":0.01153564453125,
          "z":-0.258056640625
        },
        "ground_distance":0.514923095703125,
        "speed":{
          "north":0.0,
          "east":0.0,
          "down":0.0
        },
        "air_speed":-1.0,
        "frame_base_quat":{
          "w":0.9661865234375,
          "x":0.0,
          "y":0.0,
          "z":-0.25775146484375
        },
        "frame_quat":{
          "w":0.9661865234375,
          "x":0.0,
          "y":0.0,
          "z":-0.25775146484375
        },
        "exposure_time":1.03125,
        "gain":100,
        "awb_r_gain":2.3134765625,
        "awb_b_gain":1.267578125,
        "picture_hfov":69.0,
        "picture_vfov":42.26953125,
        "link_goodput":12740,
        "link_quality":5,
        "wifi_rssi":-18,
        "battery_percentage":72,
        "animation":0,
        "state":"LANDED",
        "mode":"MANUAL",
        "frame_timestamp":41219423,
        "automation":{
          "followme_enabled":0,
          "lookatme_enabled":0,
          "angle_locked":0,
          "animation":"NONE"
        }
      }
    }
  ]
}
```


## Installation

There are two main dependencies for the uploader tool: [Docker](https://www.docker.com/) and [Python](https://www.python.org/). As these tools are so prevalent, we leave it as an excersise for the reader to track down the installation instructions if necessary (a simple google search should suffice).

### Building the pdraw Docker Image

In order to extract metadata from mp4 media files you will need to have built the [pdraw docker image](./metadata/Dockerfile) and have the image locally on your machine. Assuming you have properly installed docker, this should be as easy as navigating to the metadata directory and running the make command.
```bash
$ cd metadata
$ make

# Confirm that docker image flightparser:latest exists
$ docker image ls
```

### Setting up python environment

In order to isolate the python environment from other tools installed on your system its best to create a [python venv](https://docs.python.org/3/library/venv.html) just for this tool. Navigate to the root of the project and run the following command to setup and active the venv.

```bash
# create new venv named venv
$ python -m venv venv

# activate the venv in your current terminal
$ source venv/bin/activate
```

Note, you will need to run the source command in each terminal you open before running the script in order to activate the proper python environment.

Next you can install the required python dependencies saved in the ```requirements.txt``` file.

```bash
$ pip install -r requirements.txt
```

### Configuring API environment

The last setup step is to configure your environent so the uploader script knows how to communicate with the api. Copy the ```sample.env``` file into a file named ```.env```. By default the uploader script assumes you are uploading against a local api, however you can also change the api endpoint to an api hosted on AWS.

## Command Reference

Now that you've gotten your environment configured you are ready to import media files.

Currently the tool is divided into two command groups: drones and importer. At any time you can run a command with the ``--help`` flag to get more information about the command.

```bash
$ python cli.py --help
```

### Drones

The drones group has commands responsible for listing registered drones in the database and adding new drones to the database.

#### ```list```

This command allows you to view all of the existing drones in the database along with their friendly id name. 

```bash
$ python cli.py drones list

Name     ID
-------  ----------------
Raymond  AnafiUSA-J000208

```

#### ```create```

This command allows you to register a new drone in the database. Every drone has four values: name, id, make (defaults to Parrot), model (defaults to Anafi).

```bash
$ python cli.py drones create --name Ollie --id AnafiUSA-J000211
Drone created with uid: 1088a648-a998-45b5-9107-58264ce0e794

```

If you do not specify either of the two required parameters the command will prompt you for their values

```bash
$ python cli.py drones create
Name: Ollie
Id: AnafiUSA-J000211
Drone created with uid: 1088a648-a998-45b5-9107-58264ce0e794

```

### Importer

The importer group has two commands related to importing media from the sd card of a drone to the harddrive.

#### ```plan```

This command allows you to visualize the changes that an import will make without actually performing the import. Can be used to verify that you passed the proper arguments for the import process.

```bash
$ python cli.py importer plan /Volumes/Extreme\ Pro/Drone\ Database\ Dev/sd1 /Volumes/Extreme\ Pro/Database\ Demo
Drone: Raymond
Pilot: Jack
🦜 Squawk. Generating import plan. Squawk.
Extracting metadata from video (P0470340.MP4) in (/Volumes/Extreme Pro/Drone Database Dev/sd1)
W libmp4: empty file: '/home/pdraw/raw/P0470340.MP4'
failed to read MP4 file '/home/pdraw/raw/P0470340.MP4'
Flight changes:
        + Create Flight 2
        + Create Flight 1
        + Create Flight 1
        + Create Flight 1

Media to be imported:
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-03-22/Flight 2/P0430336.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-03-22/Flight 2/P0440337.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-03-22/Flight 2/P0450338.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-03-22/Flight 2/P0460339.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-03-22/Flight 1/P0420335.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-07-22/Flight 1/P0480341.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-07-22/Flight 1/P0490342.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0500343.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0590352.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0600353.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0600354.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0510344.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0520345.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0530346.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0540347.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0550348.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0560349.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0570350.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0580351.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/unparsed/P0470340.MP4
🦜 Squawk. Plan is complete. Squawk.

```

#### ```import```

This command allows you to extract the metadata from the media files, import them to the harddrive, and upload metadata to the api. 

```bash
$ python cli.py importer import /Volumes/Extreme\ Pro/Drone\ Database\ Dev/sd1 /Volumes/Extreme\ Pro/Database\ Demo
Drone: Raymond
Pilot: Jack
🦜 Squawk. Importing media. Squawk.
Extracting metadata from video (P0470340.MP4) in (/Volumes/Extreme Pro/Drone Database Dev/sd1)
W libmp4: empty file: '/home/pdraw/raw/P0470340.MP4'
failed to read MP4 file '/home/pdraw/raw/P0470340.MP4'
Flight changes:
        + Create Flight 2
        + Create Flight 1
        + Create Flight 1
        + Create Flight 1

Media to be imported:
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-03-22/Flight 2/P0430336.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-03-22/Flight 2/P0440337.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-03-22/Flight 2/P0450338.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-03-22/Flight 2/P0460339.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-03-22/Flight 1/P0420335.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-07-22/Flight 1/P0480341.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-07-22/Flight 1/P0490342.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0500343.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0590352.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0600353.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0600354.MP4
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0510344.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0520345.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0530346.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0540347.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0550348.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0560349.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0570350.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/06-12-22/Flight 1/P0580351.JPG
        + /Volumes/Extreme Pro/Database Demo/Drones/Raymond/unparsed/P0470340.MP4
🦜 Squawk. Import complete. Squawk.

```