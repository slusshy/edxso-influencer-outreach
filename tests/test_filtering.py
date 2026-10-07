from app.filtering.qualification import classify_and_filter

def test_qualifies_good_ai_creator():
    c = {"channel_name":"AI Builder", "description":"AI tools and machine learning", "recent_content":[], "subscribers":20000, "engagement_rate":2.0}
    assert classify_and_filter([c])[0]["status"] == "Qualified"

def test_rejects_large_creator():
    c = {"channel_name":"AI Builder", "description":"AI tools", "recent_content":[], "subscribers":200000, "engagement_rate":2.0}
    assert classify_and_filter([c])[0]["status"] == "Rejected"
<<<<<<< HEAD

def test_search_phrases_drive_topical_fit_for_non_ai_categories():
    creators = [{
        "channel_name": "Mina's Skincare Routine",
        "description": "Reviews skincare products and shares ingredient explainers.",
        "recent_content": ["A simple skincare routine"],
        "subscribers": 20000,
        "engagement_rate": 1.4,
    }]

    result = classify_and_filter(creators, relevance_terms=["skincare creators"])

    assert result[0]["status"] == "Qualified"
    assert result[0]["category"] == "Relevant to search"
    assert "skincare" in result[0]["content_themes"]

def test_topical_relevance_does_not_accept_substring_false_positive():
    creators = [{
        "channel_name": "Paid Creator Deals",
        "description": "Business and affiliate tips.",
        "recent_content": [],
        "subscribers": 20000,
        "engagement_rate": 1.4,
    }]

    result = classify_and_filter(creators, relevance_terms=["AI tools"])

    assert result[0]["status"] == "Rejected"
    assert "Insufficient relevance" in result[0]["filter_reason"]

def test_search_topic_and_each_guardrail_affect_qualification():
    creator = {
        "channel_name": "AI tool educator",
        "description": "Practical AI automation tutorials.",
        "recent_content": ["AI automation workflow"],
        "subscribers": 10000,
        "engagement_rate": 2.0,
    }
    assert classify_and_filter(
        [creator.copy()],
        min_subs=10000,
        max_subs=10000,
        min_engagement=2.0,
        relevance_terms=["AI automation"],
    )[0]["status"] == "Qualified"
    assert classify_and_filter(
        [creator.copy()],
        min_subs=10001,
        max_subs=20000,
        min_engagement=0,
        relevance_terms=["AI automation"],
    )[0]["status"] == "Rejected"
    assert classify_and_filter(
        [creator.copy()],
        min_subs=0,
        max_subs=20000,
        min_engagement=2.01,
        relevance_terms=["AI automation"],
    )[0]["status"] == "Rejected"
=======
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
