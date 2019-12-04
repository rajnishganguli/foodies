from flask import Flask, render_template

app = Flask(__name__)


# Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'},
               {'name': 'Blue Burgers', 'id': '2'},
               {'name': 'Taco Hut', 'id': '3'}]

# Fake Menu Items
item = {'name': 'Cheese Pizza', 'description': 'made with fresh cheese', 'price': '$5.99', 'course': 'Entree'}

items = [
    {'name': 'Cheese Pizza', 'description': 'made with cheese', 'price': '$5.99', 'course': 'Entree', 'id': '1'},
    {'name': 'Chocolate Cake', 'description': 'made with Chocolate', 'price': '$3.99', 'course': 'Dessert', 'id': '2'},
    {'name': 'Caesar Salad', 'description': 'with fresh vegetables', 'price': '$5.99', 'course': 'Entree', 'id': '3'},
    {'name': 'Iced Tea', 'description': 'with lemon', 'price': '$.99', 'course': 'Beverage', 'id': '4'},
    {'name': 'Spinach Dip', 'description': 'with spinach', 'price': '$1.99', 'course': 'Appetizer', 'id': '5'}]


@app.route('/')
@app.route('/restaurants')
def show_restaurants():
    # return "This page will show all restaurants"
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/restaurant/new')
def new_restaurant():
    # return "This page will be used to make new restaurants"
    return render_template('newRestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
    # return "This page will be used to edit a restaurant"
    return render_template('editRestaurant.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete')
def delete_restaurant(restaurant_id):
    # return "This page will be used to delete an existing restaurant"
    return render_template('deleteRestaurant.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu')
def show_menu(restaurant_id):
    # return "This page will be used to show menu of the given restaurant"
    return render_template('menu.html', restaurant=restaurant, items=items)


@app.route('/restaurant/<int:restaurant_id>/menu/new')
def new_menu_item(restaurant_id):
    # return "This page will be used to add a new menu item"
    return render_template('newMenuItem.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit')
def edit_menu_item(restaurant_id, menu_id):
    # return "This page will be used to update a menu item of the given restaurant"
    return render_template('editMenuItem.html', item=item)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete')
def delete_menu_item(restaurant_id, menu_id):
    # return "This page will be used to delete a menu item of the given restaurant"
    return render_template('deleteMenuItem.html', item=item)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)


