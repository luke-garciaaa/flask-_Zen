from flask import request, render_template, url_for, flash , redirect, Flask
from app import app, db, bcrypt
from app.models import User, Trackinsight, artistinsight
from app.forms import RegistrationForm, LoginForm, PostForm, UpdateArtistForm, UpdateUserForm, AddUserForm
from flask_login import login_user, current_user, logout_user, login_required
from flask import request, session, redirect,url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import time

TOKEN_INFO = 'token_info'
#                                                   ##  BEGINNING OF SPOTIFY IMPLEMENTATION  ###

##basically the redirect
@app.route('/instantspot')
def instantspot():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)
   
    

@app.route('/authorize')
def authorize_page(): 
    flash(f'Your Spotify Account has been authorized!',category = 'success')
    sp_oauth = create_spotify_oauth()
    #session.clear()                   #########################################################################
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info

    #takes user to track_page after authorization
    return redirect(url_for('track_page'))
    #return redirect(url_for('track_testing'))
    
##CHANGE REDIRECT URI

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = os.environ.get("SPOTIPY_CLIENT_ID"),
        client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET"),
        
        redirect_uri = 'http://localhost:5000/authorize',
        ## URL_FOR SUCKS AND DOESNT WORK
        scope = "user-top-read"

        
    )

@app.route('/tracktest', methods = ['GET', 'POST'])
def track_testing():
    
    try:
        token_info = get_token()
    except:
        print('User not logged in')
        redirect(url_for('authenticate_page'))
    sp = spotipy.Spotify(auth = token_info['access_token'])
    ######### BEGINNING OF INSIGHT IMPLEMENTATION
    
    track_info = []
    track_a = []
    for sp_range in ['short_term', 'medium_term', 'long_term']:
        results = sp.current_user_top_tracks(time_range=sp_range, limit=50)
        for i, item in enumerate(results['items']):
            track_info.append(item['name'])
            track_a.append(item)
    track_name = track_info[0] ##name of track
    track_album = track_a[0]['album']['name'] ##album of track

    post = Trackinsight(track_content = track_name, user_email = current_user.email, track_genre = track_album) ##works except for current_user.email
    db.session.add(post)
    db.session.commit()
    flash(f'Your track insights have been added!',category = 'success')
    return redirect(url_for('track_page'))   
    
@app.route('/artisttest', methods = ['GET', 'POST'])
def artist_testing():
    try:
        token_info = get_token()
    except:
        print('User not logged in')
        redirect(url_for('authenticate_page'))
    sp = spotipy.Spotify(auth = token_info['access_token'])
    ######### BEGINNING OF INSIGHT IMPLEMENTATION
    ranges = ['short_term', 'medium_term', 'long_term']
    artist_info = []
    artist_genre = []
    for sp_range in ['short_term', 'medium_term', 'long_term']:
        results = sp.current_user_top_artists(time_range=sp_range, limit=50)
        for i, item in enumerate(results['items']):
            artist_info.append(item['name'])
            artist_genre.append(item)
    
    artist_name = artist_info[0]
    artist_g = artist_genre[0]['genres'][0]
    artist_post = artistinsight(user_email = current_user.email, artist_content = artist_name, artist_genre = artist_g )
    db.session.add(artist_post)
    db.session.commit()
    flash(f'Your artist insights have been added!',category = 'success')
    return redirect(url_for('artist_page'))
    
                                            ###################### ENDING OF Spotify IMPLEMENTATION ##############################33
   



def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info
                                                                        ############# END OF SPOTFY ###############





#home page
@app.route('/')
def home_page():
    return render_template('home.html')

#navigates to about page
@app.route('/about')
def about_page():
    '''
    Creates a page containing information about our project and it's motivations
    '''
  
    return render_template('about.html')

#Navigates to registration page, adds methods that allows form to get and post
@app.route('/register', methods = ['GET','POST'])
def register_page():
    #checks if current user is authenticated, redirects to home page
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    #initializes class
    form = RegistrationForm()
    if form.validate_on_submit():
        #hashes password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, password= hashed_password)
        #Add user to database
        db.session.add(user)
        db.session.commit()
        #checks if the form was filled out correct
        flash(f'Your account has been created!',category = 'success')


        #redirects user to home page
        return redirect(url_for('login_page'))
    return render_template('register.html', form = form)

#Navigates to login page
@app.route('/login', methods = ['GET', 'POST'])
def login_page():
    #checks if current user is authenticated, redirects to home page
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = LoginForm()
    if form.validate_on_submit():
        # checks if user exists, if user doesn't exist, will return none,
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session.permanent = False    ################### IF THE BROWSER RESTARTS, SO DOES THE SESSION
            login_user(user)
            flash('You are now logged in!', category = 'success')
            return redirect(url_for('home_page'))
            
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

##BEGINNING OF LOGIN ONLY PAGES
#Navigates to Authenticate Spotify page, will likely need to add 
@app.route('/authenticate')
@login_required
def authenticate_page():
    return render_template('authenticate.html')





#page to manage tracks
@app.route('/tracks')
@login_required
def track_page():
    #INSTEAD OF QUERY ALL, TRY TO QUERY BY current user's email so only those are shown
    #OLD
    #track_insight = Trackinsight.query.all() 
    #NEW
    track_insight = Trackinsight.query.filter_by(user_email = current_user.email)
    return render_template('tracks.html', track_insight = track_insight)    

## DELETE Tracks
@app.route('/tracks/<int:track_id>/delete', methods = ['GET', 'POST'])
def delete_tracks(track_id):
    track = Trackinsight.query.get_or_404(track_id)
    db.session.delete(track)
    db.session.commit()
    flash('Your track insight has been deleted!', 'success')
    return redirect(url_for('track_page'))

##page to update tracks
@app.route('/tracks/<int:track_id>/update', methods = ['GET', 'POST'])
def update_tracks(track_id):
    track = Trackinsight.query.get_or_404(track_id)
    form = PostForm()
    if form.validate_on_submit():
        track.track_content = form.track.data
        track.track_genre = form.album.data
        db.session.commit()
        flash('Your track information has been updated!', 'success')
        return redirect(url_for('track_page', track_id = track.id))
    elif request.method == 'GET':
        form.track.data = track.track_content
        form.album.data = track.track_genre     
    return render_template('updatetrack.html', title = 'Update Track', form = form)



@app.route('/artists')
@login_required
def artist_page():
    artist_insight = artistinsight.query.filter_by(user_email = current_user.email)
    return render_template('artists.html',artist_insight = artist_insight)


#page to update artists
@app.route('/artists/<int:artist_id>/update', methods = ['GET', 'POST'])
def update_artists(artist_id):
    artist = artistinsight.query.get_or_404(artist_id)
    form = UpdateArtistForm()
    if form.validate_on_submit():
        artist.artist_content = form.artist.data
        artist.artist_genre = form.genre.data
        db.session.commit()
        flash('Your artist information has been updated!', 'success')
        return redirect(url_for('artist_page', artist_id = artist.id))
    elif request.method == 'GET':
        form.artist.data = artist.artist_content
        form.genre.data = artist.artist_genre     
    return render_template('updateartist.html', title = 'Update Artist', form = form)


## Delete Artist
@app.route('/artists/<int:artist_id>/delete', methods = ['GET', 'POST'])
def delete_artists(artist_id):
    artist = artistinsight.query.get_or_404(artist_id)
    db.session.delete(artist)
    db.session.commit()
    flash('Your artist insight has been deleted!', 'success')
    return redirect(url_for('artist_page'))


#page to manage users
@app.route('/admin')
@login_required
def admin_page():
    users = User.query.all()
    return render_template('admin.html', users = users)

#delete users
@app.route('/admin/<int:user_id>/delete', methods = ['GET', 'POST'])
def delete_users(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('A user has been deleted!', 'success')
    return redirect(url_for('admin_page'))
#update users
#page to update users
@app.route('/admin/<int:user_id>/update', methods = ['GET', 'POST'])
def update_users(user_id):
    user = User.query.get_or_404(user_id)
    form = UpdateUserForm()
    if form.validate_on_submit():
        user.email = form.email.data
        #OLD
        #user.password = form.password.data
        #NEW 
        user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('The user information has been updated!', 'success')
        return redirect(url_for('admin_page', user_id = user.id))
    #autofills data in update page with current data
    elif request.method == 'GET':
        form.email.data = user.email
        form.password.data = user.password    
    return render_template('updateuser.html', title = 'Update User', form = form)
#page to add users
@app.route('/admin/adduser', methods = ['GET','POST'])
@login_required
def adduser_page():
    form = AddUserForm()
    if form.validate_on_submit():
        #hashes password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, password= hashed_password)
        #Add user to database
        db.session.add(user)
        db.session.commit()
        #checks if the form was filled out correct
        flash(f'The account has been created!',category = 'success')
        return redirect(url_for('admin_page'))
    return render_template('adduser.html', form = form)

    #logout page route, directs user back to home page when user is logged out             
@app.route('/logout')
def logout_page():
    logout_user()
    flash('Your have been logged out!', 'success')
    return redirect(url_for('home_page'))
