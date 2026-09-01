import maquina_estados as maq_es
import time
import sensor_reflexivo as sr
import relatorio as rl
import pandas as pd
from config import *
import threading

def rodar_ciclos():
    try:
        sistemaCocho = maq_es.SistemaCocho()

        print("\nIniciando sistema principal()... Pressione Ctrl+C para sair.")
        print("-" * 40)
    
        sistemaCocho.configurar_cocho() 
    
        while True: #loop principal
    
            sistemaCocho.recalibrar_balanca_sem_presenca() #enquanto não há vacas no cocho, o sistema fica recalibrando a balança
    
            if sr.confirmar_presenca_sensor('1'): #se tiver vacas no sensor 1, o ciclo se inicia
                print("presença confirmada no sensor 1, entrando no ciclo cocho")
                resposta = sistemaCocho.executar_um_ciclo()
                print(resposta) #retorna os dados sobre o que aconteceu no ciclo.
                if resposta and list(resposta.values())[0]:
                    sistemaCocho.relatorio_csv = pd.read_csv(LOCAL_RELATORIO_CSV)
                    rl.salvar_registro_csv(sistemaCocho.relatorio_csv, resposta)

                    if resposta.get('peso_animal') > -1:
                        sistemaCocho.salvar_peso_animal(resposta['tag_id'], resposta['peso_animal'])
    
    except KeyboardInterrupt:
            print("\nPrograma encerrado pelo usuário.")
    finally:
        sr.GPIO.cleanup()
        print("Configurações da GPIO limpas.")

def notificar():
    try:
        while True:
            rl.sincronizar_csv_com_sheets()
            print(f"enviando csv para sheets")
            time.sleep(30)
    except KeyboardInterrupt:
        return 

def botao():
    pass


if __name__ == "__main__":
    t1 = threading.Thread(target=rodar_ciclos, args=())
    t2 = threading.Thread(target=notificar, args=())

# Iniciando as threads
t1.start()
t2.start()

# Aguardando a finalização de ambas
t1.join()
t2.join()