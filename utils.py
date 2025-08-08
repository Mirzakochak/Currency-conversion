import re

def fa_to_en(num_str: str):
    fa_digits = "??????????"
    for i, d in enumerate(fa_digits):
        num_str = num_str.replace(d, str(i))
    return num_str

def extract_amount_and_currency(text):
    text = fa_to_en(text.lower())
    match = re.search(r"(\d[\d,\.]*)\s*(toman|rial|usd|eur|gbp|try|aed|usdt|trx|dollar|euro|pound|lira|dirham|tether|tron)", text)
    if not match:
        return None, None
    amount = float(match.group(1).replace(',', ''))
    currency = match.group(2)
    mapping = {
        'toman': 'toman', 'rial': 'rial',
        'usd': 'usd', 'dollar': 'usd',
        'eur': 'eur', 'euro': 'eur',
        'gbp': 'gbp', 'pound': 'gbp',
        'try': 'try', 'lira': 'try',
        'aed': 'aed', 'dirham': 'aed',
        'usdt': 'usdt', 'tether': 'usdt',
        'trx': 'trx', 'tron': 'trx'
    }
    return amount, mapping.get(currency)
