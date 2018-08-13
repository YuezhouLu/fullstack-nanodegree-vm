from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

# import fake restaurants and fake menu items
# from FakeMenuItems import restaurant, restaurants, item, items

# Make 3 API Endpoints (only for GET request) that return a JSON object respectively:
# for a list of all restaurants
@app.route('/restaurant/JSON')
def restaurantJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants_to_be_jsonified = [restaurant.serialize for restaurant in restaurants])

# the menu for a specific restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menuItems = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    return jsonify(menu_to_be_jsonified = [menuItem.serialize for menuItem in menuItems])

# a specific menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menuItem_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menuItem_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menuItem = session.query(MenuItem).filter_by(id = menuItem_id, restaurant_id = restaurant_id).one()
    return jsonify(menuItem_to_be_jsonified = menuItem.serialize)


@app.route('/')
@app.route('/restaurant/')
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    # return "This page will show all my restaurants"
    return render_template('restaurant.html', restaurants = restaurants)

@app.route('/restaurant/new/', methods = ['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST':
        newRestaurant = Restaurant(name = request.form['restaurant_name'])
        session.add(newRestaurant)
        session.commit()
        flash("New Restaurant Created!")
        return redirect(url_for('showRestaurants'))
    else:
        # return "This page will be for making a new restaurant"
        return render_template('newrestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
    editedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        if request.form['restaurant_name']:
            editedRestaurant.name = request.form['restaurant_name']
        session.add(editedRestaurant)
        session.commit()
        flash("Restaurant Successfully Renamed!")
        return redirect(url_for('showRestaurants'))
    else:
        # return "This page will be for editing restaurant %s" % restaurant_id
        return render_template('editrestaurant.html', restaurant = editedRestaurant)

@app.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    deletedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        session.delete(deletedRestaurant)
        session.commit()
        flash("Restaurant Successfully Deleted!")
        return redirect(url_for('showRestaurants'))
    else:
        # return "This page will be for deleting restaurant %s" % restaurant_id
        return render_template('deleterestaurant.html', restaurant = deletedRestaurant)

@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menuItems = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
    # return "This page is the menu for restaurant %s" % restaurant_id
    return render_template('menu.html', restaurant = restaurant, items = menuItems)

@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newMenuItem = MenuItem(name = request.form['menuItem_name'], description = request.form['description'], price = request.form['price'], course = request.form['course'], restaurant_id = restaurant_id)
        session.add(newMenuItem)
        session.commit()
        flash("New Menu Item Created!")
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        # return "This page is for making a new menu item for restaurant %s" % restaurant_id
        return render_template('newmenuitem.html', restaurant_id = restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menuItem_id>/edit', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menuItem_id):
    editedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    editedMenuItem = session.query(MenuItem).filter_by(id = menuItem_id, restaurant_id = editedRestaurant.id).one()
    if request.method == 'POST':
        if request.form['menuItem_name']:
            editedMenuItem.name = request.form['menuItem_name']
        if request.form['description']:
            editedMenuItem.description = request.form['description']
        if request.form['price']:
            editedMenuItem.price = request.form['price']
        if request.form['course']:
            editedMenuItem.course = request.form['course']
        session.add(editedMenuItem)
        session.commit()
        flash("Menu Item Successfully Edited!")
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        # return "This page is for editing menu item %s for restaurant %s" % (menuItem_id, restaurant_id)
        return render_template('editmenuitem.html', item = editedMenuItem)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menuItem_id>/delete', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menuItem_id):
    deletedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    deletedMenuItem = session.query(MenuItem).filter_by(id = menuItem_id, restaurant_id = restaurant_id).one()
    if request.method == 'POST':
        session.delete(deletedMenuItem)
        session.commit()
        flash("Menu Item Successfully Deleted!")
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        # return "This page is for deleting menu item {} for restaurant {}".format(menu_id, restaurant_id)
        return render_template('deletemenuitem.html', item = deletedMenuItem)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)