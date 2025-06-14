# test_clinica.py

import unittest
from datetime import datetime
from modelo import (
    Clinica, Paciente, Medico, Especialidad,
    PacienteNoEncontradoException, MedicoNoEncontradoException,
    PacienteYaRegistradoException, MedicoYaRegistradoException,
    MedicoNoDisponibleException, TurnoOcupadoException, RecetaInvalidaException
)

class TestClinica(unittest.TestCase):

    def setUp(self):
        """Configura un entorno de prueba limpio antes de cada test."""
        self.clinica = Clinica()
        
        # Datos de prueba
        self.paciente1 = Paciente("Laura Nuñez", "34567890", "10/02/1989")
        self.medico1 = Medico("Roberto Sanchez", "MP9999")
        self.especialidad_cardio = Especialidad("Cardiología", ["lunes", "miércoles"])
        self.medico1.agregar_especialidad(self.especialidad_cardio)

    def test_registro_paciente_exitoso(self):
        self.clinica.agregar_paciente(self.paciente1)
        self.assertIn(self.paciente1.obtener_dni(), self.clinica._Clinica__pacientes)
        self.assertIn(self.paciente1.obtener_dni(), self.clinica._Clinica__historias_clinicas)

    def test_registro_paciente_duplicado_lanza_excepcion(self):
        self.clinica.agregar_paciente(self.paciente1)
        with self.assertRaises(PacienteYaRegistradoException):
            self.clinica.agregar_paciente(self.paciente1)

    def test_registro_medico_exitoso(self):
        self.clinica.agregar_medico(self.medico1)
        self.assertIn(self.medico1.obtener_matricula(), self.clinica._Clinica__medicos)

    def test_registro_medico_duplicado_lanza_excepcion(self):
        self.clinica.agregar_medico(self.medico1)
        with self.assertRaises(MedicoYaRegistradoException):
            self.clinica.agregar_medico(self.medico1)
            
    def test_agendar_turno_exitoso(self):
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        # Lunes 16 de junio de 2025
        fecha_turno = datetime(2025, 6, 16, 10, 0) 
        turno = self.clinica.agendar_turno(
            self.paciente1.obtener_dni(),
            self.medico1.obtener_matricula(),
            "Cardiología",
            fecha_turno
        )
        self.assertIn(turno, self.clinica.obtener_turnos())
        historia = self.clinica.obtener_historia_clinica(self.paciente1.obtener_dni())
        self.assertIn(turno, historia.obtener_turnos())

    def test_agendar_turno_paciente_inexistente_lanza_excepcion(self):
        self.clinica.agregar_medico(self.medico1)
        fecha_turno = datetime(2025, 6, 16, 10, 0)
        with self.assertRaises(PacienteNoEncontradoException):
            self.clinica.agendar_turno("DNI_FALSO", self.medico1.obtener_matricula(), "Cardiología", fecha_turno)

    def test_agendar_turno_medico_no_disponible_dia_lanza_excepcion(self):
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        # Martes 17 de junio de 2025 (el médico no atiende los martes)
        fecha_turno = datetime(2025, 6, 17, 10, 0)
        with self.assertRaises(MedicoNoDisponibleException):
            self.clinica.agendar_turno(self.paciente1.obtener_dni(), self.medico1.obtener_matricula(), "Cardiología", fecha_turno)

    def test_agendar_turno_medico_no_disponible_especialidad_lanza_excepcion(self):
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        # Lunes, pero con una especialidad que no tiene
        fecha_turno = datetime(2025, 6, 16, 10, 0)
        with self.assertRaises(MedicoNoDisponibleException):
            self.clinica.agendar_turno(self.paciente1.obtener_dni(), self.medico1.obtener_matricula(), "Dermatología", fecha_turno)

    def test_agendar_turno_duplicado_lanza_excepcion(self):
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        fecha_turno = datetime(2025, 6, 16, 11, 0)
        self.clinica.agendar_turno(self.paciente1.obtener_dni(), self.medico1.obtener_matricula(), "Cardiología", fecha_turno)
        
        # Intentar agendar en el mismo horario
        paciente2 = Paciente("Otro Paciente", "11223344", "01/01/2000")
        self.clinica.agregar_paciente(paciente2)
        with self.assertRaises(TurnoOcupadoException):
            self.clinica.agendar_turno(paciente2.obtener_dni(), self.medico1.obtener_matricula(), "Cardiología", fecha_turno)

    def test_emitir_receta_exitosa(self):
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        medicamentos = ["Aspirina", "Losartán"]
        
        receta = self.clinica.emitir_receta(
            self.paciente1.obtener_dni(),
            self.medico1.obtener_matricula(),
            medicamentos
        )
        
        historia = self.clinica.obtener_historia_clinica(self.paciente1.obtener_dni())
        self.assertIn(receta, historia.obtener_recetas())

    def test_emitir_receta_sin_medicamentos_lanza_excepcion(self):
        self.clinica.agregar_paciente(self.paciente1)
        self.clinica.agregar_medico(self.medico1)
        with self.assertRaises(RecetaInvalidaException):
            self.clinica.emitir_receta(self.paciente1.obtener_dni(), self.medico1.obtener_matricula(), [])

if __name__ == '__main__':
    unittest.main()