from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import current_user
import flask_login
from sqlalchemy import func
from . import models
from . import db
from functools import wraps


views = Blueprint('views',__name__)

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role == models.UserRole.admin:
            return f(*args, **kwargs)
        elif current_user.role == models.UserRole.user:
            return redirect(url_for('auth.user_login', next=request.url))
        else:
            return redirect(url_for('auth.admin_login', next=request.url))
    return decorated_function

@views.route("/")
def main_page():
    return render_template('main_page.html')

@views.route('/admin/home')
@flask_login.login_required
@admin_only
def admin_home():
    screening, num_results = admin_screening_auxiliar()
    return render_template('admin_home.html', packed=zip(screening, num_results), screening=screening)

def admin_screening_auxiliar():
    current_day = date.today()
    future = current_day + timedelta(weeks=1) 
    past = current_day - timedelta(weeks=1)
   
    screening = models.Screening.query.filter(models.Screening.day <= future, models.Screening.day >= past).order_by(models.Screening.day.asc(), models.Screening.time.asc()).all()
    num_results = []
    for proj in screening:
        num_results.append(proj.venue.capacity - compute_booked_seats(proj.id))
    return screening, num_results

def compute_booked_seats(id):
    screening = models.Screening.query.filter(models.Screening.id == id).one()
    sum_result = db.session.query(db.func.sum(models.Bookings.seats).label('booked')).filter(models.Bookings.screening == screening).one()
    num_booked_seats = sum_result.booked
    if (sum_result.booked != None):
        num_free_seats = screening.venue.capacity - num_booked_seats
    else:
        num_free_seats = screening.venue.capacity

    return  num_free_seats

@views.route("/add")
@admin_only
@flask_login.login_required
def add():
    Shows = models.Show.query.all()
    venues = models.Venue.query.all()
    current_day = date.today().strftime('%Y-%m-%d')
    return render_template("admin_add.html", Shows=Shows, venues=venues, current_day=current_day)



@views.route("/add", methods=["POST"])
@admin_only
@flask_login.login_required
def add_post():
    Show = request.form.get("Shows")
    venue = request.form.get("venue")
    day = request.form.get("day")
    time = request.form.get("time")
    time = time + ':00'
    day = datetime.strptime(day, "%Y-%m-%d").date()
    time = datetime.strptime(time, "%H:%M:%S").time()
    new_screening = models.Screening(day=day, time=time, show_id=Show, venue_id=venue)
    db.session.add(new_screening)
    db.session.commit()
    return redirect(url_for("views.admin_home"))


@views.route("/edit/<int:id>")
@admin_only
@flask_login.login_required
def edit(id):
    shows = models.Show.query.all()
    venues = models.Venue.query.all()
    current_data = models.Screening.query.get(id)
    return render_template("admin_edit.html", shows=shows, venues=venues, current_data=current_data)


@views.route("/edit/<int:id>", methods=["POST"])
@admin_only
@flask_login.login_required
def edit_post(id):
    show = request.form.get("shows")
    venue = request.form.get("venues")
    day = request.form.get("day")
    time = request.form.get("time")
    time = time + ':00'

    day = datetime.strptime(day, "%Y-%m-%d").date()
    time = datetime.strptime(time, "%H:%M:%S").time()

    screening = models.Screening.query.filter(models.Screening.id == id).first()
    screening.day = day
    screening.time = time
    screening.show_id = show
    screening.venue_id = venue 

    db.session.commit()
    flash("You have edited a screening", 'success')
    return redirect(url_for("views.admin_home"))

@views.route("/delete/<int:id>")
@admin_only
@flask_login.login_required
def delete(id):
    current_data = models.Screening.query.get(id)
    db.session.delete(current_data)
    db.session.commit()
    flash("You have deleted a screening", 'success')
    return redirect(url_for("views.admin_home"))

@views.route("/user/home")
@flask_login.login_required
def user_home():
    current_day = date.today()
    screening, num_results = admin_screening_auxiliar()
    all_screenings = models.Screening.query.filter(models.Screening.day >= current_day).order_by(models.Screening.day.asc(), models.Screening.time.asc()).all()
    return render_template("user_home.html", screenings=all_screenings, packed=zip(screening, num_results),screening=screening)


@views.route("/booking/", defaults={'id': None})
@views.route("/booking/<int:id>")
@flask_login.login_required
def booking(id):
    current_day = date.today()
    
    all_screenings = models.Screening.query.filter(models.Screening.day >= current_day).order_by(models.Screening.day.asc(), models.Screening.time.asc()).all()
    if id == None:
        return render_template("boookings.html", screening=None, screenings=all_screenings)
    else:
        screening = models.Screening.query.get(id)
        screenings = models.Screening.query.filter(models.Screening.show_id == screening.show_id, models.Screening.day >= current_day).order_by(models.Screening.day.asc(), models.Screening.time.asc()).all()
        return render_template("bookings.html", screening=screening, screenings=screenings)


@views.route("/booking/", methods=["POST"])
@flask_login.login_required
def booking_post():
    choosen_screening = request.form.get("screening")
    choosen_num_seats = request.form.get("seats")
    cost = request.form.get("totalPrice")

    screening = models.Screening.query.get(choosen_screening)

    booked_seats= db.session.query(func.sum(models.Bookings.seats)).filter(models.Bookings.screening_id == screening.id).scalar()

    if booked_seats == None:
        booked_seats = 0

    venue_capacity = screening.venue.capacity

    available_seats = venue_capacity - booked_seats

    if available_seats - int(choosen_num_seats) < 0:

        flash('You can only book %s'%(available_seats), 'error')
        return redirect(url_for('views.booking', id = screening.id))
    
    else:
        new_reservation = models.Bookings(user_id=current_user.id, screening_id=screening.id, seats=int(choosen_num_seats), date_time=datetime.now(), cost=int(cost))
        
        

        db.session.add(new_reservation)
        db.session.commit()
        flash("You have bought %s tickets for %s"%(choosen_num_seats, screening.show.name), 'success')
        return redirect(url_for("views.user_bookings"))

@views.route('/user/bookings')
@flask_login.login_required
def user_bookings():
    current_day = date.today()
    now = []
    past = []
    now_bookings = models.Bookings.query.filter(models.Bookings.user_id == current_user.id).order_by(models.Bookings.date_time).all()
    for book in now_bookings:
        if book.screening.day >= current_day:
            now.append(book)
        else:
            past.append(book)
    return render_template('user_history.html', now_bookings = now, past_bookings = past)

@views.route('/user/search', methods = ['POST'])
def user_search():
    current_day = date.today()
    search_term = request.form.get('searched')
    searches = models.Screening.query.join(models.Venue).join(models.Show).filter((models.Screening.day >= current_day),
    (models.Venue.location.like(f'%{search_term}%') | models.Venue.place.like(f'%{search_term}%') | models.Show.rating.like(f'%{search_term}%') | models.Show.tags.like(f'%{search_term}%') | models.Venue.name.like(f'%{search_term}%') | models.Show.name.like(f'%{search_term}%') | models.Screening.day.like(f'%{search_term}%') )).order_by(models.Screening.day.asc(), models.Screening.time.asc()).all()
    current_day = date.today()
    screening, num_results = admin_screening_auxiliar()
    return render_template("user_search.html", searches=searches, packed=zip(screening, num_results))

@views.route('/admin/venues')
@flask_login.login_required
@admin_only
def venue_view():
    venues = models.Venue.query.all()
    return render_template("venue_view.html", venues = venues)

@views.route('/admin/shows')
@admin_only
def show_view():
    shows = models.Show.query.all()
    return render_template("show_view.html", shows = shows)

@views.route('admin/venue_add')
@admin_only
@flask_login.login_required
def add_venue():
    return render_template("venue_add.html")

@views.route('admin/venue_add', methods = ['POST'])
@admin_only
@flask_login.login_required
def add_venue_post():
    name = request.form.get('name')
    capacity = request.form.get('capacity')
    place = request.form.get('place')
    location = request.form.get('location')

    new_venue = models.Venue(name=name, capacity=capacity, place=place, location=location)
    db.session.add(new_venue)
    db.session.commit()

    flash("You have added a venue", 'success')
    return redirect(url_for('views.venue_view'))

@views.route('admin/show_add')
@admin_only
@flask_login.login_required
def add_show():
    return render_template("show_add.html")

@views.route('admin/show_add', methods = ['POST'])
@admin_only
@flask_login.login_required
def add_show_post():
    name = request.form.get('name')
    tags = request.form.get('tags')
    rating = request.form.get('rating')
    price = request.form.get('price')
    img = request.form.get('img')

    new_show = models.Show(name=name, tags=tags, rating=rating, price=price, img=img)
    db.session.add(new_show)
    db.session.commit()

    flash("You have added a show", 'success')
    return redirect(url_for('views.show_view'))


@views.route("/admin/venue_edit/<int:id>")
@admin_only
@flask_login.login_required
def edit_venue(id):
    current_data = models.Venue.query.get(id)
    return render_template("venue_edit.html",current_data=current_data)


@views.route("/admin/venue_edit/<int:id>", methods=["POST"])
@admin_only
@flask_login.login_required
def edit_venue_post(id):
    name = request.form.get('name')
    capacity = request.form.get('capacity')
    place = request.form.get('place')
    location = request.form.get('location')
    

    venue = models.Venue.query.filter(models.Venue.id == id).first()
    venue.name = name
    venue.capacity = capacity
    venue.place = place
    venue.location = location 

    db.session.commit()
    flash("You have edited a venue", 'success')
    return redirect(url_for("views.venue_view"))

@views.route("/admin/venue_delete/<int:id>")
@admin_only
@flask_login.login_required
def delete_venue(id):
    current_data = models.Venue.query.get(id)
    db.session.delete(current_data)
    db.session.commit()
    flash("You have deleted a venue", 'success')
    return redirect(url_for("views.venue_view"))

@views.route("/admin/show_edit/<int:id>")
@admin_only
@flask_login.login_required
def edit_show(id):
    current_data = models.Show.query.get(id)
    return render_template("show_edit.html",current_data=current_data)


@views.route("/admin/show_edit/<int:id>", methods=["POST"])
@admin_only
@flask_login.login_required
def edit_show_post(id):
    name = request.form.get('name')
    rating = request.form.get('rating')
    price = request.form.get('price')
    tags = request.form.get('tags')
    img = request.form.get('img')

    show = models.Show.query.filter(models.Show.id == id).first()
    show.name = name
    show.rating = rating
    show.price = price
    show.tags = tags 
    show.img = img

    db.session.commit()
    flash("You have edited a show", 'success')
    return redirect(url_for("views.show_view"))

@views.route("/admin/show_delete/<int:id>")
@admin_only
@flask_login.login_required
def delete_show(id):
    current_data = models.Show.query.get(id)
    db.session.delete(current_data)
    db.session.commit()
    flash("You have deleted a show", 'success')
    return redirect(url_for("views.show_view"))

