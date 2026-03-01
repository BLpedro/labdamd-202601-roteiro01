import socket
import threading
import time

HOST = '127.0.0.1'
PORT = 65432

def processar_requisicao(conn, addr):
    print(f"[NOVA CONEXÃO] {addr} conectado.")

    # simula processamento pesado
    time.sleep(5)

    try:
        resposta = "Processado com sucesso.".encode('utf-8')
        conn.send(resposta)
    except:
        pass

    conn.close()
    print(f"[DESCONECTADO] {addr}")

def iniciar_servidor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # evita erro de porta em uso
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))

    # backlog padrão já é suficiente
    server.listen()
    print(f"[OUVINDO] Servidor rodando em {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()

        thread = threading.Thread(
            target=processar_requisicao,
            args=(conn, addr)
        )

        thread.start()

        print(f"[ATIVO] Conexões simultâneas: {threading.active_count() - 1}")

if __name__ == "__main__":
    print("--- INICIANDO SERVIDOR ---")
    iniciar_servidor()