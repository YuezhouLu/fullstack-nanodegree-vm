#============================
# Full Stack General Imports
#============================
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import *
import datetime


#============================
# Creating a Flask Instance
#============================
app = Flask(__name__)


#============================
# Database Binding and Setup
#============================
# Connect to database (Bind database with engine)
engine = create_engine('sqlite:///mygarage.db')
Base.metadata.bind = engine

# Create session. (Bind session with engine, therefore now session and database are connected!)
DBSession = sessionmaker(bind = engine)
session = DBSession()


#============================
# OAuth 2.0 Implementation
#============================
from flask import session as login_session # The login_session works like a dictionary.
import random, string # For creating the anti-forgery state token.
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE = state)

APPLICATION_NAME = "Car Sensor"
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

@app.route('/gconnect', methods=['POST']) # methods = 'POST' matches with the type of the AJAX call.
def gconnect():
    # Validate state token.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code / one-time-use code.
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object.
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # This result is the result sent from Google after server checks the access token with Google.

    # Based on the result, if there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Verify that the access token is used for the intended user.
    # Credentials/gplus_id is from the server and the result['user_id'] is from Google, so check credentials against result!
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Verify that the access token is valid for this app.
    # CLIENT_ID is from the local file (but converted to credentials according to the code in try & except),
    # so it is similar to from the server and the result is from Google, so check CLIENT_ID against result!
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Check if the user has already been logged in.
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Store the access token in the session for later use.
    # Stored for checking whether user already logged in (just above) and for the /gdisconnect method to use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Server gets user info from Google
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params = params)
    # Stored the answer including user info from Google in 'data' variable in JSON format.
    data = answer.json()

    # ADD PROVIDER TO LOGIN SESSION.
    login_session['provider'] = 'google'
    # Store the user info in the session for later use. (stored for output below and the /gdisconnect method to use)
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Use the first 2 helper methods below to check to see if a user exists in the database.
    # If not, create a new user using the credentials stored in the login_session object.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Return an output for successful Google login
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s via Google" % login_session['username'], "oauth2")
    print "gconnect done!" # Print to the console/terminal!
    return output # Return the output stuff to the 'result' variable of the success function in the login.html template.


@app.route('/fbconnect', methods = ['POST'])
def fbconnnect():
    # Validate state token.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = request.data # This access_token is same as the one-time code in the Google case
    print "access token received %s " % access_token

    # The following process is like upgrading the authorization code into a credentials object in gconnect.
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1] # result here is same as the credentials in gconnect.
    print "The result after exchanging for long lived token is %s" % result
    token = result.split(',')[0].split(':')[1].replace('"', '') # token here is same as the access_token in gconnect.
    print "The long term token is %s" % token

    # In fbconnect, there is not any process for validating the token info like in gconnect (those if functions).
    # Skipped

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v3.1/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''

    url = 'https://graph.facebook.com/v3.1/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print "url sent for API access:%s" % url
    print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook' # Refactor the code to determine which provider the user was logged into and then proceed to log them out.
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"] # This is like the gplus_id in gconnect.
    login_session['access_token'] = token # The token must be stored in the login_session in order to properly log out.

    # Get user picture (seperately in the case of Facebook sign in).
    url = 'https://graph.facebook.com/v3.1/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("Now logged in as %s via Facebook" % login_session['username'], "oauth2")
    return output


# DISCONNECT - Revoke a current user's token on the Google server.
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')

    # Only disconnect a connected user.
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']

    # Delete/revoke/disable user access token online (from Google).
    # Execute HTTP GET request to revoke current token.
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    status = result['status']
    # This result is the first ([0]) part of results sent from Google after server requests Google to revoke the current token.
    print 'result is '
    print status

    # Delete user info, id and token from local cache/session (from server).
    if result['status'] == '200': # If Google successfully revokes the access token,
        # therefore we can now delete infos and token stored in our local server.
        # Reset the user's session.
        # del login_session['access_token']
        # del login_session['gplus_id']
        # del login_session['username']
        # del login_session['email']
        # del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Google failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# DISCONNECT - Revoke a current user's id and token on the Facebook server.
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token'] # The access token must also be included to successfully log out.

    print 'In fbdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']

    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]

    success = result.split(':')[0].replace('"', '').replace('{', '')

    # Useless response, which will not show up.
    # response = make_response(json.dumps("you have been logged out."), 200)
    # response.headers['Content-Type'] = 'application/json'
    # return response

    print "you have been logged out"
    print "result is "
    print success

# Disconnect based on provider (no need to call gdisconnect or fbdisconnect anymore,
# and reset current user's login_session (locally or on our App server).
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['access_token']
        del login_session['provider']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        flash("You have successfully been logged out.", "oauth2")
        return redirect(url_for('goHome'))
    else:
        flash("You were not logged in", "oauth2")
        return redirect(url_for('goHome'))


#==============================
# Local User/Permission System
#==============================
# 3 User Helper Functions
def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None

def createUser(login_session):
    newUser = User(name = login_session['username'], email = login_session[
                   'email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user


#==============================
# JSON APIs to view Car Info
#==============================
@app.route('/garage/JSON')
def makersJSON():
    makers = session.query(Maker).all()
    return jsonify(makers = [maker.serialize for maker in makers])

@app.route('/garage/<int:maker_id>/model/JSON')
def modelsJSON(maker_id):
    maker = session.query(Maker).filter_by(id = maker_id).one()
    models = session.query(Model).filter_by(maker_id = maker_id).all()
    return jsonify(models = [model.serialize for model in models])

@app.route('/garage/<int:maker_id>/model/<int:model_id>/JSON')
def specificModelJSON(maker_id, model_id):
    model = session.query(Model).filter_by(id = model_id).one()
    return jsonify(model = model.serialize)


#============================
# Flask Routes and APIs
#============================
# Homepage
@app.route('/')
@app.route('/garage/')
def goHome():
    makers = session.query(Maker).all()
    newStock = session.query(Model).order_by(desc(Model.date)).limit(5)
    return render_template('homepage.html', makers = makers, newStock = newStock)

@app.route('/garage/<int:maker_id>/')
@app.route('/garage/<int:maker_id>/model/')
def showModels(maker_id):
    makers = session.query(Maker).all()
    maker = session.query(Maker).filter_by(id = maker_id).one()
    models = session.query(Model).filter_by(maker_id = maker_id)
    creator = getUserInfo(maker.user_id)
    if 'username' not in login_session or login_session['user_id'] != creator.id:
        return render_template('publicmodels.html', makers = makers, maker = maker, models = models, creator = creator)
    else:
        return render_template('models.html', makers = makers, maker = maker, models = models, creator = creator)

@app.route('/garage/newmaker/', methods = ['GET', 'POST'])
def newMaker():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newMaker = Maker(name = request.form['maker_name'],
                         logo = request.form['maker_logo'],
                         user_id = login_session['user_id'])
        session.add(newMaker)
        session.commit()
        flash('New Maker Created!', 'maker-related') # By using a second argument, we can now filter flash messages by category.
        return redirect(url_for('goHome'))
    else:
        return render_template('newmaker.html')

@app.route('/garage/<int:maker_id>/edit/', methods = ['GET', 'POST'])
def editMaker(maker_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedMaker = session.query(Maker).filter_by(id = maker_id).one()
    if editedMaker.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this maker. Please create your own maker in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['edited_maker_name']:
            editedMaker.name = request.form['edited_maker_name']
        if request.form['edited_maker_logo']:
            editedMaker.name = request.form['edited_maker_logo']
        session.add(editedMaker)
        session.commit()
        flash('Maker Edited!', 'maker-related')
        return redirect(url_for('goHome'))
    else:
        return render_template('editmaker.html', edited_maker = editedMaker)

@app.route('/garage/<int:maker_id>/delete/', methods = ['GET', 'POST'])
def deleteMaker(maker_id):
    if 'username' not in login_session:
        return redirect('/login')
    deletedMaker = session.query(Maker).filter_by(id = maker_id).one()
    if deletedMaker.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this maker. Please create your own maker in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(deletedMaker)
        session.commit()
        flash('Maker Deleted!', 'maker-related')
        return redirect(url_for('goHome'))
    else:
        return render_template('deletemaker.html', deleted_maker = deletedMaker)

@app.route('/garage/<int:maker_id>/model/new/', methods = ['GET', 'POST'])
def newModel(maker_id):
    if 'username' not in login_session:
        return redirect('/login')
    maker = session.query(Maker).filter_by(id = maker_id).one()
    if maker.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to add models to this maker. Please create your own maker in order to add items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newModel = Model(name = request.form['model_name'],
                         date = datetime.datetime.now(),
                         description = request.form['model_description'],
                         photo = request.form['model_photo'],
                         maker_id = maker_id,
                         user_id = maker.user_id)
        session.add(newModel)
        session.commit()
        flash('New Model %s Added!' % (newModel.name), 'model-related')
        return redirect(url_for('showModels', maker_id = maker_id))
    else:
        return render_template('newmodel.html', maker_id = maker_id)

@app.route('/garage/<int:maker_id>/model/<int:model_id>/edit/', methods = ['GET', 'POST'])
def editModel(maker_id, model_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedMaker = session.query(Maker).filter_by(id = maker_id).one()
    editedModel = session.query(Model).filter_by(id = model_id, maker_id = editedMaker.id).one()
    if editedMaker.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit models of this maker. Please create your own maker in order to edit items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['model_name']:
            editedModel.name = request.form['model_name']
        if request.form['model_description']:
            editedModel.description = request.form['model_description']
        if request.form['model_photo']:
            editedModel.photo = request.form['model_photo']
        session.add(editedModel)
        session.commit()
        flash('%s Successfully Edited!' % (editedModel.name), 'model-related')
        return redirect(url_for('showModels', maker_id = maker_id))
    else:
        return render_template('editmodel.html', maker_id = maker_id, model_id = model_id, edited_model = editedModel)

@app.route('/garage/<int:maker_id>/model/<int:model_id>/delete/', methods = ['GET', 'POST'])
def deleteModel(maker_id, model_id):
    if 'username' not in login_session:
        return redirect('/login')
    deletedMaker = session.query(Maker).filter_by(id = maker_id).one()
    deletedModel = session.query(Model).filter_by(id = model_id, maker_id = deletedMaker.id).one()
    if deletedMaker.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete models of this maker. Please create your own maker in order to delete items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(deletedModel)
        session.commit()
        flash('%s Successfully Deleted!' % (deletedModel.name), 'model-related')
        return redirect(url_for('showModels', maker_id = maker_id))
    else:
        return render_template('deletemodel.html', maker_id = maker_id, model_id = model_id, deleted_model = deletedModel)


#===================
# APP Run!
#===================
# Always put the following at end of file! Important!!!
if __name__ == '__main__':
    app.secret_key = 'SUPER_SECRET_KEY'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)