

import os
from dotenv import load_dotenv
from flask import Blueprint, jsonify, redirect, request, session
import requests
from app.models import ActivityMetaData, GithubActivity, ValueColMetaData
from app.routes.utils import get_activities
from app.services.utils import add_activities_df_to_db
from yd_extractor.github import process_repo_contributions


load_dotenv(override=True)

# GitHub OAuth credentials
GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")

github_bp = Blueprint("github", __name__ )

# Authenticate user.
@github_bp.route("/auth", methods=["GET"])
def github_login():
    # TODO: USE GITHUB APPS INSTEAD. THEY BE GIVING US TOO MUCH ACCESS WITH OAUTH!!
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=repo,user"
    return redirect(github_auth_url)

# Step 2: GitHub OAuth Callback
@github_bp.route("/callback", methods=["GET"])
def github_callback():
    code = request.args.get("code")
    if not code:
        return "Error: Missing code", 400

    # Exchange code for access token
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code
    }

    response = requests.post(token_url, headers=headers, json=data)
    token_data = response.json()

    if "access_token" not in token_data:
        return "Error: Could not get access token", 400

    access_token = token_data["access_token"]
    session["github_token"] = access_token  # Store in session

    return "Success: Successfully authenticated with github.", 200


@github_bp.route("/<int:year>", methods=["POST"])
def retrieve_github_activity(year: int):
    try:
        github_token = session["github_token"]
        if github_token is None:
            raise Exception("Error no github token found!")
    except:
        return jsonify({"error": "Authenticate first!"}), 401
    df = process_repo_contributions(github_token ,year)
    output = add_activities_df_to_db(df, GithubActivity)
    return jsonify(output), 201


@github_bp.route("/<int:year>", methods=["GET"])
def get_workout_activities(year: int):
    return get_activities(
        year=year,
        model=GithubActivity,
        metadata=ActivityMetaData(
            date_col="date",
            filter_cols=["repository_name"],
            value_cols=[
                ValueColMetaData(
                    col="total_commits",
                    units="commits"
                )
            ]
        )
    )