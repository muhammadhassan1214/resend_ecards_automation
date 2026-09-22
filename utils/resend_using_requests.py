import requests

url = "https://ecards.heart.org/SearchAllECards/ReSendECard"
REQUEST_TIMEOUT = 30


def get_cookie_header(driver):
    """Return the browser's current cookies in HTTP Cookie-header format."""
    return "; ".join(
        f"{cookie['name']}={cookie['value']}"
        for cookie in driver.get_cookies()
    )


def create_authenticated_session(driver):
    """Create a reusable requests session from the driver's current cookies."""
    session = requests.Session()
    for cookie in driver.get_cookies():
        session.cookies.set(
            cookie["name"],
            cookie["value"],
            domain=cookie.get("domain"),
            path=cookie.get("path", "/")
        )

    session.headers.update({
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://ecards.heart.org",
        "priority": "u=1, i",
        "referer": "https://ecards.heart.org/SearchAllECards",
        "request-context": "appId=cid-v1:5841778e-bd8d-489d-a816-1bf42e19ede2",
        "request-id": "|xCpJX.ApRqd",
        "sec-ch-ua": '"Google Chrome";v="153", "Not_A Brand";v="8", "Chromium";v="153"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/153.0.0.0 Safari/537.36"
        ),
        "x-requested-with": "XMLHttpRequest",
    })
    return session


def resend_ecard(session, ecard_data):
    """Resend an eCard using a reusable authenticated requests session."""

    data = {
        "ECardUId": ecard_data.get("ECardUId"),
        "StudentId": ecard_data.get("StudentId"),
        "EmailAddress": ecard_data.get("EmailAddress"),
        "Url": "/SearchAllECards/ReSendECard",
        "Action": "email",
        "CanSaveEmail": "false",
        "CanSavePhone": "false",
    }

    return session.post(url, data=data, timeout=REQUEST_TIMEOUT)
