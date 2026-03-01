import asyncio

HOST = '127.0.0.1'
PORT = 65432

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """
    Corrotina chamada pelo Event Loop para cada nova conexão.
    Substitui a função que antes rodava em uma Thread separada.
    """
    addr = writer.get_extra_info('peername')
    print(f"[NOVA CONEXÃO] {addr}")

    # 1. Lê os dados enviados pelo cliente
    data = await reader.read(1024)
    msg = data.decode('utf-8')
    print(f"[{addr}] Recebido: {msg}")

    # 2. Simula processamento pesado SEM bloquear a thread principal.
    #    asyncio.sleep suspende apenas esta corrotina, devolvendo o controle
    #    ao Event Loop para atender outros clientes enquanto aguarda.
    await asyncio.sleep(5)

    # 3. Envia a resposta ao cliente
    resposta = f"Processado: {msg}".encode('utf-8')
    writer.write(resposta)
    await writer.drain()

    # 4. Fecha a conexão
    writer.close()
    await writer.wait_closed()

    print(f"[DESCONECTADO] {addr}")


async def main():
    """
    Ponto de entrada assíncrono: cria e inicia o servidor.
    """
    server = await asyncio.start_server(handle_client, HOST, PORT)

    print(f"[ASSÍNCRONO] Servidor rodando em {HOST}:{PORT} — Event Loop ativo.")

    # Mantém o servidor rodando indefinidamente
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())