"""
api.py

Flask backend: this file creates HTTP endpoints that are used by
the Kivy app (main.py).

English Notes:
- Every endpoint uses functions from database.py.
  No direct SQL queries are written here.
- For simplicity, login does not use a password.
  Users can login/signup using only their phone number.
  (In a production app, OTP verification should be added.
  For now, this is kept simple.)

To run:
    python api.py

The server will start at:
    http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify
import database

app = Flask(__name__)

# Create database tables when the app starts
# (only if they do not already exist)
database.init_db()


@app.route("/signup", methods=["POST"])
def signup():
    """
    Creates a new user.

    Request body (JSON):
    {
        "phone": "9999999999"
    }
    """
    data = request.get_json(silent=True) or {}
    phone = data.get("phone", "").strip()

    if not phone:
        return jsonify({
            "success": False,
            "message": "Phone number required"
        }), 400

    user = database.create_user(phone)

    if user is None:
        return jsonify({
            "success": False,
            "message": "Phone already registered"
        }), 409

    return jsonify({
        "success": True,
        "user": user
    }), 201


@app.route("/login", methods=["POST"])
def login():
    """
    Logs in an existing user by checking only the phone number.

    Request body (JSON):
    {
        "phone": "9999999999"
    }
    """
    data = request.get_json(silent=True) or {}
    phone = data.get("phone", "").strip()

    if not phone:
        return jsonify({
            "success": False,
            "message": "Phone number required"
        }), 400

    user = database.get_user_by_phone(phone)

    if user is None:
        return jsonify({
            "success": False,
            "message": "User not found, please signup"
        }), 404

    return jsonify({
        "success": True,
        "user": user
    }), 200


@app.route("/watch_ad", methods=["POST"])
def watch_ad():
    """
    User watched an ad -> add reward points.

    Request body (JSON):
    {
        "user_id": 1
    }
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "user_id required"
        }), 400

    new_points = database.add_points_for_ad(user_id)

    if new_points is None:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    return jsonify({
        "success": True,
        "points_earned": database.POINTS_PER_AD,
        "total_points": new_points
    }), 200


@app.route("/balance/<int:user_id>", methods=["GET"])
def balance(user_id):
    """
    Returns the user's current points balance
    and total number of ads watched.
    """
    user = database.get_user_by_id(user_id)

    if user is None:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    ads_watched = database.get_ad_view_count(user_id)

    return jsonify({
        "success": True,
        "phone": user["phone"],
        "points": user["points"],
        "ads_watched": ads_watched
    }), 200


if __name__ == "__main__":
    # debug=True is fine for development.
    # In production, use debug=False.
    app.run(debug=True, host="0.0.0.0", port=5000)
