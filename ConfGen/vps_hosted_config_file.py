# -*-coding:utf-8

import os
import socket
import ovh

# API access
client = ovh.Client(
    endpoint='ovh-eu',
    application_key='SECRET',
    application_secret='SECRET',
    consumer_key='SECRET',
)


def writehost(h):
    with open("/etc/naemon/objects/hosted_nrpe.cfg", "a") as conffile:
        # Convert a hostname to an IP address
        ip = socket.gethostbyname(h)

        # Write to file, spaces are for aesthetic purposes only
        conffile.write("define host {\n use        template-hosts,host-pnp\n host_name  " + h + "\n address    "
                       + ip + "\n hostgroups NRPE\n}\n")


def distrib(serv):
    for server in serv:
        if server not in vpsSib:
            try:
                client.get('/vps/%s/distribution' % server)['name']

            # Except OVH fatal error when VPS is expired
            except ovh.exceptions.ResourceExpiredError:
                vpsSib.append(server)
                print(server + " expired.")


# Delete our servers and faulty servers from the loop
vpsSib = ["SECRET.ovh.net",
          "SECRET.ovh.net",
          "SECRET.ovh.net",
          "SECRET.ovh.net",
          "SECRET.vps.ovh.ca",
          "SECRET.vps.ovh.ca",
          "SECRET.vps.ovh.ca",
          "SECRET.vps.ovh.ca",
          "SECRET.ovh.net",
          "SECRET.ovh.net",
          "SECRET.ovh.net",
          "SECRET.ovh.net"]

# Request for vps info
request = client.get('/vps/')

# Put Expired VPS in vpsSib
distrib(request)

# Vps sorted to delete ours
servers = [vps for vps in request if vps not in vpsSib]

# Map servers name (vps11111.ovh.net) with its OS
vpsnames = [vps for vps in map(lambda *a: a,
                               servers,
                               [client.get('/vps/%s/distribution' % server)['name'] for server in servers])]

# Retrieve only CentOS VPS
vpsnamesCentOS = [vps[0] for vps in vpsnames
                  if vps[1] not in ['Plesk on Debian 8', 'Debian 9 (Stretch)', 'Plesk Onyx on Debian 8']]

# Remove current version of "hosted_nrpe.cfg"
if os.path.exists("/etc/naemon/objects/hosted_nrpe.cfg"):
    os.remove("/etc/naemon/objects/hosted_nrpe.cfg")

# hosted_nrpe.cfg creation
[writehost(row) for row in vpsnamesCentOS]
