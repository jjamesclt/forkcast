from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Meal, Tag

meals_bp = Blueprint("meals", __name__)

MEAL_TYPES = [
    "home-cooked",
    "takeout",
    "restaurant",
    "leftovers",
    "frozen-easy",
    "snack-dinner",
    "other",
]


@meals_bp.route("/")
def list_meals():
    meals = Meal.query.order_by(Meal.name).all()
    return render_template("meals/list.html", meals=meals)


@meals_bp.route("/add", methods=["GET", "POST"])
def add_meal():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            return redirect(url_for("meals.add_meal"))

        meal = Meal(
            name=name,
            description=request.form.get("description", "").strip(),
            meal_type=request.form.get("meal_type", "other"),
            notes=request.form.get("notes", "").strip(),
            active="active" in request.form,
        )
        db.session.add(meal)

        # Handle tags
        tag_str = request.form.get("tags", "")
        for tag_name in [t.strip().lower() for t in tag_str.split(",") if t.strip()]:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                db.session.flush()
            meal.tags.append(tag)

        db.session.commit()
        return redirect(url_for("meals.list_meals"))

    tags = Tag.query.order_by(Tag.name).all()
    return render_template("meals/add.html", meal_types=MEAL_TYPES, tags=tags)


@meals_bp.route("/edit/<int:meal_id>", methods=["GET", "POST"])
def edit_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)

    if request.method == "POST":
        meal.name = request.form.get("name", meal.name).strip()
        meal.description = request.form.get("description", "").strip()
        meal.meal_type = request.form.get("meal_type", "other")
        meal.notes = request.form.get("notes", "").strip()
        meal.active = "active" in request.form

        # Update tags
        meal.tags.clear()
        tag_str = request.form.get("tags", "")
        for tag_name in [t.strip().lower() for t in tag_str.split(",") if t.strip()]:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            meal.tags.append(tag)

        db.session.commit()
        return redirect(url_for("meals.list_meals"))

    tags = Tag.query.order_by(Tag.name).all()
    return render_template("meals/edit.html", meal=meal, meal_types=MEAL_TYPES, tags=tags)


@meals_bp.route("/toggle/<int:meal_id>", methods=["POST"])
def toggle_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    meal.active = not meal.active
    db.session.commit()
    return redirect(url_for("meals.list_meals"))
