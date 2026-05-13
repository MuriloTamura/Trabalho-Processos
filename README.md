# Trabalho 1 - Sistemas Operacionais

Simulações desenvolvidas para o Trabalho 1 da disciplina de Sistemas Operacionais do IFCE - Campus Maracanaú, conforme o enunciado do Prof. Daniel Ferreira.

O trabalho aborda três problemas clássicos de sistemas operacionais e concorrência:

- escalonamento de processos;
- sincronização entre múltiplas threads com recursos limitados;
- controle de acesso concorrente com restrições por categoria.

## Objetivo

O objetivo deste projeto é demonstrar, por meio de simulações executáveis, conceitos fundamentais de sistemas operacionais, com foco em:

- políticas de escalonamento;
- métricas de desempenho;
- exclusão mútua;
- uso de semáforos, locks e filas de espera;
- prevenção de deadlock;
- tratamento de inanição.

## Estrutura do Trabalho

O projeto está organizado em três questões:

- `questão1.py`: simulação comparativa entre RR e SRTF.
- `questao2.py`: simulação concorrente com cinco programadores, um compilador e banco de dados compartilhado.
- `Questão 3`: simulação do protocolo da sala de repouso para cães e gatos, contemplando versões com e sem possibilidade de inanição.

## Questão 1

A Questão 1 compara o algoritmo Round Robin (RR) com o algoritmo Shortest Remaining Time First (SRTF), conforme o enunciado.

### O que a simulação faz

- utiliza tempos de chegada diferentes para os processos;
- considera custo de troca de contexto igual a 1 unidade de tempo;
- compara vários valores de quantum para o RR;
- calcula métricas de desempenho;
- exibe a sequência de execução dos processos;
- apresenta uma análise comparativa entre os algoritmos.

### Métricas analisadas

- tempo médio de resposta;
- desvio padrão do tempo de resposta;
- tempo médio de retorno;
- desvio padrão do tempo de retorno;
- vazão em uma janela de tempo `T`.

### Ideia central

O RR tende a ser mais justo entre os processos, enquanto o SRTF favorece processos curtos e costuma reduzir o tempo médio de retorno. Em contrapartida, o RR pode sofrer com overhead alto para quantums pequenos, e o SRTF pode penalizar processos longos.

## Questão 2

A Questão 2 modela cinco programadores trabalhando em paralelo, cada um tentando compilar repetidamente seu módulo em um ambiente com recursos limitados.

### Regras do problema

- apenas um programador pode usar o compilador por vez;
- no máximo dois programadores podem acessar o banco de dados ao mesmo tempo;
- um programador só compila quando possui os dois recursos;
- a execução ocorre em laço infinito para fins de apresentação;
- a solução deve evitar deadlock e inanição.

### Estratégia adotada

A implementação usa `threading`, `Condition`, `Lock` e uma fila FIFO para coordenar o acesso aos recursos. Assim:

- o compilador é tratado como recurso exclusivo;
- o banco de dados é tratado como recurso com capacidade limitada;
- a fila justa organiza a ordem de atendimento;
- o sistema evita ciclos de espera;
- a saída mostra claramente o estado atual de cada programador.

### O que pode ser observado durante a execução

- qual programador está pensando;
- quem entrou na fila;
- quem está compilando;
- quantos slots do banco de dados estão livres;
- a ordem de espera dos programadores;
- o progresso contínuo da simulação sem travamento.

## Questão 3

A Questão 3 trata de um protocolo de acesso a uma sala de repouso compartilhada por cães e gatos.

### Regras do problema

- se há cachorros na sala, outros cachorros podem entrar;
- se há gatos na sala, outros gatos podem entrar;
- gatos e cachorros não podem ocupar a sala ao mesmo tempo;
- a sala pode assumir apenas três estados:
  - `EMPTY`
  - `DOGS`
  - `CATS`

### O que a solução demonstra

- controle do estado da sala;
- sincronização de entrada e saída dos animais;
- política de bloqueio por espécie;
- comparação entre uma versão com possibilidade de inanição e outra com tratamento mais justo.

### Importância da comparação

Essa questão é importante porque mostra que uma solução pode estar correta do ponto de vista de exclusão mútua, mas ainda assim ser injusta. A versão com inanição destaca esse risco, enquanto a versão sem inanição evidencia uma política mais equilibrada de acesso.

## Como executar

Abra o terminal na pasta do projeto e execute:

### Questão 1

```powershell
python questão1.py
```

### Questão 2

```powershell
python questao2.py
```

Para interromper a Questão 2, use:

```powershell
Ctrl + C
```

## Requisitos

- Python 3.10 ou superior;
- biblioteca `reportlab` para geração de PDF, quando necessário.

Se precisar instalar o `reportlab`:

```powershell
python -m pip install reportlab
```

## Geração de PDF

O projeto também pode incluir material de apoio em PDF para apresentação da Questão 2. Quando disponível, a geração pode ser feita com:

```powershell
python gerar_pdf.py
```

## Conceitos Aplicados

Este trabalho exercita os seguintes conceitos:

- Round Robin;
- SRTF preemptivo;
- troca de contexto;
- vazão;
- tempo de resposta;
- tempo de retorno;
- threads;
- exclusão mútua;
- semáforos e condições;
- deadlock;
- starvation (inanição);
- justiça no acesso a recursos compartilhados.

## Conclusão

O projeto foi construído para servir tanto como entrega acadêmica quanto como base de apresentação prática. As simulações mostram, de forma visual e executável, como diferentes políticas de escalonamento e sincronização afetam desempenho, justiça e segurança em sistemas concorrentes.

Além de resolver os problemas propostos, o trabalho ajuda a conectar a teoria vista em sala com situações reais de coordenação entre processos e threads.
