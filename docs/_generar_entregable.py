# -*- coding: utf-8 -*-
"""Genera el Entregable 1 actualizado en Word, con los diagramas embebidos."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figuras"
FIG.mkdir(exist_ok=True)

VERDE = (29, 107, 79)
VERDE_OSCURO = (15, 48, 40)
VERDE_CLARO = (231, 243, 236)
VERDE_MEDIO = (60, 179, 113)
AMBAR = (224, 177, 90)
AMBAR_CLARO = (251, 243, 228)
ROJO = (157, 52, 31)
ROJO_CLARO = (253, 236, 234)
TINTA = (30, 36, 48)
SUAVE = (92, 101, 112)
LINEA = (212, 204, 190)
BLANCO = (255, 253, 248)
PAPEL = (244, 241, 234)
AZUL = (36, 84, 130)
AZUL_CLARO = (232, 240, 248)
MORADO = (92, 62, 122)
MORADO_CLARO = (243, 236, 248)


def fuente(size, bold=False):
    nombre = "segoeuib.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(rf"C:\Windows\Fonts\{nombre}", size)


def medida(draw, text, font):
    caja = draw.textbbox((0, 0), text, font=font)
    return caja[2] - caja[0], caja[3] - caja[1]


def envolver(draw, text, font, ancho):
    lineas = []
    actual = ""
    for palabra in text.split():
        prueba = palabra if not actual else actual + " " + palabra
        if medida(draw, prueba, font)[0] <= ancho:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas or [""]


def texto(draw, x, y, text, font, fill, anchor="lt"):
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)


def texto_centro(draw, cx, cy, lineas, font, fill, inter=4):
    alturas = [medida(draw, linea, font)[1] for linea in lineas]
    total = sum(alturas) + inter * (len(lineas) - 1)
    y = cy - total / 2
    for linea, alto in zip(lineas, alturas):
        texto(draw, cx, y + alto / 2, linea, font, fill, "mm")
        y += alto + inter


def encabezado(draw, w, titulo, subtitulo):
    draw.rectangle([0, 0, w, 78], fill=VERDE_OSCURO)
    draw.rectangle([0, 78, w, 84], fill=VERDE_MEDIO)
    texto(draw, 28, 18, titulo, fuente(26, True), BLANCO)
    texto(draw, 28, 50, subtitulo, fuente(14), (214, 228, 220))


def redondeado(draw, caja, radio, fill, outline, ancho=2):
    draw.rounded_rectangle(caja, radius=radio, fill=fill, outline=outline, width=ancho)


def actor(draw, x, y, nombre, color):
    draw.ellipse([x - 16, y - 58, x + 16, y - 26], outline=color, width=3)
    draw.line([x, y - 26, x, y + 18], fill=color, width=3)
    draw.line([x - 24, y - 8, x + 24, y - 8], fill=color, width=3)
    draw.line([x, y + 18, x - 20, y + 52], fill=color, width=3)
    draw.line([x, y + 18, x + 20, y + 52], fill=color, width=3)
    lineas = envolver(draw, nombre, fuente(15, True), 150)
    texto_centro(draw, x, y + 78, lineas, fuente(15, True), color, 2)


def ovalo(draw, cx, cy, w, h, texto_caso, fill, outline):
    draw.ellipse([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], fill=fill, outline=outline, width=2)
    lineas = envolver(draw, texto_caso, fuente(14, True), w - 36)
    texto_centro(draw, cx, cy, lineas, fuente(14, True), TINTA, 2)


def linea(draw, a, b, fill, ancho=2):
    draw.line([a, b], fill=fill, width=ancho)


def flecha(draw, a, b, fill, ancho=2):
    draw.line([a, b], fill=fill, width=ancho)
    import math
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    largo = 12
    p1 = (b[0] - largo * math.cos(ang - 0.4), b[1] - largo * math.sin(ang - 0.4))
    p2 = (b[0] - largo * math.cos(ang + 0.4), b[1] - largo * math.sin(ang + 0.4))
    draw.polygon([b, p1, p2], fill=fill)


def diagrama_casos():
    w, h = 2000, 1320
    im = Image.new("RGB", (w, h), PAPEL)
    d = ImageDraw.Draw(im)
    encabezado(d, w, "DIAGRAMA DE CASOS DE USO — CUENTAS DE LA CASA", "Administrador y usuario normal sobre el sistema web Django 5.2")
    redondeado(d, [250, 110, 1750, 1185], 24, BLANCO, VERDE_OSCURO, 3)
    texto(d, 1000, 138, "«system» Sistema web Cuentas de la casa", fuente(16, True), VERDE_OSCURO, "mt")

    propios = [
        (500, 230, "CU-01  Registrarse\ncomo usuario normal"),
        (500, 340, "CU-02  Iniciar sesión"),
        (500, 450, "CU-03  Consultar el inicio\n(propias y asignadas)"),
        (500, 560, "CU-04  Consultar servicios\ny cuentas asignadas"),
        (500, 670, "CU-05  Crear cuenta propia"),
        (500, 780, "CU-06  Marcar una cuenta\ncomo pagada"),
        (500, 890, "CU-07  Editar o eliminar\nsus cuentas"),
        (500, 1000, "CU-08  Consultar cuentas\nya pagadas"),
    ]
    admin = [
        (1500, 280, "CU-09  Ver el dashboard\nagregado del grupo"),
        (1500, 410, "CU-10  Crear una cuenta\ndel grupo"),
        (1500, 540, "CU-11  Asignar la cuenta\na un usuario normal"),
        (1500, 670, "CU-12  Crear usuario\nnormal"),
        (1500, 800, "CU-13  Consultar las cuentas\nde cada usuario"),
    ]
    for cx, cy, texto_caso in propios:
        ovalo(d, cx, cy, 340, 92, texto_caso.replace("\n", " "), VERDE_CLARO, VERDE)
        linea(d, (150, 640), (cx - 170, cy), VERDE)
    for cx, cy, texto_caso in admin:
        ovalo(d, cx, cy, 360, 108, texto_caso.replace("\n", " "), MORADO_CLARO, MORADO)
        linea(d, (1850, 640), (cx + 180, cy), MORADO)
    ovalo(d, 1000, 1080, 360, 90, "CU-14  Validar servicio, valor y fecha", AMBAR_CLARO, (138, 90, 18))
    flecha(d, (670, 670), (830, 1045), (138, 90, 18))
    flecha(d, (1320, 410), (1160, 1040), (138, 90, 18))
    texto(d, 760, 820, "«include»", fuente(12), (138, 90, 18))
    texto(d, 1180, 700, "«include»", fuente(12), (138, 90, 18))

    actor(d, 130, 640, "Usuario normal", VERDE)
    actor(d, 1870, 640, "Administrador", MORADO)
    redondeado(d, [430, 1205, 1570, 1288], 12, BLANCO, LINEA)
    texto(d, 450, 1216, "Verde: usuario normal.  Morado: administrador.  Ámbar: validación incluida al crear una cuenta.", fuente(15), TINTA)
    texto(d, 450, 1244, "CU-12 deja el rol Usuario normal. El administrador ve a esa persona en su grupo y puede asignarle cuentas.", fuente(15), SUAVE)
    texto(d, 450, 1268, "La secuencia de estos casos se detalla en el Anexo A.", fuente(15), SUAVE)
    im.save(FIG / "casos_uso.png", quality=95)
    return FIG / "casos_uso.png"


def caja(draw, x, y, w, h, titulo, lineas, fill, outline, estereotipo="«component»"):
    redondeado(draw, [x, y, x + w, y + h], 12, fill, outline, 2)
    draw.rectangle([x, y, x + w, y + 36], fill=outline)
    texto(draw, x + 12, y + 8, titulo, fuente(15, True), BLANCO)
    texto(draw, x + w - 12, y + 46, estereotipo, fuente(11), outline, "ra")
    yy = y + 62
    for linea_txt in lineas:
        for envuelta in envolver(draw, linea_txt, fuente(13), w - 24):
            texto(draw, x + 12, yy, envuelta, fuente(13), TINTA)
            yy += 18


def diagrama_componentes():
    w, h = 2000, 980
    im = Image.new("RGB", (w, h), PAPEL)
    d = ImageDraw.Draw(im)
    encabezado(d, w, "DIAGRAMA DE COMPONENTES — ARQUITECTURA MTV", "Cliente, proyecto mysite, aplicación cuentas y SQLite")
    caja(d, 40, 120, 360, 430, "Cliente web", [
        "Navegador",
        "Formularios HTML y CSS",
        "Inicio, lista, servicios,",
        "panel de usuarios y perfil",
        "Cookie de sesión y token CSRF",
    ], AZUL_CLARO, AZUL)
    caja(d, 460, 120, 420, 430, "Proyecto mysite", [
        "mysite/urls.py  incluye /cuentas/",
        "settings.py",
        "Django 5.2, idioma es,",
        "zona America/Bogota",
        "Middleware de sesión,",
        "CSRF y autenticación",
        "django.contrib.auth",
    ], (236, 236, 236), (70, 78, 88))
    caja(d, 940, 120, 620, 640, "Aplicación cuentas", [
        "Enrutador cuentas/urls.py",
        "Vistas: inicio, servicios, lista,",
        "crear, editar, borrar, marcar,",
        "entrar, registro, perfil, panel",
        "Plantillas DTL en templates/cuentas",
        "Modelos:",
        "Usuario (rol administrador | usuario)",
        "Servicio (catálogo compartido)",
        "Cuenta (alcance propia | grupo,",
        "usuario, mes, valor, vence, pagada)",
        "Señal post_save: crea el perfil",
        "con el rol que corresponde",
    ], VERDE_CLARO, VERDE)
    caja(d, 1620, 120, 340, 300, "Persistencia", [
        "Django ORM",
        "SQLite  db.sqlite3",
        "Tablas Usuario, Servicio,",
        "Cuenta, auth y sesiones",
    ], (255, 244, 230), (166, 92, 24))
    caja(d, 1620, 470, 340, 250, "Contenedor", [
        "Imagen Python 3.14",
        "Dockerfile y compose",
        "La app se ejecuta dentro",
        "del contenedor web",
    ], ROJO_CLARO, ROJO)
    flecha(d, (400, 300), (460, 300), AZUL)
    texto(d, 430, 274, "HTTP", fuente(12, True), AZUL, "mm")
    flecha(d, (880, 330), (940, 330), VERDE)
    texto(d, 910, 304, "dispatch", fuente(12, True), VERDE, "mm")
    flecha(d, (1560, 280), (1620, 280), (166, 92, 24))
    texto(d, 1590, 254, "ORM", fuente(12, True), (166, 92, 24), "mm")
    texto(d, 40, 900, "Patrón MTV: la plantilla presenta, la vista decide según el rol y el modelo guarda Usuario, Servicio y Cuenta.", fuente(16), SUAVE)
    im.save(FIG / "componentes.png", quality=95)
    return FIG / "componentes.png"


def nodo(draw, x, y, w, h, titulo, fill, outline):
    prof = 18
    draw.polygon([(x + prof, y), (x + w + prof, y), (x + w, y + prof), (x, y + prof)], fill=outline)
    draw.polygon([(x + w, y + prof), (x + w + prof, y), (x + w + prof, y + h), (x + w, y + h + prof)], fill=outline)
    redondeado(draw, [x, y + prof, x + w, y + h + prof], 8, fill, outline, 3)
    texto(draw, x + 16, y + prof + 12, titulo, fuente(16, True), outline)


def diagrama_despliegue():
    w, h = 2000, 1100
    im = Image.new("RGB", (w, h), PAPEL)
    d = ImageDraw.Draw(im)
    encabezado(d, w, "DIAGRAMA DE DESPLIEGUE — DOCKER", "El navegador habla con el contenedor cuentas_django_app en el puerto 8000")
    nodo(d, 50, 160, 460, 720, "«device» Equipo del usuario", AZUL_CLARO, AZUL)
    redondeado(d, [80, 250, 470, 430], 10, BLANCO, AZUL, 2)
    texto_centro(d, 275, 310, ["Navegador", "Chrome, Edge o Firefox"], fuente(16, True), TINTA)
    texto_centro(d, 275, 370, ["Inicio, servicios, cuentas", "y panel del administrador"], fuente(14), SUAVE)
    redondeado(d, [80, 470, 470, 650], 10, BLANCO, AZUL, 2)
    texto_centro(d, 275, 540, ["Sesión y CSRF"], fuente(16, True), TINTA)
    texto_centro(d, 275, 590, ["La cookie identifica al usuario", "y con ella se conoce su rol"], fuente(14), SUAVE)

    nodo(d, 760, 140, 1160, 820, "«device» Equipo anfitrión  ·  Docker", (232, 246, 239), VERDE)
    redondeado(d, [820, 240, 1840, 620], 14, BLANCO, VERDE, 3)
    texto(d, 844, 258, "«executionEnvironment» Contenedor cuentas_django_app", fuente(16, True), VERDE)
    bloques = [
        (850, 320, "Imagen", "python:3.14.6-slim"),
        (1180, 320, "Arranque", "migrate y runserver\n0.0.0.0:8000"),
        (1510, 320, "Aplicación", "mysite + cuentas\nDjango 5.2"),
        (850, 470, "Puerto", "8000 publicado\nen el anfitrión"),
        (1180, 470, "Volúmenes", "el proyecto y\ndb.sqlite3"),
        (1510, 470, "Reinicio", "unless-stopped"),
    ]
    for x, y, titulo, cuerpo in bloques:
        redondeado(d, [x, y, x + 290, y + 120], 10, VERDE_CLARO, VERDE, 2)
        texto(d, x + 145, y + 28, titulo, fuente(15, True), VERDE, "mt")
        texto_centro(d, x + 145, y + 74, cuerpo.split("\n"), fuente(14), TINTA)
    redondeado(d, [820, 680, 1840, 880], 14, AMBAR_CLARO, (166, 92, 24), 3)
    texto(d, 844, 704, "«artifact» db.sqlite3", fuente(16, True), (166, 92, 24))
    texto(d, 844, 744, "SQLite con usuarios de autenticación, perfiles (rol), servicios y cuentas (alcance propia o grupo).", fuente(15), TINTA)
    texto(d, 844, 778, "El archivo queda montado fuera del contenedor, así que los datos sobreviven al reinicio.", fuente(15), SUAVE)
    flecha(d, (530, 480), (760, 480), VERDE_OSCURO, 3)
    redondeado(d, [548, 420, 742, 470], 8, BLANCO, VERDE_OSCURO, 2)
    texto(d, 645, 445, "HTTP  :8000", fuente(14, True), VERDE_OSCURO, "mm")
    texto(d, 50, 1020, "También puede correrse con un entorno virtual local. El despliegue definido del proyecto es Docker Compose.", fuente(16), SUAVE)
    im.save(FIG / "despliegue.png", quality=95)
    return FIG / "despliegue.png"


def diagrama_secuencia(nombre, titulo, subtitulo, actores, mensajes, altura):
    w = 1900
    im = Image.new("RGB", (w, altura), PAPEL)
    d = ImageDraw.Draw(im)
    encabezado(d, w, titulo, subtitulo)
    n = len(actores)
    margen = 120
    paso = (w - margen * 2) / (n - 1)
    xs = [margen + i * paso for i in range(n)]
    y0 = 130
    for x, nombre_actor in zip(xs, actores):
        ancho = max(170, medida(d, nombre_actor, fuente(15, True))[0] + 28)
        redondeado(d, [x - ancho / 2, y0, x + ancho / 2, y0 + 46], 8, VERDE_OSCURO, VERDE_OSCURO)
        texto(d, x, y0 + 23, nombre_actor, fuente(15, True), BLANCO, "mm")
        d.line([(x, y0 + 46), (x, altura - 40)], fill=(190, 184, 172), width=2)
    y = 220
    for tipo, *resto in mensajes:
        if tipo == "msg":
            origen, destino, etiqueta = resto
            x1, x2 = xs[origen], xs[destino]
            d.line([(x1, y), (x2, y)], fill=VERDE_OSCURO, width=2)
            punta = x2 - 10 if x2 > x1 else x2 + 10
            flecha(d, (x1, y), (punta, y), VERDE_OSCURO, 2)
            texto(d, (x1 + x2) / 2, y - 16, etiqueta, fuente(13), TINTA, "mm")
            y += 52
        elif tipo == "ret":
            origen, destino, etiqueta = resto
            x1, x2 = xs[origen], xs[destino]
            d.line([(x1, y), (x2, y)], fill=SUAVE, width=2)
            texto(d, (x1 + x2) / 2, y - 16, etiqueta, fuente(13), SUAVE, "mm")
            y += 48
        elif tipo == "alt":
            texto_alt = resto[0]
            redondeado(d, [70, y, w - 70, y + 36], 6, AMBAR_CLARO, (166, 92, 24), 2)
            texto(d, 88, y + 18, texto_alt, fuente(14, True), (120, 72, 12), "lm")
            y += 52
    im.save(FIG / nombre, quality=95)
    return FIG / nombre


def secuencias():
    a = diagrama_secuencia(
        "secuencia_acceso.png",
        "ANEXO A.1  SECUENCIA — REGISTRO E INICIO DE SESIÓN",
        "El alta crea un usuario normal. El inicio de sesión abre el tablero que corresponde al rol.",
        ["Persona", "Vista", "Auth Django", "Perfil Usuario"],
        [
            ("msg", 0, 1, "POST /cuentas/registro/  usuario y contraseña"),
            ("msg", 1, 2, "create_user y validate_password"),
            ("msg", 2, 3, "crear perfil con rol Usuario normal"),
            ("ret", 3, 1, "perfil listo"),
            ("msg", 1, 2, "login y abrir sesión"),
            ("ret", 2, 0, "redirige a Inicio"),
            ("alt", "Si el usuario ya existe, las contraseñas no coinciden o no cumplen las reglas"),
            ("ret", 1, 0, "vuelve al formulario con el mensaje de error"),
            ("alt", "Inicio de sesión en /cuentas/entrar/"),
            ("msg", 0, 1, "POST usuario y contraseña"),
            ("msg", 1, 2, "authenticate"),
            ("alt", "Credenciales válidas"),
            ("msg", 2, 0, "sesión iniciada y redirección a Inicio"),
            ("alt", "Credenciales inválidas"),
            ("ret", 1, 0, "Usuario o contraseña incorrectos"),
        ],
        1180,
    )
    b = diagrama_secuencia(
        "secuencia_usuario.png",
        "ANEXO A.2  SECUENCIA — USUARIO NORMAL",
        "Solo ve sus cuentas, marca como pagadas las suyas y crea cuentas propias.",
        ["Usuario normal", "Vista", "Consulta", "Cuenta"],
        [
            ("msg", 0, 1, "GET /cuentas/"),
            ("msg", 1, 2, "propias del usuario y cuentas del grupo asignadas a él"),
            ("ret", 2, 0, "dos tortas y tabla de pendientes, sin cuentas ajenas"),
            ("msg", 0, 1, "POST /cuentas/nueva/  servicio, mes, valor y fecha"),
            ("msg", 1, 3, "crear con alcance propia y usuario actual"),
            ("ret", 3, 0, "la cuenta no entra en los totales del grupo"),
            ("msg", 0, 1, "POST /cuentas/cuenta/<id>/pagar/"),
            ("msg", 1, 3, "buscar la cuenta del mismo usuario"),
            ("alt", "La cuenta es de ese usuario"),
            ("msg", 3, 0, "pagada = verdadero y vuelve a la lista"),
            ("alt", "La cuenta es de otra persona"),
            ("ret", 1, 0, "404. No se modifica."),
        ],
        1120,
    )
    c = diagrama_secuencia(
        "secuencia_admin.png",
        "ANEXO A.3  SECUENCIA — ADMINISTRADOR",
        "El panel agrega las cuentas del grupo, crea la cuenta y la asigna a un usuario normal.",
        ["Administrador", "Panel", "Perfil", "Cuenta"],
        [
            ("msg", 0, 1, "GET /cuentas/usuarios/"),
            ("msg", 1, 2, "¿el rol es administrador?"),
            ("alt", "No es administrador"),
            ("ret", 1, 0, "403 Sin permiso"),
            ("alt", "Sí es administrador"),
            ("msg", 1, 3, "resumen de todas las cuentas con alcance grupo"),
            ("ret", 3, 0, "torta: pagadas y por pagar, cantidad y valor"),
            ("msg", 0, 1, "POST destino, servicio, mes, valor y fecha"),
            ("msg", 1, 2, "el destino debe ser un usuario normal"),
            ("msg", 1, 3, "crear cuenta con alcance grupo y ese usuario"),
            ("ret", 3, 0, "la cuenta queda asignada y entra al dashboard del grupo"),
            ("alt", "El destino no es un usuario normal o faltan datos"),
            ("ret", 1, 0, "Elige un usuario del grupo y revisa el formulario"),
        ],
        1180,
    )
    return a, b, c


def sombrear_celda(celda, color):
    tc = celda._tc
    pr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    shd.set(qn("w:val"), "clear")
    pr.append(shd)


def poner_bordes(tabla):
    tbl = tabla._tbl
    pr = tbl.tblPr if tbl.tblPr is not None else OxmlElement("w:tblPr")
    borders = OxmlElement("w:tblBorders")
    for borde in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{borde}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "E4DCCF")
        borders.append(el)
    pr.append(borders)


def parrafo(doc, texto_plano, estilo=None, bold=False, size=11, color=None, espacio=8, centro=False, despues=None):
    p = doc.add_paragraph()
    if estilo:
        p.style = estilo
    if centro:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = p.paragraph_format
    pf.space_after = Pt(espacio)
    pf.space_before = Pt(0)
    pf.line_spacing = 1.12
    run = p.add_run(texto_plano)
    run.bold = bold
    run.font.name = "Calibri"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor(*(color or (30, 36, 48)))
    return p


def viñeta(doc, texto_plano):
    p = doc.add_paragraph(style="List Bullet")
    p.clear()
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(texto_plano)
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(30, 36, 48)
    return p


def titulo(doc, texto_plano, nivel):
    p = doc.add_heading(texto_plano, level=nivel)
    for run in p.runs:
        run.font.color.rgb = RGBColor(15, 48, 40)
        run.font.name = "Calibri"
    return p


def tabla(doc, encabezados, filas, anchos):
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.autofit = False
    poner_bordes(t)
    for i, texto_h in enumerate(encabezados):
        celda = t.rows[0].cells[i]
        celda.text = ""
        p = celda.paragraphs[0]
        run = p.add_run(texto_h)
        run.bold = True
        run.font.name = "Calibri"
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(255, 253, 248)
        sombrear_celda(celda, "0F3028")
        celda.width = Cm(anchos[i])
    for fila in filas:
        celdas = t.add_row().cells
        for i, valor in enumerate(fila):
            celdas[i].text = ""
            p = celdas[i].paragraphs[0]
            run = p.add_run(valor)
            run.font.name = "Calibri"
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(30, 36, 48)
            celdas[i].width = Cm(anchos[i])
    doc.add_paragraph()
    return t


def imagen(doc, ruta, ancho=6.4):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run()
    run.add_picture(str(ruta), width=Inches(ancho))


def pie_y_encabezado(doc):
    seccion = doc.sections[0]
    seccion.top_margin = Cm(2.2)
    seccion.bottom_margin = Cm(2)
    seccion.left_margin = Cm(2.2)
    seccion.right_margin = Cm(2.2)
    seccion.header_distance = Cm(0.6)
    seccion.footer_distance = Cm(0.6)
    encabezado_doc = seccion.header
    encabezado_doc.is_linked_to_previous = False
    p = encabezado_doc.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run("Entregable 1  ·  Gestor de Cuentas y Recibos del Hogar")
    run.font.name = "Calibri"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(29, 107, 79)
    pie = seccion.footer
    pie.is_linked_to_previous = False
    p = pie.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("UNINPAHU  ·  Ingeniería de Software  ·  Bogotá D.C.  ·  2026  ·  ")
    run.font.name = "Calibri"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(92, 101, 112)
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run2 = p.add_run()
    run2._r.append(fld_begin)
    run3 = p.add_run()
    run3._r.append(instr)
    run3.font.size = Pt(9)
    run4 = p.add_run()
    run4._r.append(fld_end)


def construir():
    casos = diagrama_casos()
    componentes = diagrama_componentes()
    despliegue = diagrama_despliegue()
    seq1, seq2, seq3 = secuencias()

    doc = Document()
    pie_y_encabezado(doc)
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor(30, 36, 48)

    parrafo(doc, "ENTREGABLE 1", bold=True, size=12, color=(29, 107, 79), centro=True, espacio=4)
    parrafo(doc, "Gestor de Cuentas y Recibos del Hogar", bold=True, size=26, color=(15, 48, 40), centro=True, espacio=4)
    parrafo(doc, "Definición de la solución (SRS) actualizada", size=14, color=(92, 101, 112), centro=True, espacio=16)
    for nombre in ("Kevin Sabogal", "Brayan Sepulveda", "Diana Ramirez"):
        parrafo(doc, nombre, bold=True, size=13, centro=True, espacio=2)
    parrafo(doc, "", espacio=8)
    for linea_txt in (
        "Fundación Universitaria para el Desarrollo Humano",
        "UNINPAHU",
        "Ingeniería de Software",
        "Bogotá D.C.",
        "2026",
    ):
        parrafo(doc, linea_txt, size=12, centro=True, espacio=1, color=(92, 101, 112))

    titulo(doc, "1. Definición de la solución", 1)
    parrafo(
        doc,
        "Este documento actualiza la definición del Gestor de Cuentas y Recibos del Hogar con lo que el sistema ya hace. "
        "La aplicación se llama Cuentas de la casa. El proyecto Django es mysite y la aplicación es cuentas. "
        "Los cambios que se resaltan son la puesta en marcha con Docker, los dos roles y la separación entre cuentas propias y cuentas del grupo.",
    )

    titulo(doc, "1.1 Problema a resolver", 2)
    parrafo(
        doc,
        "En la mayoría de los hogares, el seguimiento de la luz, el agua, el gas, el internet, el arriendo y otras cuentas mensuales se hace de memoria o en papeles que se pierden. "
        "Eso produce olvidos, recargos por mora y la falta de un lugar único para ver qué está pendiente y qué ya se pagó.",
    )
    parrafo(
        doc,
        "Además, en la misma casa conviven dos clases de cuentas. Unas son del grupo, como el arriendo o los servicios que el administrador asigna. "
        "Otras son propias de cada persona y no deben sumarse al total del grupo ni verse entre compañeros. "
        "Si todo queda en un solo listado, el total de la casa se mezcla con gastos personales y cada quien ve cuentas que no le corresponden.",
    )

    titulo(doc, "1.2 Justificación", 2)
    parrafo(
        doc,
        "Una aplicación web centraliza el registro y deja un historial del estado de cada recibo, sin convertirse en una pasarela de pagos. "
        "Separar el rol de administrador del usuario normal permite que una persona organice las cuentas compartidas y que las demás consulten solo lo suyo. "
        "Docker deja el mismo entorno listo en cualquier equipo del curso: misma versión de Python, mismas dependencias y la base de datos montada junto al proyecto.",
    )

    titulo(doc, "1.3 Objetivos", 2)
    parrafo(
        doc,
        "Objetivo general. Desarrollar una aplicación web en la que los miembros de un hogar registren y consulten sus cuentas, con un administrador para las cuentas del grupo y un usuario normal para las cuentas que le corresponden.",
        bold=False,
    )
    parrafo(doc, "Objetivos específicos.", bold=True, espacio=4)
    for item in (
        "Implementar el registro, el inicio de sesión, el perfil y el cambio de contraseña con el sistema de autenticación de Django.",
        "Definir dos roles: Administrador y Usuario normal.",
        "Registrar cuentas ancladas a un usuario, con servicio, mes, valor, fecha de vencimiento, estado y alcance (propia o del grupo).",
        "Ofrecer al usuario normal un inicio con dos gráficas de torta y la tabla de sus cuentas pendientes.",
        "Ofrecer al administrador un panel con los indicadores agregados del grupo, la creación de cuentas y su asignación a usuarios normales.",
        "Empaquetar y ejecutar el sistema con Docker.",
    ):
        viñeta(doc, item)

    titulo(doc, "1.4 Alcance", 2)
    parrafo(doc, "El sistema cubre el registro, el control y el seguimiento de las cuentas. Entra en el alcance:")
    for item in (
        "Autenticación: registro, entrada, salida y cambio de contraseña.",
        "Implementación de Docker: imagen, Compose, migraciones al arrancar y publicación del puerto 8000.",
        "Roles Administrador y Usuario normal.",
        "Para el administrador: crear cuentas del grupo, asignarlas a usuarios normales, contar con el alta de usuarios normales y entrar al panel de dashboard con los indicadores agregados.",
        "Para el usuario normal: consultar los servicios y las cuentas que le fueron asignadas, marcarlas como pagadas y crear cuentas propias.",
        "Operaciones de consulta, creación, edición y borrado sobre las cuentas del propio usuario.",
        "Catálogo compartido de servicios (luz, agua, arriendo y los demás que existan).",
        "Dos tableros en el inicio y la tabla de pendientes con fecha, servicio, valor y tipo de cuenta.",
    ):
        viñeta(doc, item)
    parrafo(
        doc,
        "Fuera del alcance. El sistema no es una pasarela de pagos. No hace transacciones bancarias ni vincula tarjetas. Marcar una cuenta como pagada solo cambia su estado dentro de la aplicación. "
        "Tampoco suma las cuentas propias al total del grupo ni las muestra a los demás usuarios.",
    )

    titulo(doc, "1.5 Tecnologías seleccionadas", 2)
    parrafo(doc, "La solución usa el framework Django sobre Python y deja el despliegue descrito en Docker.")
    tabla(
        doc,
        ["Capa", "Tecnología", "Uso en el proyecto"],
        [
            ["Backend", "Python y Django 5.2", "Vistas, autenticación, modelos y panel"],
            ["Base de datos", "SQLite", "Archivo db.sqlite3 con usuarios, servicios y cuentas"],
            ["Frontend", "HTML5 y CSS3", "Formularios, tableros de torta y tablas, sin framework de interfaz"],
            ["Versiones", "Git y GitHub", "Repositorio del proyecto"],
            ["Despliegue", "Docker y Docker Compose", "Contenedor cuentas_django_app en el puerto 8000"],
        ],
        [4, 5.5, 7],
    )
    parrafo(doc, "Implementación de Docker.", bold=True, espacio=4)
    parrafo(
        doc,
        "El archivo dockerfile parte de la imagen python:3.14.6-slim, instala las dependencias de requirements.txt y deja el directorio de trabajo en /app. "
        "Al iniciar el contenedor ejecuta las migraciones y levanta el servidor de desarrollo en 0.0.0.0:8000.",
    )
    parrafo(
        doc,
        "docker-compose.yml define el servicio web, con el nombre de contenedor cuentas_django_app. Publica el puerto 8000 del contenedor en el puerto 8000 del equipo. "
        "Monta el proyecto completo y el archivo db.sqlite3, de modo que el código y los datos se conservan fuera de la imagen. La política de reinicio es unless-stopped. "
        "En local también puede ejecutarse con un entorno virtual, las migraciones y runserver; el despliegue definido para entregar el sistema es Docker.",
    )

    titulo(doc, "1.6 Roles", 2)
    parrafo(doc, "Solo existen dos roles, guardados en el perfil Usuario que acompaña a cada cuenta de autenticación.")
    tabla(
        doc,
        ["Rol", "Cómo se obtiene", "Qué habilita"],
        [
            [
                "Administrador",
                "Perfil de un usuario staff o superuser",
                "Crear cuentas del grupo, asignarlas a usuarios normales, ver el alta de esos usuarios y abrir el panel con los indicadores agregados",
            ],
            [
                "Usuario normal",
                "Todo registro nuevo",
                "Consultar sus servicios y cuentas asignadas, marcarlas como pagadas y crear cuentas propias",
            ],
        ],
        [3.5, 5, 8],
    )
    parrafo(doc, "Administrador.", bold=True, espacio=4)
    parrafo(
        doc,
        "El administrador es el único que ve el conjunto de las cuentas del grupo. En /cuentas/usuarios/ encuentra el dashboard: una gráfica de torta con las cuentas del grupo pagadas y por pagar, en cantidad y en valor. "
        "Desde el mismo panel crea una cuenta, elige el usuario normal de destino y la asigna. Esa cuenta queda con alcance grupo, a nombre de esa persona, y entra en los indicadores agregados. "
        "Al elegir un usuario se abre el detalle de sus cuentas del grupo y el estado de cada una. Si un usuario normal intenta abrir el panel, la aplicación responde sin permiso.",
    )
    parrafo(
        doc,
        "La creación de usuarios normales queda habilitada en el registro. Quien se registra recibe el rol Usuario normal y aparece en el grupo del administrador, listo para recibir cuentas. "
        "El administrador no comparte su rol con esos registros: el alta no crea otros administradores.",
    )
    parrafo(doc, "Usuario normal.", bold=True, espacio=4)
    parrafo(
        doc,
        "En el inicio ve dos tableros. El de cuentas propias reúne las que él mismo creó. El de cuentas del grupo reúne solo las que el administrador le asignó. Debajo, la tabla de pendientes muestra fecha, servicio, valor y si la cuenta es propia o del grupo. "
        "No aparecen las cuentas de las otras personas. Puede consultar el catálogo de servicios y las cuentas de esos servicios que son suyas, marcar como pagada una cuenta desde la lista o desde el detalle, y crear cuentas nuevas. "
        "Lo que crea queda como cuenta propia: solo él la ve y no se suma a las cuentas del grupo. Editar una cuenta no cambia el estado de pagada; ese cambio se hace con el botón Marcar como pagada.",
    )

    titulo(doc, "1.7 Información general del dominio", 2)
    parrafo(doc, "Tres modelos sostienen el sistema.")
    tabla(
        doc,
        ["Modelo", "Datos", "Regla"],
        [
            ["Usuario", "Usuario de autenticación y rol", "Un perfil por persona. El rol es administrador o usuario normal"],
            ["Servicio", "Nombre", "Catálogo compartido. No pertenece a una sola persona"],
            ["Cuenta", "Usuario, alcance, servicio, mes, valor, vencimiento y pagada", "Alcance propia o grupo. Siempre tiene un dueño"],
        ],
        [3.2, 6.5, 6.8],
    )
    parrafo(
        doc,
        "Una cuenta propia la crea el usuario y solo entra en su tablero. Una cuenta del grupo la crea el administrador, queda asignada a un usuario normal y solo el administrador ve el total de todas ellas. "
        "El usuario normal ve, de ese conjunto, únicamente las que están a su nombre.",
    )

    titulo(doc, "2. Diagramas UML", 1)
    parrafo(
        doc,
        "Se actualizan el diagrama de casos de uso, el de componentes y el de despliegue. "
        "El diagrama de secuencia no se inserta en esta sección: describe la interacción en el tiempo y se referencia como Anexo A.",
    )

    titulo(doc, "2.1 Diagrama de casos de uso", 2)
    parrafo(
        doc,
        "El usuario normal consulta, crea y marca sus cuentas. El administrador crea cuentas del grupo, las asigna, crea el contexto de usuarios normales y lee el dashboard agregado. "
        "Crear una cuenta incluye la validación del servicio, el valor y la fecha.",
    )
    imagen(doc, casos, 6.5)
    parrafo(doc, "Figura 1. Casos de uso del administrador y del usuario normal.", size=10, color=(92, 101, 112), centro=True, espacio=12)

    titulo(doc, "2.2 Diagrama de componentes", 2)
    parrafo(
        doc,
        "La arquitectura sigue el patrón MTV de Django. El navegador habla con mysite, mysite entrega el control a la aplicación cuentas y los modelos persisten en SQLite. "
        "El rol vive en el perfil Usuario y el alcance vive en Cuenta. El contenedor Docker envuelve esa misma aplicación; no cambia las responsabilidades de cada componente.",
    )
    imagen(doc, componentes, 6.5)
    parrafo(doc, "Figura 2. Componentes de la aplicación y de su contenedor.", size=10, color=(92, 101, 112), centro=True, espacio=12)

    titulo(doc, "2.3 Diagrama de despliegue", 2)
    parrafo(
        doc,
        "El despliegue de referencia es Docker. El equipo del usuario abre el navegador contra el puerto 8000. "
        "En el equipo anfitrión, Docker Compose levanta el contenedor cuentas_django_app, aplica las migraciones y publica el servidor. "
        "La base SQLite viaja en un volumen, separada del ciclo de vida de la imagen.",
    )
    imagen(doc, despliegue, 6.5)
    parrafo(doc, "Figura 3. Despliegue con Docker Compose y volumen de SQLite.", size=10, color=(92, 101, 112), centro=True, espacio=12)

    titulo(doc, "3. Backlog", 1)
    parrafo(doc, "Las historias quedan con el estado que tienen en el sistema actual.")
    tabla(
        doc,
        ["ID", "Historia", "Prioridad", "Estado"],
        [
            ["US-01", "Como persona, quiero registrarme e iniciar sesión, para proteger las cuentas del hogar.", "Alta", "Implementado"],
            ["US-02", "Como usuario normal, quiero crear una cuenta propia, para llevar un gasto que no entra en el grupo.", "Alta", "Implementado"],
            ["US-03", "Como usuario normal, quiero ver en el inicio mis pendientes, para saber qué me toca pagar.", "Alta", "Implementado"],
            ["US-04", "Como usuario normal, quiero marcar una cuenta como pagada desde la lista, para no entrar a editarla.", "Alta", "Implementado"],
            ["US-05", "Como usuario normal, quiero consultar los servicios y las cuentas que me asignaron.", "Alta", "Implementado"],
            ["US-06", "Como usuario, quiero editar o eliminar una cuenta mía, para corregir un dato.", "Media", "Implementado"],
            ["US-07", "Como hogar, quiero dos roles, administrador y usuario normal, para separar quién organiza el grupo.", "Alta", "Implementado"],
            ["US-08", "Como administrador, quiero crear una cuenta y asignarla a un usuario normal.", "Alta", "Implementado"],
            ["US-09", "Como administrador, quiero un dashboard con los indicadores agregados del grupo.", "Alta", "Implementado"],
            ["US-10", "Como administrador, quiero que el alta deje usuarios normales y verlos en mi panel.", "Alta", "Implementado"],
            ["US-11", "Como equipo, quiero ejecutar el sistema con Docker, para no depender de la instalación manual.", "Alta", "Implementado"],
        ],
        [2, 9.2, 2.6, 2.8],
    )

    titulo(doc, "4. Repositorio", 1)
    parrafo(doc, "https://github.com/DazhyGM/PROYECTO_PYTHON.git", bold=True)
    parrafo(
        doc,
        "Para levantarlo con Docker: docker compose up --build. La aplicación queda en http://127.0.0.1:8000/cuentas/. "
        "El inicio pide sesión. El panel de usuarios solo responde al rol Administrador.",
    )

    titulo(doc, "Anexo A. Diagrama de secuencia", 1)
    parrafo(
        doc,
        "Este anexo complementa la sección 2. No reemplaza los diagramas de casos de uso, componentes ni despliegue. "
        "Muestra el orden de los mensajes en el registro, en el trabajo del usuario normal y en el panel del administrador.",
    )
    titulo(doc, "A.1 Registro e inicio de sesión", 2)
    parrafo(doc, "El registro crea la cuenta de acceso y el perfil con rol Usuario normal. El inicio de sesión redirige al inicio, que ya respeta ese rol.")
    imagen(doc, seq1, 6.5)
    parrafo(doc, "Figura A.1. Secuencia de registro e inicio de sesión.", size=10, color=(92, 101, 112), centro=True, espacio=12)

    titulo(doc, "A.2 Usuario normal", 2)
    parrafo(doc, "El inicio arma las dos tortas con las cuentas de esa persona. Crear una cuenta la marca como propia. Marcar como pagada solo procede si la cuenta le pertenece.")
    imagen(doc, seq2, 6.5)
    parrafo(doc, "Figura A.2. Secuencia del usuario normal.", size=10, color=(92, 101, 112), centro=True, espacio=12)

    titulo(doc, "A.3 Administrador", 2)
    parrafo(doc, "El panel rechaza a quien no tiene el rol. Si lo tiene, calcula los indicadores de todas las cuentas del grupo y permite crear una cuenta asignada a un usuario normal.")
    imagen(doc, seq3, 6.5)
    parrafo(doc, "Figura A.3. Secuencia del administrador.", size=10, color=(92, 101, 112), centro=True, espacio=8)

    destino = ROOT / "Entregable 1 - Gestor de Cuentas y Recibos.docx"
    doc.core_properties.title = "Entregable 1 - Gestor de Cuentas y Recibos del Hogar"
    doc.core_properties.subject = "Definición de la solución actualizada con Docker, roles y anexo de secuencia"
    doc.core_properties.author = "Kevin Sabogal, Brayan Sepulveda, Diana Ramirez"
    doc.core_properties.category = "UNINPAHU"
    doc.save(destino)
    return destino


if __name__ == "__main__":
    print(construir())
