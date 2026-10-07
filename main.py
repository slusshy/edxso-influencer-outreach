import argparse
<<<<<<< HEAD
import hashlib
import logging
import sys

from app.errors import safe_provider_error

QUERIES = ["AI tools", "machine learning", "generative AI", "LLM tutorials", "AI automation", "Python AI"]
CAMPAIGN = "A paid/affiliate collaboration for an AI productivity SaaS that helps professionals automate repetitive workflows."
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
logger = logging.getLogger(__name__)


def _safe_error_message(error: Exception) -> str:
    return safe_provider_error(error, provider="Project API")


def run(
    target: int,
    personalize: bool,
    simulate_send: bool,
    campaign: str = CAMPAIGN,
    queries: list[str] | None = None,
    min_subs: int = 5000,
    max_subs: int = 100000,
    min_engagement: float = 0.5,
):
    from app.discovery.youtube import discover_multiple_queries
    from app.enrichment.metrics import enrich_engagement
    from app.enrichment.contact import enrich_contact
    from app.filtering.qualification import classify_and_filter
    from app.database.export import export_csv
    from app.database.export_outreach import export_outreach_tracker
    from app.outreach.email_sender import send_or_simulate

    search_queries = queries or QUERIES
    creators = discover_multiple_queries(search_queries, target=target)
    print(f"Discovered {len(creators)} unique creators")
    creators = enrich_engagement(creators, recent_videos=5)
    creators = enrich_contact(creators)
    creators = classify_and_filter(
        creators,
        min_subs=min_subs,
        max_subs=max_subs,
        min_engagement=min_engagement,
        relevance_terms=search_queries,
    )
    if personalize:
        from app.personalization.gemini import personalize_qualified

        creators = personalize_qualified(creators, campaign)

    qualified = [c for c in creators if c.get("status") == "Qualified"]
    print(f"Qualified {len(qualified)} / {len(creators)}")
    campaign_id = hashlib.sha256(campaign.strip().casefold().encode("utf-8")).hexdigest()[:20]
    if simulate_send:
        for c in qualified:
            c["send_status"] = send_or_simulate(
                c,
                campaign_id,
                "Creator partnership opportunity",
                dry_run=True,
            )
    export_csv(creators)
    export_outreach_tracker()
    print("Saved dataset to data/influencers.csv")
    return {
        "discovered": len(creators),
        "qualified": len(qualified),
        "total": len(creators),
        "campaign": campaign,
        "creators": creators,
    }


def run_analysis(
    target: int = 20,
    personalize: bool = True,
    simulate_send: bool = True,
    campaign: str = CAMPAIGN,
    queries: list[str] | None = None,
    min_subs: int = 5000,
    max_subs: int = 100000,
    min_engagement: float = 0.5,
):
    sys.stdout.flush()
    sys.stderr.flush()
    try:
        result = run(
            target=target,
            personalize=personalize,
            simulate_send=simulate_send,
            campaign=campaign,
            queries=queries,
            min_subs=min_subs,
            max_subs=max_subs,
            min_engagement=min_engagement,
        )
        return {
            "success": True,
            "summary": {
                "discovered": result["discovered"],
                "qualified": result["qualified"],
                "campaign": result["campaign"],
                "target": target,
                "search_phrases": queries or QUERIES,
                "min_subs": min_subs,
                "max_subs": max_subs,
                "min_engagement": min_engagement,
                "personalize": personalize,
            },
            "creators": result["creators"],
        }
    except Exception as exc:
        logger.error("Creator research pipeline failed (%s)", type(exc).__name__)
        return {
            "success": False,
            "error": _safe_error_message(exc),
            "summary": {
                "discovered": 0,
                "qualified": 0,
                "campaign": campaign,
            },
            "creators": [],
        }
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
=======
from app.discovery.youtube import discover_multiple_queries
from app.enrichment.metrics import enrich_engagement
from app.enrichment.contact import enrich_contact
from app.filtering.qualification import classify_and_filter
from app.personalization.gemini import personalize_qualified
from app.database.export import export_csv
from app.outreach.email_sender import send_or_simulate

QUERIES = ["AI tools", "machine learning", "generative AI", "LLM tutorials", "AI automation", "Python AI"]
CAMPAIGN = "A paid/affiliate collaboration for an AI productivity SaaS that helps professionals automate repetitive workflows."


def run(target: int, personalize: bool, simulate_send: bool):


    creators = discover_multiple_queries(QUERIES, target=target)
    print(f"Discovered {len(creators)} unique creators")
    creators = enrich_engagement(creators, recent_videos=5)
    creators = enrich_contact(creators)
    creators = classify_and_filter(creators)
    if personalize:
        creators = personalize_qualified(creators, CAMPAIGN)
    export_csv(creators)

    qualified = [c for c in creators if c.get("status") == "Qualified"]
    print(f"Qualified {len(qualified)} / {len(creators)}")
    if simulate_send:
        for c in qualified:
            c["send_status"] = send_or_simulate(c, "edxso-ai-productivity-001", "AI productivity collaboration", dry_run=True)
    print("Saved dataset to data/influencers.csv")
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--target", type=int, default=60)
    p.add_argument("--personalize", action="store_true")
    p.add_argument("--simulate-send", action="store_true")
    args = p.parse_args()
    run(args.target, args.personalize, args.simulate_send)
