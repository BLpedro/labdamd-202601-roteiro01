

**Disciplina:** Laboratório de Desenvolvimento de Aplicações Móveis e Distribuídas  
**Professor:** Cristiano de Macedo Neto  

---

## Questão 1 — Backlog e Recusa de Conexões

### Contexto experimental

Ao executar o `clientenervoso.py` (10 clientes simultâneos) contra o `servergargalo.py`, todos os clientes que chegaram a conectar receberam **`socket.timeout`** ao aguardar a resposta. Contra o `server.py`, os mesmos 10 clientes foram atendidos com sucesso.

### Explicação técnica

Quando uma aplicação chama `socket.listen(n)`, ela não cria diretamente a conexão ela instrui o kernel do Sistema Operacional a manter uma **fila de conexões pendentes** (backlog) de tamanho `n`. O kernel gerencia essa fila de forma autônoma: ao receber um pacote SYN de um cliente, ele completa o handshake TCP por conta própria (SYN → SYN-ACK → ACK) e coloca a conexão estabelecida nessa fila. Só então a aplicação, ao chamar `accept()`, retira uma conexão da fila para atender.

O `servergargalo.py` configura `listen(1)` um backlog de apenas 1 conexão e ainda executa um `time.sleep(10)` antes de cada `accept()`. Isso cria um gargalo duplo: a fila é minúscula e é drenada lentamente. Com 10 clientes chegando simultaneamente, a fila satura rapidamente.

O comportamento exato após a saturação no S.O **Windows** (S.O utilizado neste experimento): o kernel não rejeita ativamente ele simplesmente não responde ao SYN excedente. O cliente fica aguardando o SYN-ACK que nunca chega, até estourar o próprio timeout de conexão (`socket.timeout`).



O `server.py`, por contraste, usa `server.listen()` sem restrição (o padrão do Windows aceita até 200 conexões pendentes no backlog), e chama `accept()` continuamente, delegando cada conexão a uma Thread imediatamente. A fila é drenada quase instantaneamente, e todos os 10 clientes são atendidos sem qualquer erro.

---

## Questão 2 — Custo de Recursos: Threads vs. Event Loop

### Observação experimental — `server.py` (Multithread)

Durante a execução do `clientenervoso.py` com 10 clientes simultâneos contra o `server.py`, o log exibiu:



 valor máximo observado de `threading.active_count()` foi **10 threads de cliente + 1 thread principal = 11 threads ativas** no processo Python simultaneamente.

### Custo de memória — Threads

No Windows, cada thread criada pelo Sistema Operacional recebe por padrão **1 MB de stack reservado** (com commit inicial de 4 KB, expansível). Com 10 threads de cliente ativas simultaneamente:

- **Stack reservado**: 10 × 1 MB = **~10 MB** apenas em memória de pilha de threads
- **Estruturas de controle do kernel**: cada thread exige um objeto `ETHREAD` no kernel do Windows, com custo adicional de memória no espaço privilegiado
- **Heap da aplicação**: memória alocada pelos objetos Python dentro de cada thread (sockets, buffers, frames de execução)

Durante os 5 segundos de `time.sleep(5)` em que cada thread ficava bloqueada aguardando, todas as 10 threads permaneciam **vivas e alocadas no SO**, consumindo memória e sendo candidatas ao escalonador — mesmo sem fazer nenhum trabalho útil.

### Custo de CPU — Context Switch

Com 10 threads bloqueadas em I/O/sleep, o escalonador do Windows realizava **trocas de contexto periódicas** entre elas para verificar se alguma havia desbloqueado. Cada troca de contexto envolve salvar e restaurar o estado completo dos registradores da CPU para a thread que sai e para a thread que entra. Esse overhead cresce linearmente com o número de threads — com centenas de conexões simultâneas, o custo de context switch pode superar o tempo de processamento útil.

### Custo de memória — Event Loop (`server_async.py`)

Com o `server_async.py`, o mesmo teste de 10 clientes simultâneos foi atendido com **1 única thread** ativa no processo Python. O estado de cada corrotina suspensa em `await asyncio.sleep(5)` é armazenado como um objeto Python no **heap**, não como uma stack de thread no kernel. O custo por corrotina suspensa é da ordem de poucos kilobytes — ordens de grandeza menor que uma thread.

### Comparativo direto (baseado na observação experimental)

| Métrica | Multithread — `server.py` | Assíncrono — `server_async.py` |
|---|---|---|
| Threads ativas (10 clientes) | **11 threads** (observado) | **1 thread** |
| Stack de threads (Windows) | ~10 MB reservados | ~1 MB (só thread principal) |
| Context switches (kernel) | Frequentes entre 11 threads | Mínimos (chaveamento em nível de usuário) |
| Custo por conexão adicional | 1 nova thread + 1 MB de stack | 1 nova corrotina + ~KB de heap |
| Escalabilidade para 1.000 clientes | ~1 GB só em stacks + instabilidade por context switch | ~MB de heap + Event Loop estável |

### Conclusão

A diferença não é apenas conceitual: com apenas 10 clientes, o modelo multithread já alocava 11 threads no kernel do Windows, cada uma com stack própria e sujeita ao escalonador. O modelo assíncrono eliminou esse custo completamente — uma única thread, sem context switches de kernel, atendeu a mesma carga. Essa vantagem se torna crítica na escala do problema C10K (10.000 conexões simultâneas), onde o modelo de threads se torna insustentável por consumo de memória e CPU.

**Referências:** Silberschatz, Galvin & Gagne (2018, cap. 4); Ousterhout (1996), *Why Threads Are A Bad Idea*; Kegel (2006).

---

## Referências Bibliográficas

- KEGEL, D. **The C10K Problem**, 2006. Disponível em: http://www.kegel.com/c10k.html.
- OUSTERHOUT, J. **Why Threads Are A Bad Idea (for most purposes)**. USENIX Technical Conference, 1996.
- PYTHON SOFTWARE FOUNDATION. **asyncio — Asynchronous I/O**. Python 3 Documentation. Disponível em: https://docs.python.org/3/library/asyncio.html.
- SILBERSCHATZ, A.; GALVIN, P. B.; GAGNE, G. **Operating System Concepts**. 10. ed. Wiley, 2018. cap. 4.
- TANENBAUM, A. S.; WETHERALL, D. J. **Computer Networks**. 5. ed. Pearson Prentice Hall, 2011. cap. 6.
