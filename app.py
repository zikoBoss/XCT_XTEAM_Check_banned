
from flask import Flask, request, Response
import requests
import json
import os

app = Flask(__name__)

# API جلب معلومات اللاعب الجديد
PLAYER_INFO_API = "https://mahir-info-api.vercel.app/info"

# API فحص حالة الحظر - سنحافظ عليه كما هو
BAN_CHECK_API = "https://ff.garena.com/api/antihack/check_banned"


def json_response(data, status_code=200):
    return Response(
        json.dumps(data, indent=4, ensure_ascii=False),
        status=status_code,
        mimetype="application/json"
    )


def get_player_info(player_id):
    try:
        response = requests.get(
            PLAYER_INFO_API,
            params={"uid": player_id},
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        basic_info = data.get("basicInfo") or {}

        return {
            "nickname": basic_info.get(
                "nickname", "Not available"
            ),
            "region": basic_info.get(
                "region", "Unknown"
            )
        }

    except Exception as e:
        print(f"[PLAYER INFO ERROR] {e}")

        return {
            "nickname": "Not available",
            "region": "Unknown"
        }


def check_banned(player_id):

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
        "Accept": "application/json",
        "referer": "https://ff.garena.com/en/support/",
        "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"
    }

    try:
        # أولاً: فحص حالة الحظر
        response = requests.get(
            BAN_CHECK_API,
            params={
                "lang": "en",
                "uid": player_id
            },
            headers=headers,
            timeout=15
        )

        if response.status_code != 200:
            return json_response({
                "status": "error",
                "message": "Failed to fetch ban status",
                "status_code": 500
            }, 500)

        data = response.json().get("data", {})

        is_banned = bool(data.get("is_banned", 0))

        ban_status = (
            "BANNED" if is_banned else "NOT BANNED"
        )

        # ثانياً: جلب الاسم والمنطقة من API الجديد
        player_info = get_player_info(player_id)

        result = {
            "status": ban_status,
            "uid": player_id,
            "nickname": player_info["nickname"],
            "region": player_info["region"],
            "account_status": ban_status,
            "is_banned": is_banned,
            "powered_by": "XcT-x-TeAm"
        }

        return json_response(result)

    except Exception as e:
        return json_response({
            "status": "exception",
            "error": str(e),
            "status_code": 500
        }, 500)


@app.route("/check", methods=["GET"])
def check():

    player_id = request.args.get("uid", "").strip()

    if not player_id:
        return json_response({
            "status": "error",
            "message": "uid is required",
            "status_code": 400
        }, 400)

    return check_banned(player_id)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
