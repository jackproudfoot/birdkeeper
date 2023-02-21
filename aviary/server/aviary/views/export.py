# from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from ..models import Flight, FlightMedia, Media

import json

def flight(request, id):
    
    # get Flight
    flight = None

    try:
        flight = Flight.objects.get(pk=id)
    except ObjectDoesNotExist:
        return HttpResponse(f'error flight {id} does not exist')
    except:
       return HttpResponse(f'error when exporting flight: {e}')

    geojson = flight.feature_collection()

    return HttpResponse(json.dumps(geojson))