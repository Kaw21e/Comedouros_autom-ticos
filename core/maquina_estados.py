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
        self.peso_racao_buffer = []
        self.relatorio_csv = None

        

    def configurar_cocho(self):
        try:
            sr.setup_gpio() # setando gpios do sensor
            self.leitor_rfid = rfid.iniciar_leitor()
            self.tag_info = pd.read_csv('tag_info.csv')
            self.relatorio_csv = pd.read_csv(LOCAL_RELATORIO_CSV)
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
        """
        recalibra a balança se ninguém estiver em cima. para casos quando o sistema já está rodando.
        """
        if (not sr.sensor_tem_presenca('1')) and (not sr.sensor_tem_presenca('2')):
            for num in BALANCAS.keys():
                tara = bl.retarar_balanca(num)
                if (not sr.sensor_tem_presenca('1')) and (not sr.sensor_tem_presenca('2')):
                    bl.salvar_tara(num, tara)
                    print(f'tara da balança{num} foi salva')

    def salvar_peso_animal(self, tag, peso):
        if peso and peso > 0:
            self.tag_info.loc[self.tag_info['tag_id'] == tag, 'peso'] = round(peso, 2)
            self.tag_info.to_csv('tag_info.csv', index=False)

    def executar_um_ciclo(self):        
        """
        Roda apenas UMA vez o ciclo completo de um animal.
        Retorna um dicionário com o que aconteceu para o main.py.
        """

        tag = nome_animal = saida = peso_racao_despejada = minutos = segundos = peso_animal_atual = 0
        self.peso_racao_buffer = []
        peso_animal_buffer = []
        peso_racao_despejada = 0
        entrada = time.ctime()
        inicio = time.monotonic()
        
        try:
            
            while sr.confirmar_presenca_sensor('1'): #começa confirmando a presença do animal

                tag = rfid.normalizar_tag_id(rfid.ler_tags(self.leitor_rfid, timeout=5))#se animal está presente, tenta ler o rfid   2. IDENTIFICAÇÃO (RFID)

                if tag: #se achou o rfid
                        
                    print(f"tag lida: {tag}")

                    if tag in self.tag_info['tag_id'].values: #vê se a tag ta no .csv

                        peso_racao = self.tag_info.loc[self.tag_info['tag_id'] == tag, 'valor'].values[0] #pega o peso da ração no .csv
                        nome_animal = self.tag_info.loc[self.tag_info['tag_id'] == tag, 'nome'].values[0]
                        peso_animal_anterior = self.tag_info.loc[self.tag_info['tag_id'] == tag, 'peso'].values[0]
                            
                        print(f"tag encontrada, a vaquinha {nome_animal} vai comer {peso_racao}g de ração hoje!")

                        #começa a rodar o motor e ler balanca 3. ALIMENTAÇÃO (Motor/Balança)
                        while sr.confirmar_presenca_sensor('1'): 

                            peso1, _ = bl.ler_peso(1)
                            if peso1 is not None:
                                self.peso_racao_buffer.append(peso1)

                            if len(self.peso_racao_buffer) > 10:
                                self.peso_racao_buffer.pop(0)
                                print(f'lendo peso despejado {peso_racao_despejada}')
                                if (peso_racao_despejada:= np.median(self.peso_racao_buffer)) > peso_racao:
                                    print(f'{peso_racao_despejada} > {peso_racao}')
                                    break
                            if (peso_racao_despejada > (0.7*peso_racao)):
                                print(f'{peso_racao_despejada} > 0.7* {peso_racao}')
                                motor._definir_estado_normal(1,"horario", 80)
                            else:
                                motor._definir_estado_normal(1,"horario", 150)


                        motor._definir_estado_normal(1, "parado", 0)

                        motor._definir_estado_normal(2, "horario", 255)

                        for _ in range(10):
                            peso2,_ = bl.ler_peso(2)
                            if peso2 is not None:
                                peso_animal_buffer.append(peso2)

                        if len(peso_animal_buffer) >= 3:
                            peso_animal_atual = np.median(peso_animal_buffer)
                            if pd.notna(peso_animal_anterior) and abs(peso_animal_atual - peso_animal_anterior) / peso_animal_anterior > 0.20:
                                print(f'peso medido {peso_animal_atual:.1f} desviou >20% de {peso_animal_anterior:.1f}, descartando')
                                peso_animal_atual = -1
                        else:
                            print('poucas leituras validas da balanca 2, usando peso anterior')
                            peso_animal_atual = -1

                        time.sleep(7)
                        motor._definir_estado_normal(2, "parado", 0)

                        sr.aguardar_sensor_livre('1')
                        saida = time.ctime()
                        fim = time.monotonic()
                        segundos_no_cocho = fim - inicio
                        minutos = int(segundos_no_cocho // 60)
                        segundos = int(segundos_no_cocho % 60)
                        break

                    elif tag:
                        print(f"Tag {tag} não foi encontrada no sistema csv")
                        return None
        except Exception as e:
            print(f"Erro no sistema principal: {e}")
            return None
        return {
            'tag_id': tag,
            'nome': nome_animal,
            'hora_entrada' : entrada,
            'hora_saida' : saida,
            'tempo_cocho' : f"{minutos}m {segundos:02d}s" if minutos != 0 or segundos != 0 else 0,
            'peso_animal' : peso_animal_atual,
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