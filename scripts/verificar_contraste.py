import pathlib
import re
import sys

CSS = pathlib.Path(__file__).resolve().parent.parent / "app" / "static" / "css" / "style.css"
BLANCO = "#ffffff"

PARES = [
    ("Texto principal sobre fondo de página", "texto", "verde-50", 7),
    ("Texto principal sobre tarjetas", "texto", BLANCO, 7),
    ("Texto principal sobre filas alternas", "texto", "franja", 7),
    ("Texto secundario sobre tarjetas", "texto-suave", BLANCO, 7),
    ("Texto secundario sobre fondo de página", "texto-suave", "verde-50", 7),
    ("Texto secundario sobre filas alternas", "texto-suave", "franja", 7),
    ("Enlaces sobre tarjetas", "verde-800", BLANCO, 7),
    ("Enlaces sobre fondo de página", "verde-800", "verde-50", 7),
    ("Enlaces sobre filas alternas", "verde-800", "franja", 7),
    ("Enlaces sobre fila resaltada", "verde-800", "verde-100", 7),
    ("Enlaces al pasar el cursor", "verde-950", BLANCO, 7),
    ("Títulos sobre fondo de página", "verde-900", "verde-50", 7),
    ("Títulos sobre tarjetas", "verde-900", BLANCO, 7),
    ("Menú, pie y encabezados de tabla (texto blanco)", BLANCO, "verde-900", 7),
    ("Botón principal", BLANCO, "verde-800", 7),
    ("Botón principal (cursor/activo)", BLANCO, "verde-950", 7),
    ("Botón de peligro", BLANCO, "rojo", 7),
    ("Botón de peligro (cursor/activo)", BLANCO, "#5f1414", 7),
    ("Botón principal deshabilitado", BLANCO, "#3d6b4f", 4.5),
    ("Errores y stock bajo sobre tarjetas", "rojo", BLANCO, 7),
    ("Stock bajo sobre filas alternas", "rojo", "franja", 7),
    ("Stock bajo sobre lote vencido", "rojo", "rojo-claro", 7),
    ("Texto de ayuda (placeholder)", "placeholder", BLANCO, 7),
    ("Controles deshabilitados", "deshabilitado-tx", "deshabilitado-bg", 7),
    ("Alerta de éxito", "#0a2e19", "#dcf1e3", 7),
    ("Alerta de error", "#5f1414", "#fde8e8", 7),
    ("Alerta de aviso", "#4a3000", "#fff3cd", 7),
    ("Alerta informativa", "#0b3552", "#dbeefa", 7),
    ("Borde de campos de formulario (componente UI)", "borde-campo", BLANCO, 3),
    ("Borde de campos sobre fondo de página (UI)", "borde-campo", "verde-50", 3),
    ("Anillo de foco sobre contenido claro (UI)", "foco", BLANCO, 3),
    ("Anillo de foco sobre fondo de página (UI)", "foco", "verde-50", 3),
    ("Anillo de foco blanco sobre menú y pie (UI)", BLANCO, "verde-900", 3),
]


def variables():
    return {m.group(1): m.group(2) for m in re.finditer(r"--c-([\w-]+):\s*(#[0-9a-fA-F]{6})", CSS.read_text())}


def luminancia(hex_):
    r, g, b = (int(hex_.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def razon(a, b):
    mayor, menor = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (mayor + 0.05) / (menor + 0.05)


def evaluar():
    v = variables()
    res = lambda x: x if x.startswith("#") else v[x]
    out = []
    for nombre, fg, bg, minimo in PARES:
        r = razon(res(fg), res(bg))
        out.append((nombre, round(r, 2), minimo, r >= minimo))
    return out


if __name__ == "__main__":
    filas = evaluar()
    if "--md" in sys.argv:
        print("| Combinación | Contraste | Requisito |\n|---|---|---|")
        for n, r, m, ok in filas:
            print(f"| {n} | {r}:1 | ≥ {m}:1 |")
    else:
        for n, r, m, ok in filas:
            print(f"{'OK ' if ok else 'FALLA'} {r:>6}:1 (mín {m}:1)  {n}")
    sys.exit(0 if all(f[3] for f in filas) else 1)
