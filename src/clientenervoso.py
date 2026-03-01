import socket
import threading
import time

HOST = '127.0.0.1'
PORT = 65432

# Opção B: timeouts separados para conexão e para resposta.
# O cliente é "nervoso" apenas para entrar — se o servidor não aceitar
# o handshake TCP rapidamente, desiste. Mas uma vez conectado, espera
# o tempo necessário para receber a resposta.
TIMEOUT_CONEXAO = 2   # segundos para o handshake TCP ser aceito
TIMEOUT_RESPOSTA = 10 # segundos para aguardar a resposta após conectar

def cliente_nervoso(id_cliente):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Fase 1: tentativa de conexão com timeout curto.
        # Se o backlog do SO estiver cheio, falha rápido aqui.
        client.settimeout(TIMEOUT_CONEXAO)

        print(f"[CLIENTE {id_cliente:02d}] 🟡 Tentando entrar...")
        client.connect((HOST, PORT))

        # Fase 2: conexão estabelecida — agora envia a mensagem
        # e aguarda a resposta com um timeout mais generoso.
        print(f"[CLIENTE {id_cliente:02d}] 🟢 Conectou! Enviando mensagem...")
        client.sendall(f"Olá do cliente {id_cliente:02d}".encode('utf-8'))

        # Amplia o timeout para aguardar a resposta do servidor
        client.settimeout(TIMEOUT_RESPOSTA)
        print(f"[CLIENTE {id_cliente:02d}] ⏳ Aguardando resposta (até {TIMEOUT_RESPOSTA}s)...")

        msg = client.recv(1024)
        print(f"[CLIENTE {id_cliente:02d}] 🏆 SUCESSO: {msg.decode()}")

    except socket.timeout as e:
        # Diferencia onde ocorreu o timeout para diagnóstico mais preciso
        print(f"[CLIENTE {id_cliente:02d}] ⏱️  TIMEOUT: {e}")
    except ConnectionRefusedError:
        print(f"[CLIENTE {id_cliente:02d}] ⛔ RECUSADO: A fila estava cheia!")
    except Exception as e:
        print(f"[CLIENTE {id_cliente:02d}] ❌ ERRO: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    print("--- INICIANDO ATAQUE DE 10 CLIENTES SIMULTÂNEOS ---")
    print(f"    Timeout de conexão : {TIMEOUT_CONEXAO}s")
    print(f"    Timeout de resposta: {TIMEOUT_RESPOSTA}s")
    print()

    threads = []
    for i in range(1, 11):
        t = threading.Thread(target=cliente_nervoso, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n--- ATAQUE CONCLUÍDO ---")