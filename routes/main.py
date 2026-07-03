from datetime import date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, User, Meal, Tag, MealSession, Vote, MealHistory

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    users = User.query.filter_by(active=True).all()
    current_user_id = session.get("current_user_id")
    current_user = User.query.get(current_user_id) if current_user_id else None

    # Get or create today's dinner session
    today = date.today()
    meal_session = MealSession.query.filter_by(
        session_date=today, meal_period="dinner", status="open"
    ).first()

    tags = Tag.query.order_by(Tag.name).all()
    selected_tags = request.args.getlist("tags")

    # Get active meals, optionally filtered by tags
    meals_query = Meal.query.filter_by(active=True)
    if selected_tags:
        meals_query = meals_query.filter(
            Meal.tags.any(Tag.name.in_(selected_tags))
        )
    meals = meals_query.order_by(Meal.name).all()

    # Get votes for current session
    votes = {}
    if meal_session:
        for vote in Vote.query.filter_by(session_id=meal_session.id).all():
            key = (vote.meal_id, vote.user_id)
            votes[key] = vote.vote_type

    # Get vetoed meal IDs for current session
    vetoed_meal_ids = set()
    if meal_session:
        vetoed = Vote.query.filter_by(session_id=meal_session.id, vote_type="veto").all()
        vetoed_meal_ids = {v.meal_id for v in vetoed}

    # Calculate recency for de-preferencing
    recency = {}
    for meal in meals:
        last_eaten = (
            MealHistory.query.filter_by(meal_id=meal.id, actually_eaten=True)
            .order_by(MealHistory.eaten_date.desc())
            .first()
        )
        if last_eaten:
            days_ago = (today - last_eaten.eaten_date).days
            recency[meal.id] = days_ago

    # Score meals for ranking
    meal_scores = []
    for meal in meals:
        score = 0
        days_ago = recency.get(meal.id)

        # De-preference recently eaten
        if days_ago is not None:
            if days_ago <= 1:
                score -= 30
            elif days_ago <= 3:
                score -= 20
            elif days_ago <= 7:
                score -= 10

        # Add votes, subtract vetoes
        if meal_session:
            for user in users:
                key = (meal.id, user.id)
                if key in votes:
                    if votes[key] == "vote":
                        score += 10
                    elif votes[key] == "veto":
                        score -= 100

        meal_scores.append((meal, score, days_ago))

    # Sort by score descending
    meal_scores.sort(key=lambda x: x[1], reverse=True)

    return render_template(
        "index.html",
        users=users,
        current_user=current_user,
        meal_session=meal_session,
        tags=tags,
        selected_tags=selected_tags,
        meal_scores=meal_scores,
        votes=votes,
        vetoed_meal_ids=vetoed_meal_ids,
    )


@main_bp.route("/set-user", methods=["POST"])
def set_user():
    user_id = request.form.get("user_id")
    if user_id:
        session["current_user_id"] = int(user_id)
    return redirect(url_for("main.index"))


@main_bp.route("/start-session", methods=["POST"])
def start_session():
    today = date.today()
    existing = MealSession.query.filter_by(
        session_date=today, meal_period="dinner", status="open"
    ).first()
    if not existing:
        new_session = MealSession(session_date=today, meal_period="dinner", status="open")
        db.session.add(new_session)
        db.session.commit()
    return redirect(url_for("main.index"))


@main_bp.route("/vote", methods=["POST"])
def vote():
    user_id = session.get("current_user_id")
    meal_id = request.form.get("meal_id")
    vote_type = request.form.get("vote_type")
    session_id = request.form.get("session_id")

    if not all([user_id, meal_id, vote_type, session_id]):
        return redirect(url_for("main.index"))

    # Remove existing vote for this user/meal/session
    Vote.query.filter_by(
        session_id=int(session_id), meal_id=int(meal_id), user_id=int(user_id)
    ).delete()

    new_vote = Vote(
        session_id=int(session_id),
        meal_id=int(meal_id),
        user_id=int(user_id),
        vote_type=vote_type,
    )
    db.session.add(new_vote)
    db.session.commit()

    # Preserve tag filters
    tags = request.form.get("selected_tags", "")
    tag_params = "&".join(f"tags={t}" for t in tags.split(",") if t)
    return redirect(url_for("main.index") + (f"?{tag_params}" if tag_params else ""))


@main_bp.route("/select-meal", methods=["POST"])
def select_meal():
    user_id = session.get("current_user_id")
    meal_id = request.form.get("meal_id")
    session_id = request.form.get("session_id")

    if not all([user_id, meal_id, session_id]):
        return redirect(url_for("main.index"))

    meal_session = MealSession.query.get(int(session_id))
    if meal_session and meal_session.status == "open":
        meal_session.status = "selected"
        meal_session.selected_meal_id = int(meal_id)
        meal_session.selected_by_user_id = int(user_id)

        # Record in history
        history = MealHistory(
            meal_id=int(meal_id),
            session_id=meal_session.id,
            eaten_date=meal_session.session_date,
            meal_period=meal_session.meal_period,
            selected_by_user_id=int(user_id),
            actually_eaten=True,
        )
        db.session.add(history)
        db.session.commit()

    return redirect(url_for("main.index"))
