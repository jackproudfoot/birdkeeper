# from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie

import json

from django.contrib.auth.models import User
from ..models import Flight

def index(request):
    return HttpResponse("hello world")

@ensure_csrf_cookie
def csrf(request):
    return HttpResponse('csrf cookie set')

def flight(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))

        pilot = None

        try:
            pilot = User.objects.get(username=body['pilot'])
        except Exception as e:
            return HttpResponse(f'error when retrieving pilot {e}')
        
        flight = Flight(drone=body['drone'], start=body['start'], end=body['end'], pilot=pilot).save()

        return HttpResponse(flight)
    
    return HttpResponse(f"error method {request.method} not supported")
