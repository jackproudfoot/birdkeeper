# from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

import json

from django.contrib.auth.models import User
from ..models import Flight, Drone, Media, FlightMedia

def index(request):
    return HttpResponse("hello world")

@ensure_csrf_cookie
def csrf(request):
    return HttpResponse('csrf cookie set')

@csrf_exempt
def flight(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))

        pilot = None

        try:
            pilot = User.objects.get(username=body['pilot_name'])
        except Exception as e:
            return HttpResponseBadRequest(f'error when retrieving pilot: {e}')
        

        drone = None


        try:
            drone = Drone.objects.get(drone_id=body['drone_id'])
        except Exception as e:
            try:
                drone = Drone(name=body['drone_name'], drone_id=body['drone_id'], make='Parrot', model='Anafi')

                drone.save()
            except Exception as e:
                return HttpResponseBadRequest(f'error when creating new drone {body["drone_id"]}: {e}')
                
        flight = Flight(drone=drone, run_id=body['run_id'], start=body['start'], end=body['end'], pilot=pilot)

        flight.save()

        return HttpResponse(json.dumps({'flight_uid': flight.id}))
    
    return HttpResponse(f"error method {request.method} not supported")


@csrf_exempt
def flight_media(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))

        
        flight = None

        try:
            flight = Flight.objects.get(id=body['flight_uid'])
        except Exception as e:
            return HttpResponseBadRequest(f'error when retrieving flight {e}')


        media_data = body['media_data']

        media = Media(file=media_data['file'], type=media_data['type'], geometry=media_data['geometry'], recorded=media_data['datetime_recorded'])
                
        media.save()

        FlightMedia(flight=flight, media=media).save()

        return HttpResponse(media)
    
    return HttpResponse(f"error method {request.method} not supported")


@csrf_exempt
def drones(request):
    if request.method == 'GET':
        try:
            drones = Drone.objects.all()
        except Exception as e:
            return HttpResponseBadRequest(f'error when retrieving drones {e}')
        

        dicts = [{'name': drone.name, 'drone_id': drone.drone_id} for drone in drones]


        return HttpResponse(json.dumps(dicts))

    elif request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))

        
        drone = Drone(name=body['name'], drone_id=body['drone_id'], make=body['make'], model=body['model'])

        drone.save()

        return HttpResponse(drone)
    
    return HttpResponse(f"error method {request.method} not supported")
