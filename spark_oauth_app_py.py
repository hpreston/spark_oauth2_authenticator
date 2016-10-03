#! /usr/bin/python
"""
This is a basic application to handle the processing of OAUTH2 Authentication/Authorizations
from Cisco Spark.  The flow of the OAUTH2 process is:

1) End User accesses the application that integrates with Spark
2) The application redirects the user to Cisco Spark to login
   The application includes its return address in the "state" field of the request to authenticate
3) The User logs into Spark and Approves the access to resources
4) Spark redirects user to THIS application to complete the authorization processing
5) This application takes the Authorization Code from Spark, and uses it to request the
   Access and Refresh tokens from Cisco Spark.
   This request includes the Client ID and Secret for the registered Integration with Spark
6) Cisco Spark validates the Authorization Code and returns an Access and Refresh Token
7) This application redirects the user back to the original application address sent in the "state" field
   The redirect is sent with the access_token and refresh_token included in query string parameters.

This application can be used by multiple end user applications.  Each application would include the same Client_ID
in login requests to Spark, and include the unique URL for users to be redirected to once the authentication has
completed in the "state" field.

"""

from flask import Flask, request, redirect
import requests

app = Flask(__name__)


@app.route('/authorize')
def authorize():
    """
    This is the redirect path Cisco Spark uses following a successful
    login.  This function attempts to convert the Authorization Code
    into an access_token and refresh_token that will be returned to the
    originating application as query parameters.
    :return:
    """
    sys.stderr.write("\n")
    sys.stderr.write("Incoming Authorization\n")

    code = request.args.get("code")
    spark_access_token_data["code"] = code
    state = request.args.get("state")

    sys.stderr.write("  Return state: " + state + "\n")

    sys.stderr.write("  Requesting Access Token from Cisco Spark\n")
    r = requests.post(spark_access_token_url, data=spark_access_token_data)
    if r.status_code == 200:
        sys.stderr.write("    Success\n")
        access_info = r.json()
        sys.stderr.write("  Sending redirect back with tokens included.\n")
        redirect_url = "%s?access_token=%s&refresh_token=%s" % \
                       (state, access_info["access_token"], access_info["refresh_token"])
        return redirect(redirect_url)
    else:
        sys.stderr.write("    Error Detected\n")
        sys.stderr.write("      Status Code: " + str(r.status_code) + "\n")
        sys.stderr.write("      Body: " + r.text + "\n")
        message = "Error Detected<br>"
        message += "Status Code: " + str(r.status_code) + "<br>"
        message += "Body: " + r.text + "<br>"
        message += "<a href='%s'>Click to return to originating app.</a>" % state
        return message


if __name__ == '__main__':

    import os
    import sys

    # Retrieve the Client ID, Client Secret, and the address for the server from Environment Variables
    spark_client_id = os.getenv("CLIENT_ID")
    spark_client_secret = os.getenv("CLIENT_SECRET")
    server_address = os.getenv("SERVER_ADDRESS")

    if None in [spark_client_id, spark_client_secret, server_address]:
        sys.stderr.write("Required parameter missing.  Set CLIENT_ID, CLIENT_SECRET, and SERVER_ADDRESS ENV. \n")
        sys.exit("Required parameter missing.  Set CLIENT_ID, CLIENT_SECRET, and SERVER_ADDRESS ENV.")

    # Details needed to perform the authorization with Spark
    spark_access_token_url = "https://api.ciscospark.com/v1/access_token"
    spark_access_token_data = {
        "grant_type": "authorization_code",
        "client_id": spark_client_id,
        "client_secret": spark_client_secret,
        "code": "",
        "redirect_uri": server_address + "/authorize"

    }

    sys.stderr.write("Cisco Spark OAUTH2 Authentication Server \n")
    sys.stderr.write("Client ID: " + spark_client_id + "\n")
    sys.stderr.write("Client Secret: HIDDEN \n")
    sys.stderr.write("Local Redirect URI: " + spark_access_token_data["redirect_uri"] + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)

