import csv
import io
import json
import logging
import math
import os
import re
import uuid

from flask import Flask, jsonify, make_response, render_template, request

from app.database.db import get_campaign_run, list_campaign_runs, save_campaign_run
from app.database.export import FIELDS
from app.errors import safe_provider_error
from app.personalization.gemini import get_client
from main import CAMPAIGN, run_analysis

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/run")
def run_pipeline():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"success": False, "error": "Send campaign settings as a JSON object."}), 400

    try:
        target = int(payload.get("target", 20))
        min_subs = int(payload.get("min_subs", 5000))
        max_subs = int(payload.get("max_subs", 100000))
        min_engagement = float(payload.get("min_engagement", 0.5))
    except (TypeError, ValueError, OverflowError):
        return jsonify({"success": False, "error": "Target and audience limits must be whole numbers; engagement must be numeric."}), 422

    campaign = payload.get("campaign", CAMPAIGN)
    queries_input = payload.get("queries")
    personalize = payload.get("personalize", True)
    review_log = payload.get("review_log", True)
    if not isinstance(personalize, bool) or not isinstance(review_log, bool):
        return jsonify({"success": False, "error": "Personalization and review-log options must be true or false."}), 422
    if not isinstance(campaign, str) or not campaign.strip() or len(campaign) > 1200:
        return jsonify({"success": False, "error": "Add a campaign brief between 1 and 1,200 characters."}), 422
    if not isinstance(queries_input, list) or not all(isinstance(query, str) for query in queries_input):
        return jsonify({"success": False, "error": "Search phrases must be provided as a list of text values."}), 422

    queries = list(dict.fromkeys(query.strip() for query in queries_input if query.strip()))
    if not 1 <= len(queries) <= 10 or any(len(query) > 100 for query in queries):
        return jsonify({"success": False, "error": "Choose between 1 and 10 search phrases, each no longer than 100 characters."}), 422
    stop_words = {
        "a", "an", "and", "are", "as", "at", "by", "for", "from", "in",
        "into", "is", "it", "of", "on", "or", "the", "to", "with", "your",
    }
    if any(
        not any(
            len(token) >= 2 and token.casefold() not in stop_words
            for token in re.findall(r"[\w+#.-]+", query)
        )
        for query in queries
    ):
        return jsonify({"success": False, "error": "Each search phrase needs a meaningful topic or creator niche."}), 422
    if not 5 <= target <= 100:
        return jsonify({"success": False, "error": "The creator target must be between 5 and 100."}), 422
    if min_subs < 0 or max_subs < 1 or max_subs > 100_000_000 or min_subs > max_subs:
        return jsonify({"success": False, "error": "Audience limits must be positive and the minimum cannot exceed the maximum."}), 422
    if not math.isfinite(min_engagement) or not 0 <= min_engagement <= 100:
        return jsonify({"success": False, "error": "Minimum engagement must be between 0 and 100 percent."}), 422

    result = run_analysis(
        target=target,
        personalize=personalize,
        simulate_send=review_log,
        campaign=campaign.strip(),
        queries=queries,
        min_subs=min_subs,
        max_subs=max_subs,
        min_engagement=min_engagement,
    )
    if not result["success"]:
        return jsonify(result), 502

    run_id = uuid.uuid4().hex
    try:
        save_campaign_run(run_id, result)
    except Exception:
        logger.exception("Could not save campaign snapshot")
        return jsonify({
            "success": False,
            "error": "The research completed but the campaign snapshot could not be saved.",
        }), 500

    result["run_id"] = run_id
    return jsonify(result)


@app.post("/api/suggest-searches")
def suggest_searches():
    payload = request.get_json(silent=True)
    brief = payload.get("campaign") if isinstance(payload, dict) else None
    if not isinstance(brief, str) or not brief.strip() or len(brief) > 1200:
        return jsonify({"error": "Enter a campaign brief between 1 and 1,200 characters first."}), 422

    try:
        client = get_client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                "Suggest 6 concise YouTube creator-discovery search phrases for this "
                "campaign. Focus on creator niches, subject areas, and content formats "
                "that would plausibly reach its intended audience. Do not invent product "
                "claims, brands, audience demographics, or partnership terms. Return "
                "only a JSON array of strings, no markdown.\n\n"
                f"Campaign brief:\n{brief.strip()}"
            ),
        )
        text = (response.text or "").strip()
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
        suggestions = json.loads(text)
        if not isinstance(suggestions, list):
            raise ValueError("The suggestion model did not return a JSON list.")
        phrases = list(dict.fromkeys(
            " ".join(item.split())
            for item in suggestions
            if isinstance(item, str) and item.strip() and len(item.strip()) <= 80
        ))
        if not 1 <= len(phrases) <= 8:
            raise ValueError("The suggestion model returned an unexpected number of search phrases.")
        return jsonify({"queries": phrases})
    except Exception as exc:
        logger.warning("Search phrase suggestions failed (%s)", type(exc).__name__)
        return jsonify({"error": safe_provider_error(exc, provider="Gemini")}), 502


@app.get("/api/history")
def campaign_history():
    return jsonify({"campaigns": list_campaign_runs()})


@app.get("/api/history/<run_id>")
def campaign_snapshot(run_id: str):
    result = get_campaign_run(run_id)
    if result is None:
        return jsonify({"error": "Campaign snapshot not found."}), 404
    result["run_id"] = run_id
    return jsonify(result)


@app.get("/api/history/<run_id>/export.csv")
def export_campaign(run_id: str):
    result = get_campaign_run(run_id)
    if result is None:
        return jsonify({"error": "Campaign snapshot not found."}), 404

    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(result["creators"])
    response = make_response("\ufeff" + output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f'attachment; filename="fieldnotes-{run_id[:8]}.csv"'
    return response


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
