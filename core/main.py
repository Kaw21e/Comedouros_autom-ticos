import maquina_estados as maq_es
import time
import sensor_reflexivo as sr

if __name__ == "__main__":
    try:
        sistemaCocho = maq_es.SistemaCocho()
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