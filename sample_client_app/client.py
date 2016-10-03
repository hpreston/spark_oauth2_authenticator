#! /usr/bin/python
"""
This is a sample client application that Integrates with Cisco Spark through OAUTH2.  It is provided
as a sample application showing how the OAUTH2 process works with Cisco Spark and integrates with the
AUTHENTICATOR application 'spark_oauth_app_py.py'.

The general flow outlined below can be replicated with other useful client applications.

The flow of the OAUTH2 process is:

1) End User accesses THIS application that integrates with Spark
2) THIS application redirects the user to Cisco Spark to login
   THIS application includes its return address in the "state" field of the request to authenticate
3) The User logs into Spark and Approves the access to resources
4) Spark redirects user to the AUTHENTICATOR application to complete the authorization processing
5) The AUTHENTICATOR application takes the Authorization Code from Spark, and uses it to request the
   Access and Refresh tokens from Cisco Spark.
   This request includes the Client ID and Secret for the registered Integration with Spark
6) Cisco Spark validates the Authorization Code and returns an Access and Refresh Token
7) The AUTHENTICATOR application redirects the user back to THIS application address sent in the "state" field
   The redirect is sent with the access_token and refresh_token included in query string parameters.

"""

from flask import Flask, request
import urllib2
from ciscosparkapi import CiscoSparkAPI

app = Flask(__name__)


@app.route('/')
def client():
    message = "<h1>Spark OAUTH2 Sample Client App</h1>"

    access_token = request.args.get("access_token")
    refresh_token = request.args.get("refresh_token")

    message += '<a href="%s">Login to Spark</a><br>' % spark_auth_url

    if access_token is not None:
        message += "Access_token: %s <br>" % access_token
        message += "Refresh_token: %s <br>" % refresh_token

        print "Trying to connect to spark."
        spark = CiscoSparkAPI(access_token=access_token)
        me = spark.people.me()

        message += "<h2>Your Details</h2>"
        message += "<img src='%s' width='150'><br>" % me.avatar
        message += "Name: %s <br>" % me.displayName
        message += "Email: %s <br>" % me.emails[0]
        message += "id: %s <br>" % me.id

        message += "<h2>Room List</h2>"
        for room in spark.rooms.list():
            message += "Room Name: %s <br> Room Id: %s <br><br>" % (room.title, room.id)

    return message


if __name__ == '__main__':
    import os
    import sys

    # Retrieve the Client ID, Authenticator URL, and the address for the app from Environment Variables
    spark_client_id = os.getenv("CLIENT_ID")
    authenticator_url = urllib2.quote(os.getenv("AUTHENTICATOR_URL"))
    app_address = urllib2.quote(os.getenv("APP_ADDRESS"))

    if None in [spark_client_id, authenticator_url]:
        sys.stderr.write("Required parameter missing.  Set CLIENT_ID, APP_ADDRESS, and AUTHENTICATOR_URL ENV. \n")
        sys.exit("Required parameter missing.  Set CLIENT_ID, APP_ADDRESS, and AUTHENTICATOR ENV.")

    spark_response_type = "code"
    spark_scope = "spark%3Amessages_write%20" \
                  "spark%3Ateams_read%20" \
                  "spark%3Arooms_read%20" \
                  "spark%3Amemberships_read%20" \
                  "spark%3Amessages_read%20" \
                  "spark%3Arooms_write%20" \
                  "spark%3Apeople_read%20" \
                  "spark%3Akms%20" \
                  "spark%3Ateam_memberships_write%20" \
                  "spark%3Ateam_memberships_read%20" \
                  "spark%3Ateams_write%20" \
                  "spark%3Amemberships_write"

    spark_auth_url = "https://api.ciscospark.com/v1/authorize?" \
                     "client_id=%s&" \
                     "response_type=%s&" \
                     "redirect_uri=%s&" \
                     "scope=%s&state=%s"
    spark_auth_url = spark_auth_url % (
                                         spark_client_id,
                                         spark_response_type,
                                         authenticator_url,
                                         spark_scope,
                                         app_address
                                      )
    print spark_auth_url

    app.run(debug=True, host='0.0.0.0', port=5001)
