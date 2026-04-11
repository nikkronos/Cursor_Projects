"""
Backend для виджета «Лимиты» — пачка лимитных заявок через T-Invest API.
Токен: TINKOFF_INVEST_TOKEN. SANDBOX=1 — песочница.
Счёт: всегда первый из GetAccounts.
"""
import logging
import os
import time
import uuid
from flask import Flask, jsonify, request, send_from_directory
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== Конфигурация ==========
API_URL_PROD = "https://invest-public-api.tbank.ru/rest"
API_URL_SANDBOX = "https://sandbox-invest-public-api.tbank.ru/rest"
ORDERBOOK_CACHE_TTL = 10  # секунд
INSTRUMENTS_CACHE_TTL = 300  # 5 минут
POST_ORDER_DELAY = 0.5  # пауза между заявками (сек), чтобы не превысить лимит API

_cache = {}
_cache_lock = __import__("threading").Lock()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def _load_env_from_file():
    for path in ["env_vars.txt", ".env", "../env_vars.txt", "../../Main_docs/env_vars.txt"]:
        try:
            full_path = os.path.join(os.path.dirname(__file__), path)
            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, _, value = line.partition("=")
                            key, value = key.strip(), value.strip()
                            if key and value and not os.environ.get(key):
                                os.environ[key] = value
                                logger.info("Loaded %s from %s", key, path)
        except Exception as e:
            logger.debug("Could not read %s: %s", path, e)


_load_env_from_file()

app = Flask(__name__, static_folder="static", static_url_path="")


def _get_api_url():
    use_sandbox = os.environ.get("SANDBOX", "1").strip().lower() in ("1", "true", "yes")
    return API_URL_SANDBOX if use_sandbox else API_URL_PROD


def _get_headers():
    token = os.environ.get("TINKOFF_INVEST_TOKEN", "").strip()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _quotation_to_float(q) -> float:
    if not q:
        return 0.0
    units = int(q.get("units", 0) or 0)
    nano = int(q.get("nano", 0) or 0)
    return units + nano / 1e9


def _float_to_quotation(price: float) -> dict:
    """Цена (float) в формат API Quotation: units (string), nano (int)."""
    if price < 0:
        price = 0.0
    units = int(price)
    nano = int(round((price - units) * 1e9))
    if nano >= 1e9:
        nano = 0
        units += 1
    return {"units": str(units), "nano": nano}


def _cache_get(key):
    with _cache_lock:
        item = _cache.get(key)
        if item is None:
            return None
        value, expires_at = item
        if time.time() > expires_at:
            del _cache[key]
            return None
        return value


def _cache_set(key, value, ttl_seconds):
    with _cache_lock:
        _cache[key] = (value, time.time() + ttl_seconds)


# ========== API T-Invest ==========

def _get_first_account_id():
    """Вернуть ID первого счёта или None."""
    cache_key = "first_account_id"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    base_url = _get_api_url()
    headers = _get_headers()
    try:
        url = f"{base_url}/tinkoff.public.invest.api.contract.v1.UsersService/GetAccounts"
        resp = requests.post(url, headers=headers, json={}, timeout=15, verify=False)
        resp.raise_for_status()
        data = resp.json()
        accounts = data.get("accounts", [])
        if not accounts:
            return None
        first_id = accounts[0].get("id", "")
        _cache_set(cache_key, first_id, 60)
        return first_id
    except Exception as e:
        logger.warning("GetAccounts: %s", e)
        return None


def _load_instruments():
    """Список инструментов: акции + фьючерсы. Кэш 5 мин."""
    cache_key = "instruments_all"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    base_url = _get_api_url()
    headers = _get_headers()
    items = []
    # Shares
    try:
        url = f"{base_url}/tinkoff.public.invest.api.contract.v1.InstrumentsService/Shares"
        resp = requests.post(url, headers=headers, json={}, timeout=30, verify=False)
        resp.raise_for_status()
        data = resp.json()
        for inv in data.get("instruments", []):
            status = inv.get("tradingStatus", "")
            if status and status != "SECURITY_TRADING_STATUS_TRADING":
                continue
            items.append({
                "figi": inv.get("figi", ""),
                "ticker": inv.get("ticker", ""),
                "name": inv.get("name") or inv.get("ticker", ""),
                "instrument_uid": inv.get("uid", "") or inv.get("figi", ""),
                "instrument_type": "share",
                "lot": int(inv.get("lot", 1) or 1),
            })
    except Exception as e:
        logger.warning("Shares: %s", e)
    # Futures
    try:
        url = f"{base_url}/tinkoff.public.invest.api.contract.v1.InstrumentsService/Futures"
        resp = requests.post(url, headers=headers, json={}, timeout=30, verify=False)
        resp.raise_for_status()
        data = resp.json()
        for inv in data.get("instruments", []):
            items.append({
                "figi": inv.get("figi", ""),
                "ticker": inv.get("ticker", ""),
                "name": inv.get("name") or inv.get("ticker", ""),
                "instrument_uid": inv.get("uid", "") or inv.get("figi", ""),
                "instrument_type": "futures",
                "lot": int(inv.get("lot", 1) or 1),
            })
    except Exception as e:
        logger.warning("Futures: %s", e)
    _cache_set(cache_key, items, INSTRUMENTS_CACHE_TTL)
    logger.info("instruments loaded: %d", len(items))
    return items


def _get_orderbook(instrument_id):
    """Стакан по инструменту. Кэш 10 сек."""
    cache_key = f"orderbook_{instrument_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    base_url = _get_api_url()
    headers = _get_headers()
    try:
        url = f"{base_url}/tinkoff.public.invest.api.contract.v1.MarketDataService/GetOrderBook"
        resp = requests.post(
            url, headers=headers,
            json={"instrumentId": instrument_id, "depth": 10},
            timeout=15, verify=False
        )
        resp.raise_for_status()
        data = resp.json()
        bids = data.get("bids", [])
        asks = data.get("asks", [])
        best_bid = _quotation_to_float(bids[0].get("price")) if bids else None
        best_ask = _quotation_to_float(asks[0].get("price")) if asks else None
        last_price = _quotation_to_float(data.get("lastPrice"))
        # Текущая цена для расчёта уровней: last или середина спреда
        if last_price and last_price > 0:
            current_price = last_price
        elif best_bid and best_ask:
            current_price = (best_bid + best_ask) / 2
        else:
            current_price = best_bid or best_ask
        result = {
            "instrument_id": instrument_id,
            "current_price": round(current_price, 4) if current_price else None,
            "best_bid": round(best_bid, 4) if best_bid else None,
            "best_ask": round(best_ask, 4) if best_ask else None,
            "last_price": round(last_price, 4) if last_price else None,
        }
        _cache_set(cache_key, result, ORDERBOOK_CACHE_TTL)
        return result
    except Exception as e:
        logger.warning("GetOrderBook %s: %s", instrument_id, e)
        return {"instrument_id": instrument_id, "error": str(e)}


def _post_order(account_id, instrument_id, direction, price_float, quantity_lots):
    """Выставить одну лимитную заявку. direction: ORDER_DIRECTION_BUY / ORDER_DIRECTION_SELL."""
    base_url = _get_api_url()
    headers = _get_headers()
    url = f"{base_url}/tinkoff.public.invest.api.contract.v1.OrdersService/PostOrder"
    payload = {
        "accountId": account_id,
        "instrumentId": instrument_id,
        "quantity": str(int(quantity_lots)),
        "price": _float_to_quotation(price_float),
        "direction": direction,
        "orderType": "ORDER_TYPE_LIMIT",
        "orderId": str(uuid.uuid4()),
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15, verify=False)
        data = resp.json() if resp.content else {}
        if resp.status_code != 200:
            return {"ok": False, "status": resp.status_code, "message": data.get("message") or resp.text}
        return {"ok": True, "orderId": data.get("orderId"), "data": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ========== Маршруты ==========

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/accounts")
def api_accounts():
    """Первый счёт (для подстановки в заявки)."""
    token = os.environ.get("TINKOFF_INVEST_TOKEN", "").strip()
    if not token:
        return jsonify({"error": "TINKOFF_INVEST_TOKEN not set"}), 503
    account_id = _get_first_account_id()
    if not account_id:
        return jsonify({"error": "No accounts"}), 503
    return jsonify({"accountId": account_id})


@app.route("/api/instruments")
def api_instruments():
    """Список инструментов (акции + фьючерсы) для поиска."""
    token = os.environ.get("TINKOFF_INVEST_TOKEN", "").strip()
    if not token:
        return jsonify({"error": "TINKOFF_INVEST_TOKEN not set"}), 503
    items = _load_instruments()
    return jsonify({"instruments": items})


@app.route("/api/orderbook")
def api_orderbook():
    """Текущая цена по инструменту (кэш 10 сек)."""
    token = os.environ.get("TINKOFF_INVEST_TOKEN", "").strip()
    if not token:
        return jsonify({"error": "TINKOFF_INVEST_TOKEN not set"}), 503
    instrument_id = request.args.get("instrument_id", "").strip()
    if not instrument_id:
        return jsonify({"error": "instrument_id required"}), 400
    result = _get_orderbook(instrument_id)
    if result.get("error"):
        return jsonify(result), 502
    return jsonify(result)


@app.route("/api/orders/limit-batch", methods=["POST"])
def api_orders_limit_batch():
    """
    Выставить пачку лимитных заявок.
    Body: instrument_id, direction ("buy" | "sell"), total_rub, count, step_pct.
    instrument_id — uid или figi. lot берётся из кэша инструментов.
    """
    token = os.environ.get("TINKOFF_INVEST_TOKEN", "").strip()
    if not token:
        return jsonify({"error": "TINKOFF_INVEST_TOKEN not set"}), 503
    account_id = _get_first_account_id()
    if not account_id:
        return jsonify({"error": "No accounts"}), 503

    data = request.get_json() or {}
    instrument_id = (data.get("instrument_id") or "").strip()
    direction = (data.get("direction") or "").strip().lower()
    total_rub = float(data.get("total_rub") or 0)
    count = int(data.get("count") or 0)
    step_pct = float(data.get("step_pct") or 0)

    if not instrument_id:
        return jsonify({"error": "instrument_id required"}), 400
    if direction not in ("buy", "sell"):
        return jsonify({"error": "direction must be buy or sell"}), 400
    if total_rub <= 0 or count <= 0 or step_pct <= 0:
        return jsonify({"error": "total_rub, count, step_pct must be positive"}), 400

    # Текущая цена и лот
    ob = _get_orderbook(instrument_id)
    if ob.get("error"):
        return jsonify({"error": "orderbook: " + ob.get("error", "")}), 502
    current_price = ob.get("current_price")
    if not current_price or current_price <= 0:
        return jsonify({"error": "No current price for instrument"}), 400

    instruments = _load_instruments()
    inv = next((i for i in instruments if i.get("instrument_uid") == instrument_id or i.get("figi") == instrument_id), None)
    lot_size = int(inv.get("lot", 1)) if inv else 1

    rub_per_order = total_rub / count
    direction_api = "ORDER_DIRECTION_BUY" if direction == "buy" else "ORDER_DIRECTION_SELL"
    results = []

    for i in range(count):
        pct = step_pct * (i + 1)
        if direction == "buy":
            price = current_price * (1 - pct / 100.0)
        else:
            price = current_price * (1 + pct / 100.0)
        if price <= 0:
            results.append({"index": i + 1, "ok": False, "error": "price <= 0"})
            continue
        # Лотов на заявку: рубли / (цена за единицу * единиц в лоте) = рубли / (price * lot_size)
        quantity_lots = int(rub_per_order / (price * lot_size))
        if quantity_lots <= 0:
            results.append({"index": i + 1, "ok": False, "error": "quantity_lots is 0"})
            continue
        time.sleep(POST_ORDER_DELAY)
        r = _post_order(account_id, instrument_id, direction_api, price, quantity_lots)
        r["index"] = i + 1
        r["price"] = round(price, 4)
        r["quantity_lots"] = quantity_lots
        results.append(r)

    return jsonify({"results": results})


def main():
    port = int(os.environ.get("PORT", "5000"))
    sandbox = "sandbox" if os.environ.get("SANDBOX", "1").strip().lower() in ("1", "true", "yes") else "prod"
    logger.info("Starting Limits server port=%s mode=%s", port, sandbox)
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
