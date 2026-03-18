class Habito:
    def __init__(self, nombre, frecuencia, duración, id):
        self.nombre = nombre
        self.frecuencia = frecuencia
        self.duración = duración
        self.cumplido = False
        self.id = id

    def imprimir(self):
        return(f"{self.nombre} {self.duración} {self.frecuencia}")
    
    def guardar_habito(self):
        with open("data.txt", "a", encoding="utf-8") as file:
            file.write(f"{self.imprimir()}")
    
    def asignar_id(self):
        with open("data.txt", "r", encoding="utf-8") as file:
            for linea in file:
                self.id +=1

    def eliminar_habito(self):
        with open("data.txt", "w", encoding="utf-8") as file:
            lines = file.readlines()
            del lines[self.id]
            file.writelines(lines)