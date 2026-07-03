import requests as http_requests
from flask import Blueprint, request, jsonify
from config import Config
from models import Meal, Tag

llm_bp = Blueprint("llm", __name__)


def _get_llm_config():
    config = Config()
    if not config.llm_enabled:
        return None
    return config


def _call_llm(prompt):
    """Call the configured LLM and return the response text."""
    config = _get_llm_config()
    if not config:
        return None

    if config.LLM_TYPE == "ollama":
        url = f"http://{config.LLM_URL}:{config.LLM_PORT}/api/generate"
        payload = {
            "model": config.LLM_MODEL,
            "prompt": prompt,
            "stream": False,
        }
        try:
            resp = http_requests.post(url, json=payload, timeout=60)
            resp.raise_for_status()
            return resp.json().get("response", "")
        except Exception as e:
            return f"LLM error: {e}"

    elif config.LLM_TYPE == "chatgpt":
        url = f"{config.LLM_URL}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {config.LLM_APIKEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config.LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            resp = http_requests.post(url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"LLM error: {e}"

    return None


@llm_bp.route("/suggest", methods=["POST"])
def suggest():
    """Ask the LLM to suggest meals from the database based on user input."""
    config = _get_llm_config()
    if not config:
        return jsonify({"error": "LLM not configured"}), 400

    user_input = request.json.get("query", "")
    if not user_input:
        return jsonify({"error": "No query provided"}), 400

    # Build context from database
    meals = Meal.query.filter_by(active=True).all()
    meal_list = "\n".join(
        f"- {m.name} (type: {m.meal_type}, tags: {', '.join(t.name for t in m.tags)})"
        for m in meals
    )

    prompt = f"""You are a meal suggestion assistant. Based on the user's request, suggest meals from the following database. Only suggest meals that exist in the list.

Available meals:
{meal_list}

User request: "{user_input}"

Respond with a short list of suggested meal names and a brief reason for each. Keep it concise."""

    response = _call_llm(prompt)
    if response is None:
        return jsonify({"error": "LLM call failed"}), 500

    return jsonify({"suggestions": response})


@llm_bp.route("/suggest-tags", methods=["POST"])
def suggest_tags():
    """Ask the LLM to suggest tags for a meal."""
    config = _get_llm_config()
    if not config:
        return jsonify({"error": "LLM not configured"}), 400

    meal_name = request.json.get("meal_name", "")
    meal_description = request.json.get("description", "")

    existing_tags = [t.name for t in Tag.query.all()]

    prompt = f"""You are a meal tagging assistant. Suggest relevant tags for this meal.

Meal: {meal_name}
Description: {meal_description}

Existing tags in the system: {', '.join(existing_tags)}

Suggest 3-6 tags. Prefer existing tags when they fit. You may suggest new tags if needed.
Respond with only a comma-separated list of tag names, nothing else."""

    response = _call_llm(prompt)
    if response is None:
        return jsonify({"error": "LLM call failed"}), 500

    return jsonify({"tags": response})
