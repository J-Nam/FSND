#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ~TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
#show = db.Table('Show',
#    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
#    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
#    db.Column('start_time', db.DateTime, nullable=True)
#)

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    #foreignkey
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    #relationship
    venue = db.relationship('Venue', backref='show', lazy=True, cascade='all, delete')
    artist = db.relationship('Artist', backref='show', lazy=True, cascade='all, delete')
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(200))
    # ~TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(200))

    # ~TODO: implement any missing fields, as a database migration using Flask-Migrate

# ~TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # ~TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []

  areas = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  print(areas)
  for city, state in areas:
    info = {}
    info["city"] = city
    info["state"] = state
    venues = []
    venuelist = Venue.query.filter_by(city = city).all()
    for venue in venuelist:
      venueinfo = {}
      venueinfo["id"] = venue.id
      venueinfo["name"] = venue.name
      venueinfo["num_upcoming_shows"] = len(venue.show)
      venues.append(venueinfo)
      info["venues"] = venues

    data.append(info)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # ~TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  response = {}
  data = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  count = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).count()
  response["count"] = count
  response["data"] = data
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # ~TODO: replace with real venue data from the venues table, using venue_id
  data = {}
  venue = Venue.query.get(venue_id)
  data["id"] = venue.id
  data["name"] = venue.name
  data["genres"] = venue.genres
  data["address"] = venue.address
  data["city"] = venue.city
  data["state"] = venue.state
  data["phone"] = venue.phone
  data["website"] = venue.website
  data["facebook_link"] = venue.facebook_link
  data["seeking_talent"] = venue.seeking_talent
  data["seeking_description"] = venue.seeking_description
  data["image_link"] = venue.image_link
  past_shows = []
  upcoming_shows = []

  shows = Show.query.filter_by(venue_id=venue_id).all()
  
  for show in shows:
    if show.start_time < datetime.datetime.now():
      past_shows_info = {}
      past_shows_info["artist_id"] = show.artist.id
      past_shows_info["artist_name"] = show.artist.name
      past_shows_info["artist_image_link"] = show.artist.image_link
      past_shows_info["start_time"] = str(show.start_time)
      past_shows.append(past_shows_info)
    else:
      upcoming_shows_info = {}
      upcoming_shows_info["artist_id"] = show.artist.id
      upcoming_shows_info["artist_name"] = show.artist.name
      upcoming_shows_info["artist_image_link"] = show.artist.image_link
      upcoming_shows_info["start_time"] = str(show.start_time)
      upcoming_shows.append(upcoming_shows_info)

  data["past_shows"] = past_shows
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = len(data["past_shows"])
  data["upcoming_shows_count"] = len(data["upcoming_shows"])

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # ~TODO: insert form data as a new Venue record in the db, instead    
  # TODO: modify data to be the data object returned from db insertion

  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.getlist("genres")
  genres = ','.join([str(el) for el in genres])
  facebook_link = request.form.get('facebook_link')

  error = False
  try:
      venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link)
      db.session.add(venue)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
  finally:    
  # on successful db insert, flash success
      db.session.close()
  if error:
      flash('Oops, an error occurred. Please try it again!')
  else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # ~TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # ~TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except:
      db.session.rollback()
  finally:
      db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # ~TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # ~TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = {}
  data = []
  search = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike('%' + search + '%')).all()
  count = Artist.query.filter(Artist.name.ilike('%' + search + '%')).count()
  response["count"] = count
  for artist in artists:
    data.append(artist)

  response["data"] = data

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # ~TODO: replace with real venue data from the venues table, using venue_id
  data = {}
  artist = Artist.query.get(artist_id)
  data["id"] = artist.id
  data["name"] = artist.name
  data["genres"] = artist.genres
  data["city"] = artist.city
  data["state"] = artist.state
  data["phone"] = artist.phone
  data["website"] = artist.website
  data["facebook_link"] = artist.facebook_link
  data["seeking_venue"] = artist.seeking_venue
  data["seeking_description"] = artist.seeking_description
  data["image_link"] = artist.image_link
  past_shows = []
  upcoming_shows = []

  shows = Show.query.filter_by(artist_id=artist_id).all()
  
  for show in shows:
    if show.start_time < datetime.datetime.now():
      past_shows_info = {}
      past_shows_info["venue_id"] = show.venue.id
      past_shows_info["venue_name"] = show.venue.name
      past_shows_info["venue_image_link"] = show.venue.image_link
      past_shows_info["start_time"] = str(show.start_time)
      past_shows.append(past_shows_info)
    else:
      upcoming_shows_info = {}
      upcoming_shows_info["venue_id"] = show.venue.id
      upcoming_shows_info["venue_name"] = show.venue.name
      upcoming_shows_info["venue_image_link"] = show.venue.image_link
      upcoming_shows_info["start_time"] = str(show.start_time)
      upcoming_shows.append(upcoming_shows_info)

  data["past_shows"] = past_shows
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = len(data["past_shows"])
  data["upcoming_shows_count"] = len(data["upcoming_shows"])
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  query = Artist.query.get(artist_id)
  artist = {}
  artist["id"] = query.id
  artist["name"] = query.name
  artist["genres"] = query.genres
  artist["city"] = query.city
  artist["state"] = query.state
  artist["phone"] = query.phone
  artist["website"] = query.website
  artist["facebook_link"] = query.facebook_link
  artist["seeking_venue"] = query.seeking_venue
  artist["seeking_description"] = query.seeking_description
  artist["image_link"] = query.image_link
  # ~TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # ~TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
      name = request.form.get("name")
      genres = request.form.getlist("genres")
      genres = ','.join([str(el) for el in genres])
      city = request.form.get("city")
      state = request.form.get("state")
      phone = request.form.get("phone")
      website = request.form.get("website")
      facebook_link = request.form.get("facebook_link")
      seeking_venue = request.form.get("seeking_venue")
      seeking_description = request.form.get("seeking_description")
      image_link = request.form.get("image_link")

      artist = Artist.query.get(artist_id)

      artist.name = name
      artist.genres = genres
      artist.city = city
      artist.state = state
      artist.phone = phone
      artist.website = website
      artist.facebook_link = facebook_link
      artist.seeking_venue = seeking_venue
      artist.seeking_description = seeking_description
      artist.image_link = image_link
      
      db.session.commit()
  except:
      db.session.rollback()
  finally:
      db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # ~TODO: populate form with values from venue with ID <venue_id>
  query = Venue.query.get(venue_id)
  venue = {}
  venue["id"] = query.id
  venue["name"] = query.name
  venue["genres"] = query.genres
  venue["city"] = query.city
  venue["state"] = query.state
  venue["address"] = query.address
  venue["phone"] = query.phone
  venue["website"] = query.website
  venue["facebook_link"] = query.facebook_link
  venue["seeking_venue"] = None
  venue["seeking_description"] = None
  venue["image_link"] = query.image_link
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # ~TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
      name = request.form.get("name")
      genres = request.form.getlist("genres")
      genres = ','.join([str(el) for el in genres])
      city = request.form.get("city")
      state = request.form.get("state")
      address = request.form.get("address")
      phone = request.form.get("phone")
      website = request.form.get("website")
      facebook_link = request.form.get("facebook_link")
      seeking_talent = request.form.get("seeking_talent")
      seeking_description = request.form.get("seeking_description")
      image_link = request.form.get("image_link")
      print(genres)
      venue = Venue.query.get(venue_id)

      venue.name = name
      venue.genres = genres
      venue.city = city
      venue.state = state
      venue.address = address
      venue.phone = phone
      venue.website = website
      venue.facebook_link = facebook_link
      venue.seeking_talent = seeking_talent
      venue.seeking_description = seeking_description
      venue.image_link = image_link
      
      db.session.commit()
  except:
      db.session.rollback()
  finally:
      db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # ~TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = request.form.getlist("genres")
  genres = ','.join([str(el) for el in genres])
  facebook_link = request.form.get('facebook_link')

  error = False
  try:
      artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link)
      db.session.add(artist)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
  finally:    
      db.session.close()
  if error:
      flash('Oops, an error occurred. Please try it again!')
  else:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # ~TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # ~TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Show.query.all()
  for show in shows:
      datainfo = {}
      datainfo["venue_id"] = show.venue_id
      datainfo["venue_name"] = show.venue.name
      datainfo["artist_id"] = show.artist.id
      datainfo["artist_name"] = show.artist.name
      datainfo["artist_image_link"] = show.artist.image_link
      datainfo["start_time"] = str(show.start_time)
      data.append(datainfo)
      print(show.artist)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # ~TODO: insert form data as a new Show record in the db, instead
  artist_id = request.form.get("artist_id")
  venue_id = request.form.get("venue_id")
  start_time = request.form.get("start_time")
  error = False
  try:
      newshow = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      db.session.add(newshow)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Please try it again.')
  else:
      # on successful db insert, flash success
      flash('Show was successfully listed!')
  # ~TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
