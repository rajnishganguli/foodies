from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)


# # Fake Restaurants
# restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}
#
# restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'},
#                {'name': 'Blue Burgers', 'id': '2'},
#                {'name': 'Taco Hut', 'id': '3'}]
#
# # Fake Menu Items
# item = {'name': 'Cheese Pizza', 'description': 'made with fresh cheese', 'price': '$5.99', 'course': 'Entree'}
#
# items = [
#     {'name': 'Cheese Pizza', 'description': 'made with cheese', 'price': '$5.99', 'course': 'Entree', 'id': '1'},
#     {'name': 'Chocolate Cake', 'description': 'made with Choco', 'price': '$3.99', 'course': 'Dessert', 'id': '2'},
#     {'name': 'Caesar Salad', 'description': 'with fresh vegetables', 'price': '$5.99', 'course': 'Entree', 'id': '3'},
#     {'name': 'Iced Tea', 'description': 'with lemon', 'price': '$.99', 'course': 'Beverage', 'id': '4'},
#     {'name': 'Spinach Dip', 'description': 'with spinach', 'price': '$1.99', 'course': 'Appetizer', 'id': '5'}]

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine


# Show all restaurants
@app.route('/')
@app.route('/restaurants/')
def show_restaurants():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)


# Send JSON for all the restaurants
@app.route('/restaurants/JSON')
def show_restaurants_json():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants = [restaurant.serialize for restaurant in restaurants])


# Make a new Restaurant
@app.route('/restaurant/new', methods=['GET', 'POST'])
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
def show_menu(restaurant_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return render_template('menu.html', restaurant=restaurant, items=items)


# Send JSON for all the menu-items of a restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def show_menu_json(restaurant_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems = [item.serialize for item in items])


# Send JSON for all the menu-items of a restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def show_menu_item_json(restaurant_id, menu_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem = item.serialize)

# Create new menu item
@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
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
    app.secret_key = "abracadabra"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)


