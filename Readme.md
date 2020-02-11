Description
-----------
It is simple food app that stores restaurants and their menus. 
It supports addition of new restaurants, new menu items as well as ability to update and delete them.
It has REST API endpoints to gather restaurant data as JSON. The APIs are protected with google sign-in(OAuth 2.0).

Getting started:
----------------
0: Run following command to install all the dependencies.

pip install -r requirements.txt


1: Make a file named credentials.py and initialize the following variables.

GOOGLE_CLIENT_ID = YOUR_CLIENT_ID

GOOGLE_CLIENT_SECRET = YOUR_CLIENT_SECRET

GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

You need to login to google to get these data.
In any case don't upload these to github.


2: Then load the data using:    python lots_of_menus.py


3: Then start the server using: python project_server.py
