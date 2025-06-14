# cli.py

from datetime import datetime
from modelo import (
    Clinica, Paciente, Medico, Especialidad,
    PacienteNoEncontradoException, MedicoNoEncontradoException,
    PacienteYaRegistradoException, MedicoYaRegistradoException,

    MedicoNoDisponibleException, TurnoOcupadoException, RecetaInvalidaException
)

class ClinicaCLI:
    def __init__(self):
        self.clinica = Clinica()
        self._cargar_datos_iniciales()

    def _cargar_datos_iniciales(self):
        """Carga algunos datos de ejemplo para facilitar la prueba."""
        try:
            # Médicos
            medico1 = Medico("Carlos Rivera", "MP1234")
            medico1.agregar_especialidad(Especialidad("Cardiología", ["lunes", "miércoles"]))
            medico1.agregar_especialidad(Especialidad("Clínica", ["viernes"]))
            
            medico2 = Medico("Ana Gómez", "MP5678")
            medico2.agregar_especialidad(Especialidad("Pediatría", ["martes", "jueves"]))

            self.clinica.agregar_medico(medico1)
            self.clinica.agregar_medico(medico2)

            # Pacientes
            paciente1 = Paciente("Juan Pérez", "30123456", "15/05/1982")
            paciente2 = Paciente("María López", "35789012", "20/11/1990")
            
            self.clinica.agregar_paciente(paciente1)
            self.clinica.agregar_paciente(paciente2)
            print("✔️  Datos iniciales cargados correctamente.")
        except (PacienteYaRegistradoException, MedicoYaRegistradoException) as e:
            print(f"⚠️  Advertencia al cargar datos iniciales: {e}")

    def mostrar_menu(self):
        print("\n--- Menú Clínica ---")
        print("1) Agregar paciente")
        print("2) Agregar médico")
        print("3) Agregar especialidad a médico")
        print("4) Agendar turno")
        print("5) Emitir receta")
        print("6) Ver historia clínica de paciente")
        print("7) Ver todos los turnos")
        print("8) Ver todos los pacientes")
        print("9) Ver todos los médicos")
        print("0) Salir")

    def ejecutar(self):
        while True:
            self.mostrar_menu()
            opcion = input("Seleccione una opción: ")

            if opcion == '1':
                self._agregar_paciente()
            elif opcion == '2':
                self._agregar_medico()
            elif opcion == '3':
                self._agregar_especialidad_a_medico()
            elif opcion == '4':
                self._agendar_turno()
            elif opcion == '5':
                self._emitir_receta()
            elif opcion == '6':
                self._ver_historia_clinica()
            elif opcion == '7':
                self._ver_todos_los_turnos()
            elif opcion == '8':
                self._ver_todos_los_pacientes()
            elif opcion == '9':
                self._ver_todos_los_medicos()
            elif opcion == '0':
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción no válida. Intente de nuevo.")

    def _agregar_paciente(self):
        try:
            nombre = input("Nombre completo del paciente: ")
            dni = input("DNI del paciente: ")
            fecha_nac = input("Fecha de nacimiento (dd/mm/aaaa): ")
            paciente = Paciente(nombre, dni, fecha_nac)
            self.clinica.agregar_paciente(paciente)
            print(f"✔️  Paciente '{nombre}' agregado exitosamente.")
        except (ValueError, PacienteYaRegistradoException) as e:
            print(f"❌ Error: {e}")

    def _agregar_medico(self):
        try:
            nombre = input("Nombre completo del médico: ")
            matricula = input("Matrícula del médico: ")
            medico = Medico(nombre, matricula)
            self.clinica.agregar_medico(medico)
            print(f"✔️  Médico '{nombre}' agregado exitosamente.")
        except (ValueError, MedicoYaRegistradoException) as e:
            print(f"❌ Error: {e}")

    def _agregar_especialidad_a_medico(self):
        try:
            matricula = input("Matrícula del médico: ")
            medico = self.clinica.obtener_medico_por_matricula(matricula)
            
            tipo_esp = input("Nombre de la especialidad: ")
            dias_str = input("Días de atención (separados por coma, ej: lunes,martes): ")
            dias = [dia.strip() for dia in dias_str.split(',')]
            
            especialidad = Especialidad(tipo_esp, dias)
            medico.agregar_especialidad(especialidad)
            print(f"✔️  Especialidad '{tipo_esp}' agregada al Dr. {medico._Medico__nombre}.")
        except (MedicoNoEncontradoException, ValueError) as e:
            print(f"❌ Error: {e}")

    def _agendar_turno(self):
        try:
            dni = input("DNI del paciente: ")
            matricula = input("Matrícula del médico: ")
            especialidad = input("Especialidad requerida: ")
            fecha_str = input("Fecha y hora del turno (dd/mm/aaaa HH:MM): ")
            fecha_hora = datetime.strptime(fecha_str, "%d/%m/%Y %H:%M")
            
            self.clinica.agendar_turno(dni, matricula, especialidad, fecha_hora)
            print("✔️  Turno agendado exitosamente.")
        except (ValueError, PacienteNoEncontradoException, MedicoNoEncontradoException, 
                  TurnoOcupadoException, MedicoNoDisponibleException) as e:
            print(f"❌ Error al agendar turno: {e}")


    def _emitir_receta(self):
        try:
            dni = input("DNI del paciente: ")
            matricula = input("Matrícula del médico que emite: ")
            medicamentos_str = input("Medicamentos (separados por coma): ")
            medicamentos = [med.strip() for med in medicamentos_str.split(',')]
            
            self.clinica.emitir_receta(dni, matricula, medicamentos)
            print("✔️  Receta emitida y guardada en la historia clínica.")
        except (PacienteNoEncontradoException, MedicoNoEncontradoException, RecetaInvalidaException) as e:
            print(f"❌ Error al emitir receta: {e}")

    def _ver_historia_clinica(self):
        try:
            dni = input("DNI del paciente para ver su historia: ")
            historia = self.clinica.obtener_historia_clinica(dni)
            print(historia)
        except PacienteNoEncontradoException as e:
            print(f"❌ Error: {e}")

    def _ver_todos_los_turnos(self):
        turnos = self.clinica.obtener_turnos()
        if not turnos:
            print("\nℹ️  No hay turnos agendados en el sistema.")
            return
        print("\n--- Listado de Todos los Turnos ---")
        for turno in sorted(turnos, key=lambda t: t.obtener_fecha_hora()):
            print(turno)

    def _ver_todos_los_pacientes(self):
        pacientes = self.clinica.obtener_pacientes()
        if not pacientes:
            print("\nℹ️  No hay pacientes registrados.")
            return
        print("\n--- Listado de Pacientes ---")
        for paciente in pacientes:
            print(paciente)

    def _ver_todos_los_medicos(self):
        medicos = self.clinica.obtener_medicos()
        if not medicos:
            print("\nℹ️  No hay médicos registrados.")
            return
        print("\n--- Listado de Médicos ---")
        for medico in medicos:
            print(medico)


if __name__ == "__main__":
    cli = ClinicaCLI()
    cli.ejecutar()