from config import *
import sensor_reflexivo as sr
import time
import leitor_fonkan as rfid
import pandas as pd
import motor
import balanca as bl
import numpy as np


class SistemaCocho:
    def __init__(self):
        self.leitor_rfid = None
        self.tag_info = None
        self.peso_buffer = []

        

    def configurar_cocho(self):
        try:
            sr.setup_gpio() # setando gpios do sensor
            self.leitor_rfid = rfid.iniciar_leitor()
            self.tag_info = pd.read_csv('tag_info.csv')
            motor.setup_todos_os_motores()
            motor._definir_estado_normal(2, "horario", 255)
            time.sleep(7)
            motor._definir_estado_normal(2, "parado", 0)
            for num, config in BALANCAS.items():
                bl.setup_balanca(config["DT"], config["SCK"])
                bl.calibrar_balanca(num)    

        except Exception as e:
            print(f"erro na configuração do sistema: {e}")

    def recalibrar_balanca_sem_presenca(self):
        sr.aguardar_sensores_livres()
        for num in BALANCAS.items():
            bl.calibrar_balanca(num)
        return

    def executar_um_ciclo(self):        
        """
        Roda apenas UMA vez o ciclo completo de um animal.
        Retorna um dicionário com o que aconteceu para o main.py.
        """
        entrada = time.ctime()
        comeco = time.monotonic()
        try:
            while True:
                if sr.confirmar_presenca_sensor('1'): #começa testando a presença do animal

                    tag = rfid.normalizar_tag_id(rfid.ler_tags(self.leitor_rfid, timeout=5))#se animal está presente, tenta ler o rfid   2. IDENTIFICAÇÃO (RFID)

                    if tag: #se achou o rfid
                        
                        print(f"tag lida: {tag}")

                        if tag in self.tag_info['tag_id'].values: #vê se a tag ta no .csv

                            peso_racao = self.tag_info.loc[self.tag_info['tag_id'] == tag, 'valor'].values[0] #pega o peso da ração no .csv
                            nome_animal = self.tag_info.loc[self.tag_info['tag_id'] == tag, 'nome'].values[0]
                            
                            
                            print(f"tag encontrada, a vaquinha {nome_animal} vai comer {peso_racao}g de ração hoje!")

                            #começa a rodar o motor e ler balanca 3. ALIMENTAÇÃO (Motor/Balança)
                            while sr.confirmar_presenca_sensor('1'):
                                peso1, bruto1 = bl.ler_peso(1)
                                self.peso_buffer.append(peso1)
                                if len(self.peso_buffer) > 10:
                                    self.peso_buffer.pop(0)
                                    if (peso_racao_despejada:= np.median(self.peso_buffer)) > peso_racao:
                                        break
                                motor._definir_estado_normal(1,"horario", 150)

                            
                            motor._definir_estado_normal(2, "horario", 255)
                            motor._definir_estado_normal(1, "parado", 0)
                            time.sleep(7)
                            motor._definir_estado_normal(2, "parado", 0)
                            if not sr.confirmar_presenca_sensor('1'):
                                saida = time.ctime()
                                fim = time.monotonic()
                                segundos_no_cocho = fim - inicio
                                minutos = int(segundos_no_cocho // 60)
                                segundos = int(segundos_no_cocho % 60)
                                break
                    else:
                        time.sleep(1) #da tempo para o sensor rfid respirar caso não encontre a tag
        except Exception as e:
            print(f"Erro no sistema principal: {e}")
            return None
        return {
            'tag_id': tag,
            'nome': nome_animal,
            'hora_entrada' : entrada,
            'hora_saida' : saida,
            'tempo_cocho' : f"{minutos}m {segundos:02d}s",
            'peso_animal' : None,
            'peso_racao' : peso_racao_despejada
        }

if __name__ == "__main__":
    try:
        sistemaCocho = SistemaCocho()
        print("\nIniciando o teste da função principal()... Pressione Ctrl+C para sair.")
        print("-" * 40)
        sistemaCocho.configurar_cocho()
        while True:
            resposta = sistemaCocho.executar_um_ciclo()
            print(resposta)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")
    finally:
        sr.GPIO.cleanup()
        print("Configurações da GPIO limpas.")