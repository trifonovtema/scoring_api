import hashlib
import json
from src.scoring_requests import OnlineScoreRequest


def get_score(
    store,
    online_score_request: OnlineScoreRequest,
) -> float:
    key_parts = [
        online_score_request.first_name or "",
        online_score_request.last_name or "",
        online_score_request.phone or "",
        (
            online_score_request.birthday.strftime("%Y%m%d")
            if online_score_request.birthday
            else ""
        ),
    ]
    key = "uid:" + hashlib.md5("".join(key_parts).encode("utf-8")).hexdigest()

    # Try to get from cache
    score = store.cache_get(key)
    if score is not None:
        return float(score)

    # Calculate score
    score = 0.0
    if online_score_request.phone:
        score += 1.5
    if online_score_request.email:
        score += 1.5
    if online_score_request.birthday and online_score_request.gender is not None:
        score += 1.5
    if online_score_request.first_name and online_score_request.last_name:
        score += 0.5

    # Cache the score for 60 minutes
    store.cache_set(key, score, 60 * 60)
    return score


def get_interests(store, cid: str) -> list:
    r = store.get(f"i:{cid}")
    return json.loads(r) if r else []
