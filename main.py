import argparse
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


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--target", type=int, default=60)
    p.add_argument("--personalize", action="store_true")
    p.add_argument("--simulate-send", action="store_true")
    args = p.parse_args()
    run(args.target, args.personalize, args.simulate_send)
