#!/usr/bin/python
# -*-coding:utf-8

import os
import socket
import MySQLdb
import json
import requests
import ovh

# Use Python2.7
# Install MySQLdb "pip install mysqlclient"
# Install requests "pip install requests"
# The script will create a hosted.cfg for Naemon with all the registered domains and IPs from clients
# hosted by us, then send it to the Naemon server
# Errors will be written to naemon.log file, which will be sent to slack then deleted

# Clients with outdated Siberian don't have registered license, hence need to be monitored manually


log = open("/home/xtraball/naemon/naemon.log", "a")


def definehost(h):
    with open("/home/xtraball/naemon/hosted.cfg", "a") as output:
        ip = socket.gethostbyname(h)             # Retrieve IP with hostname
        output.write("define host {\n use        template-hosts,host-pnp\n host_name  " + h + "\n address    "
                     + ip + "\n hostgroups hosted\n}\n")


########################################################################################################################
#                                                                                                                      #
#                                             OVH Configuration                                                        #
#                                                                                                                      #
########################################################################################################################


# API access
client = ovh.Client(
        endpoint='ovh-eu',
        application_key='SECRET',
        application_secret='SECRET',
        consumer_key='SECRET',
)

# Request for vps info
servers = client.get('/vps/')


########################################################################################################################
#                                                                                                                      #
#                                        MySQL connection and data select                                              #
#                                                                                                                      #
########################################################################################################################


db = MySQLdb.connect(host="127.0.0.1",
                     user="SECRET",
                     passwd="SECRET",
                     db="SECRET")

cur = db.cursor()


cur.execute("SELECT licenses.registrated_host,siberian_payment_id "
            "FROM `support_accesses` "
            "LEFT JOIN purchases ON `support_accesses`.purchaseId = purchases.id "
            "LEFT JOIN licenses ON purchases.id = `licenses`.purchaseId "
            "WHERE ((has_support_until IS NOT NULL AND has_support_until > CURRENT_TIMESTAMP) "
            "OR (force_support_until IS NOT NULL AND `force_support_until` > CURRENT_TIMESTAMP)) "
            "AND purchases.type IN ('MAE Hosted', 'PE Hosted') "
            "ORDER BY `support_accesses`.`purchaseId` DESC;")

hostNumber = 0
b = 1


########################################################################################################################
#                                                                                                                      #
#                                                hosted.cfg Creation                                                   #
#                                                                                                                      #
########################################################################################################################

for row in cur.fetchall():
    if row[0] is None:
        log.write("License linked to purchase ID <https://SECRET.com&id=%s|%s> unregistered\n" % (row[1], row[1]))
        b += 1
        continue
    else:
        hostname = json.loads(row[0])
        for host in hostname:
            if host == '':
                continue
            elif host not in servers:
                try:
                    definehost(host)
                    hostNumber += 1
                except socket.gaierror:
                    log.write("DNS issue for %s\n" % host)
        b += 1

log.write("%s Hosts registered\n" % hostNumber)

cur.close()
db.close()

os.system("/usr/bin/rsync -av --remove-source-files -e "
          "'ssh -i /home/xtraball/.ssh/id_ecdsa_naemon' /home/xtraball/naemon/hosted.cfg "
          "root@SECRET://etc/naemon/objects/ >> /home/xtraball/naemon/naemon.log")

log.close()


########################################################################################################################
#                                                                                                                      #
#                                                    Slack log report                                                  #
#                                                                                                                      #
########################################################################################################################

webhook_url = "https://hooks.slack.com/services/SECRET/SECRET/SECRET"

with open("/home/xtraball/naemon/naemon.log", "r") as naemonLog:
    slackLog = naemonLog.read()

response = requests.post(
    webhook_url, json={"text": slackLog},
    headers={'Content-Type': 'application/json'}
)
if response.status_code != 200:
    raise ValueError(
        'Request to slack returned an error %s, the response is:\n%s'
        % (response.status_code, response.text)
    )


os.remove("/home/xtraball/naemon/naemon.log")
