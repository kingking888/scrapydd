import functools
from .models import User, UserKey, session_scope
from six.moves.urllib.parse import urlsplit, urlencode
from six.moves.urllib_parse import urlparse
from tornado.web import HTTPError
from tornado.httpclient import HTTPRequest
import logging
import hmac
import hashlib

logger = logging.getLogger(__name__)

try:
    from urllib.parse import parse_qs, quote
except ImportError:
    from urlparse import parse_qs
    from urllib import quote


def generate_digest(secret, method, path, query, body):
    parsed_query = parse_qs(query, keep_blank_values=True)

    canonical_query = []

    for key in sorted(parsed_query.keys()):
        for value in sorted(parsed_query[key]):
            canonical_query.append("=".join((key, quote(value))))

    return hmac.new(
        secret.encode("utf-8"),
        "\n".join((method, path, "&".join(canonical_query), "")).encode("utf-8") +
        body,
        hashlib.sha256).hexdigest()


def signin_view(func):
    pass


def authentication_check(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        assert self.request.uri is not None
                        next_url = self.request.uri
                    url += "?" + urlencode(dict(next=next_url))
                self.redirect(url)
                return None
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper


class AuthenticationProvider(object):
    def get_user(self, handler):
        raise NotImplementedError()


class NoAuthenticationProvider(object):
    def get_user(self, handler):
        return 'admin'


class CookieAuthenticationProvider(object):
    def get_user(self, handler):
        user_cookie = handler.get_secure_cookie("user")
        if user_cookie:
            #return json.loads(user_cookie)
            return user_cookie
        return None


class HmacAuthorize(object):
    def get_user(self, handler):
        authorization = handler.request.headers.get("Authorization", "").split(" ")
        if len(authorization) != 3:
            logging.info("Invalid Authorization header {}".format(authorization))
            return None

        algorithm, key, provided_digest = authorization
        if algorithm != "HMAC":
            logging.info("Invalid algorithm {}".format(algorithm))
            return None

        with session_scope() as session:
            user_key = session.query(UserKey).filter_by(app_key=key).first()

            if user_key is None:
                logging.info("Invalid HMAC key {}".format(key))
                return None
            secret = user_key.app_secret
            expected_digest = generate_digest(
                secret, handler.request.method, handler.request.path, handler.request.query,
                handler.request.body)

            if not hmac.compare_digest(expected_digest, provided_digest):
                logging.info("Invalid HMAC digest {}".format(provided_digest))
                return None

            return user_key.user.username


def authenticated_request(*args, **kwargs):
    app_key = kwargs.pop("app_key")
    app_secret = kwargs.pop("app_secret")

    if len(args) > 0:
        url = args[0]
    elif "url" in kwargs:
        url = kwargs["url"]
    else:
        raise TypeError("Missing argument: 'url'")

    parsed_url = urlparse(url)

    path = parsed_url.path
    query = parsed_url.query

    body = kwargs.get("body", "")
    if isinstance(body, str):
        body = body.encode("utf-8")

    digest = generate_digest(app_secret, kwargs.get("method", "GET"), path, query, body)

    headers = kwargs.get("headers", {})
    headers["Authorization"] = "HMAC {} {}".format(app_key, digest)
    kwargs["headers"] = headers

    return HTTPRequest(*args, **kwargs)

