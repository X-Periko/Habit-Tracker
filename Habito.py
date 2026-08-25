from datetime import date
import database


class Habito:
    def __init__(self, nombre, frecuencia, duracion, cumplido=False, ultima_actualizacion=None, id=None):
        self.id = id
        self.nombre = nombre
        self.frecuencia = frecuencia
        self.duracion = duracion
        self.cumplido = cumplido
        self.ultima_actualizacion = ultima_actualizacion

    def imprimir(self) -> str:
        frecuencia_texto = "diaria" if self.frecuencia == "d" else "semanal" if self.frecuencia == "s" else "mensual"
        estado = "Cumplido" if self.cumplido else "Sin cumplir"
        return (f"Hábito: {self.nombre}\n"
                f"    - Frecuencia: {frecuencia_texto}\n"
                f"    - Duración: {self.duracion} minutos\n"
                f"    - {estado}\n")

    def guardar(self):
        """Inserta el hábito si es nuevo (self.id is None), o actualiza la fila existente."""
        with database.conectar() as conn:
            if self.id is None:
                cursor = conn.execute(
                    "INSERT INTO habitos (nombre, frecuencia, duracion, cumplido, ultima_actualizacion) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (self.nombre, self.frecuencia, self.duracion, int(self.cumplido), self.ultima_actualizacion)
                )
                self.id = cursor.lastrowid
            else:
                conn.execute(
                    "UPDATE habitos SET nombre=?, frecuencia=?, duracion=?, cumplido=?, ultima_actualizacion=? "
                    "WHERE id=?",
                    (self.nombre, self.frecuencia, self.duracion, int(self.cumplido),
                     self.ultima_actualizacion, self.id)
                )

    def eliminar(self):
        if self.id is not None:
            with database.conectar() as conn:
                conn.execute("DELETE FROM habitos WHERE id=?", (self.id,))

    def marcar_cumplido(self):
        self.cumplido = True
        self.ultima_actualizacion = date.today().isoformat()
        self.guardar()

    @staticmethod
    def cargar_todos():
        with database.conectar() as conn:
            filas = conn.execute("SELECT * FROM habitos ORDER BY id").fetchall()
        return [
            Habito(
                nombre=f["nombre"],
                frecuencia=f["frecuencia"],
                duracion=f["duracion"],
                cumplido=bool(f["cumplido"]),
                ultima_actualizacion=f["ultima_actualizacion"],
                id=f["id"],
            )
            for f in filas
        ]