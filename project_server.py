from flask import Flask

app = Flask(__name__)


@app.route('/')
@app.route('/restaurants')
def show_restaurants():
    return "This page will show all restaurants"


@app.route('/restaurant/new')
def new_restaurant():
    return "This page will be used to make new restaurants"


@app.route('/restaurant/<int:restaurant_id>/edit')
def edit_restaurant(restaurant_id):
    return "This page will be used to edit a restaurant"


@app.route('/restaurant/<int:restaurant_id>/delete')
def delete_restaurant(restaurant_id):
    return "This page will be used to delete an existing restaurant"


@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu')
def show_menu(restaurant_id):
    return "This page will be used to show menu of the given restaurant"


@app.route('/restaurant/<int:restaurant_id>/menu/new')
def new_menu_item(restaurant_id):
    return "This page will be used to add a new menu item"


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit')
def edit_menu_item(restaurant_id, menu_id):
    return "This page will be used to update a menu item of the given restaurant"


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete')
def delete_menu_item(restaurant_id, menu_id):
    return "This page will be used to delete a menu item of the given restaurant"


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)


