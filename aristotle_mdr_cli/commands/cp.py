import click
import json
import requests
import os
from aristotle_mdr_cli.utils import AristotleCommand, TokenAuth

"""
Copy metadata from one registry to another
"""

class Copy(AristotleCommand):
    def __init__(self, origin, destination, uuid, explode=False):
        origin = self.ac_url(origin)
        destination = self.ac_url(destination)
        self.uuid = uuid
        self.explode = explode

        self.origin = {
            'url': origin.rstrip('/') + f"/api/v3",
            'auth': self.get_auth(origin),
        }

        self.destination = {
            'url': destination.rstrip('/') + f"/api/v3",
            'auth': self.get_auth(destination),
        }

    def copy(self):
        # self.send_manifest()
        url = self.origin['url']+'/metadata/' + self.uuid + "/"
        # origin_token = 
        params = {"explode": self.explode}
        response = requests.get(
            url,
            auth=TokenAuth(self.origin['auth']),
            headers={
                "accept": "application/json",
            }
        )
        print(response)
        print(response.json())
        data = response.json()
        data['fields'].pop('superseded_by', None)
        params = {}
        if self.explode:
            params.update({"explode": True})
        response = requests.post(
            self.destination['url']+'/metadata/', # + self.uuid + "/"
            auth=TokenAuth(self.destination['auth']),
            params=params,
            json=data
        )
        print(response.request.headers)
        print(response)
        print(response.text)

    @classmethod
    def run(cls, *args, **kwargs):
        cls(*args, **kwargs).copy()

    def send_manifest(self):
        print("Creating manifest")

        organisations = requests.get(
            self.origin['url']+'/organizations/',
            # auth=(self.origin['username'], self.origin['password']),
        )
        organisations = organisations.json()

        registration_authorities = requests.get(
            self.origin['url']+'/ras/',
            # auth=(self.origin['username'], self.origin['password']),
        ).json()

        manifest = {
            "organizations": [
                {
                    "uuid": org['uuid'],
                    "name": org['name'],
                    "definition": org['definition'],
                    "namespaces": []
                }
                for org in organisations
            ],
            "registration_authorities": [
                {
                    "uuid": ra['uuid'],
                    "name": ra['name'],
                    "definition": ra['definition'],
                    "namespaces": []
                }
                for ra in registration_authorities
            ],
            "metadata": []
        }
        print("Sending manifest")
        # print(manifest)
        r= requests.post(
            self.destination['url']+'/metadata/',
            auth=(self.destination['username'], self.destination['password']),
            json=manifest
        )
        print(r)
        print(r.text)
        return r


    def send_metadata_item_to_destination(self, metadata):
        # legacy fix
        if 'ids' in metadata.keys():
            identifiers = []
            for i in metadata['ids']:
                i['identifier'] = i.pop('id')
            metadata['identifiers'] = identifiers
        return requests.post(
            self.destination['url']+'/metadata/',
            auth=(self.destination['username'], self.destination['password']),
            json=metadata
        ) #, headers=headers)

    def get_metadata_items_from_origin(self, object_type): #args, endpoint, user, password):
        page = 1
        while True:
            print("Getting page", page)
            result = requests.get(
                self.origin['url']+'/metadata/',
                # auth=(self.origin['username'], self.origin['password']),
                params={"page":page, "type":"%s:%s"%object_type}
            )
            if result.status_code == 200:
                data = result.json()
                print("about to send {n} objects".format(n=len(data['results'])))
                for obj in data['results']:
                    yield obj
                page += 1
                if not data['next']:
                    break
            else:
                # TODO - maybe a warning?
                click.echo("Unable to fetch %s:%s"%object_type)
                break

@click.command()
# @click.option('--origin', '-O', help='Origin registry')
# @click.option('--destination', '-D', help='Destination registry')
@click.argument('origin') #, '-O', help='Origin registry')
@click.argument('destination') #, '-D', help='Destination registry')
@click.argument('uuid') #, default=None, help='UUID of item to fetch')
@click.option('--api_version', default=3, help='API version')
# @click.option('--uuid', default=None, help='UUID of item to fetch')
@click.option('--explode', '-X', is_flag=True, help='UUID of item to fetch')
# @click.option('--uuid_file', default=None, help='File with a list of UUIDs to fetch.')
def command(origin, destination, api_version, uuid, explode):
    """
    Copy metadata from one registry to another.
    V3 API only
    """
    cp = Copy.run(origin, destination, uuid, explode=explode)
    # cp.copy()


if __name__ == "__main__":
    command()
