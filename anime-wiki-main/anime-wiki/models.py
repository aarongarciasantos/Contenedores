class Personaje:
    def __init__(self, nombre, anime, descripcion, habilidades):
        self.__nombre = nombre
        self.__anime = anime
        self.__descripcion = descripcion
        self.__habilidades = habilidades

        self.set_nombre(nombre)
        self.set_anime(anime)
        self.set_descripcion(descripcion)
        self.set_habilidades(habilidades)

    def get_nombre(self):
        return self.__nombre

    def set_nombre(self, nombre):
        nombre = nombre.strip()
        if len(nombre) < 2 or len(nombre) > 50:
            raise ValueError("El nombre tiene que tener entre 2 y 50 letras.")
        self.__nombre = nombre

    def get_anime(self):
        return self.__anime

    def set_anime(self, anime):
        anime = anime.strip()
        if len(anime) < 2 or len(anime) > 60:
            raise ValueError("El nombre del anime no es correcto.")
        self.__anime = anime

    def get_descripcion(self):
        return self.__descripcion

    def set_descripcion(self, descripcion):
        descripcion = descripcion.strip()
        if len(descripcion) < 5 or len(descripcion) > 300:
            raise ValueError("La descripción debe tener entre 5 y 300 letras.")
        self.__descripcion = descripcion

    def get_habilidades(self):
        return self.__habilidades

    def set_habilidades(self, habilidades):
        habilidades = habilidades.strip()
        if len(habilidades) < 2 or len(habilidades) > 150:
            raise ValueError("Escribe las habilidades del personaje.")
        self.__habilidades = habilidades

    def to_dict(self):
        return {
            "nombre": self.__nombre,
            "anime": self.__anime,
            "descripcion": self.__descripcion,
            "habilidades": self.__habilidades,
        }
