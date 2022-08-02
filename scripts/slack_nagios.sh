#!/bin/bash

# This script is used by Nagios to post alerts into a Slack channel
# using the Incoming WebHooks integration. Create the channel, botname
# and integration first and then add this notification script in your
# Nagios configuration.
#
# All variables that start with NAGIOS_ are provided by Nagios as 
# environment variables when an notification is generated.
# A list of the env variables is available here: 
#   http://nagios.sourceforge.net/docs/3_0/macrolist.html
#
# More info on Slack
# Website: https://slack.com/
# Twitter: @slackhq, @slackapi
#
# My info
# Website: http://matthewcmcmillan.blogspot.com/
# Twitter: @matthewmcmillan

#Modify these variables for your environment
MY_NAGIOS_HOSTNAME="naemon.SECRET.com"
SLACK_HOSTNAME="SECRET.slack.com"
SLACK_CHANNEL="#nagioscore"
SLACK_BOTNAME="nagios"


#Set the message icon based on Nagios service state
if [ "$3" = "CRITICAL" ]
then
    COLOR="#f70c00"
elif [ "$3" = "WARNING" ]
then
    COLOR="#ffaa01"
elif [ "$3" = "OK" ]
then
    COLOR="#00ce29"
elif [ "$3" = "UNKNOWN" ]
then
    COLOR="#ffaa01"
else
    COLOR="#c202c9"
fi

#Send message to Slack
curl -X POST --data "payload={\"channel\": \"${SLACK_CHANNEL}\", \"username\": \"${SLACK_USERNAME}\", \"attachments\": [{ \"color\": \"${COLOR}\", \"pretext\": \"Host: $1\", \"text\": \"Service: $2\nMessage: $4 \n<https://${MY_NAGIOS_HOSTNAME}/thruk/#cgi-bin/status.cgi?host=$1| See Naemon>\" }]}"  https://hooks.slack.com/services/SECRET/SECRET/SECRET 
