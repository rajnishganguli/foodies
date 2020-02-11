from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User
from oauthlib.oauth2 import WebApplicationClient
from flask_login import (LoginManager, current_user, login_required, login_user,logout_user,)
import os
import json
import requests

# Flask app setup
app = Flask(__name__)


# Configuration:
# GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
# GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
from credentials import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DISCOVERY_URL


# Initializing the database engine.
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine


# User session management setup: https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)


# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content. <a href='/login'>Google Login</a>", 403


@login_manager.user_loader
def load_user(user_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    session.close()
    return user

# Show all restaurants
@app.route('/')
@app.route('/restaurants/')
def show_restaurants():
    if current_user.is_authenticated:
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        restaurants = session.query(Restaurant).all()
        return render_template('restaurants.html', restaurants=restaurants)
    else:
        return '<a class="button" href="/login">Google Login</a>'


# Login route
@app.route("/login")
def login():
    # Find out what URL(authorization URL) to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(authorization_endpoint,
                                             redirect_uri=request.base_url + "/callback",
                                             scope=["openid", "email", "profile"],
                                             )
    return redirect(request_uri)


# Route at which google responds with authorization code
@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Finally!
    token_url, headers, body = client.prepare_token_request(token_endpoint,
                                                            authorization_response=request.url,
                                                            redirect_url=request.base_url,
                                                            code=code,
                                                            )
    token_response = requests.post(token_url,
                                   headers=headers,
                                   data=body,
                                   auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
                                   )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens,
    # let's find and hit URL from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    # But first we need to add the TOKEN to the userinfo_endpoint
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our app,
    # and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided by Google
    user = User(id=unique_id, name=users_name, email=users_email, profile_pic=picture)

    # Doesn't exist? Add to database
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    db_user = session.query(User).filter_by(id=unique_id).first()
    if not db_user:
        session.add(user)
        session.commit()

    # Begin user session by logging the user in
    login_user(user)
    session.close()

    # Send user back to homepage
    return redirect(url_for("show_restaurants"))


# Route to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("show_restaurants"))


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


# Send JSON for all the restaurants
@app.route('/restaurants/JSON')
@login_required
def show_restaurants_json():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants = [restaurant.serialize for restaurant in restaurants])


# Make a new Restaurant
@app.route('/restaurant/new', methods=['GET', 'POST'])
@login_required
def new_restaurant():
    if request.method == 'POST':
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        new_restaurant = Restaurant(name=request.form['name'])
        session.add(new_restaurant)
        session.commit()
        flash("New Restaurant created!")
        return redirect(url_for('show_restaurants'))
    else:
        return render_template('newRestaurant.html')


# Edit an existing restaurant
@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_restaurant(restaurant_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    restaurant_to_be_edited = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            restaurant_to_be_edited.name = request.form['name']
            session.add(restaurant_to_be_edited)
            session.commit()
            flash("Restaurant successfully edited.")
        return redirect(url_for('show_restaurants'))
    else:
        return render_template('editRestaurant.html', restaurant=restaurant_to_be_edited)


# Delete an existing restaurant
@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_restaurant(restaurant_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    restaurant_to_be_deleted = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurant_to_be_deleted)
        session.commit()
        flash("Restaurant successfully deleted")
        return redirect(url_for('show_restaurants'))
    else:
        return render_template('deleteRestaurant.html', restaurant=restaurant_to_be_deleted)


# Show menu items for a restaurant
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu')
@login_required
def show_menu(restaurant_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return render_template('menu.html', restaurant=restaurant, items=items)


# Send JSON for all the menu-items of a restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
@login_required
def show_menu_json(restaurant_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems = [item.serialize for item in items])


# Send JSON for all the menu-items of a restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
@login_required
def show_menu_item_json(restaurant_id, menu_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem = item.serialize)


# Create new menu item
@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
@login_required
def new_menu_item(restaurant_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if request.method == 'POST':
        new_item = MenuItem(name = request.form['name'],
                            description = request.form['description'],
                            price = request.form['price'],
                            course = request.form['course'],
                            restaurant_id = restaurant_id)
        session.add(new_item)
        session.commit()
        flash("New Menu Item Created!")
        return redirect(url_for('show_menu', restaurant_id=restaurant_id))
    else:
        return render_template('newMenuItem.html', restaurant_id=restaurant_id)


# Edit an existing menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_menu_item(restaurant_id, menu_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    item_to_be_edited = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            item_to_be_edited.name = request.form['name']
        if request.form['description']:
            item_to_be_edited.description = request.form['description']
        if request.form['price']:
            item_to_be_edited.price = request.form['price']
        if request.form['course']:
            item_to_be_edited.course = request.form['course']
        session.add(item_to_be_edited)
        session.commit()
        flash("Menu item successfully updated.")
        return redirect(url_for('show_menu', restaurant_id=restaurant_id))
    else:
        return render_template('editMenuItem.html', item=item_to_be_edited)


# Delete an existing menu_item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_menu_item(restaurant_id, menu_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    item_to_be_deleted = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(item_to_be_deleted)
        session.commit()
        flash("Menu item successfully deleted.")
        return redirect(url_for('show_menu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item=item_to_be_deleted)


if __name__ == '__main__':
    app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
    app.debug = True
    app.run(ssl_context="adhoc")


