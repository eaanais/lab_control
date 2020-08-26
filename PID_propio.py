import time


class PID_propio:

    def __init__(Kp, Ki, Kd, Kw, voltaje_max):
        # CONSTANTES
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.Kw = Kw
        self.referencia = 0
        # VARIABLES MANIPULADAS
        self.manipulada_max = voltaje_max
        self.manipulada = 0
        self.manipulada_original = 0
        # TIEMPOS
        self.tiempo_actual = time.time()
        self.tiempo_anterior = self.tiempo_actual
        self.tiempo_muestreo = 0
        # ERRORES
        self.error_anterior = 0
        # Componentes P + I + D
        self.P = 0
        self.I = 0
        self.D = 0

    def actualizar(self, valor_actual):
        error_actual = self.referencia - valor_actual
        self.tiempo_actual = time.time()
        delta_tiempo = self.tiempo_actual - self.tiempo_anterior
        delta_error = error_actual - self.error_anterior

        if delta_tiempo < self.tiempo_muestreo:
            time.sleep(self.tiempo_muestreo - delta_tiempo)

        self.P = self.Kp*error_actual
        self.I += (self.Ki*error_actual + self.Kw*(self.manipulada - self.manipulada_original))*delta_tiempo

        if delta_tiempo > 0:
            self.D = self.Kd*delta_error/delta_tiempo

        self.manipulada_original = self.P + self.I + self.D
        print(f'Variable manipulada original : {self.manipulada_original}')
        if self.manipulada_original > self.manipulada_max:
            self.manipulada = self.manipulada_max
        elif self.manipulada_original < -self.manipulada_max:
            self.manipulada = -self.manipulada_max
        else:
            self.manipulada = self.manipulada_original

        self.tiempo_anterior = self.tiempo_actual
        self.error_anterior = error_actual
        return self.manipulada


controlador = PID_propio(0.2, 0.1, 0, 0.3, 1)
# controlador.referencia = x  (actualiza referencia de altura)
# controlador.actualizar(altura_actual) (controla a partir de la altura actual )
