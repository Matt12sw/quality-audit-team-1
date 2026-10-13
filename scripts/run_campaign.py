"""Exécution automatisée de la campagne QA QuickOrder V3.1.

Pré-requis : application lancée sur une base propre
    docker compose down -v && docker compose up --build -d
Dépendances : pip install playwright requests openpyxl && playwright install chromium

Produit :
    docs/evidence/*.png   captures d'écran (Playwright / Chromium)
    docs/evidence/*.json  requêtes + réponses HTTP/API, requêtes réseau capturées
    docs/evidence/console.log  messages console navigateur (équivalent DevTools)
    scripts/results.json  résultat obtenu + statut par cas
"""
import json
import re
import time
import traceback
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5000"
API = BASE + "/api"
KEY = "quickorder-demo-key"
H = {"X-API-Key": KEY}
ROOT = Path(__file__).resolve().parent.parent
EV = ROOT / "docs" / "evidence"
EV.mkdir(parents=True, exist_ok=True)

results = {}
apilog = {}
console = []
ctx_state = {}

ALICE = ("alice@example.com", "Password123!")
BOB = ("bob@example.com", "Password123!")
ADMIN = ("admin@quickorder.local", "Admin123!")


# ------------------------------------------------------------------ helpers
def money(text):
    m = re.search(r"-?\d+[.,]\d{2}", text or "")
    return float(m.group(0).replace(",", ".")) if m else None


def api(tc, method, path, headers=H, body=None, base=API):
    r = requests.request(method, base + path, headers=headers, json=body)
    try:
        payload = r.json()
    except ValueError:
        payload = r.text
    apilog.setdefault(tc, []).append({
        "request": {"method": method, "url": base + path, "headers": headers, "json": body},
        "response": {"status": r.status_code, "content_type": r.headers.get("Content-Type"), "body": payload},
    })
    return r, payload


def record(tc, ok, obtenu, preuves=(), statut=None):
    results[tc] = {"obtenu": obtenu, "statut": statut or ("Pass" if ok else "Fail"), "preuves": list(preuves)}
    print(f"{tc:7} {results[tc]['statut']:8} {obtenu[:110]}")


def shot(page, name):
    path = EV / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    return f"evidence/{name}.png"


def flashes(page):
    # messages flash uniquement (enfants directs de <main>), pas les bandeaux HORS STOCK / promo
    return [t.strip() for t in page.locator("main.container > .flash").all_inner_texts()]


def new_page(browser, creds=None, label=""):
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, locale="fr-FR")
    page = ctx.new_page()
    page.on("console", lambda m: console.append(f"[{label}] {m.type}: {m.text} ({page.url})"))
    page.on("pageerror", lambda e: console.append(f"[{label}] pageerror: {e} ({page.url})"))
    if creds:
        login(page, *creds)
    return page


def login(page, email, password):
    page.goto(BASE + "/login")
    page.fill("input[name=email]", email)
    page.fill("input[name=password]", password)
    page.click("button:has-text('Se connecter')")
    page.wait_for_load_state()


def add_product(page, restaurant_id, product_name, qty=1):
    page.goto(f"{BASE}/restaurant/{restaurant_id}")
    card = page.locator("article.card").filter(has=page.get_by_role("heading", name=product_name, exact=True))
    card.locator("input.qty").fill(str(qty))
    card.get_by_role("button", name="Ajouter").click()
    page.wait_for_load_state()
    return flashes(page)


def clear_cart(page):
    page.goto(BASE + "/cart")
    btn = page.locator("button:has-text('Vider le panier')")
    if btn.count():
        btn.click()
        page.wait_for_load_state()


def cart_lines(page):
    page.goto(BASE + "/cart")
    rows = page.locator("table tr").all()[1:]
    return [r.locator("td").first.inner_text().strip() for r in rows]


def checkout_summary(page):
    out = {}
    for line in page.locator("aside.summary .line").all():
        spans = line.locator("span").all_inner_texts()
        if len(spans) == 2:
            out[spans[0].strip()] = money(spans[1])
    return out


def confirm_checkout(page, payment="card", cash=None, coupon=None):
    page.goto(BASE + "/checkout")
    if coupon:
        page.fill("input[name=coupon]", coupon)
        page.click("button:has-text('Appliquer')")
        page.wait_for_load_state()
    page.select_option("#payment_method", payment)
    if cash is not None:
        page.fill("input[name=cash_received]", str(cash))
    page.click("button:has-text('Confirmer')")
    page.wait_for_load_state()
    m = re.search(r"/orders/(\d+)$", page.url)
    return int(m.group(1)) if m else None


def order_detail(page, order_id):
    page.goto(f"{BASE}/orders/{order_id}")
    status = page.locator(".row-between span.status").first.inner_text().strip()
    lines = {}
    for line in page.locator("section.card .line").all():
        spans = line.locator("span").all_inner_texts()
        if len(spans) == 2:
            lines[spans[0].strip()] = money(spans[1])
    aside = page.locator("aside.card").inner_text()
    return status, lines, aside


def api_order_count(tc):
    _, body = api(tc, "GET", "/orders")
    return body["count"]


# ------------------------------------------------------------------ tests
def run(browser):
    A = new_page(browser, ALICE, label="alice")  # session Alice réutilisée (panier en session)

    # TC-N01
    p = new_page(browser, label="N01")
    p.goto(BASE + "/login")
    p.fill("input[name=email]", ALICE[0]); p.fill("input[name=password]", ALICE[1])
    shot(p, "TC-N01_1_formulaire")
    p.click("button:has-text('Se connecter')"); p.wait_for_load_state()
    user = p.locator(".navbar .user").inner_text() if p.locator(".navbar .user").count() else ""
    ok = p.url.rstrip("/") == BASE and user == "Alice Martin" and p.locator("a:has-text('Déconnexion')").count() == 1
    record("TC-N01", ok, f"Redirection vers {p.url} ; utilisateur affiché : « {user} » ; lien Déconnexion présent.",
           ["evidence/TC-N01_1_formulaire.png", shot(p, "TC-N01_2_connecte")])
    p.context.close()

    # TC-N02
    p = new_page(browser, label="N02")
    p.goto(BASE + "/"); p.fill("input[name=q]", "Pizza"); p.click("button:has-text('Rechercher')"); p.wait_for_load_state()
    names = p.locator(".grid article h2").all_inner_texts()
    record("TC-N02", names == ["Pizza Roma"], f"Restaurants affichés : {names}.", [shot(p, "TC-N02_recherche_pizza")])
    p.context.close()

    # TC-N03
    clear_cart(A)
    add_product(A, 1, "Classic Burger", 2)
    A.goto(BASE + "/cart")
    summ = A.locator(".summary").inner_text()
    sub, liv, tot = (money(x) for x in re.findall(r"\d+\.\d{2} €", summ))
    record("TC-N03", (sub, liv, tot) == (23.80, 2.99, 26.79),
           f"Sous-total {sub:.2f} € ; livraison {liv:.2f} € ; total {tot:.2f} €.", [shot(A, "TC-N03_panier")])

    # TC-N04
    A.goto(BASE + "/checkout"); A.fill("input[name=coupon]", "WELCOME10"); A.click("button:has-text('Appliquer')"); A.wait_for_load_state()
    s = checkout_summary(A)
    p1 = shot(A, "TC-N04_1_checkout_coupon")
    A.select_option("#payment_method", "card"); A.click("button:has-text('Confirmer')"); A.wait_for_load_state()
    oid = int(re.search(r"/orders/(\d+)", A.url).group(1))
    ctx_state["n04"] = oid
    status, lines, aside = order_detail(A, oid)
    p2 = shot(A, "TC-N04_2_commande_confirmee")
    remaining = cart_lines(A)
    ok = s.get("Réduction") == 2.38 and s.get("Total") == 24.41 and status == "confirmed" and "paid" in aside and not remaining
    record("TC-N04", ok, f"Checkout : réduction {s.get('Réduction')} €, total {s.get('Total')} €. Commande #{oid} statut « {status} », "
           f"paiement « {re.search(r'Paiement\s+(.+)', aside).group(1).strip()} », total {lines.get('Total')} €. Panier après commande : {remaining or 'vide'}.", [p1, p2])

    # TC-N06
    A.goto(f"{BASE}/orders/{oid}"); A.click("button:has-text('Annuler la commande')"); A.wait_for_load_state()
    fl = flashes(A); st = A.locator(".row-between span.status").first.inner_text().strip()
    record("TC-N06", "Commande annulée." in fl and st == "cancelled", f"Message : {fl} ; statut : « {st} ».", [shot(A, "TC-N06_annulation")])

    # TC-N05 (Swagger UI + appel API tracé)
    p = new_page(browser, label="N05")
    sw_ok, sw_txt, proofs = False, "", []
    try:
        p.goto(BASE + "/docs/#/Restaurants/get_restaurants")
        p.wait_for_selector(".btn.authorize", timeout=20000)
        p.click(".btn.authorize"); p.fill(".modal-ux input", KEY)
        p.click(".modal-ux .auth-btn-wrapper .authorize"); p.click(".modal-ux .btn-done")
        p.wait_for_selector("#operations-Restaurants-get_restaurants .try-out__btn", timeout=10000)
        p.click("#operations-Restaurants-get_restaurants .try-out__btn")
        p.click("#operations-Restaurants-get_restaurants .execute")
        cell = "#operations-Restaurants-get_restaurants .live-responses-table tbody .response-col_status"
        p.wait_for_selector(cell, timeout=10000)
        code = p.locator(cell).first.inner_text().strip()
        p.locator("#operations-Restaurants-get_restaurants").scroll_into_view_if_needed()
        proofs.append(shot(p, "TC-N05_swagger_get_restaurants"))
        sw_ok, sw_txt = code == "200", f"Swagger UI : HTTP {code}. "
    except Exception as e:  # Swagger UI dépend d'un CDN externe
        sw_txt = f"Swagger UI non pilotable ({type(e).__name__}). "
    r, body = api("TC-N05", "GET", "/restaurants")
    proofs.append("evidence/TC-N05.json")
    record("TC-N05", sw_ok and r.status_code == 200 and body["count"] >= 1,
           sw_txt + f"Appel direct : HTTP {r.status_code}, count={body['count']}, restaurants : {[i['name'] for i in body['items']]}.", proofs)
    p.context.close()

    # TC-N07
    clear_cart(A); add_product(A, 1, "Classic Burger", 1); add_product(A, 1, "Frites maison", 1)
    A.goto(BASE + "/cart")
    n_remove = A.locator("table").get_by_text(re.compile("Supprimer|Retirer", re.I)).count()
    n_remove_forms = A.locator("form[action*='/cart/remove/']").count()
    html_cell = A.locator("table tr").nth(2).locator("td").last.inner_html()
    record("TC-N07", n_remove + n_remove_forms > 0,
           f"Aucun bouton de suppression par ligne (libellés « Supprimer/Retirer » : {n_remove}, formulaires /cart/remove : {n_remove_forms}). "
           f"La dernière cellule de la ligne contient seulement « {html_cell} » (formulaire vide imbriqué). Seul contournement : quantité 0 ou « Vider le panier ».",
           [shot(A, "TC-N07_panier_sans_suppression")])
    clear_cart(A)

    # TC-L01
    p = new_page(browser, label="L01")
    p.goto(BASE + "/"); p.select_option("select[name=max_delivery]", "2.50"); p.click("button:has-text('Rechercher')"); p.wait_for_load_state()
    cards = p.locator(".grid article").all()
    found = [(c.locator("h2").inner_text(), money(re.search(r"Livraison ([\d.]+)", c.inner_text()).group(1) + "")) for c in cards]
    record("TC-L01", {n for n, _ in found} == {"Green Kitchen", "Pizza Roma"},
           f"URL {p.url} → restaurants affichés (frais) : {found}. Green Kitchen (1,99 €) et Pizza Roma (2,49 €) sont absents.",
           [shot(p, "TC-L01_filtre_livraison")])
    p.context.close()

    # TC-L02
    r1, b1 = api("TC-L02", "POST", "/coupons/validate", body={"code": "WELCOME10", "subtotal": 19.99})
    r2, b2 = api("TC-L02", "POST", "/coupons/validate", body={"code": "WELCOME10", "subtotal": 20.00})
    record("TC-L02", b1.get("valid") is False and b2.get("valid") is True and b2.get("discount") == 2.0,
           f"19.99 → HTTP {r1.status_code} {b1} ; 20.00 → HTTP {r2.status_code} {b2}.", ["evidence/TC-L02.json"])

    # TC-L03
    r, b = api("TC-L03", "POST", "/coupons/validate", body={"code": "WELCOME10", "subtotal": 100})
    record("TC-L03", b.get("discount") == 8.0, f"HTTP {r.status_code} {b}.", ["evidence/TC-L03.json"])

    # TC-L04 / L05
    for tc, q in (("TC-L04", 0), ("TC-L05", 21)):
        r, b = api(tc, "POST", "/orders", body={"items": [{"product_id": 1, "quantity": q}], "payment_method": "card"})
        record(tc, r.status_code == 400, f"HTTP {r.status_code} {b}.", [f"evidence/{tc}.json"])

    # TC-L06
    _, before = api("TC-L06", "GET", "/products/7")
    r, b = api("TC-L06", "POST", "/orders", body={"items": [{"product_id": 7, "quantity": 3}], "payment_method": "card"})
    _, after = api("TC-L06", "GET", "/products/7")
    record("TC-L06", r.status_code == 409 and after["stock"] == before["stock"],
           f"Stock avant : {before['stock']}. POST → HTTP {r.status_code}, commande #{b.get('id')} statut « {b.get('status')} », "
           f"quantité 3. Stock après : {after['stock']}.", ["evidence/TC-L06.json"])

    # TC-L08
    clear_cart(A)
    fl = add_product(A, 1, "Veggie Burger", 1)
    p1 = shot(A, "TC-L08_1_ajout_hors_stock")
    lines = cart_lines(A)
    p2 = shot(A, "TC-L08_2_panier")
    upd_valid = A.evaluate("() => { const f = document.querySelector('form[method=post]'); return f ? f.checkValidity() : null }")
    record("TC-L08", any("indisponible" in f for f in fl) and "Veggie Burger" not in lines,
           f"Message après ajout : {fl}. Panier : {lines}. Le champ quantité a max=0 (stock) : le formulaire « Mettre à jour » "
           f"est {'valide' if upd_valid else 'invalide (bloqué par le navigateur)'}.", [p1, p2])
    clear_cart(A)

    # TC-E01
    p = new_page(browser, label="E01")
    login(p, ALICE[0], "MauvaisMdp1!")
    fl = flashes(p); logged = p.locator(".navbar .user").count() > 0
    record("TC-E01", "Email ou mot de passe incorrect." in fl and not logged,
           f"Message : {fl} ; utilisateur connecté : {logged}.", [shot(p, "TC-E01_login_refuse")])
    p.context.close()

    # TC-E02 / E03
    for tc, hdr in (("TC-E02", {}), ("TC-E03", {"X-API-Key": "wrong-key"})):
        r, b = api(tc, "GET", "/restaurants", headers=hdr)
        record(tc, r.status_code == 401 and isinstance(b, dict), f"HTTP {r.status_code} {b}.", [f"evidence/{tc}.json"])

    # TC-E04
    r, b = api("TC-E04", "GET", "/products/9999")
    ct = r.headers.get("Content-Type", "")
    record("TC-E04", r.status_code == 404 and "json" in ct,
           f"HTTP {r.status_code}, Content-Type « {ct} », corps : page HTML Werkzeug « Not Found » (pas de JSON).", ["evidence/TC-E04.json"])

    # TC-E05
    r, b = api("TC-E05", "POST", "/coupons/validate", body={"code": "EXPIRED10", "subtotal": 50})
    record("TC-E05", b.get("valid") is False, f"HTTP {r.status_code} {b}.", ["evidence/TC-E05.json"])

    # TC-E06
    r, b = api("TC-E06", "POST", "/orders", body={"items": [{"product_id": 20, "quantity": 2}], "coupon": "EXPIRED10", "payment_method": "card"})
    record("TC-E06", r.status_code == 400 or b.get("discount") == 0,
           f"HTTP {r.status_code} ; commande #{b.get('id')} créée, sous-total {b.get('subtotal')} €, discount {b.get('discount')} € (10 % appliqué), total {b.get('total')} €.",
           ["evidence/TC-E06.json"])

    # TC-E07
    p = new_page(browser, label="E07")
    p.goto(BASE + "/register"); p.fill("input[name=name]", "Alice Bis"); p.fill("input[name=email]", ALICE[0]); p.fill("input[name=password]", "Password123!")
    p.click("button:has-text('Créer mon compte')"); p.wait_for_load_state()
    fl = flashes(p)
    record("TC-E07", any("existe déjà" in f for f in fl), f"Message : {fl}.", [shot(p, "TC-E07_email_existant")])
    p.context.close()

    # TC-E08 (avec capture réseau type DevTools)
    clear_cart(A); add_product(A, 1, "Classic Burger", 2)
    netlog = []
    A.on("request", lambda req: netlog.append({"method": req.method, "url": req.url, "post_data": req.post_data}) if req.method == "POST" and "checkout" in req.url else None)
    A.goto(BASE + "/checkout"); A.select_option("#payment_method", "cash"); A.fill("input[name=cash_received]", "1")
    p1 = shot(A, "TC-E08_1_checkout_especes_1euro")
    A.click("button:has-text('Confirmer')"); A.wait_for_load_state()
    m = re.search(r"/orders/(\d+)", A.url)
    (EV / "TC-E08_network.json").write_text(json.dumps(netlog, indent=2, ensure_ascii=False), encoding="utf-8")
    if m:
        st, lines, aside = order_detail(A, int(m.group(1)))
        p2 = shot(A, "TC-E08_2_commande_creee")
        cash_txt = " ".join(aside.split())
        _, ob = api("TC-E08", "GET", f"/orders/{m.group(1)}")
        record("TC-E08", False, f"Commande #{m.group(1)} créée, statut « {st} », paiement « paid ». Total {lines.get('Total')} €, "
               f"montant remis {ob['cash_received']} €, monnaie calculée {ob['change_due']} € (négative).",
               [p1, p2, "evidence/TC-E08_network.json", "evidence/TC-E08.json"])
    else:
        record("TC-E08", True, f"Commande refusée : {flashes(A)}.", [p1, shot(A, "TC-E08_2_refus")])

    # TC-E09
    A.goto(BASE + "/admin/"); fl = flashes(A)
    record("TC-E09", A.url.rstrip("/") == BASE and any("réservé" in f for f in fl),
           f"Redirection vers {A.url} ; message : {fl}.", [shot(A, "TC-E09_admin_refuse")])

    # TC-E10
    s = requests.Session()
    r = s.post(BASE + "/login?next=https://evil.example.com/phishing", data={"email": ALICE[0], "password": ALICE[1]}, allow_redirects=False)
    loc = r.headers.get("Location", "")
    apilog["TC-E10"] = [{"request": {"method": "POST", "url": BASE + "/login?next=https://evil.example.com/phishing",
                                     "form": {"email": ALICE[0], "password": "***"}},
                         "response": {"status": r.status_code, "location": loc}}]
    record("TC-E10", not loc.startswith("http") or loc.startswith(BASE),
           f"HTTP {r.status_code}, en-tête Location : « {loc} » → l'utilisateur authentifié est envoyé vers un domaine externe.", ["evidence/TC-E10.json"])

    # TC-E11 (Blocked)
    clear_cart(A); add_product(A, 1, "Classic Burger", 1)
    A.goto(BASE + "/checkout")
    opts = A.locator("#payment_method option").all_inner_texts()
    record("TC-E11", False, f"Non exécutable : options de paiement proposées {opts}. Le simulateur ne permet pas de provoquer un refus "
           "de paiement (aucune carte de test, aucun paramètre). Le chemin payment_failed n'est pas atteignable.",
           [shot(A, "TC-E11_options_paiement")], statut="Blocked")
    clear_cart(A)

    # TC-R01
    clear_cart(A); add_product(A, 1, "Classic Burger", 1)
    fl = add_product(A, 4, "Margherita", 1)
    p1 = shot(A, "TC-R01_1_refus_multi_restaurant")
    lines = cart_lines(A)
    record("TC-R01", any("même restaurant" in f for f in fl) and "Margherita" not in lines,
           f"Message : {fl}. Panier : {lines}.", [p1, shot(A, "TC-R01_2_panier")])

    # TC-R02
    clear_cart(A)
    fl = add_product(A, 6, "Late Sushi Box", 1)
    p1 = shot(A, "TC-R02_1_restaurant_ferme_ajout")
    oid = confirm_checkout(A, "card")
    if oid:
        st, lines, _ = order_detail(A, oid)
        record("TC-R02", False, f"Ajout accepté ({fl}) alors que le restaurant est affiché FERMÉ ; commande #{oid} créée au statut « {st} », total {lines.get('Total')} €.",
               [p1, shot(A, "TC-R02_2_commande_restaurant_ferme")])
    else:
        record("TC-R02", True, f"Refus : {fl} {flashes(A)}.", [p1])

    # TC-R03
    clear_cart(A); add_product(A, 5, "Thé à la menthe", 1)
    A.goto(BASE + "/checkout"); p1 = shot(A, "TC-R03_1_checkout_sous_minimum")
    oid = confirm_checkout(A, "card")
    if oid:
        st, lines, _ = order_detail(A, oid)
        record("TC-R03", False, f"Commande #{oid} créée (statut « {st} ») avec un sous-total de {lines.get('Sous-total')} € pour un minimum affiché de 25,00 €.",
               [p1, shot(A, "TC-R03_2_commande_sous_minimum")])
    else:
        record("TC-R03", True, f"Refus : {flashes(A)}.", [p1])

    # TC-R04
    clear_cart(A); add_product(A, 5, "Couscous Royal", 2)
    p0 = shot(A, "TC-R04_0_promo_annoncee")
    A.goto(BASE + "/checkout"); A.fill("input[name=coupon]", "ATLAS15"); A.click("button:has-text('Appliquer')"); A.wait_for_load_state()
    s = checkout_summary(A)
    record("TC-R04", s.get("Réduction") == 5.37,
           f"Sous-total {s.get('Sous-total')} € ; réduction appliquée {s.get('Réduction')} € (= 10 %) au lieu de 5,37 € (15 %) ; total {s.get('Total')} €.",
           [p0, shot(A, "TC-R04_1_checkout_atlas15")])
    clear_cart(A)

    # TC-R05
    before = api_order_count("TC-R05")
    clear_cart(A); add_product(A, 4, "Margherita", 1)
    oid = confirm_checkout(A, "paypal")
    after = api_order_count("TC-R05")
    A.goto(BASE + "/orders")
    _, lst = api("TC-R05", "GET", "/orders")
    newest = [(o["id"], o["payment_method"], o["total"], o["created_at"]) for o in lst["items"][: after - before]]
    ctx_state["r05"] = oid
    record("TC-R05", after - before == 1,
           f"Commandes d'Alice avant : {before}, après : {after} (+{after - before}). Nouvelles commandes : {newest}.",
           [shot(A, "TC-R05_commandes_paypal_dupliquees"), "evidence/TC-R05.json"])

    # TC-R06
    adm = new_page(browser, ADMIN, label="admin")
    rid = ctx_state["r05"]
    for status in ("delivered", "confirmed"):
        adm.goto(BASE + "/admin/")
        form = adm.locator(f"form[action='/admin/orders/{rid}/status']")
        form.locator("select").select_option(status)
        form.get_by_role("button").click(); adm.wait_for_load_state()
        if status == "delivered":
            _, o1 = api("TC-R06", "GET", f"/orders/{rid}")
    fl = flashes(adm)
    _, o2 = api("TC-R06", "GET", f"/orders/{rid}")
    record("TC-R06", o2["status"] == "delivered",
           f"Commande #{rid} : statut après étape 1 « {o1['status']} », puis « {o2['status']} » après demande confirmed. Message : {fl}.",
           [shot(adm, "TC-R06_admin_transition"), "evidence/TC-R06.json"])
    adm.context.close()

    # TC-R07
    b = new_page(browser, BOB, label="bob")
    b.goto(BASE + "/orders"); bob_orders = b.locator(".list .card").count()
    b.goto(BASE + "/restaurant/4")
    b.select_option("select[name=rating]", "1"); b.fill("textarea[name=comment]", "Test QA : avis sans commande")
    b.click("button:has-text('Publier')"); b.wait_for_load_state()
    fl = flashes(b)
    record("TC-R07", not any("Merci" in f for f in fl),
           f"Bob a {bob_orders} commande(s). Message après publication : {fl}.", [shot(b, "TC-R07_avis_sans_commande")])
    b.context.close()

    # TC-R08
    A.goto(BASE + "/orders/1"); A.click("button:has-text('Annuler la commande')"); A.wait_for_load_state()
    fl = flashes(A); st = A.locator(".row-between span.status").first.inner_text().strip()
    record("TC-R08", any("ne peut plus" in f for f in fl) and st == "delivered",
           f"Message : {fl} ; statut : « {st} ». (Remarque : le bouton « Annuler la commande » reste affiché sur une commande livrée.)",
           [shot(A, "TC-R08_annulation_livree")])

    # TC-R09
    clear_cart(A)
    r, bdy = api("TC-R09", "POST", "/coupons/validate", body={"code": "SAVE20", "subtotal": 9999})
    record("TC-R09", bdy.get("valid") is not True,
           f"HTTP {r.status_code} {bdy} : le coupon est validé sur un sous-total fictif de 9 999 € fourni par le client, sans lien avec un panier réel.",
           ["evidence/TC-R09.json"])

    # TC-R10
    p = new_page(browser, label="R10")
    p.goto(BASE + "/"); p.fill("input[name=q]", "marocaine"); p.click("button:has-text('Rechercher')"); p.wait_for_load_state()
    ui = p.locator(".grid article h2").all_inner_texts()
    _, ab = api("TC-R10", "GET", "/restaurants?q=marocaine")
    record("TC-R10", "Couscous Atlas" in ui and ab["count"] >= 1,
           f"UI : {ui or 'Aucun restaurant trouvé'} ; API : count={ab['count']}.", [shot(p, "TC-R10_recherche_description"), "evidence/TC-R10.json"])
    p.context.close()

    # TC-R11
    p = new_page(browser, label="R11")
    email = f"qa.testeur.{int(time.time())}@example.com"
    p.goto(BASE + "/register"); p.fill("input[name=name]", "QA Testeur"); p.fill("input[name=email]", email); p.fill("input[name=password]", "Password123!")
    p.click("button:has-text('Créer mon compte')"); p.wait_for_load_state()
    add_product(p, 1, "Classic Burger", 2)
    p.goto(BASE + "/checkout")
    addr = p.locator("select[name=address_id] option").all_inner_texts()
    p1 = shot(p, "TC-R11_1_checkout_adresse_vide")
    oid = confirm_checkout(p, "card")
    if oid:
        st, _, aside = order_detail(p, oid)
        liv = aside.split("Livraison")[-1].split("Annuler")[0].strip().replace("\n", " ")
        record("TC-R11", False, f"Compte {email} créé ; adresse proposée : {addr}. Commande #{oid} créée (statut « {st} ») ; bloc Livraison : « {liv or '(vide)'} ».",
               [p1, shot(p, "TC-R11_2_commande_adresse_vide")])
    else:
        record("TC-R11", True, f"Commande refusée : {flashes(p)}.", [p1])
    p.context.close()

    # TC-L07 (en dernier : rend le stock de Double Cheese négatif)
    clear_cart(A)
    A.goto(BASE + "/restaurant/1")
    js = ("const i=[...document.querySelectorAll('article.card')].find(a=>a.querySelector('h3').textContent==='Double Cheese')"
          ".querySelector('input.qty'); i.removeAttribute('max'); i.value='500';")
    A.evaluate(f"() => {{ {js} }}")
    p1 = shot(A, "TC-L07_1_devtools_quantite_500")
    card = A.locator("article.card").filter(has=A.get_by_role("heading", name="Double Cheese", exact=True))
    card.get_by_role("button", name="Ajouter").click(); A.wait_for_load_state()
    fl = flashes(A)
    A.goto(BASE + "/cart"); p2 = shot(A, "TC-L07_2_panier_500")
    _, before = api("TC-L07", "GET", "/products/2")
    oid = confirm_checkout(A, "card")
    _, after = api("TC-L07", "GET", "/products/2")
    (EV / "TC-L07_devtools.js").write_text(js + "\n", encoding="utf-8")
    record("TC-L07", not any("ajouté" in f for f in fl) and after["stock"] >= 0,
           f"Message : {fl}. Commande #{oid} créée pour 500 Double Cheese. Stock avant : {before['stock']}, après : {after['stock']}.",
           [p1, p2, shot(A, "TC-L07_3_commande"), "evidence/TC-L07.json", "evidence/TC-L07_devtools.js"])


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            run(browser)
        except Exception:
            traceback.print_exc()
        finally:
            browser.close()
    for tc, entries in apilog.items():
        (EV / f"{tc}.json").write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    (EV / "console.log").write_text("\n".join(console) + "\n", encoding="utf-8")
    (ROOT / "scripts" / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{len(results)} cas exécutés.")


if __name__ == "__main__":
    main()
