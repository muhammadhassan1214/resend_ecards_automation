import requests

url = "https://ecards.heart.org/SearchAllECards/ReSendECard"


def get_cookie_header(driver):
    """Return the browser's current cookies in HTTP Cookie-header format."""
    return "; ".join(
        f"{cookie['name']}={cookie['value']}"
        for cookie in driver.get_cookies()
    )


def resend_ecard(driver, ecard_data, cookie=None):
    """Resend an eCard using the driver's current authenticated cookies."""
    cookie = cookie or get_cookie_header(driver)

    data = {
        "ECardUId": ecard_data.get("ECardUId"),
        "StudentId": ecard_data.get("StudentId"),
        "EmailAddress": ecard_data.get("EmailAddress"),
        "Url": "/SearchAllECards/ReSendECard",
        "Action": "email",
        "CanSaveEmail": "false",
        "CanSavePhone": "false"
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://ecards.heart.org',
        'priority': 'u=1, i',
        'referer': 'https://ecards.heart.org/SearchAllECards',
        'request-context': 'appId=cid-v1:5841778e-bd8d-489d-a816-1bf42e19ede2',
        'request-id': '|xCpJX.ApRqd',
        'sec-ch-ua': '"Google Chrome";v="153", "Not_A Brand";v="8", "Chromium";v="153"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'Cookie': cookie
    }

    response = requests.post(url, headers=headers, data=data)
    return response
