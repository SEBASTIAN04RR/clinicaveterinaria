import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# Conectar a la base de datos SQLite
conn = sqlite3.connect('clinica_veterinaria.db')
cursor = conn.cursor()

# Crear tabla de medicamentos si no existe
cursor.execute('''CREATE TABLE IF NOT EXISTS medicamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE,
                    cantidad INTEGER,
                    precio REAL)''')
conn.commit()

# Clases de Datos
class Propietario:
    def __init__(self, nombre, contacto):
        self.nombre = nombre
        self.contacto = contacto

class Paciente:
    def __init__(self, nombre, especie, raza, edad, propietario):
        self.nombre = nombre
        self.especie = especie
        self.raza = raza
        self.edad = edad
        self.propietario = propietario
        self.historial_medico = []

    def actualizar_info(self, nombre, especie, raza, edad, propietario):
        self.nombre = nombre
        self.especie = especie
        self.raza = raza
        self.edad = edad
        self.propietario = propietario

    def agregar_consulta(self, consulta):
        self.historial_medico.append(consulta)

class Cita:
    def __init__(self, paciente, fecha, hora):
        self.paciente = paciente
        self.fecha = fecha
        self.hora = hora

class Consulta:
    def __init__(self, paciente, diagnostico, tratamiento, medicamentos):
        self.paciente = paciente
        self.diagnostico = diagnostico
        self.tratamiento = tratamiento
        self.medicamentos = medicamentos

class Medicamento:
    def __init__(self, nombre, cantidad, precio):
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio

    def actualizar_inventario(self, cantidad):
        self.cantidad += cantidad

class ClinicaVeterinaria:
    def __init__(self):
        self.pacientes = []
        self.citas = []

    def registrar_paciente(self, paciente):
        self.pacientes.append(paciente)

    def actualizar_paciente(self, paciente, nombre, especie, raza, edad, propietario):
        paciente.actualizar_info(nombre, especie, raza, edad, propietario)

    def programar_cita(self, cita):
        self.citas.append(cita)

    def registrar_medicamento(self, medicamento):
        cursor.execute("INSERT OR IGNORE INTO medicamentos (nombre, cantidad, precio) VALUES (?, ?, ?)",
                       (medicamento.nombre, medicamento.cantidad, medicamento.precio))
        cursor.execute("UPDATE medicamentos SET cantidad = cantidad + ?, precio = ? WHERE nombre = ?",
                       (medicamento.cantidad, medicamento.precio, medicamento.nombre))
        conn.commit()

    def actualizar_medicamento(self, nombre, cantidad, precio):
        cursor.execute("UPDATE medicamentos SET cantidad = ?, precio = ? WHERE nombre = ?",
                       (cantidad, precio, nombre))
        conn.commit()

    def vender_medicamento(self, nombre_medicamento, cantidad_vendida):
        cursor.execute("SELECT cantidad FROM medicamentos WHERE nombre = ?", (nombre_medicamento,))
        resultado = cursor.fetchone()
        if resultado:
            cantidad_actual = resultado[0]
            if cantidad_actual >= cantidad_vendida:
                nueva_cantidad = cantidad_actual - cantidad_vendida
                cursor.execute("UPDATE medicamentos SET cantidad = ? WHERE nombre = ?",
                               (nueva_cantidad, nombre_medicamento))
                conn.commit()
                return True
            else:
                return False
        return None

    def obtener_medicamentos(self):
        cursor.execute("SELECT nombre, cantidad, precio FROM medicamentos")
        return cursor.fetchall()

    def generar_reporte_pacientes(self):
        reporte = "Reporte de Pacientes Atendidos:\n"
        for paciente in self.pacientes:
            reporte += f"Nombre: {paciente.nombre}, Especie: {paciente.especie}, Raza: {paciente.raza}, Edad: {paciente.edad}, Propietario: {paciente.propietario.nombre}\n"
        return reporte

    def generar_reporte_citas(self):
        reporte = "Reporte de Citas Programadas:\n"
        for cita in self.citas:
            reporte += f"Paciente: {cita.paciente.nombre}, Fecha: {cita.fecha}, Hora: {cita.hora}\n"
        return reporte

    def generar_reporte_ventas(self):
        reporte = "Reporte de Ventas de Medicamentos:\n"
        cursor.execute("SELECT nombre, cantidad, precio FROM medicamentos")
        medicamentos = cursor.fetchall()
        for medicamento in medicamentos:
            reporte += f"Nombre: {medicamento[0]}, Cantidad: {medicamento[1]}, Precio: {medicamento[2]}\n"
        return reporte

    def alerta_inventario_bajo(self):
        alertas = []
        cursor.execute("SELECT nombre FROM medicamentos WHERE cantidad <= 10")
        medicamentos = cursor.fetchall()
        for medicamento in medicamentos:
            alertas.append(f"El medicamento {medicamento[0]} tiene un inventario bajo.")
        return alertas

# Interfaz Gráfica
class Aplicacion:
    def __init__(self, root, clinica):
        self.root = root
        self.clinica = clinica
        self.root.title("Clínica Veterinaria Cute Pets")
        self.root.geometry("400x300")

        self.estilo_widgets()

        self.tab_control = ttk.Notebook(root)
        self.tab_login = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_login, text="Login Empleados")
        self.tab_control.pack(expand=1, fill="both")

        self.crear_tab_login()

    def estilo_widgets(self):
        style = ttk.Style()
        style.configure('TButton', padding=6, relief="flat", background="#FFDDC1", borderwidth=0, focuscolor="#FFDDC1")
        style.map('TButton', background=[('active', '#FFABAB')])
        style.configure('TFrame', background='#FFE0B5')
        style.configure('TLabel', background='#FFE0B5', font=('Arial', 12))
        style.configure('TEntry', font=('Arial', 12))
        self.root.option_add('*TEntry*Font', 'Arial 12')
        self.root.option_add('*TButton*Font', 'Arial 12')
        self.root.option_add('*TLabel*Font', 'Arial 12')

    def crear_tab_login(self):
        # Crear GUI para login de empleados
        frame = ttk.Frame(self.tab_login)
        frame.pack(expand=True)

        ttk.Label(frame, text="Usuario").grid(row=0, column=0, pady=10, padx=5)
        self.usuario_entry = ttk.Entry(frame)
        self.usuario_entry.grid(row=0, column=1, pady=10, padx=5)

        ttk.Label(frame, text="Contraseña").grid(row=1, column=0, pady=10, padx=5)
        self.contrasena_entry = ttk.Entry(frame, show="*")
        self.contrasena_entry.grid(row=1, column=1, pady=10, padx=5)

        ttk.Button(frame, text="Ingresar", command=self.verificar_login).grid(row=2, columnspan=2, pady=20)

    def crear_tabs(self):
        self.tab_pacientes = ttk.Frame(self.tab_control)
        self.tab_citas = ttk.Frame(self.tab_control)
        self.tab_reportes = ttk.Frame(self.tab_control)
        self.tab_inventario = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_pacientes, text="Pacientes")
        self.tab_control.add(self.tab_citas, text="Citas")
        self.tab_control.add(self.tab_reportes, text="Reportes")
        self.tab_control.add(self.tab_inventario, text="Inventario")
        self.crear_tab_pacientes()
        self.crear_tab_citas()
        self.crear_tab_reportes()
        self.crear_tab_inventario()

    def crear_tab_pacientes(self):
        # Crear GUI para gestionar pacientes
        frame = ttk.Frame(self.tab_pacientes)
        frame.pack(padx=20, pady=20)

        ttk.Label(frame, text="Nombre de la mascota").grid(row=0, column=0, pady=5, padx=5)
        self.nombre_paciente_entry = ttk.Entry(frame)
        self.nombre_paciente_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Especie").grid(row=1, column=0, pady=5, padx=5)
        self.especie_paciente_entry = ttk.Entry(frame)
        self.especie_paciente_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Raza").grid(row=2, column=0, pady=5, padx=5)
        self.raza_paciente_entry = ttk.Entry(frame)
        self.raza_paciente_entry.grid(row=2, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Edad").grid(row=3, column=0, pady=5, padx=5)
        self.edad_paciente_entry = ttk.Entry(frame)
        self.edad_paciente_entry.grid(row=3, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Nombre del propietario").grid(row=4, column=0, pady=5, padx=5)
        self.propietario_nombre_entry = ttk.Entry(frame)
        self.propietario_nombre_entry.grid(row=4, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Contacto del propietario").grid(row=5, column=0, pady=5, padx=5)
        self.propietario_contacto_entry = ttk.Entry(frame)
        self.propietario_contacto_entry.grid(row=5, column=1, pady=5, padx=5)

        ttk.Button(frame, text="Registrar Paciente", command=self.registrar_paciente).grid(row=6, columnspan=2, pady=10)
        ttk.Button(frame, text="Actualizar Paciente", command=self.actualizar_paciente).grid(row=7, columnspan=2, pady=10)

    def crear_tab_citas(self):
        # Crear GUI para gestionar citas
        frame = ttk.Frame(self.tab_citas)
        frame.pack(padx=20, pady=20)

        ttk.Label(frame, text="Nombre del paciente").grid(row=0, column=0, pady=5, padx=5)
        self.nombre_cita_entry = ttk.Entry(frame)
        self.nombre_cita_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Fecha (dd/mm/yyyy)").grid(row=1, column=0, pady=5, padx=5)
        self.fecha_cita_entry = ttk.Entry(frame)
        self.fecha_cita_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Hora (hh:mm)").grid(row=2, column=0, pady=5, padx=5)
        self.hora_cita_entry = ttk.Entry(frame)
        self.hora_cita_entry.grid(row=2, column=1, pady=5, padx=5)

        ttk.Button(frame, text="Programar Cita", command=self.programar_cita).grid(row=3, columnspan=2, pady=10)

    def crear_tab_reportes(self):
        # Crear GUI para generar reportes
        frame = ttk.Frame(self.tab_reportes)
        frame.pack(padx=20, pady=20)

        ttk.Button(frame, text="Reporte de Pacientes", command=self.generar_reporte_pacientes).grid(row=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Reporte de Citas", command=self.generar_reporte_citas).grid(row=1, columnspan=2, pady=10)
        ttk.Button(frame, text="Reporte de Ventas", command=self.generar_reporte_ventas).grid(row=2, columnspan=2, pady=10)

    def crear_tab_inventario(self):
        # Crear GUI para gestionar inventario de medicamentos
        frame = ttk.Frame(self.tab_inventario)
        frame.pack(padx=20, pady=20)

        ttk.Label(frame, text="Nombre del medicamento").grid(row=0, column=0, pady=5, padx=5)
        self.nombre_medicamento_entry = ttk.Entry(frame)
        self.nombre_medicamento_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Cantidad").grid(row=1, column=0, pady=5, padx=5)
        self.cantidad_medicamento_entry = ttk.Entry(frame)
        self.cantidad_medicamento_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Precio").grid(row=2, column=0, pady=5, padx=5)
        self.precio_medicamento_entry = ttk.Entry(frame)
        self.precio_medicamento_entry.grid(row=2, column=1, pady=5, padx=5)

        ttk.Button(frame, text="Registrar Medicamento", command=self.registrar_medicamento).grid(row=3, columnspan=2, pady=10)
        ttk.Button(frame, text="Actualizar Medicamento", command=self.actualizar_medicamento).grid(row=4, columnspan=2, pady=10)
        ttk.Button(frame, text="Vender Medicamento", command=self.vender_medicamento).grid(row=5, columnspan=2, pady=10)
        ttk.Button(frame, text="Actualizar Inventario", command=self.mostrar_inventario).grid(row=6, columnspan=2, pady=10)

    def registrar_paciente(self):
        nombre = self.nombre_paciente_entry.get()
        especie = self.especie_paciente_entry.get()
        raza = self.raza_paciente_entry.get()
        edad = int(self.edad_paciente_entry.get())
        propietario_nombre = self.propietario_nombre_entry.get()
        propietario_contacto = self.propietario_contacto_entry.get()
        propietario = Propietario(propietario_nombre, propietario_contacto)

        paciente = Paciente(nombre, especie, raza, edad, propietario)
        self.clinica.registrar_paciente(paciente)
        messagebox.showinfo("Registro Exitoso", "Paciente registrado exitosamente")

    def actualizar_paciente(self):
        nombre = self.nombre_paciente_entry.get()
        especie = self.especie_paciente_entry.get()
        raza = self.raza_paciente_entry.get()
        edad = int(self.edad_paciente_entry.get())
        propietario_nombre = self.propietario_nombre_entry.get()
        propietario_contacto = self.propietario_contacto_entry.get()
        propietario = Propietario(propietario_nombre, propietario_contacto)

        paciente = next((p for p in self.clinica.pacientes if p.nombre == nombre), None)
        if paciente:
            self.clinica.actualizar_paciente(paciente, nombre, especie, raza, edad, propietario)
            messagebox.showinfo("Actualización Exitosa", "Paciente actualizado exitosamente")
        else:
            messagebox.showerror("Error", "Paciente no encontrado")

    def programar_cita(self):
        nombre_paciente = self.nombre_cita_entry.get()
        fecha = self.fecha_cita_entry.get()
        hora = self.hora_cita_entry.get()

        paciente = next((p for p in self.clinica.pacientes if p.nombre == nombre_paciente), None)
        if paciente:
            cita = Cita(paciente, fecha, hora)
            self.clinica.programar_cita(cita)
            messagebox.showinfo("Cita Programada", "Cita programada exitosamente")
        else:
            messagebox.showerror("Error", "Paciente no encontrado")

    def registrar_medicamento(self):
        nombre = self.nombre_medicamento_entry.get()
        cantidad = int(self.cantidad_medicamento_entry.get())
        precio = float(self.precio_medicamento_entry.get())

        medicamento = Medicamento(nombre, cantidad, precio)
        self.clinica.registrar_medicamento(medicamento)
        messagebox.showinfo("Registro Exitoso", "Medicamento registrado exitosamente")

    def actualizar_medicamento(self):
        nombre = self.nombre_medicamento_entry.get()
        cantidad = int(self.cantidad_medicamento_entry.get())
        precio = float(self.precio_medicamento_entry.get())

        medicamento = next((m for m in self.clinica.obtener_medicamentos() if m[0] == nombre), None)
        if medicamento:
            self.clinica.actualizar_medicamento(nombre, cantidad, precio)
            messagebox.showinfo("Actualización Exitosa", "Medicamento actualizado exitosamente")
        else:
            messagebox.showerror("Error", "Medicamento no encontrado")

    def vender_medicamento(self):
        nombre = self.nombre_medicamento_entry.get()
        cantidad = int(self.cantidad_medicamento_entry.get())

        resultado = self.clinica.vender_medicamento(nombre, cantidad)
        if resultado is True:
            messagebox.showinfo("Venta Exitosa", "Medicamento vendido exitosamente")
        elif resultado is False:
            messagebox.showerror("Error", "No hay suficiente cantidad del medicamento")
        else:
            messagebox.showerror("Error", "Medicamento no encontrado")

    def mostrar_inventario(self):
        inventario = self.clinica.obtener_medicamentos()
        reporte = "Inventario de Medicamentos:\n"
        for medicamento in inventario:
            reporte += f"Nombre: {medicamento[0]}, Cantidad: {medicamento[1]}, Precio: {medicamento[2]}\n"
        messagebox.showinfo("Inventario", reporte)
        alertas = self.clinica.alerta_inventario_bajo()
        if alertas:
            for alerta in alertas:
                messagebox.showwarning("Alerta de Inventario Bajo", alerta)

    def generar_reporte_pacientes(self):
        reporte = self.clinica.generar_reporte_pacientes()
        messagebox.showinfo("Reporte de Pacientes", reporte)

    def generar_reporte_citas(self):
        reporte = self.clinica.generar_reporte_citas()
        messagebox.showinfo("Reporte de Citas", reporte)

    def generar_reporte_ventas(self):
        reporte = self.clinica.generar_reporte_ventas()
        messagebox.showinfo("Reporte de Ventas", reporte)

    def verificar_login(self):
        usuario = self.usuario_entry.get()
        contrasena = self.contrasena_entry.get()
        if usuario == "Clínica Veterinaria Cute Pets" and contrasena == "Lucas18yaeslegal":
            self.tab_control.forget(self.tab_login)
            self.crear_tabs()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

root = tk.Tk()
clinica = ClinicaVeterinaria()
app = Aplicacion(root, clinica)
root.mainloop()
