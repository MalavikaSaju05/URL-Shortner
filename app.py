from flask import Flask, render_template, request, redirect

from models import db, URL

import random
import string

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# Generate random short code
def generate_short_code():

    characters = string.ascii_letters + string.digits

    while True:

        short_code = ''.join(
            random.choice(characters)
            for _ in range(6)
        )

        # Ensure uniqueness
        existing_url = URL.query.filter_by(
            short_code=short_code
        ).first()

        if not existing_url:
            return short_code


# Homepage
@app.route('/', methods=['GET', 'POST'])

def home():

    short_url = None

    if request.method == 'POST':

        original_url = request.form['url']

        # Check if URL already exists
        existing_url = URL.query.filter_by(
            original_url=original_url
        ).first()

        # If already exists, reuse short code
        if existing_url:

            short_code = existing_url.short_code

        else:

            short_code = generate_short_code()

            new_url = URL(
                original_url=original_url,
                short_code=short_code
            )

            db.session.add(new_url)

            db.session.commit()

        short_url = request.host_url + short_code

    return render_template(
        'index.html',
        short_url=short_url
    )


# Redirect Route
@app.route('/<short_code>')

def redirect_url(short_code):

    if short_code == "favicon.ico":
        return ""

    url = URL.query.filter_by(
        short_code=short_code
    ).first()

    if url:

        # Increase click count
        url.clicks += 1

        db.session.commit()

        return redirect(url.original_url)

    return "URL not found"


# Analytics Dashboard
@app.route('/dashboard')

def dashboard():

    urls = URL.query.order_by(
        URL.clicks.desc()
    ).all()

    total_clicks = sum(
        url.clicks for url in urls
    )

    total_urls = len(urls)

    return render_template(
        'dashboard.html',
        urls=urls,
        total_clicks=total_clicks,
        total_urls=total_urls
    )


# Run Flask App
if __name__ == "__main__":

    app.run(debug=True)
    