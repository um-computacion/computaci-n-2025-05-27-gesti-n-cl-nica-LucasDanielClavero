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
        self.clinica = Clinica()
        self.paciente1 = Paciente("Laura Nuñez", "34567890", "10/02/1989")
        self.medico1 = Medico("Roberto Sanchez", "MP9999")
        self.especialidad_cardio = Especialidad("Cardiología", ["lunes", "miércoles"])
        self.medico1.agregar_especialidad(self.especialidad_cardio)

    # ------------------- Pacientes y Médicos -------------------

    def test_registro_paciente_exitoso(self):
        self.clinica.agregar_paciente(self.paciente1)
        self.assertIn(self.paciente1.obtener_dni(), self.clinica._Clinica__pacientes)

    def test_registro_paciente_duplicado(self):
        self.clinica.agregar_paciente(self.paciente1)
        with self.assertRaises(PacienteYaRegistradoException):
            self.clinica.agregar_paciente(self.paciente1)

    def test_registro_medico_exitoso(self):
        self.clinica.agregar_medico(self.medico1)
        self.assertIn(self.medico1.obtener_matricula(), self.clinica._Clinica__medicos)

    def test_registro_medico_duplicado(self):
        self.clinica.agregar_medico(self.medico1)
        with self.assertRaises(MedicoYaRegistradoException):
            self.clinica.agregar_medico(self.medico1)

    def test_paciente_con_datos_invalidos(self):
        with self.assertRaises(ValueError):
            Paciente("", "", "")

    def test_medico_con_datos_invalidos(self):
        with self.assertRaises(ValueError):
            Medico("", "")

    # ------------------- Especialidades -------------------

    def test_agregar_especialidad_nueva_a_medico(self):
        nueva_especialidad = Especialidad("Dermatología", ["martes"])
        self.medico1.agregar_especialidad(nueva_especialidad)
        especialidades = self.medico1.obtener_especialidades()
        self.assertIn(nueva_especialidad, especialidades)

    def test_evitar_especialidad_duplicada(self):
        cantidad_inicial = len(self.medico1.obtener_especialidades())
        self.medico1.agregar_especialidad(self.especialidad_cardio)  # No se agrega duplicado
        cantidad_final = len(self.medico1.obtener_especialidades())
        self.assertEqual(cantidad_inicial, cantidad_final)

    # ------------------- Turnos -------------------

    def test_agendar_turno_exitoso(self):
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        fecha = datetime(2025, 6, 16, 10, 0)  # lunes
        turno = self.clinica.agendar_turno(
            self.paciente1.obtener_dni(),
            self.medico1.obtener_matricula(),
            "Cardiología",
            fecha
        )
        self.assertIn(turno, self.clinica.obtener_turnos())

    def test_turno_duplicado(self):
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        fecha = datetime(2025, 6, 16, 11, 0)
        self.clinica.agendar_turno(self.paciente1.obtener_dni(), self.medico1.obtener_matricula(), "Cardiología", fecha)

        paciente2 = Paciente("Otro Paciente", "11223344", "01/01/2000")
        self.clinica.agregar_paciente(paciente2)
        with self.assertRaises(TurnoOcupadoException):
            self.clinica.agendar_turno(paciente2.obtener_dni(), self.medico1.obtener_matricula(), "Cardiología", fecha)

    def test_turno_con_paciente_inexistente(self):
        self.clinica.agregar_medico(self.medico1)
        fecha = datetime(2025, 6, 16, 10, 0)
        with self.assertRaises(PacienteNoEncontradoException):
            self.clinica.agendar_turno("DNI_FAKE", self.medico1.obtener_matricula(), "Cardiología", fecha)

    def test_turno_con_medico_inexistente(self):
        self.clinica.agregar_paciente(self.paciente1)
        fecha = datetime(2025, 6, 16, 10, 0)
        with self.assertRaises(MedicoNoEncontradoException):
            self.clinica.agendar_turno(self.paciente1.obtener_dni(), "FAKE_MP", "Cardiología", fecha)

    def test_turno_especialidad_no_atendida_por_medico(self):
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        fecha = datetime(2025, 6, 16, 10, 0)
        with self.assertRaises(MedicoNoDisponibleException):
            self.clinica.agendar_turno(self.paciente1.obtener_dni(), self.medico1.obtener_matricula(), "Dermatología", fecha)

    def test_turno_en_dia_que_no_trabaja(self):
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        fecha = datetime(2025, 6, 17, 10, 0)  # martes
        with self.assertRaises(MedicoNoDisponibleException):
            self.clinica.agendar_turno(self.paciente1.obtener_dni(), self.medico1.obtener_matricula(), "Cardiología", fecha)

    # ------------------- Recetas -------------------

    def test_emitir_receta_exitosa(self):
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        receta = self.clinica.emitir_receta(self.paciente1.obtener_dni(), self.medico1.obtener_matricula(), ["Paracetamol"])
        historia = self.clinica.obtener_historia_clinica(self.paciente1.obtener_dni())
        self.assertIn(receta, historia.obtener_recetas())

    def test_receta_con_paciente_inexistente(self):
        self.clinica.agregar_medico(self.medico1)
        with self.assertRaises(PacienteNoEncontradoException):
            self.clinica.emitir_receta("00000000", self.medico1.obtener_matricula(), ["Ibuprofeno"])

    def test_receta_con_medico_inexistente(self):
        self.clinica.agregar_paciente(self.paciente1)
        with self.assertRaises(MedicoNoEncontradoException):
            self.clinica.emitir_receta(self.paciente1.obtener_dni(), "MATRICULA_FAKE", ["Ibuprofeno"])

    def test_emitir_receta_sin_medicamentos(self):
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        with self.assertRaises(RecetaInvalidaException):
            self.clinica.emitir_receta(self.paciente1.obtener_dni(), self.medico1.obtener_matricula(), [])

    def test_historia_clinica_almacena_turnos_y_recetas(self):
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)

        # Agendar turno
        fecha_turno = datetime(2025, 6, 16, 10, 0)
        turno = self.clinica.agendar_turno(
            self.paciente1.obtener_dni(),
            self.medico1.obtener_matricula(),
            "Cardiología",
            fecha_turno
        )

        # Emitir receta
        receta = self.clinica.emitir_receta(
            self.paciente1.obtener_dni(),
            self.medico1.obtener_matricula(),
            ["Aspirina"]
        )

        historia = self.clinica.obtener_historia_clinica(self.paciente1.obtener_dni())

        # Verificar que el turno y la receta se guardaron
        self.assertIn(turno, historia.obtener_turnos())
        self.assertIn(receta, historia.obtener_recetas())