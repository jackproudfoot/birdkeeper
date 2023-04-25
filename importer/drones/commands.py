import click
import json
from tabulate import tabulate
import requests
from urllib.parse import urljoin
import os


@click.group()
def drones():
    pass

@drones.command()
def list():
    """List drones in the database"""

    res = requests.get(f"{os.environ.get('API_URL')}/drones")

    

    drones = json.loads(res.text)

    drones_formatted = []


    for drone in drones:
        drones_formatted.append([drone['name'], drone['drone_id']])

    output = tabulate(drones_formatted, headers=['Name', 'ID'])

    click.echo(output)


@drones.command()
@click.option('--name', prompt=True)
@click.option('--id', prompt=True)
@click.option('--make', default='Parrot')
@click.option('--model', default='Anafi')
def create(name, id, make, model):
    """Add new drone to the database"""

    res = requests.post(f"{os.environ.get('API_URL')}/drones", json={
        'name': name,
        'drone_id': id,
        'make': make,
        'model': model
    })

    if (res.status_code != 200):
        click.echo(click.style('Error creating drone: {}'.format(res.text), fg='red'))
        exit(1)
    
    click.echo('Drone created')