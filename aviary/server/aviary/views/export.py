# from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from ..models import Flight, FlightMedia, Media, ObservationMedia, Observation

import json

def flight(request, id):
    
    # get Flight
    flight = None

    try:
        flight = Flight.objects.get(pk=id)
    except ObjectDoesNotExist:
        return HttpResponse(f'error flight {id} does not exist')
    except Exception as e:
       return HttpResponse(f'error when exporting flight: {e}')

    feature = flight.feature()

    return HttpResponse(json.dumps({
            'type': 'FeatureCollection',
            'features': [feature]
    }))

def observations(request):

    flight_id = request.GET.get('flight')


    observations = None

    if (flight_id != None):
        flight_medias = FlightMedia.objects.filter(flight=flight_id).prefetch_related("media")


        observations = [observ.observation for fl_media in flight_medias for observ in ObservationMedia.objects.filter(media=fl_media.media).prefetch_related('observation')]

        observations = list(set(observations))
    else:
        observations = Observation.objects.all()


    features = [feat for observation in observations for feat in observation.features()]
        

    return HttpResponse(json.dumps({
            'type': 'FeatureCollection',
            'features': features
    }))