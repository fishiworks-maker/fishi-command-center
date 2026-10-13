"""Minimal authorized, read-only Reddit API client."""
import base64
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class RedditAPIError(RuntimeError):
    pass


def _request(url, *, method="GET", headers=None, data=None, retries=2):
    for attempt in range(retries + 1):
        req = Request(url, data=data, method=method, headers=headers or {})
        try:
            with urlopen(req, timeout=25) as response:
                return json.load(response)
        except HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < retries:
                wait = exc.headers.get("Retry-After")
                time.sleep(min(60, max(1, int(wait))) if wait and wait.isdigit() else 2 ** attempt)
                continue
            raise RedditAPIError(f"Reddit API returned HTTP {exc.code}; check approval and credentials") from exc
        except URLError as exc:
            raise RedditAPIError(f"Network error: {exc.reason}") from exc


def get_app_token(client_id, client_secret, user_agent):
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    payload = _request(
        "https://www.reddit.com/api/v1/access_token",
        method="POST",
        headers={"Authorization": f"Basic {basic}", "User-Agent": user_agent,
                 "Content-Type": "application/x-www-form-urlencoded"},
        data=urlencode({"grant_type": "client_credentials"}).encode(),
    )
    if not payload.get("access_token"):
        raise RedditAPIError("No access token returned; verify authorized app configuration")
    return payload["access_token"]


def get_user_submissions(username, token, user_agent, limit=100):
    url = f"https://oauth.reddit.com/user/{username}/submitted?{urlencode({'limit': min(limit, 100), 'raw_json': 1})}"
    payload = _request(url, headers={"Authorization": f"Bearer {token}", "User-Agent": user_agent})
    return [child["data"] for child in payload.get("data", {}).get("children", [])]
