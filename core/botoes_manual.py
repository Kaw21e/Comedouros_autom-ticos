import motor as mt
from config import *
import time
import RPi.GPIO as GPIO
import balanca as bl


# --- Monitoramento de Botões ---
def monitorar_botao_motor(motor_id, estado_anterior):
    pino_botao = PINO_BOTAO_MANUAL_MOTOR1 if motor_id == 1 else PINO_BOTAO_MANUAL_MOTOR2

    estado_atual = GPIO.input(pino_botao)

    if estado_atual == BOTAO_PRESSIONADO:
        print(f"botão {motor_id} foi pressionado")
        mt._definir_estado_manual(motor_id, 'horario',255)
    elif estado_atual != estado_anterior:
        mt._liberar_controle_manual(motor_id)
    time.sleep(0.05)
    return estado_atual

def setup_botoes():
    GPIO.setup(PINO_BOTAO_MANUAL_MOTOR1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PINO_BOTAO_MANUAL_MOTOR2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BOTAO_CALIBRAR1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BOTAO_CALIBRAR2, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def calibrar(balanca, estado_anterior):
    pino_botao = BOTAO_CALIBRAR1 if balanca == 1 else BOTAO_CALIBRAR2

    estado_atual = GPIO.input(pino_botao)

    if estado_atual == BOTAO_PRESSIONADO and estado_atual != estado_anterior:
        tara = bl.retarar_balanca(balanca)
        bl.salvar_tara(balanca, tara)
        print(f'balança {balanca} foi tarada')



if __name__ == "__main__":
    mt.setup_todos_os_motores()
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PINO_BOTAO_MANUAL_MOTOR1, GPIO.IN, pull_up_down=GPIO.PUD_UP)



