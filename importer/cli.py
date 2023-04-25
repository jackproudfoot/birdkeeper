import click
from dotenv import load_dotenv

from importer import commands as import_commands
from drones import commands as drone_commands

@click.group()
def entry_point():
    pass

entry_point.add_command(import_commands.importer)
entry_point.add_command(drone_commands.drones)

if __name__ == '__main__':
    load_dotenv()
    entry_point()