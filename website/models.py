from . import db  
from flask_login import UserMixin 
import enum

class UserRole(enum.Enum):
    user = 1
    admin = 2

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    role = db.Column(db.Enum(UserRole), unique=False, nullable=False)

    user_booked = db.relationship('Bookings', cascade="all,delete", backref='user', lazy=True)


class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(240), unique=False, nullable=False)
    rating = db.Column(db.String(10), unique=False, nullable=False)
    price = db.Column(db.Integer, nullable = False)
    tags = db.Column(db.String(150), nullable = False)
    img = db.Column(db.String(512))

    screened = db.relationship('Screening', cascade="all,delete", backref='show', lazy=True)

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    capacity = db.Column(db.Integer, unique=False, nullable=False)
    place = db.Column(db.String(20), unique =False, nullable=False)
    location = db.Column(db.String(20), unique =False, nullable=False)

    screened = db.relationship('Screening', cascade="all,delete", backref='venue', lazy=True)

class Screening(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date(), unique=False, nullable=False)
    time = db.Column(db.Time(), unique=False, nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable = False)

    booked = db.relationship('Bookings', cascade="all,delete", backref='screening', lazy=True)

class Bookings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    screening_id = db.Column(db.Integer, db.ForeignKey('screening.id'), nullable=False)
    seats = db.Column(db.Integer, unique=False, nullable=False)
    cost = db.Column(db.Integer, unique =False, nullable=False)
    date_time = db.Column(db.DateTime(), unique=False, nullable=False)

