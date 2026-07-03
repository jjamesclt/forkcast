from flask import Blueprint, redirect, url_for
from models import db, MealSession

sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.route("/cancel/<int:session_id>", methods=["POST"])
def cancel_session(session_id):
    meal_session = MealSession.query.get_or_404(session_id)
    meal_session.status = "canceled"
    db.session.commit()
    return redirect(url_for("main.index"))
