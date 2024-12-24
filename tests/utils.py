import hashlib
import datetime


def set_valid_auth(request):
    from src.settings import SecuritySettings

    if request.get("login") == SecuritySettings.ADMIN_LOGIN:
        request["token"] = hashlib.sha512(
            (
                datetime.datetime.now().strftime("%Y%m%d%H")
                + SecuritySettings.ADMIN_SALT
            ).encode("utf-8")
        ).hexdigest()
    else:
        msg = (
            request.get("account", "")
            + request.get("login", "")
            + SecuritySettings.SALT
        ).encode("utf-8")
        request["token"] = hashlib.sha512(msg).hexdigest()


def get_response(request, headers, context, settings):
    from src import handler

    return handler.method_handler(
        {"body": request, "headers": headers}, context, settings
    )
