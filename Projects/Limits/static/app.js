(function () {
  const FAVORITES_KEY = "limits_favorites";
  const PRICE_INTERVAL_MS = 10000;

  let instruments = [];
  let selectedInstrument = null;
  let priceTimer = null;

  const el = {
    search: document.getElementById("search"),
    favOnly: document.getElementById("favOnly"),
    instruments: document.getElementById("instruments"),
    currentInstrument: document.getElementById("currentInstrument"),
    currentPrice: document.getElementById("currentPrice"),
    priceMeta: document.getElementById("priceMeta"),
    totalRub: document.getElementById("totalRub"),
    count: document.getElementById("count"),
    stepPct: document.getElementById("stepPct"),
    btnBuy: document.getElementById("btnBuy"),
    btnSell: document.getElementById("btnSell"),
    log: document.getElementById("log"),
  };

  function getFavorites() {
    try {
      const raw = localStorage.getItem(FAVORITES_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  function setFavorites(ids) {
    try {
      localStorage.setItem(FAVORITES_KEY, JSON.stringify(ids));
    } catch (e) {
      log("Ошибка сохранения избранного: " + e.message, "error");
    }
  }

  function toggleFavorite(uid) {
    const fav = getFavorites();
    const idx = fav.indexOf(uid);
    if (idx >= 0) fav.splice(idx, 1);
    else fav.push(uid);
    setFavorites(fav);
    renderInstruments();
  }

  function log(msg, type) {
    el.log.textContent = msg;
    el.log.className = "log" + (type ? " " + type : "");
  }

  function api(path, opts) {
    const url = path.startsWith("/") ? path : "/api/" + path;
    return fetch(url, opts).then((r) => {
      if (!r.ok) return r.json().then((j) => Promise.reject(j || { message: r.statusText }));
      return r.json();
    });
  }

  function loadInstruments() {
    return api("instruments").then((data) => {
      instruments = data.instruments || [];
      renderInstruments();
      return instruments;
    }).catch((err) => {
      log("Ошибка загрузки инструментов: " + (err.error || err.message || "network"), "error");
      instruments = [];
    });
  }

  function filterList() {
    const q = (el.search.value || "").trim().toLowerCase();
    const favOnly = el.favOnly.checked;
    const fav = getFavorites();
    return instruments.filter((i) => {
      if (favOnly && !fav.includes(i.instrument_uid)) return false;
      if (!q) return true;
      const ticker = (i.ticker || "").toLowerCase();
      const name = (i.name || "").toLowerCase();
      return ticker.includes(q) || name.includes(q);
    });
  }

  function renderInstruments() {
    const list = filterList();
    const fav = getFavorites();
    el.instruments.innerHTML = list.map((i) => {
      const star = fav.includes(i.instrument_uid) ? " ★" : "";
      return `<option value="${i.instrument_uid}" data-fig="${i.figi}">${i.ticker} — ${i.name}${star}</option>`;
    }).join("");
  }

  function selectInstrument(uid) {
    selectedInstrument = instruments.find((i) => i.instrument_uid === uid) || null;
    if (selectedInstrument) {
      el.currentInstrument.textContent = selectedInstrument.ticker + " — " + selectedInstrument.name;
      fetchPrice();
      startPriceTimer();
    } else {
      el.currentInstrument.textContent = "—";
      el.currentPrice.textContent = "—";
      stopPriceTimer();
    }
  }

  function fetchPrice() {
    if (!selectedInstrument) return;
    api("orderbook?instrument_id=" + encodeURIComponent(selectedInstrument.instrument_uid))
      .then((data) => {
        const p = data.current_price;
        el.currentPrice.textContent = p != null ? p.toLocaleString("ru-RU", { minimumFractionDigits: 2, maximumFractionDigits: 4 }) : "—";
        el.priceMeta.textContent = "Обновление раз в 10 сек";
      })
      .catch((err) => {
        el.currentPrice.textContent = "—";
        el.priceMeta.textContent = "Ошибка: " + (err.error || err.message || "network");
      });
  }

  function startPriceTimer() {
    stopPriceTimer();
    priceTimer = setInterval(fetchPrice, PRICE_INTERVAL_MS);
  }

  function stopPriceTimer() {
    if (priceTimer) {
      clearInterval(priceTimer);
      priceTimer = null;
    }
  }

  function placeBatch(direction) {
    if (!selectedInstrument) {
      log("Выберите инструмент", "error");
      return;
    }
    const totalRub = parseFloat(el.totalRub.value);
    const count = parseInt(el.count.value, 10);
    const stepPct = parseFloat(el.stepPct.value);
    if (!(totalRub > 0 && count > 0 && stepPct > 0)) {
      log("Заполните сумму, количество заявок и шаг %", "error");
      return;
    }
    el.btnBuy.disabled = true;
    el.btnSell.disabled = true;
    log("Отправка " + count + " заявок...");
    api("orders/limit-batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        instrument_id: selectedInstrument.instrument_uid,
        direction: direction,
        total_rub: totalRub,
        count: count,
        step_pct: stepPct,
      }),
    })
      .then((data) => {
        const results = data.results || [];
        const ok = results.filter((r) => r.ok).length;
        const fail = results.filter((r) => !r.ok).length;
        let text = "Готово: " + ok + " успешно, " + fail + " с ошибкой.\n";
        results.forEach((r) => {
          text += "Заявка " + r.index + ": " + (r.ok ? "OK, цена " + r.price : (r.error || r.message || "ошибка")) + "\n";
        });
        log(text, fail > 0 ? "error" : "success");
      })
      .catch((err) => {
        log("Ошибка: " + (err.error || err.message || "network"), "error");
      })
      .finally(() => {
        el.btnBuy.disabled = false;
        el.btnSell.disabled = false;
      });
  }

  el.search.addEventListener("input", renderInstruments);
  el.favOnly.addEventListener("change", renderInstruments);

  el.instruments.addEventListener("dblclick", () => {
    const opt = el.instruments.options[el.instruments.selectedIndex];
    if (!opt) return;
    const uid = opt.value;
    const fav = getFavorites();
    const idx = fav.indexOf(uid);
    if (idx >= 0) fav.splice(idx, 1);
    else fav.push(uid);
    setFavorites(fav);
    renderInstruments();
  });

  el.instruments.addEventListener("change", () => {
    const opt = el.instruments.options[el.instruments.selectedIndex];
    if (opt) selectInstrument(opt.value);
  });

  el.btnBuy.addEventListener("click", () => placeBatch("buy"));
  el.btnSell.addEventListener("click", () => placeBatch("sell"));

  loadInstruments();
})();
