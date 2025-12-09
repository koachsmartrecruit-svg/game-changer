import os
import json
import random
import string
from datetime import datetime
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    session,
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from slugify import slugify
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------
# PATHS
# ---------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ---------------------------------
# APP CONFIG
# ---------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key-change-this"

# ---- EMAIL CONFIGURATION (GMAIL) ----
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = 'sudiksha746@gmail.com'

mail = Mail(app)

# ---- DB Configuration ----
DB_URL = os.getenv("DATABASE_URL")

# Fix for SQLAlchemy (Postgres URLs must start with postgresql://, not postgres://)
if DB_URL and DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --- FIX FOR SSL DISCONNECTS ---
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,  # Checks if connection is alive before using it
    "pool_recycle": 300,    # Refreshes connection every 5 minutes
}

# Initialize DB exactly once here
db = SQLAlchemy(app)

# ---- File Upload Configuration ----
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Login Manager Configuration
login_manager = LoginManager(app)
login_manager.login_view = "login"

SPORTS_LIST = [
    "Cricket",
    "Football",
    "Badminton",
    "Kabaddi",
    "Hockey",
    "Athletics",
    "Swimming",
    "Tennis",
    "Table Tennis",
    "Basketball",
    "Volleyball",
    "Wrestling",
    "Boxing",
    "Shooting",
    "Archery",
    "Weightlifting",
    "Gymnastics",
    "Judo",
    "Squash",
    "Chess",
]


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------
# MODELS
# ---------------------------------
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coach_id = db.Column(db.Integer, db.ForeignKey('coach.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1 to 5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to access the student's name
    student = db.relationship('User', backref='reviews_written', lazy=True)

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), default="hirer")  # 'coach' or 'hirer'
    is_organization = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Relationships
    coach_profile = db.relationship("Coach", backref="user", uselist=False)
    bookings_made = db.relationship("Booking", backref="student", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Coach(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    sport = db.Column(db.String(500), nullable=False)
    sports_prices = db.Column(db.Text, default="{}")
    pincode = db.Column(db.String(10))
    state = db.Column(db.String(100))
    city = db.Column(db.String(120), nullable=False)
    price_per_session = db.Column(db.Integer, nullable=False)
    experience_years = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=4.5)
    tagline = db.Column(db.String(255))
    specialties = db.Column(db.Text)
    age = db.Column(db.Integer)
    phone = db.Column(db.String(15))
    profile_image = db.Column(db.String(300), default="default_coach.jpg")
    achievements = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    travel_radius = db.Column(db.Integer, default=0) # 0 means "I don't travel / At my venue only"
    reviews = db.relationship('Review', backref='coach', lazy=True, cascade="all, delete-orphan")
    
    # Relationships
    bookings_received = db.relationship("Booking", backref="coach", lazy=True)

    def get_whatsapp_url(self):
        if not self.phone:
            return "#"
        
        # 1. Clean the number (remove spaces, dashes, plus signs)
        clean_number = "".join(filter(str.isdigit, self.phone))
        
        # 2. Add Country Code (Assuming India +91 if user entered 10 digits)
        if len(clean_number) == 10:
            clean_number = "91" + clean_number
            
        # 3. Generate Link with pre-filled message
        message = f"Hi {self.name}, I saw your profile on GameChanger and I am interested in training."
        # Simple URL encoding for spaces
        message = message.replace(" ", "%20")
        
        return f"https://wa.me/{clean_number}?text={message}"

    def get_sports_list(self):
        return self.sport.split(",") if self.sport else []

    def get_price_dict(self):
        try:
            return json.loads(self.sports_prices) if self.sports_prices else {}
        except Exception:
            return {}


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coach_id = db.Column(db.Integer, db.ForeignKey("coach.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # The Hirer
    sport = db.Column(db.String(100), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_slug(name, sport_str):
    first_sport = sport_str.split(",")[0] if sport_str else "coach"
    base = slugify(f"{name}-{first_sport}")
    slug = base
    counter = 2
    while Coach.query.filter_by(slug=slug).first():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


# ---------------------------------
# ROUTES
# ---------------------------------
@app.route("/review/<int:coach_id>", methods=["POST"])
@login_required
def add_review(coach_id):
    coach = Coach.query.get_or_404(coach_id)
    
    # SECURITY CHECK: Has the user booked this coach?
    valid_booking = Booking.query.filter_by(
        user_id=current_user.id, 
        coach_id=coach.id, 
        status='Confirmed'
    ).first()
    
    if not valid_booking:
        flash("You must complete a session with this coach before leaving a review.", "danger")
        return redirect(url_for('coach_detail', slug=coach.slug))

    # 1. Get Form Data
    rating = int(request.form.get("rating"))
    comment = request.form.get("comment")
    
    # 2. Save Review
    new_review = Review(
        coach_id=coach.id,
        user_id=current_user.id,
        rating=rating,
        comment=comment
    )
    db.session.add(new_review)
    
    # 3. Recalculate Average Rating
    db.session.commit() 
    
    all_reviews = Review.query.filter_by(coach_id=coach.id).all()
    if all_reviews:
        avg_rating = sum([r.rating for r in all_reviews]) / len(all_reviews)
        coach.rating = round(avg_rating, 1)
        db.session.commit()
    
    flash("Review submitted successfully!", "success")
    return redirect(url_for('coach_detail', slug=coach.slug))
@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    
    if email:
        # Check if already subscribed
        existing = Subscriber.query.filter_by(email=email).first()
        
        if existing:
            flash("You are already subscribed!", "info")
        else:
            # 1. Save to Database
            new_sub = Subscriber(email=email)
            db.session.add(new_sub)
            db.session.commit()
            
            # 2. Send Welcome Email
            try:
                msg = Message("Welcome to the Club! 🏆", recipients=[email])
                msg.body = (
                    "Hi there,\n\n"
                    "Thanks for joining the GameChanger community! You're now on the list to receive "
                    "updates on top coaches, training tips, and exclusive offers.\n\n"
                    "Ready to level up? Find your mentor today: " + url_for('coaches', _external=True) + "\n\n"
                    "Best,\nThe GameChanger Team"
                )
                mail.send(msg)
            except Exception as e:
                print(f"Email failed: {e}") # Print error to console but don't crash app
            
            flash("Thanks for subscribing! A welcome email is on its way.", "success")
    else:
        flash("Please enter a valid email.", "danger")
        
    # Redirect back to the page they came from
    return redirect(request.referrer or url_for('home'))

# --- ADMIN DASHBOARD ---
@app.route("/admin")
@login_required
def admin_dashboard():
    # 1. SECURITY: Strict Admin Check
    if current_user.email != app.config['MAIL_USERNAME']:
        flash("Access Denied: You are not the Super Admin.", "danger")
        return redirect(url_for('home'))

    # 2. GATHER STATS
    stats = {
        'total_users': User.query.count(),
        'total_coaches': Coach.query.count(),
        'total_bookings': Booking.query.count(),
        'subscribers': Subscriber.query.count(),
        # Calculate rough revenue (Sum of all booking prices) - optional logic
        'revenue': sum([b.coach.price_per_session for b in Booking.query.all() if b.coach])
    }
    
    # 3. FETCH DATA
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    pending_coaches = Coach.query.filter_by(is_verified=False).limit(5).all()
    
    return render_template("admin_dashboard.html", stats=stats, bookings=recent_bookings, pending_coaches=pending_coaches)

# --- ADMIN ACTION: MANUAL VERIFY ---
@app.route("/admin/verify/<int:coach_id>")
@login_required
def admin_verify_coach(coach_id):
    if current_user.email != app.config['MAIL_USERNAME']:
        return redirect(url_for('home'))
        
    coach = Coach.query.get_or_404(coach_id)
    coach.is_verified = True
    db.session.commit()
    flash(f"Verified Coach {coach.name} successfully.", "success")
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/email", methods=["GET", "POST"])
@login_required
def admin_email():
    # SECURITY: Only allow the email owner to access this page
    if current_user.email != app.config['MAIL_USERNAME']:
        flash("Access Denied: Admin only.", "danger")
        return redirect(url_for('home'))

    # Get all subscribers
    subscribers = Subscriber.query.all()
    
    if request.method == "POST":
        subject = request.form.get("subject")
        body_text = request.form.get("message")
        
        if not subject or not body_text:
            flash("Please fill in both subject and message.", "warning")
        else:
            sent_count = 0
            try:
                # Open ONE connection for bulk sending (Much faster)
                with mail.connect() as conn:
                    for sub in subscribers:
                        msg = Message(subject, recipients=[sub.email])
                        msg.body = body_text + "\n\n--\nUnsubscribe: Reply with 'UNSUBSCRIBE'"
                        conn.send(msg)
                        sent_count += 1
                
                flash(f"Successfully sent email to {sent_count} subscribers!", "success")
                return redirect(url_for('coach_dashboard'))
                
            except Exception as e:
                print(f"Bulk email error: {e}")
                flash("An error occurred while sending emails.", "danger")

    return render_template("admin_email.html", subscriber_count=len(subscribers))

@app.route("/")
def home():
    top_coaches = Coach.query.order_by(Coach.rating.desc()).limit(3).all()
    return render_template("home.html", coaches=top_coaches)


@app.route("/plans")
def plans():
    return render_template("plans.html")


@app.route("/coaches")
def coaches():
    sport_filter = request.args.get("sport", "").strip()
    city_filter = request.args.get("city", "").strip()
    query = Coach.query
    if sport_filter:
        query = query.filter(Coach.sport.ilike(f"%{sport_filter}%"))
    if city_filter:
        query = query.filter(Coach.city.ilike(f"%{city_filter}%"))
    coaches_list = query.order_by(Coach.id.desc()).all()
    return render_template("coaches.html", coaches=coaches_list)


@app.route("/coaches/<slug>")
def coach_detail(slug):
    coach = Coach.query.filter_by(slug=slug).first_or_404()
    achievements = coach.achievements.splitlines() if coach.achievements else []
    specialties = [s.strip() for s in (coach.specialties or "").split(",") if s.strip()]
    
    # LOGIC: Check if user can review
    can_review = False
    if current_user.is_authenticated and current_user.role != 'coach':
        # Check for ANY confirmed booking
        booking = Booking.query.filter_by(
            user_id=current_user.id, 
            coach_id=coach.id, 
            status='Confirmed'
        ).first()
        if booking:
            can_review = True

    return render_template(
        "coach_detail.html",
        coach=coach,
        achievements=achievements,
        specialties=specialties,
        can_review=can_review  # <--- PASS THIS FLAG
    )

@app.route("/book/<int:coach_id>", methods=["POST"])
@login_required
def book_session(coach_id):
    coach = Coach.query.get_or_404(coach_id)

    sport = request.form.get("sport")
    date_str = request.form.get("date")
    time_slot = request.form.get("time")
    message = request.form.get("message")
    location = request.form.get("location")

    if not date_str or not time_slot:
        flash("Please select a valid date and time.", "danger")
        return redirect(url_for("coach_detail", slug=coach.slug))

    try:
        # Convert String to Date Object
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # 1. SECURITY CHECK: Is the date in the past?
        today = datetime.now().date()
        if date_obj < today:
            flash("You cannot book a session in the past.", "danger")
            return redirect(url_for("coach_detail", slug=coach.slug))
            
        # 2. SECURITY CHECK: Is the time passed (if booking for today)?
        if date_obj == today:
            # Convert "09:00 AM" to 24-hour integer (e.g., 9)
            time_obj = datetime.strptime(time_slot, "%I:%M %p").time()
            now_time = datetime.now().time()
            
            if time_obj < now_time:
                flash("That time slot has already passed for today.", "danger")
                return redirect(url_for("coach_detail", slug=coach.slug))

    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for("coach_detail", slug=coach.slug))

    new_booking = Booking(
        coach_id=coach.id,
        user_id=current_user.id,
        sport=sport,
        booking_date=date_obj,
        booking_time=time_slot,
        message=message,
        location=location,
        status="Confirmed",
    )

    db.session.add(new_booking)
    db.session.commit()

    flash(f"Session booked successfully with Coach {coach.name}!", "success")
    return redirect(url_for("coach_dashboard"))
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("coach_dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "hirer")  # Default to 'hirer'
        org_type = request.form.get("org_type", "individual")  # 'individual' or 'organization'

        # Logic: If they are a hirer and selected 'organization', set flag True
        is_org = False
        if role == "hirer" and org_type == "organization":
            is_org = True

        if not name or not email or not password:
            flash("Fill all fields.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("Email taken.", "danger")
        else:
            user = User(name=name, email=email, role=role, is_organization=is_org)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash(f"Welcome, {name}!", "success")

            if role == "coach":
                return redirect(url_for("coach_dashboard"))
            else:
                # Redirect Hirers to Plans page first to upsell, or Dashboard
                if is_org:
                    return redirect(url_for("plans"))  # Send organizations to pricing immediately
                return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("coach_dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            if user.role == "coach":
                return redirect(url_for("coach_dashboard"))
            else:
                return redirect(url_for("home"))
        else:
            flash("Invalid credentials.", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/send_otp", methods=["POST"])
@login_required
def send_otp():
    try:
        otp = "".join(random.choices(string.digits, k=6))
        session["verification_otp"] = otp
        msg = Message("Verify your Game Changer Account", recipients=[current_user.email])
        msg.body = (
            f"Hello {current_user.name},\n\n"
            f"Your Verification OTP is: {otp}\n\n"
            "Do not share this with anyone."
        )
        mail.send(msg)
        return {"status": "success", "message": "OTP sent to " + current_user.email}
    except Exception as e:
        print(e)
        return {"status": "error", "message": "Failed to send email. Check app config."}


@app.route("/verify/coach", methods=["POST"])
@login_required
def verify_coach():
    user_code = request.form.get("code")
    stored_otp = session.get("verification_otp")
    if stored_otp and user_code == stored_otp:
        if current_user.coach_profile:
            current_user.coach_profile.is_verified = True
            db.session.commit()
            session.pop("verification_otp", None)
            flash("Success! You are now a Verified Coach.", "success")
        else:
            flash("Please create a coach profile first.", "warning")
    else:
        flash("Invalid OTP. Please try again.", "danger")
    return redirect(url_for("coach_dashboard"))


@app.route("/dashboard", methods=["GET", "POST"])  # Universal Dashboard Link
@login_required
def coach_dashboard():
    # If user is a coach, show coach profile management
    coach = current_user.coach_profile

    my_bookings = (
        Booking.query.filter_by(user_id=current_user.id)
        .order_by(Booking.booking_date.desc())
        .all()
    )

    received_bookings = []
    if coach:
        received_bookings = (
            Booking.query.filter_by(coach_id=coach.id)
            .order_by(Booking.booking_date.desc())
            .all()
        )

    context = {
        "coach": coach,
        "sports_list": SPORTS_LIST,
        "my_bookings": my_bookings,
        "received_bookings": received_bookings,
    }

    if request.method == "POST":
        if current_user.role != "coach":
            flash("Only coaches can update profile settings.", "danger")
            return redirect(url_for("coach_dashboard"))

        name = request.form.get("name", "").strip()
        tagline = request.form.get("tagline", "").strip()
        achievements = request.form.get("achievements", "").strip()
        specialties = request.form.get("specialties", "").strip()
        pincode = request.form.get("pincode", "").strip()
        state = request.form.get("state", "").strip()
        city = request.form.get("city", "").strip()
        exp_raw = request.form.get("experience_years", "").strip()
        age_raw = request.form.get("age", "").strip()
        phone = request.form.get("phone", "").strip()

        try:
            exp = int(exp_raw) if exp_raw else 0
            age = int(age_raw) if age_raw else 0
        except ValueError:
            flash("Age/Experience must be numbers.", "danger")
            return render_template("dashboard_coach.html", **context)

        selected_sports = request.form.getlist("sports")
        prices_dict = {}
        for sport in selected_sports:
            price_input = request.form.get(f"price_{sport}")
            if price_input:
                try:
                    prices_dict[sport] = int(price_input)
                except ValueError:
                    prices_dict[sport] = 0

        sports_str = ",".join(selected_sports)
        prices_json = json.dumps(prices_dict)
        starting_price = min(prices_dict.values()) if prices_dict else 0

        if not name or not city or not selected_sports:
            flash("Name, City and at least one Sport are required.", "danger")
            return render_template("dashboard_coach.html", **context)

        image_filename = coach.profile_image if coach else "default_coach.jpg"
        if "profile_image" in request.files:
            file = request.files["profile_image"]
            if file and file.filename != "" and allowed_file(file.filename):
                ext = file.filename.rsplit(".", 1)[1].lower()
                new_filename = secure_filename(
                    f"coach_{current_user.id}_{int(datetime.now().timestamp())}.{ext}"
                )
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], new_filename))
                image_filename = new_filename

        if coach is None:
            slug = create_slug(name, sports_str)
            coach = Coach(
                user_id=current_user.id,
                slug=slug,
                name=name,
                sport=sports_str,
                sports_prices=prices_json,
                city=city,
                state=state,
                pincode=pincode,
                price_per_session=starting_price,
                experience_years=exp,
                age=age,
                phone=phone,
                tagline=tagline,
                specialties=specialties,
                profile_image=image_filename,
                achievements=achievements,
            )
            db.session.add(coach)
        else:
            coach.name = name
            coach.sport = sports_str
            coach.sports_prices = prices_json
            coach.city = city
            coach.state = state
            coach.pincode = pincode
            coach.price_per_session = starting_price
            coach.experience_years = exp
            coach.age = age
            coach.phone = phone
            coach.tagline = tagline
            coach.specialties = specialties
            coach.profile_image = image_filename
            coach.achievements = achievements

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("coach_dashboard"))

    return render_template("dashboard_coach.html", **context)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)