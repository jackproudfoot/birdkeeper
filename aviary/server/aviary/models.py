from django.db import models
from django.contrib.auth.models import User

class Flight(models.Model):
    drone = models.CharField(max_length=60)
    start = models.DateTimeField()
    end   = models.DateTimeField()
    pilot = models.ForeignKey(User, on_delete=models.DO_NOTHING)

class Media(models.Model):
    file     = models.URLField()
    type     = models.CharField(max_length=20)
    geo_data = models.JSONField()

class FlightMedia(models.Model):
    flight_id = models.ForeignKey(Flight, on_delete=models.CASCADE)
    media_id  = models.ForeignKey(Media, on_delete=models.CASCADE)

class Observation(models.Model):
    description = models.TextField()
    type        = models.CharField(max_length=80)

class ObservationMedia(models.Model):
    observation_id = models.ForeignKey(Observation, on_delete=models.CASCADE)
    media_id       = models.ForeignKey(Media, on_delete=models.CASCADE)

class Identification(models.Model):
    source  = models.TextField()
    species = models.TextField()

class IdentificationObservation(models.Model):
    observation_id    = models.ForeignKey(Observation, on_delete=models.CASCADE)
    identification_id = models.ForeignKey(Identification, on_delete=models.CASCADE)