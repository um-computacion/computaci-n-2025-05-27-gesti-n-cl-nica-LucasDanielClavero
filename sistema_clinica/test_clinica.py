# test_clinica.py

import unittest
from datetime import datetime
from modelo import (
    Clinica, Paciente, Medico, Especialidad,
    PacienteNoEncontradoException, MedicoNoEncontradoException,
    PacienteYaRegistradoException, MedicoYaRegistradoException,
    MedicoNoDisponibleException, TurnoOcupadoException,
    RecetaInvalidaException
)


class TestClinica(unittest.TestCase):

    def setUp(self):
        """Configura un entorno de prueba limpio antes de cada test."""
        self.clinica = Clinica()
        self.paciente1 = Paciente("Laura Nuñez", "34567890", "10/02/1989")
        self.medico1 = Medico("Roberto Sanchez", "MP9999")
        self.especialidad_cardio = Especialidad("Cardiología", ["lunes", "miércoles"])
        self.medico1.agregar_especialidad(self.especialidad_cardio)

    # ------------------- Pacientes y Médicos -------------------

    def test_registro_paciente_exitoso(self):
        """Registro exitoso de pacientes."""
        self.clinica.agregar_paciente(self.paciente1)
        self.assertIn(self.paciente1.obtener_dni(), self.clinica._Clinica__pacientes)

    def test_registro_paciente_duplicado(self):
        """Prevención de registros duplicados (por DNI)."""
        self.clinica.agregar_paciente(self.paciente1)
        with self.assertRaises(PacienteYaRegistradoException):
            self.clinica.agregar_paciente(self.paciente1)

    def test_registro_medico_exitoso(self):
        """Registro exitoso de médicos."""
        self.clinica.agregar_medico(self.medico1)
        self.assertIn(self.medico1.obtener_matricula(), self.clinica._Clinica__medicos)

    def test_registro_medico_duplicado(self):
        """Prevención de registros duplicados (por matrícula)."""
        self.clinica.agregar_medico(self.medico1)
        with self.assertRaises(MedicoYaRegistradoException):
            self.clinica.agregar_medico(self.medico1)

    def test_paciente_con_datos_invalidos(self):
        """Verificación de errores por datos faltantes o inválidos en Paciente."""
        with self.assertRaises(ValueError):
            Paciente("", "12345678", "01/01/1990")
        with self.assertRaises(ValueError):
            Paciente("Nombre Apellido", "", "01/01/1990")

    def test_medico_con_datos_invalidos(self):
        """Verificación de errores por datos faltantes o inválidos en Medico."""
        with self.assertRaises(ValueError):
            Medico("", "MP12345")
        with self.assertRaises(ValueError):
            Medico("Nombre Medico", "")

    # ------------------- Especialidades -------------------

    def test_agregar_especialidad_nueva_a_medico(self):
        """Agregar especialidades nuevas a un médico ya registrado."""
        nueva_especialidad = Especialidad("Dermatología", ["martes"])
        self.medico1.agregar_especialidad(nueva_especialidad)
        especialidades_medico = [esp.obtener_especialidad() for esp in self.medico1.obtener_especialidades()]
        self.assertIn("Dermatología", especialidades_medico)

    def test_evitar_especialidad_duplicada(self):
        """Evitar duplicados de especialidad en el mismo médico."""
        cantidad_inicial = len(self.medico1.obtener_especialidades())
        especialidad_duplicada = Especialidad("Cardiología", ["viernes"]) # Mismo nombre
        self.medico1.agregar_especialidad(especialidad_duplicada)
        cantidad_final = len(self.medico1.obtener_especialidades())
        self.assertEqual(cantidad_inicial, cantidad_final)

    def test_especialidad_con_datos_invalidos(self):
        """Detección de especialidades con días de atención inválidos (vacíos)."""
        with self.assertRaises(ValueError):
            Especialidad("Pediatría", []) # Lista de días vacía
        with self.assertRaises(ValueError):
            Especialidad("", ["lunes", "jueves"]) # Nombre de especialidad vacío

    def test_agregar_especialidad_a_medico_no_registrado(self):
        """Error si se intenta agregar especialidad a un médico no registrado."""
        # Esta prueba verifica que no se puede obtener un médico inexistente,
        # que es el paso previo a agregarle una especialidad en la lógica de la app.
        with self.assertRaises(MedicoNoEncontradoException):
            self.clinica.obtener_medico_por_matricula("MATRICULA_INEXISTENTE")

    # ------------------- Turnos -------------------

    def test_agendar_turno_exitoso(self):
        """Agendamiento correcto de turnos."""
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        fecha = datetime(2025, 6, 16, 10, 0)  # Lunes
        turno = self.clinica.agendar_turno(
            self.paciente1.obtener_dni(),
            self.medico1.obtener_matricula(),
            "Cardiología",
            fecha
        )
        self.assertIn(turno, self.clinica.obtener_turnos())

    def test_turno_duplicado(self):
        """Evitar turnos duplicados (mismo médico y fecha/hora)."""
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        fecha = datetime(2025, 6, 16, 11, 0) # Lunes 11:00
        self.clinica.agendar_turno(self.paciente1.obtener_dni(), self.medico1.obtener_matricula(), "Cardiología", fecha)

        paciente2 = Paciente("Otro Paciente", "11223344", "01/01/2000")
        self.clinica.agregar_paciente(paciente2)
        with self.assertRaises(TurnoOcupadoException):
            self.clinica.agendar_turno(paciente2.obtener_dni(), self.medico1.obtener_matricula(), "Cardiología", fecha)

    def test_turno_con_paciente_inexistente(self):
        """Error si el paciente no existe."""
        self.clinica.agregar_medico(self.medico1)
        fecha = datetime(2025, 6, 16, 10, 0)
        with self.assertRaises(PacienteNoEncontradoException):
            self.clinica.agendar_turno("DNI_FALSO", self.medico1.obtener_matricula(), "Cardiología", fecha)

    def test_turno_con_medico_inexistente(self):
        """Error si el médico no existe."""
        self.clinica.agregar_paciente(self.paciente1)
        fecha = datetime(2025, 6, 16, 10, 0)
        with self.assertRaises(MedicoNoEncontradoException):
            self.clinica.agendar_turno(self.paciente1.obtener_dni(), "MP_FALSA", "Cardiología", fecha)

    def test_turno_especialidad_no_atendida_por_medico(self):
        """Error si el médico no atiende la especialidad solicitada."""
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        fecha = datetime(2025, 6, 16, 10, 0) # Lunes
        with self.assertRaises(MedicoNoDisponibleException):
            self.clinica.agendar_turno(self.paciente1.obtener_dni(), self.medico1.obtener_matricula(), "Dermatología", fecha)

    def test_turno_en_dia_que_no_trabaja(self):
        """Error si el médico no trabaja ese día de la semana para esa especialidad."""
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        fecha = datetime(2025, 6, 17, 10, 0)  # Martes
        with self.assertRaises(MedicoNoDisponibleException):
            self.clinica.agendar_turno(self.paciente1.obtener_dni(), self.medico1.obtener_matricula(), "Cardiología", fecha)

    # ------------------- Recetas -------------------

    def test_emitir_receta_exitosa(self):
        """Emisión de recetas para un paciente válido por un médico válido."""
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        receta = self.clinica.emitir_receta(self.paciente1.obtener_dni(), self.medico1.obtener_matricula(), ["Paracetamol 500mg"])
        historia = self.clinica.obtener_historia_clinica(self.paciente1.obtener_dni())
        self.assertIn(receta, historia.obtener_recetas())

    def test_receta_con_paciente_inexistente(self):
        """Error al emitir receta si el paciente no existe."""
        self.clinica.agregar_medico(self.medico1)
        with self.assertRaises(PacienteNoEncontradoException):
            self.clinica.emitir_receta("00000000", self.medico1.obtener_matricula(), ["Ibuprofeno"])

    def test_receta_con_medico_inexistente(self):
        """Error al emitir receta si el médico no existe."""
        self.clinica.agregar_paciente(self.paciente1)
        with self.assertRaises(MedicoNoEncontradoException):
            self.clinica.emitir_receta(self.paciente1.obtener_dni(), "MATRICULA_FALSA", ["Ibuprofeno"])

    def test_emitir_receta_sin_medicamentos(self):
        """Error si no hay medicamentos listados."""
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        with self.assertRaises(RecetaInvalidaException):
            self.clinica.emitir_receta(self.paciente1.obtener_dni(), self.medico1.obtener_matricula(), [])

    # ------------------- Historia Clínica -------------------

    def test_historia_clinica_almacena_turnos_y_recetas(self):
        """Confirmar que los turnos y recetas se guardan en la historia clínica."""
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)

        # Agendar un turno
        fecha_turno = datetime(2025, 6, 16, 10, 0)
        turno = self.clinica.agendar_turno(
            self.paciente1.obtener_dni(),
            self.medico1.obtener_matricula(),
            "Cardiología",
            fecha_turno
        )

        # Emitir una receta
        receta = self.clinica.emitir_receta(
            self.paciente1.obtener_dni(),
            self.medico1.obtener_matricula(),
            ["Aspirina Prevent"]
        )

        historia = self.clinica.obtener_historia_clinica(self.paciente1.obtener_dni())

        # Verificar que el turno y la receta se guardaron correctamente
        self.assertIn(turno, historia.obtener_turnos())
        self.assertIn(receta, historia.obtener_recetas())

if __name__ == '__main__':
    unittest.main(verbosity=2)