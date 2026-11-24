
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from models import Personaje

app = Flask(__name__)
app.secret_key = "wiki-anime-clave"

MAX_PERSONAJES = 5


TRIGGER = [
    {"slug": "ryuko", "nombre": "Ryuko Matoi", "anime": "Kill la Kill",
     "descripcion": "Una estudiante que busca al responsable de la muerte de su padre.",
     "habilidades": "Senketsu y espada de media tijera"},
    {"slug": "satsuki", "nombre": "Satsuki Kiryuin", "anime": "Kill la Kill",
     "descripcion": "La presidenta del consejo de la Academia Honnouji.",
     "habilidades": "Espada Bakuzan y Junketsu"},
    {"slug": "akko", "nombre": "Akko Kagari", "anime": "Little Witch Academia",
     "descripcion": "Una chica que quiere convertirse en una gran bruja.",
     "habilidades": "Magia y bastón Shiny Rod"},
    {"slug": "lio", "nombre": "Lio Fotia", "anime": "Promare",
     "descripcion": "El líder de un grupo de personas que tienen poderes de fuego.",
     "habilidades": "Control del fuego"},
    {"slug": "michiru", "nombre": "Michiru Kagemori", "anime": "BNA",
     "descripcion": "Una chica que puede transformarse en un animal.",
     "habilidades": "Transformación y fuerza"},
]


DAI_GURREN = [
    {"slug": "simon", "nombre": "Simon", "anime": "Tengen Toppa Gurren Lagann",
     "descripcion": "Un chico que encuentra el robot Lagann y se une a la lucha.",
     "habilidades": "Pilotar Lagann y poder espiral"},
    {"slug": "kamina", "nombre": "Kamina", "anime": "Tengen Toppa Gurren Lagann",
     "descripcion": "Es uno de los fundadores del Equipo Gurren y anima al grupo.",
     "habilidades": "Lucha con espada y pilotaje"},
    {"slug": "yoko", "nombre": "Yoko Littner", "anime": "Tengen Toppa Gurren Lagann",
     "descripcion": "Una luchadora que ayuda a Simon y Kamina.",
     "habilidades": "Buena puntería y manejo de rifle"},
    {"slug": "nia", "nombre": "Nia Teppelin", "anime": "Tengen Toppa Gurren Lagann",
     "descripcion": "Una chica que conoce a Simon y se une al grupo.",
     "habilidades": "Ayudar y apoyar a sus compañeros"},
    {"slug": "viral", "nombre": "Viral", "anime": "Tengen Toppa Gurren Lagann",
     "descripcion": "Un guerrero que al principio es enemigo del Equipo Gurren.",
     "habilidades": "Lucha y pilotaje de robots"},
    {"slug": "kittan", "nombre": "Kittan Bachika", "anime": "Tengen Toppa Gurren Lagann",
     "descripcion": "El líder de los Hermanos Negros.",
     "habilidades": "Manejo de armas y pilotaje"},
    {"slug": "leeron", "nombre": "Leeron", "anime": "Tengen Toppa Gurren Lagann",
     "descripcion": "Es el mecánico y el técnico del grupo.",
     "habilidades": "Reparar robots y máquinas"},
]

CATALOGOS = {
    "trigger": TRIGGER,
    "dai-gurren": DAI_GURREN
}


def leer_personajes():
    return session.get("personajes", [])


def guardar_personajes(personajes):
    session["personajes"] = personajes


def siguiente_id(personajes):
    numero = 1

    for personaje in personajes:
        if int(personaje["id"]) >= numero:
            numero = int(personaje["id"]) + 1

    return str(numero)


def nombre_repetido(nombre, anime, personajes, id_actual=None):
    for personaje in personajes:
        mismo_nombre = personaje["nombre"].lower() == nombre.lower()
        mismo_anime = personaje["anime"].lower() == anime.lower()
        otro_personaje = personaje["id"] != id_actual

        if mismo_nombre and mismo_anime and otro_personaje:
            return True

    return False


def datos_formulario():
    return {
        "nombre": request.form.get("nombre", "").strip(),
        "anime": request.form.get("anime", "").strip(),
        "descripcion": request.form.get("descripcion", "").strip(),
        "habilidades": request.form.get("habilidades", "").strip(),
    }


def mostrar_formulario(datos=None, titulo="Añadir personaje"):
    if datos is None:
        datos = {}

    return render_template(
        "formulario.html",
        personaje=datos,
        titulo=titulo
    )


@app.route("/")
def inicio():
    personajes = leer_personajes()

    return render_template(
        "index.html",
        total=len(personajes),
        max_personajes=MAX_PERSONAJES,
        trigger=TRIGGER,
        dai_gurren=DAI_GURREN,
        guardados=[
            (p["nombre"].lower(), p["anime"].lower())
            for p in personajes
        ],
    )


@app.route("/buscar")
def buscar():
    nombre = request.args.get("q", "")
    lista = []

    for grupo in CATALOGOS:
        for personaje in CATALOGOS[grupo]:
            if nombre.lower() in personaje["nombre"].lower():
                lista.append(personaje)

    return render_template(
        "buscar.html",
        resultados=lista,
        consulta=nombre
    )


@app.route("/personajes")
def lista_personajes():
    return render_template(
        "personajes.html",
        personajes=leer_personajes()
    )


@app.route("/personajes/nuevo", methods=["GET", "POST"])
def nuevo_personaje():
    if request.method == "GET":
        return mostrar_formulario()

    datos = datos_formulario()
    personajes = leer_personajes()

    try:
        nuevo = Personaje(
            datos["nombre"],
            datos["anime"],
            datos["descripcion"],
            datos["habilidades"]
        )

        if len(personajes) >= MAX_PERSONAJES:
            raise ValueError("Solo puedes guardar cinco personajes.")

        if nombre_repetido(
            datos["nombre"],
            datos["anime"],
            personajes
        ):
            raise ValueError("Ese personaje ya está guardado.")

        ficha = nuevo.to_dict()
        ficha["id"] = siguiente_id(personajes)

        personajes.append(ficha)
        guardar_personajes(personajes)

        flash("Personaje añadido.")
        return redirect(url_for("lista_personajes"))

    except ValueError as error:
        flash(str(error))
        return mostrar_formulario(datos), 400


@app.route("/catalogo/<grupo>/<slug>/anadir", methods=["POST"])
def anadir_catalogo(grupo, slug):
    if grupo not in CATALOGOS:
        abort(404)

    elegido = None

    for personaje in CATALOGOS[grupo]:
        if personaje["slug"] == slug:
            elegido = personaje

    if elegido is None:
        abort(404)

    personajes = leer_personajes()

    if len(personajes) >= MAX_PERSONAJES:
        flash("Tu colección ya tiene cinco personajes.")

    elif nombre_repetido(
        elegido["nombre"],
        elegido["anime"],
        personajes
    ):
        flash("Ese personaje ya está guardado.")

    else:
        nuevo = Personaje(
            elegido["nombre"],
            elegido["anime"],
            elegido["descripcion"],
            elegido["habilidades"]
        )

        ficha = nuevo.to_dict()
        ficha["id"] = siguiente_id(personajes)

        personajes.append(ficha)
        guardar_personajes(personajes)

        flash("Personaje añadido a tu colección.")

    return redirect(url_for("inicio") + "#" + grupo)


@app.route("/personajes/<int:personaje_id>")
def detalle_personaje(personaje_id):
    for personaje in leer_personajes():
        if int(personaje["id"]) == personaje_id:
            return render_template(
                "detalle.html",
                personaje=personaje
            )

    abort(404)


@app.route("/personajes/<int:personaje_id>/editar", methods=["GET", "POST"])
def editar_personaje(personaje_id):
    personajes = leer_personajes()
    personaje = None

    for p in personajes:
        if int(p["id"]) == personaje_id:
            personaje = p

    if personaje is None:
        abort(404)

    if request.method == "GET":
        return mostrar_formulario(
            personaje,
            "Editar personaje"
        )

    datos = datos_formulario()

    try:
        actualizado = Personaje(
            datos["nombre"],
            datos["anime"],
            datos["descripcion"],
            datos["habilidades"]
        )

        if nombre_repetido(
            datos["nombre"],
            datos["anime"],
            personajes,
            personaje["id"]
        ):
            raise ValueError("Ya existe ese personaje.")

        ficha = actualizado.to_dict()
        ficha["id"] = personaje["id"]

        for i in range(len(personajes)):
            if personajes[i]["id"] == personaje["id"]:
                personajes[i] = ficha

        guardar_personajes(personajes)
        flash("Personaje cambiado.")

        return redirect(
            url_for(
                "detalle_personaje",
                personaje_id=personaje_id
            )
        )

    except ValueError as error:
        flash(str(error))
        datos["id"] = str(personaje_id)

        return mostrar_formulario(
            datos,
            "Editar personaje"
        ), 400


@app.route("/personajes/<int:personaje_id>/eliminar", methods=["POST"])
def eliminar_personaje(personaje_id):
    personajes = leer_personajes()
    nuevos = []

    for personaje in personajes:
        if int(personaje["id"]) != personaje_id:
            nuevos.append(personaje)

    if len(nuevos) == len(personajes):
        abort(404)

    guardar_personajes(nuevos)
    flash("Personaje eliminado.")

    return redirect(url_for("lista_personajes"))


@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
