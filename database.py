import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "habitos.db"


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acceder a las columnas por nombre: fila["nombre"]
    return conn


def crear_tablas():
    with conectar() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS habitos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                frecuencia TEXT NOT NULL,       -- 'd' diario, 's' semanal, 'm' mensual
                duracion INTEGER NOT NULL,      -- minutos
                cumplido INTEGER NOT NULL DEFAULT 0,   -- 0/1 (SQLite no tiene booleano nativo)
                ultima_actualizacion TEXT       -- fecha ISO (YYYY-MM-DD) de la última vez marcado
            )
        """)


if __name__ == "__main__":
    crear_tablas()
    print(f"Base de datos creada en: {DB_PATH}")