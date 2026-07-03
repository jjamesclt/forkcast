from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table for meal <-> tags
meal_tags = db.Table(
    "meal_tags",
    db.Column("meal_id", db.Integer, db.ForeignKey("meals.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)


class Meal(db.Model):
    __tablename__ = "meals"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    meal_type = db.Column(db.String(50), default="other")
    notes = db.Column(db.Text, default="")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tags = db.relationship("Tag", secondary=meal_tags, backref="meals", lazy="selectin")


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class MealSession(db.Model):
    __tablename__ = "meal_sessions"
    id = db.Column(db.Integer, primary_key=True)
    session_date = db.Column(db.Date, default=date.today)
    meal_period = db.Column(db.String(20), default="dinner")
    status = db.Column(db.String(20), default="open")  # open, selected, canceled
    selected_meal_id = db.Column(db.Integer, db.ForeignKey("meals.id"), nullable=True)
    selected_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    selected_meal = db.relationship("Meal", foreign_keys=[selected_meal_id])
    selected_by = db.relationship("User", foreign_keys=[selected_by_user_id])


class Vote(db.Model):
    __tablename__ = "votes"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("meal_sessions.id"), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey("meals.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # vote or veto

    session = db.relationship("MealSession", backref="votes")
    meal = db.relationship("Meal")
    user = db.relationship("User")


class MealHistory(db.Model):
    __tablename__ = "meal_history"
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey("meals.id"), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("meal_sessions.id"), nullable=True)
    eaten_date = db.Column(db.Date, default=date.today)
    meal_period = db.Column(db.String(20), default="dinner")
    selected_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    actually_eaten = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    meal = db.relationship("Meal")
    selected_by = db.relationship("User")
    session = db.relationship("MealSession")
