from app.services.analyzer import analyze_payload


def test_analyze_payload_detects_cta_and_positive_reaction():
    comments = [
        {"text": "Очень полезно, спасибо!"},
        {"text": "Круто, как это настроить?"},
        {"text": "Огонь!"},
    ]
    result = analyze_payload(
        caption="Сохрани и подпишись, чтобы не потерять. Как выйти на новый уровень в Reels?",
        likes=120,
        comments_count=15,
        views=1000,
        comments=comments,
    )

    assert result.cta_detected is True
    assert result.transfer_score >= 6
    assert result.audience_reaction["positive_comments"] >= 2
    assert result.engagement_rate > 0


def test_analyze_payload_uses_proxy_er_when_views_missing():
    result = analyze_payload(
        caption="Тестовый пост без просмотров.",
        likes=100,
        comments_count=20,
        views=0,
        comments=[{"text": "Класс!"}],
    )

    assert result.engagement_rate_by_views == 0.0
    assert result.engagement_rate_proxy > 0.0
    assert result.engagement_rate_proxy <= 100.0
    assert result.engagement_basis == "comments_proxy"
    assert result.engagement_rate == result.engagement_rate_proxy
