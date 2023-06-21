from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    scenes = db.relationship('Scene', backref='movie', lazy=True)

class Scene(db.Model):
    __tablename__ = 'scenes'

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    scene_description = db.Column(db.Text, nullable=False)
    speaker_name = db.Column(db.String(256), nullable=False)
    foreground_image_prompt = db.Column(db.Text, nullable=False)
    background_image_prompt = db.Column(db.Text, nullable=False)
    foreground_image_url = db.Column(db.String(256), nullable=True)
    background_image_url = db.Column(db.String(256), nullable=True)
    audio_url = db.Column(db.String(256), nullable=True)
    duration = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
