from flask import Flask, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import hashlib
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class URLMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<URLMapping(original_url={self.original_url}, short_url={self.short_url})>"

@app.before_request
def create_tables():
    db.create_all()

def generate_short_url():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(6))

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    original_url = data.get('original_url')
    
    if not original_url:
        return jsonify({'error': 'Missing original URL'}), 400
    
    short_url = generate_short_url()
    new_url = URLMapping(original_url=original_url, short_url=short_url)
    db.session.add(new_url)
    db.session.commit()
    
    return jsonify({'short_url': f'http://localhost:5000/{short_url}'}), 201

@app.route('/<short_url>')
def redirect_to_url(short_url):
    url_mapping = URLMapping.query.filter_by(short_url=short_url).first()
    if url_mapping:
        return redirect(url_mapping.original_url)
    return jsonify({'error': 'URL not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
