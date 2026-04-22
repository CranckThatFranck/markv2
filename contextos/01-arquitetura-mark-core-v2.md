# Arquitetura do Mark Core v2

## Objetivo
Este documento define a arquitetura oficial do novo backend/core dos agentes Mark, refeito do zero para substituir a dependência estrutural do Open Interpreter como motor central do produto e já nascer com suporte oficial a múltiplos providers de modelo, incluindo Gemini via API e Vertex AI do Google Cloud.

## Decisão-Mãe
O Mark Core v2 não deve depender do Open Interpreter como núcleo agentic do produto.
O Open Interpreter pode existir apenas como referência histórica do Mark Alfa, mas não como base arquitetural do novo backend.

## Motivação do Pivot
O Mark Alfa comprovou valor em:
- UX inicial do frontend
- empacotamento `.deb` e `.rpm`
- daemonização via systemd
- persistência de sessão
- contrato WebSocket/JSON
- rotação de chaves
- fallback de modelos
- operação local e remota

Mas falhou como fundação confiável do backend por:
- travamentos recorrentes
- dependência excessiva de wrappers externos
- fragilidade do tool calling
- comportamento imprevisível sob carga
- baixa confiabilidade para operações longas
- excesso de tempo gasto corrigindo integrações frágeis em vez de evoluir o produto

O pivot existe para preservar o que funcionou ao redor e reescrever apenas o núcleo agentic.

## Objetivo do Mark Core v2
O Mark Core v2 deve ser um daemon local confiável, instalável e versionável, capaz de:
- receber tarefas
- planejar ou executar conforme o modo solicitado
- usar ferramentas locais e remotas com segurança
- transmitir progresso em tempo real
- manter sessão, histórico e estado
- suportar interrupção real
- suportar rotação de credenciais e fallback de modelo
- operar localmente ou ser controlado remotamente
- servir como base dos futuros Marks e do Jarvis Master

## Escopo Inicial
O Mark Core v2 cobre inicialmente:
- backend daemon Linux
- comunicação WebSocket/JSON
- motor agentic próprio
- ferramentas controladas
- execução local e SSH
- persistência
- logs
- systemd
- instalação por `.deb` e `.rpm`
- suporte dual de provider para modelos:
  - Gemini via API
  - Vertex AI via Google Cloud

O frontend atual pode ser reaproveitado e adaptado ao novo contrato, sem redesenhar o produto inteiro.

## Stack Oficial do Novo Core

### Linguagem
Python 3.12 ou superior compatível com o ecossistema alvo.

### Camada de API/Transporte
- FastAPI
- Uvicorn
- WebSocket nativo no backend

### Providers e Modelos
- Provider 1: Gemini via API Key
- Provider 2: Vertex AI via Google Cloud
- Sem Open Interpreter no centro
- Sem LiteLLM como orquestrador central do produto

### Execução local
- `asyncio`
- `subprocess`
- PTY quando estritamente necessário
- `psutil` para inspeção e gerenciamento de processo

### Execução remota
- `asyncssh`

### Persistência
- SQLite para sessões, tarefas e eventos
- JSON para configurações simples e arquivos auxiliares

### Testes
- pytest
- pytest-asyncio

## Princípios Arquiteturais
1. Uma responsabilidade por camada.
2. O backend é a fonte de verdade.
3. O frontend é apenas cliente de controle e observação.
4. O loop agentic deve ser explícito, rastreável e previsível.
5. Tool calling deve ser controlado pelo próprio produto.
6. Logs devem ser legíveis e auditáveis.
7. Interrupção deve ser real, não simbólica.
8. Fallbacks devem ser explícitos e documentados.
9. Persistência deve ser simples, suficiente e recuperável.
10. Primeiro confiável. Depois sofisticado.
11. Provider de modelo é detalhe de infraestrutura, não arquitetura de negócio.
12. O agent loop deve continuar funcional mesmo se um provider específico falhar.

## Visão de Alto Nível
O novo backend é dividido em módulos claros.

### app
Camada de inicialização do serviço.

Responsável por:
- bootstrap do backend
- carregamento de config
- carregamento de regras iniciais
- inicialização dos stores
- subida da API e do WebSocket

### protocol
Contrato JSON/WebSocket do produto.

Responsável por:
- schemas de entrada e saída
- tipos de eventos
- tipos de ações
- serialização consistente
- compatibilidade de protocolo

### session
Estado operacional e memória de curto/médio prazo.

Responsável por:
- sessão ativa
- histórico
- revisão do histórico
- status atual
- task atual
- metadados de conexão

### agent
Motor agentic próprio.

Responsável por:
- montar contexto da tarefa
- aplicar regras iniciais
- decidir próximo passo
- pedir uso de ferramenta
- consolidar resposta final
- diferenciar Plan e Agent

### tools
Ferramentas disponíveis ao agente.

Primeira leva:
- shell
- python
- read_file
- write_file
- list_dir
- search_text
- ssh_exec
- system_info

### execution
Execução real de tarefas.

Responsável por:
- subprocessos
- streaming stdout/stderr
- tempo limite
- rastreamento PID/PGID
- interrupção
- prevenção de zumbis

### security
Guardrails e políticas.

Responsável por:
- validação de comandos
- modo plan vs agent
- ações sensíveis
- caminhos proibidos
- hosts remotos autorizados
- confirmações quando necessário

### storage
Persistência do produto.

Responsável por:
- banco SQLite
- config persistente
- regras iniciais
- sessão/histórico
- metadados de credenciais
- cadastro de modelos extras

### logging
Observabilidade.

Responsável por:
- logs do backend
- logs de evento
- logs de erro
- logs de task
- logs de fallback
- logs de troca de modelo/credencial/provider

## Arquitetura de Providers
O Mark Core v2 deve separar claramente:
- motor agentic
- catálogo de modelos
- credenciais
- provider real que executa a chamada

### Conceito
O agente não fala diretamente com “Gemini API” ou “Vertex AI”.
Ele fala com uma camada interna chamada `model_router`.

O `model_router`:
- recebe o model id solicitado
- identifica o provider correspondente
- resolve credenciais
- resolve região quando aplicável
- resolve opções do request
- chama o client certo
- devolve resposta normalizada ao agent loop

### Providers oficiais da primeira versão

#### Google AI API
Responsável por modelos acessados com API Key simples.

Exemplos de id:
- `gemini/gemini-3-flash-preview`
- `gemini/gemini-3.1-pro-preview`
- `gemini/gemini-3.1-pro-preview-customtools`
- `gemini/gemini-2.5-flash`
- `gemini/gemini-2.5-pro`

Credenciais esperadas:
- `GOOGLE_API_KEY`

#### Vertex AI
Responsável por modelos acessados pelo Google Cloud.

Exemplos de id:
- `vertex_ai/gemini-2.5-pro`
- `vertex_ai/gemini-2.5-flash`
- `vertex_ai/gemini-3.1-pro-preview`
- `vertex_ai/gemini-3.1-pro-preview-customtools`
- modelos futuros disponibilizados na conta do Google Cloud
- modelos não-Gemini disponibilizados via Vertex AI quando oficialmente suportados pelo produto

Credenciais esperadas:
- `GOOGLE_APPLICATION_CREDENTIALS`
- `VERTEXAI_PROJECT`
- `VERTEXAI_LOCATION`

### Regras de provider
1. O provider é derivado do model id ou da configuração persistida.
2. O frontend não precisa conhecer detalhes internos do SDK usado por cada provider.
3. O backend expõe tudo como um catálogo unificado de modelos.
4. Fallback entre modelos deve considerar compatibilidade de provider.
5. Fallback entre providers só deve ocorrer quando explicitamente permitido pela política do produto.

## Formato de Decisão do Agente
O novo core não deve depender de tool calls opacos ou frágeis.
O modelo deve responder em JSON estruturado e previsível.

Exemplo de uso de ferramenta:
```json
{
  "mode": "agent",
  "decision": "use_tool",
  "tool_name": "shell",
  "tool_input": {
    "command": "systemctl status jarvis-backend"
  },
  "reason": "Verificar o estado atual do serviço"
}

Exemplo de resposta final:

{
  "mode": "agent",
  "decision": "final_answer",
  "message": "O serviço está ativo e sem falhas recentes."
}

Modo Plan e Modo Agent
Plan

No modo Plan o agente:

analisa
lê contexto
quebra problema em etapas
propõe ações
não executa ações sensíveis no sistema
não altera arquivos críticos por padrão
não dispara ferramenta de impacto
Agent

No modo Agent o agente:

executa o plano
chama ferramentas
testa
corrige
registra andamento
conclui ou interrompe
Ferramentas da Primeira Versão
shell_tool

Executa comandos shell controlados com:

streaming
timeout
rastreamento PID/PGID
kill switch
python_tool

Executa trechos Python controlados para automação local.

file_tool

Permite:

ler arquivo
escrever arquivo
listar diretórios
buscar texto
system_tool

Permite:

estado do sistema
info de CPU
memória
disco
serviços
ssh_tool

Executa operações SSH remotas controladas.
Só deve existir após o núcleo local estar estável.

Segurança Inicial

O Mark Core v2 deve nascer mais seguro do que o Mark Alfa.

Regras obrigatórias
comandos destrutivos devem ser bloqueados ou exigir confirmação
modo Plan não executa
ações de alto risco exigem validação
caminhos sensíveis devem ser protegidos
operações remotas devem respeitar allowlist ou política equivalente
toda ação relevante deve ser logada
credenciais de provider nunca devem ser expostas no frontend como texto aberto após salvas
Persistência Oficial
Código do produto
/opt/jarvis/backend
/opt/jarvis/frontend
/opt/jarvis/venv
Estado e dados
/var/lib/jarvis-mark/estado/config.json
/var/lib/jarvis-mark/estado/session.json
/var/lib/jarvis-mark/estado/tasks.db
/var/lib/jarvis-mark/estado/providers.json
Logs
/var/log/jarvis/backend.log
/var/log/jarvis/events.log
/var/log/jarvis/errors.log
Regras iniciais
/opt/jarvis/backend/product_config/initial_rules.txt
Reaproveitamento do Mark Alfa
Reaproveitar
frontend atual como base
contrato WebSocket atual como ponto de partida
empacotamento .deb e .rpm
initial_rules.txt
UX já validada
documentação de contexto
gestão de host local/remoto no frontend
gestão visual de modelos e API keys
fluxo de persistência e reconexão
Não reaproveitar como núcleo
Open Interpreter como motor central
LiteLLM como orquestrador principal
tool calling implícito
traduções frágeis entre providers
Estrutura Inicial Sugerida
src/backend/
├── main.py
├── api/
│   ├── websocket.py
│   └── health.py
├── agent/
│   ├── engine.py
│   ├── planner.py
│   ├── prompts.py
│   └── tool_router.py
├── models/
│   ├── router.py
│   ├── registry.py
│   ├── fallback.py
│   ├── providers/
│   │   ├── google_ai_client.py
│   │   └── vertex_ai_client.py
│   ├── credentials/
│   │   ├── key_manager.py
│   │   ├── vertex_credentials.py
│   │   └── provider_store.py
│   └── policies/
│       ├── provider_policy.py
│       └── model_policy.py
├── tools/
│   ├── shell_tool.py
│   ├── python_tool.py
│   ├── file_tool.py
│   ├── ssh_tool.py
│   └── system_tool.py
├── execution/
│   ├── process_manager.py
│   ├── stream_manager.py
│   ├── interrupt_manager.py
│   └── task_runner.py
├── session/
│   ├── session_store.py
│   ├── history_store.py
│   └── state_manager.py
├── protocol/
│   ├── schemas.py
│   ├── events.py
│   └── actions.py
├── storage/
│   ├── db.py
│   ├── config_store.py
│   ├── rules_store.py
│   └── provider_store.py
├── security/
│   ├── policies.py
│   ├── command_guard.py
│   └── confirmations.py
├── logging/
│   ├── logger.py
│   └── audit.py
└── product_config/
    └── initial_rules.txt
Critério de Sucesso Arquitetural

A arquitetura do Mark Core v2 estará correta quando:

o backend puder operar sem Open Interpreter no centro
o loop agentic for previsível e rastreável
as ferramentas forem controladas pelo próprio produto
o kill switch funcionar de forma real
o frontend puder continuar sendo cliente do backend
o sistema conseguir operar tanto com Google AI API quanto com Vertex AI
o sistema puder crescer para multiagentes e Jarvis Master sem gambiarra estrutural
Regra Final

O novo core não nasce para ser apenas mais uma tentativa.
Ele nasce para ser a fundação real, confiável e extensível dos futuros Marks, com suporte limpo a múltiplos providers de modelo desde a base.
