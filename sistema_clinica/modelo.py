# modelo.py

import datetime

# --- Excepciones Personalizadas ---

class PacienteNoEncontradoException(Exception):
    """Lanzada cuando un paciente no se encuentra en el sistema."""
    pass

class MedicoNoEncontradoException(Exception):
    """Lanzada cuando un médico no se encuentra en el sistema."""
    pass

class PacienteYaRegistradoException(Exception):
    """Lanzada al intentar registrar un DNI ya existente."""
    pass

class MedicoYaRegistradoException(Exception):
    """Lanzada al intentar registrar una matrícula ya existente."""
    pass

class MedicoNoDisponibleException(Exception):
    """Lanzada cuando un médico no está disponible para un turno."""
    pass

class TurnoOcupadoException(Exception):
    """Lanzada al intentar agendar un turno en un horario ya ocupado."""
    pass

class RecetaInvalidaException(Exception):
    """Lanzada cuando los datos para una receta son inválidos."""
    pass


# --- Clases del Dominio ---

class Paciente:
    def __init__(self, nombre: str, dni: str, fecha_nacimiento: str):
        if not nombre or not dni:
            raise ValueError("El nombre y el DNI no pueden estar vacíos.")
        self.__nombre = nombre
        self.__dni = dni
        self.__fecha_nacimiento = fecha_nacimiento

    def obtener_dni(self) -> str:
        return self.__dni

    def __str__(self) -> str:
        return f"Paciente: {self.__nombre} (DNI: {self.__dni})"


class Especialidad:
    def __init__(self, tipo: str, dias: list[str]):
        if not tipo or not dias:
            raise ValueError("El tipo y los días de atención son requeridos.")
        self.__tipo = tipo
        # Guardamos los días en minúsculas para una comparación insensible a mayúsculas
        self.__dias = [dia.lower() for dia in dias]

    def obtener_especialidad(self) -> str:
        return self.__tipo

    def verificar_dia(self, dia: str) -> bool:
        return dia.lower() in self.__dias

    def __str__(self) -> str:
        dias_str = ", ".join(d.capitalize() for d in self.__dias)
        return f"{self.__tipo} (Días: {dias_str})"


class Medico:
    def __init__(self, nombre: str, matricula: str):
        if not nombre or not matricula:
            raise ValueError("El nombre y la matrícula no pueden estar vacíos.")
        self.__nombre = nombre
        self.__matricula = matricula
        self.__especialidades = []

    def agregar_especialidad(self, especialidad: Especialidad):
        # Evitar duplicados de especialidades
        for esp in self.__especialidades:
            if esp.obtener_especialidad() == especialidad.obtener_especialidad():
                return
        self.__especialidades.append(especialidad)

    def obtener_matricula(self) -> str:
        return self.__matricula

    def obtener_especialidad_para_dia(self, dia: str) -> str | None:
        for especialidad in self.__especialidades:
            if especialidad.verificar_dia(dia):
                return especialidad.obtener_especialidad()
        return None
        
    def obtener_especialidades(self) -> list[Especialidad]:
        return self.__especialidades

    def __str__(self) -> str:
        especialidades_str = "; ".join(str(esp) for esp in self.__especialidades)
        if not especialidades_str:
            especialidades_str = "Sin especialidades asignadas"
        return f"Dr. {self.__nombre} (Matrícula: {self.__matricula}) - Especialidades: {especialidades_str}"


class Turno:
    def __init__(self, paciente: Paciente, medico: Medico, fecha_hora: datetime.datetime, especialidad: str):
        self.__paciente = paciente
        self.__medico = medico
        self.__fecha_hora = fecha_hora
        self.__especialidad = especialidad

    def obtener_medico(self) -> Medico:
        return self.__medico

    def obtener_fecha_hora(self) -> datetime.datetime:
        return self.__fecha_hora

    def __str__(self) -> str:
        fecha_str = self.__fecha_hora.strftime("%d/%m/%Y a las %H:%M")
        return (f"Turno: {fecha_str} - Paciente: {self.__paciente.obtener_dni()} | "
                f"Dr. {self.__medico._Medico__nombre} | Especialidad: {self.__especialidad}")


class Receta:
    def __init__(self, paciente: Paciente, medico: Medico, medicamentos: list[str]):
        if not medicamentos:
            raise RecetaInvalidaException("La lista de medicamentos no puede estar vacía.")
        self.__paciente = paciente
        self.__medico = medico
        self.__medicamentos = medicamentos
        self.__fecha = datetime.datetime.now()

    def __str__(self) -> str:
        fecha_str = self.__fecha.strftime("%d/%m/%Y")
        medicamentos_str = ", ".join(self.__medicamentos)
        return (f"Receta ({fecha_str}) - Emitida por Dr. {self.__medico._Medico__nombre} "
                f"para {self.__paciente._Paciente__nombre}: {medicamentos_str}")


class HistoriaClinica:
    def __init__(self, paciente: Paciente):
        self.__paciente = paciente
        self.__turnos = []
        self.__recetas = []

    def agregar_turno(self, turno: Turno):
        self.__turnos.append(turno)

    def agregar_receta(self, receta: Receta):
        self.__recetas.append(receta)

    def obtener_turnos(self) -> list[Turno]:
        return self.__turnos.copy()

    def obtener_recetas(self) -> list[Receta]:
        return self.__recetas.copy()

    def __str__(self) -> str:
        historia_str = f"--- Historia Clínica de {self.__paciente._Paciente__nombre} ---\n"
        
        historia_str += "\n>> Turnos Agendados:\n"
        if not self.__turnos:
            historia_str += "No hay turnos registrados.\n"
        else:
            for turno in sorted(self.__turnos, key=lambda t: t.obtener_fecha_hora()):
                historia_str += f"- {turno}\n"

        historia_str += "\n>> Recetas Emitidas:\n"
        if not self.__recetas:
            historia_str += "No hay recetas registradas.\n"
        else:
            for receta in self.__recetas:
                historia_str += f"- {receta}\n"
        
        return historia_str


# --- Clase Principal de Gestión ---

class Clinica:
    def __init__(self):
        self.__pacientes = {}
        self.__medicos = {}
        self.__turnos = []
        self.__historias_clinicas = {}

    # --- Métodos de Registro y Acceso ---
    def agregar_paciente(self, paciente: Paciente):
        if self.validar_existencia_paciente(paciente.obtener_dni()):
            raise PacienteYaRegistradoException(f"El DNI {paciente.obtener_dni()} ya está registrado.")
        self.__pacientes[paciente.obtener_dni()] = paciente
        self.__historias_clinicas[paciente.obtener_dni()] = HistoriaClinica(paciente)

    def agregar_medico(self, medico: Medico):
        if self.validar_existencia_medico(medico.obtener_matricula()):
            raise MedicoYaRegistradoException(f"La matrícula {medico.obtener_matricula()} ya está registrada.")
        self.__medicos[medico.obtener_matricula()] = medico

    def obtener_pacientes(self) -> list[Paciente]:
        return list(self.__pacientes.values())

    def obtener_medicos(self) -> list[Medico]:
        return list(self.__medicos.values())

    def obtener_medico_por_matricula(self, matricula: str) -> Medico:
        if not self.validar_existencia_medico(matricula):
            raise MedicoNoEncontradoException(f"No se encontró un médico con matrícula {matricula}.")
        return self.__medicos[matricula]

    # --- Métodos de Gestión de Turnos ---
    def agendar_turno(self, dni: str, matricula: str, especialidad_solicitada: str, fecha_hora: datetime.datetime):
        if not self.validar_existencia_paciente(dni):
            raise PacienteNoEncontradoException(f"El paciente con DNI {dni} no está registrado.")
        
        medico = self.obtener_medico_por_matricula(matricula)
        
        if not self.validar_turno_no_duplicado(matricula, fecha_hora):
            raise TurnoOcupadoException(f"El Dr. {medico._Medico__nombre} ya tiene un turno a las {fecha_hora.strftime('%H:%M')}.")

        dia_semana = self.obtener_dia_semana_en_espanol(fecha_hora)
        
        if not self.validar_especialidad_en_dia(medico, especialidad_solicitada, dia_semana):
            raise MedicoNoDisponibleException(
                f"El Dr. {medico._Medico__nombre} no atiende {especialidad_solicitada} los días {dia_semana.capitalize()}."
            )

        paciente = self.__pacientes[dni]
        nuevo_turno = Turno(paciente, medico, fecha_hora, especialidad_solicitada)
        
        self.__turnos.append(nuevo_turno)
        self.__historias_clinicas[dni].agregar_turno(nuevo_turno)
        return nuevo_turno

    def obtener_turnos(self) -> list[Turno]:
        return self.__turnos.copy()

    # --- Métodos de Recetas e Historias Clínicas ---
    def emitir_receta(self, dni: str, matricula: str, medicamentos: list[str]):
        if not self.validar_existencia_paciente(dni):
            raise PacienteNoEncontradoException(f"El paciente con DNI {dni} no está registrado.")
        
        medico = self.obtener_medico_por_matricula(matricula)
        paciente = self.__pacientes[dni]
        
        try:
            nueva_receta = Receta(paciente, medico, medicamentos)
        except RecetaInvalidaException as e:
            raise e # Relanzamos la excepción
            
        self.__historias_clinicas[dni].agregar_receta(nueva_receta)
        return nueva_receta

    def obtener_historia_clinica(self, dni: str) -> HistoriaClinica:
        if not self.validar_existencia_paciente(dni):
            raise PacienteNoEncontradoException(f"No se puede obtener la historia de un paciente con DNI {dni} que no existe.")
        return self.__historias_clinicas[dni]

    # --- Métodos de Validación y Utilidades ---
    def validar_existencia_paciente(self, dni: str) -> bool:
        return dni in self.__pacientes

    def validar_existencia_medico(self, matricula: str) -> bool:
        return matricula in self.__medicos

    def validar_turno_no_duplicado(self, matricula: str, fecha_hora: datetime.datetime) -> bool:
        for turno in self.__turnos:
            if turno.obtener_medico().obtener_matricula() == matricula and turno.obtener_fecha_hora() == fecha_hora:
                return False
        return True

    def obtener_dia_semana_en_espanol(self, fecha_hora: datetime.datetime) -> str:
        dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        return dias[fecha_hora.weekday()]

    def obtener_especialidad_disponible(self, medico: Medico, dia_semana: str) -> str | None:
        for esp in medico.obtener_especialidades():
            if esp.verificar_dia(dia_semana):
                return esp.obtener_especialidad()
        return None

    def validar_especialidad_en_dia(self, medico: Medico, especialidad_solicitada: str, dia_semana: str) -> bool:
        for esp in medico.obtener_especialidades():
            if esp.obtener_especialidad().lower() == especialidad_solicitada.lower() and esp.verificar_dia(dia_semana):
                return True
        return False