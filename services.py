import aiohttp
from config import CURRENCY_API_KEY

# ======= For fiat currencies (USD, EUR, etc.) to IRR
async def get_fiat_rate(from_currency):
    url = f"https://api.currencyapi.com/v3/latest?base_currency={from_currency.upper()}&currencies=IRR"
    headers = {"apikey": CURRENCY_API_KEY}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            try:
                return data["data"]["IRR"]["value"]
            except Exception as e:
                print("Fiat API error:", data)
                return None


# ======= For crypto to toman (via CoinGecko + USD rate)
async def get_crypto_rate(crypto):
    crypto_map = {
        "usdt": "tether",
        "trx": "tron"
    }

    crypto_id = crypto_map.get(crypto)
    if not crypto_id:
        return None

    async with aiohttp.ClientSession() as session:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
        async with session.get(url) as resp:
            data = await resp.json()
            try:
                price_in_usd = data[crypto_id]["usd"]
            except Exception as e:
                print("Crypto API error:", data)
                return None

    usd_to_irr = await get_fiat_rate("usd")
    if not usd_to_irr:
        return None

    return price_in_usd * usd_to_irr


# ======= For crypto <-> fiat (usd, eur, gbp)
async def get_crypto_to_fiat(crypto, fiat):
    crypto_map = {
        "usdt": "tether",
        "trx": "tron"
    }

    crypto_id = crypto_map.get(crypto)
    fiat = fiat.lower()

    if not crypto_id or fiat not in ["usd", "eur", "gbp"]:
        return None

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={fiat}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            try:
                return data[crypto_id][fiat]
            except Exception as e:
                print("Crypto to Fiat API error:", data)
                return None
