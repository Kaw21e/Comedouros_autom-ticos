import datetime as dt
import RPi.GPIO as GPIO
import pigpio


# --- Sensor de reflexivo ---
SENSOR_1_PIN = 40
SENSOR_2_PIN = 38
SENSOR_1_PRESENCA_NIVEL = GPIO.HIGH
SENSOR_2_PRESENCA_NIVEL = GPIO.HIGH
SENSOR_1_PULL_UP_DOWN = GPIO.PUD_UP
SENSOR_2_PULL_UP_DOWN = GPIO.PUD_UP
SENSOR_1_CONFIRMATION_TIME = 0.5
SENSOR_1_RELEASE_CONFIRMATION_TIME = 1.0
SENSOR_2_RELEASE_CONFIRMATION_TIME = 1.0
SENSOR_1_POLL_INTERVAL = 0.05
SENSOR_2_POLL_INTERVAL = 0.05
SENSOR_2_CONFIRMATION_TIME = 0.5



# --- CONFIGURAÇÕES DO LEITOR RFID ---
RFID_PORTA_SERIAL = "/dev/ttyUSB0"
RFID_BAUDRATE = 38400
RFID_POTENCIA_DB = 15

# --- CONFIGURAÇÕES DA BALANCA ---
BALANCAS = {
        1: {"DT": 15, "SCK": 13, "fator": -134.118, "tara": 0},  # Balança da ração
        2: {"DT": 7, "SCK": 11, "fator": -7228.267, "tara": 0},   # Balança do animal
    }


# --- Dados Relatorio cocho csv ---

#autorizações para acesar os serviços
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


LOCAL_RELATORIO_CSV = "/home/raspberry/comedouros-automaticos_2.0/core/relatorio_cocho.csv"
LOCAL_CREDENCIAL = "/home/raspberry/comedouros-automaticos_2.0/core/SheetsKey.json"
NOME_PLANILHA = "Relatorio_Cocho" 

# --- Dados tag_info.csv ---

TAG_INFO_CSV = "/home/raspberry/comedouros-automaticos_2.0/core/tag_info.csv"
