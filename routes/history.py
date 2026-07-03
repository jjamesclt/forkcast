from flask import Blueprint, render_template, request, redirect, url_for
from models import db, MealHistory

history_bp = Blueprint("history", __name__)


@history_bp.route("/")
def list_history():
    history = (
        MealHistory.query.order_by(MealHistory.eaten_date.desc()).limit(50).all()
    )
    return render_template("history/list.html", history=history)


@history_bp.route("/toggle-eaten/<int:history_id>", methods=["POST"])
def toggle_eaten(history_id):
    entry = MealHistory.query.get_or_404(history_id)
    entry.actually_eaten = not entry.actually_eaten
    db.session.commit()
    return redirect(url_for("history.list_history"))
