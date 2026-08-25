from app.filtering.qualification import classify_and_filter

def test_qualifies_good_ai_creator():
    c = {"channel_name":"AI Builder", "description":"AI tools and machine learning", "recent_content":[], "subscribers":20000, "engagement_rate":2.0}
    assert classify_and_filter([c])[0]["status"] == "Qualified"

def test_rejects_large_creator():
    c = {"channel_name":"AI Builder", "description":"AI tools", "recent_content":[], "subscribers":200000, "engagement_rate":2.0}
    assert classify_and_filter([c])[0]["status"] == "Rejected"
