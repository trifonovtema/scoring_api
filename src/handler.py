from src.scoring_requests import (
    MethodRequest,
    OnlineScoreRequest,
    ClientsInterestsRequest,
)
from src.scoring import get_score, get_interests
from src.settings import Responses


ONLINE_SCORE_REQUIRED_PAIRS = [
    ("phone", "email"),
    ("first_name", "last_name"),
    ("gender", "birthday"),
]


def method_handler(request, ctx, store):
    body = request.get("body", None)
    if body is None or body == {}:
        return (
            Responses.ERRORS[Responses.INVALID_REQUEST] + ": Request body is empty",
            Responses.INVALID_REQUEST,
        )

    method_request = MethodRequest(**body)
    if not method_request.check_auth():
        return Responses.ERRORS[Responses.FORBIDDEN], Responses.FORBIDDEN

    if not method_request.is_valid():
        return (
            Responses.ERRORS[Responses.INVALID_REQUEST]
            + ": "
            + ", ".join(method_request.errors),
            Responses.INVALID_REQUEST,
        )

    match method_request.method:
        case "online_score":
            return online_score_handler(method_request, ctx, store)
        case "clients_interests":
            return clients_interests_handler(method_request, ctx, store)
        case _:
            return (
                Responses.ERRORS[Responses.INVALID_REQUEST] + ": Wrong method",
                Responses.INVALID_REQUEST,
            )


def clients_interests_handler(request: MethodRequest, ctx, store):
    client_interests_request = ClientsInterestsRequest(**request.arguments)

    if not client_interests_request.is_valid():
        return (
            Responses.ERRORS[Responses.INVALID_REQUEST]
            + ": "
            + ", ".join(client_interests_request.errors),
            Responses.INVALID_REQUEST,
        )

    res = {}
    ctx["nclients"] = 0

    for cid in client_interests_request.client_ids:
        res[cid] = get_interests(store=store, cid=cid)
        ctx["nclients"] += 1
    return res, Responses.OK


def online_score_handler(request: MethodRequest, ctx, store):
    online_score_request = OnlineScoreRequest(**request.arguments)
    if not online_score_request.is_valid():
        return (
            Responses.ERRORS[Responses.INVALID_REQUEST]
            + ": "
            + ", ".join(online_score_request.errors),
            Responses.INVALID_REQUEST,
        )

    ctx["has"] = []

    for field, value in request.arguments.items():
        if value is not None:
            ctx["has"].append(field)

    if not any(
        all(arg in ctx["has"] for arg in pair) for pair in ONLINE_SCORE_REQUIRED_PAIRS
    ):
        return (
            Responses.ERRORS[Responses.INVALID_REQUEST]
            + ": At least one pair (phone-email, first name-last name, gender-birthday) must have values",
            Responses.INVALID_REQUEST,
        )

    if request.is_admin:
        return {"score": 42}, Responses.OK

    return {
        "score": get_score(
            store=store,
            online_score_request=online_score_request,
        )
    }, Responses.OK
