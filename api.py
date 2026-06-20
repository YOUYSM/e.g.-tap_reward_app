"""
api.py
Flask backend: HTTP endpoints jo Kivy app (main.py) call karega.
"""

from flask import Flask, request, jsonify
import database

app = Flask(__name__)
database.init_db()


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    phone = data.get("phone", "").strip()

    if not phone:
        return jsonify({"success": False, "message": "Phone number required"}), 400

    user = database.create_user(phone)
    if user is None:
        return jsonify({"success": False, "message": "Phone already registered"}), 409

    return jsonify({"success": True, "user": user}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    phone = data.get("phone", "").strip()

    if not phone:
        return jsonify({"success": False, "message": "Phone number required"}), 400

    user = database.get_user_by_phone(phone)
    if user is None:
        return jsonify({"success": False, "message": "User not found, please signup"}), 404

    return jsonify({"success": True, "user": user}), 200


@app.route("/watch_ad", methods=["POST"])
def watch_ad():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"success": False, "message": "user_id required"}), 400

    new_points = database.add_points_for_ad(user_id)
    if new_points is None:
        return jsonify({"success": False, "message": "User not found"}), 404

    return jsonify({
        "success": True,
        "points_earned": database.POINTS_PER_AD,
        "total_points": new_points
    }), 200


@app.route("/balance/<int:user_id>", methods=["GET"])
def balance(user_id):
    user = database.get_user_by_id(user_id)
    if user is None:
        return jsonify({"success": False, "message": "User not found"}), 404

    ads_watched = database.get_ad_view_count(user_id)

    return jsonify({
        "success": True,
        "phone": user["phone"],
        "points": user["points"],
        "ads_watched": ads_watched
    }), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
