from app import app, db, User, Coach
from werkzeug.security import generate_password_hash
from slugify import slugify
import json
import random

# Default password for everyone: 'password'
# Hash it once to use for all
DEFAULT_PASS_HASH = generate_password_hash('password')

def seed():
    with app.app_context():
        print("🌱 cleaning old data (optional)...")
        # db.drop_all() # Uncomment if you want to wipe everything clean first
        # db.create_all()

        print("🌱 Seeding Students...")
        students = [
            ("Aravind S", "aravind@student.com", "Mumbai"),
            ("Sneha P", "sneha@student.com", "Delhi"),
            ("Rahul K", "rahul@student.com", "Bangalore"),
            ("Pooja M", "pooja@student.com", "Pune"),
            ("Karan J", "karan@student.com", "Chennai")
        ]
        
        for name, email, city in students:
            if not User.query.filter_by(email=email).first():
                user = User(
                    name=name, email=email, city=city, 
                    role='hirer', is_organization=False, 
                    password_hash=DEFAULT_PASS_HASH
                )
                db.session.add(user)
        db.session.commit()

        print("🌱 Seeding Academies/Recruiters...")
        academies = [
            ("Mumbai Cricket Assoc", "mca@academy.com", "Mumbai"),
            ("Delhi Sports Club", "dsc@academy.com", "Delhi"),
            ("Bangalore Football FC", "bfc@academy.com", "Bangalore"),
            ("Pune Tennis Center", "ptc@academy.com", "Pune"),
            ("Chennai Super Kings Acad", "csk@academy.com", "Chennai")
        ]

        for name, email, city in academies:
            if not User.query.filter_by(email=email).first():
                user = User(
                    name=name, email=email, city=city, 
                    role='hirer', is_organization=True, # <--- The Key Flag
                    password_hash=DEFAULT_PASS_HASH
                )
                db.session.add(user)
        db.session.commit()

        print("🌱 Seeding Coaches...")
        coaches_data = [
            {
                "name": "Vikram Rathour", "email": "vikram@coach.com", "city": "Mumbai", "sport": "Cricket",
                "price": 2000, "tagline": "Batting technique specialist.", "radius": 15
            },
            {
                "name": "Saina Nehwal Pro", "email": "saina@coach.com", "city": "Hyderabad", "sport": "Badminton",
                "price": 3000, "tagline": "Olympic level badminton training.", "radius": 0
            },
            {
                "name": "Baichung Bhutia", "email": "baichung@coach.com", "city": "Kolkata", "sport": "Football",
                "price": 1500, "tagline": "Striker training and agility.", "radius": 20
            },
            {
                "name": "Mary Kom Acad", "email": "mary@coach.com", "city": "Imphal", "sport": "Boxing",
                "price": 1000, "tagline": "Mental toughness and boxing fundamentals.", "radius": 5
            },
            {
                "name": "Gagan Narang", "email": "gagan@coach.com", "city": "Pune", "sport": "Shooting",
                "price": 2500, "tagline": "Precision and focus training.", "radius": 0
            }
        ]

        for c in coaches_data:
            if not User.query.filter_by(email=c['email']).first():
                # 1. Create User
                user = User(
                    name=c['name'], email=c['email'], city=c['city'],
                    role='coach', is_organization=False,
                    password_hash=DEFAULT_PASS_HASH
                )
                db.session.add(user)
                db.session.commit() # Commit to get ID

                # 2. Create Coach Profile
                slug = slugify(f"{c['name']}-{c['sport']}")
                prices = json.dumps({c['sport']: c['price']})
                
                coach = Coach(
                    user_id=user.id,
                    slug=slug,
                    name=c['name'],
                    sport=c['sport'],
                    sports_prices=prices,
                    city=c['city'],
                    state="India",
                    price_per_session=c['price'],
                    experience_years=random.randint(5, 20),
                    tagline=c['tagline'],
                    travel_radius=c['radius'],
                    rating=round(random.uniform(4.0, 5.0), 1),
                    is_verified=True
                )
                db.session.add(coach)
        
        db.session.commit()
        print("✅ Done! Login with any email and password: 'password'")

if __name__ == "__main__":
    seed()