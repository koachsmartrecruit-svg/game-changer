# Game-Changer

Game-Changer is a full-stack sports coaching marketplace where athletes and parents can discover coaches, book training sessions, and track progress, while coaches manage their clients, schedules, and payments from one place.

## What this app does (non-technical)

- For athletes and parents
  - Browse coaches across multiple sports by city, skill level, and price.
  - View rich coach profiles with bios, experience, and reviews before booking.
  - Book 1:1 sessions, group classes, or packages and pay securely online.
  - Track upcoming sessions and see post-session notes and goals.

- For coaches
  - Create a professional coaching profile to showcase skills and experience.
  - Define offerings (session types, duration, pricing, location/online).
  - Manage bookings and availability from a single dashboard.
  - Keep a training history and notes for each athlete.

- For platform/admin
  - View usage metrics (users, coaches, bookings).
  - Feature or verify selected coaches.
  - Handle support requests and refunds/edge cases.

## Tech stack

- Backend: Flask (Python) web framework
- Frontend: Jinja templates, HTML, CSS, Bootstrap, vanilla JavaScript
- Database: Relational DB via SQLAlchemy (e.g., Postgres/MySQL/SQLite)
- Auth: Email/password (and optionally social login)
- Payments: Stripe (or similar) for secure payments and packages

## Main features

- Coach discovery
  - Filter coaches by sport, location, skill level, and price range.
  - Coach profile pages with bio, experience, photos, and reviews.

- Booking & scheduling
  - Pick dates and time slots from coach availability.
  - Confirm and pay for a session or multi-session package.
  - See your upcoming sessions in a simple dashboard.

- Training management
  - Coaches add notes after each session (what was done, key feedback, homework).
  - Athletes/parents can review progress over time.

- Reviews & ratings
  - Athletes can rate and review coaches after sessions.
  - Ratings help new users choose the right coach faster.

## Folder structure (typical)

- `app.py` – main Flask application and route definitions
- `templates/` – HTML templates (home, coach list, coach detail, dashboards)
- `static/` – CSS, JS, images, and frontend assets
- `models.py` or inline models – database models for User, Coach, Athlete, Session, Booking, Review, etc.
- `requirements.txt` – Python dependencies

## Getting started

1. Clone the repository:
   ```bash
   git clone https://github.com/koachsmartrecruit-svg/game-changer.git
   cd game-changer
