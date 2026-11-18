from html.parser import HTMLParser

from scripts.verificar_contraste import evaluar


class Documento(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.h1 = 0
        self.ids = []
        self.label_for = set()
        self.controles = []
        self.tablas = 0
        self.captions = 0
        self.th_sin_scope = 0
        self.salto = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "label" and a.get("for"):
            self.label_for.add(a["for"])
        if tag in ("input", "select", "textarea") and a.get("type") not in ("hidden", "submit", "button"):
            self.controles.append(a)
        if tag == "table":
            self.tablas += 1
        if tag == "caption":
            self.captions += 1
        if tag == "th" and "scope" not in a:
            self.th_sin_scope += 1
        if tag == "a" and a.get("href") == "#contenido":
            self.salto = True


def _analizar(client, url):
    r = client.get(url)
    assert r.status_code == 200, url
    d = Documento()
    d.feed(r.get_data(as_text=True))
    return d


def test_contraste_del_tema_cumple_wcag_aaa():
    fallos = [f for f in evaluar() if not f[3]]
    assert not fallos, fallos


def test_paginas_publicas_y_privadas_son_accesibles(login, datos):
    c = login("admin")
    pid = datos["producto_id"]
    urls = ["/dashboard", "/productos", f"/productos/{pid}", "/productos/nuevo", f"/productos/{pid}/entrada",
            f"/productos/{pid}/salida", "/movimientos", "/reposiciones", "/proveedores", "/proveedores/nuevo", "/chat"]
    for url in urls:
        d = _analizar(c, url)
        assert d.lang == "es", url
        assert d.h1 == 1, url
        assert d.salto, url
        assert len(d.ids) == len(set(d.ids)), url
        assert all(k.get("id") in d.label_for or k.get("aria-label") for k in d.controles), url
        assert d.tablas == d.captions and d.th_sin_scope == 0, url
    c.post("/logout")
    for url in ("/login", "/registro", "/olvide"):
        d = _analizar(c, url)
        assert d.lang == "es" and d.h1 == 1 and d.salto
        assert all(k.get("id") in d.label_for for k in d.controles), url


def test_errores_de_formulario_se_asocian_al_campo(client):
    r = client.post("/registro", data={"nombre": "A", "email": "x", "area": "ventas", "password": "1", "confirmar": "2"})
    html = r.get_data(as_text=True)
    assert 'aria-invalid="true"' in html
    assert 'aria-describedby="email-error"' in html
    assert 'id="email-error"' in html and "invalid-feedback" in html


def test_bootstrap_se_sirve_localmente_sin_cdn(client):
    html = client.get("/login").get_data(as_text=True)
    assert "vendor/bootstrap.min.css" in html and "cdn" not in html.lower()
    assert client.get("/static/vendor/bootstrap.min.css").status_code == 200
    assert client.get("/static/vendor/bootstrap.bundle.min.js").status_code == 200
