import socket
import time

HOST = '127.0.0.1'
PORT = 65432

def iniciar_servidor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
    except OSError:
        print("Erro: Porta em uso. Espere um pouco ou mude a porta.")
        return

    # Backlog de 1: Tenta forçar a fila a ser minúscula.
    # Nota: O Windows/Linux pode "arredondar" isso para cima, por isso
    # vamos atacar com MUITOS clientes para garantir que estoure.
    server.listen(1)
    
    print(f"[SERVIDOR MONOTAREFA] Rodando em {HOST}:{PORT}")
    print("Capacidade: 1 atendendo + 1 na espera.")
    print("O resto deve falhar ou dar timeout.\n")
    
    while True:
        # O servidor aceita um...
        conn, addr = server.accept()
        print(f"--- [ATENDENDO] {addr} ---")
        
        # ...e dorme no serviço!
        # Como não tem threads, ele NÃO volta para o 'accept()'
        # O SO vai segurar alguns na fila, mas logo ela enche.
        time.sleep(10) 
        
        try:
            conn.send(b"Atendido com sucesso.")
            conn.close()
        except:
            pass
        print(f"--- [FINALIZADO] {addr} ---\n")

if __name__ == "__main__":
    iniciar_servidor()