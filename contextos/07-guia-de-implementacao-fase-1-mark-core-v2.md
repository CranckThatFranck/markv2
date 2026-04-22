# Guia de Implementação Fase 1 do Mark Core v2

## Objetivo
Transformar a arquitetura do Mark Core v2 em uma sequência braçal, linear e validável para a primeira fase de implementação do novo backend/core.

## Escopo da Fase 1
A Fase 1 deve entregar a fundação mínima funcional do novo core:
- backend sobe
- WebSocket sobe
- `sync_state`
- `get_status`
- sessão/histórico persistidos
- `initial_rules.txt`
- registry de modelos/providers
- client Google AI API
- client Vertex AI
- `execute_task`
- `interrupt`
- ferramenta shell
- logs básicos

## Regra de Execução
1. Nenhuma etapa estrutural deve ser pulada.
2. Nenhuma etapa posterior deve assumir que a anterior já “deve estar funcionando”.
3. Validar cada etapa localmente antes de avançar.

## Pré-condições
Antes de codar:
1. Ler a arquitetura do Mark Core v2.
2. Ler o contrato operacional do Mark Core v2.
3. Ler o roadmap do Mark Core v2.
4. Ler a política de providers, modelos e credenciais.
5. Ler a estrutura de diretórios do v2.
6. Garantir que o Mark Alfa foi congelado como referência.

## Etapa 1 - Criar a estrutura inicial do backend
Objetivo:
Preparar a árvore real do novo core.

Criar:
- `src/backend/main.py`
- `src/backend/api/`
- `src/backend/protocol/`
- `src/backend/session/`
- `src/backend/agent/`
- `src/backend/models/`
- `src/backend/tools/`
- `src/backend/execution/`
- `src/backend/storage/`
- `src/backend/security/`
- `src/backend/logging/`
- `src/backend/product_config/`

Validar:
- a árvore existe
- os módulos importam sem erro básico
- o repositório está coerente com a documentação

## Etapa 2 - Criar requirements-backend.txt
Objetivo:
Definir as dependências mínimas do v2.

Incluir no mínimo:
- fastapi
- uvicorn
- pydantic
- websockets se necessário ao ecossistema
- sqlalchemy ou sqlmodel
- aiosqlite ou equivalente
- httpx
- google-generativeai ou client equivalente para Google AI API, se essa for a opção oficial adotada
- bibliotecas oficiais ou equivalentes para Vertex AI
- psutil
- asyncssh
- pytest
- pytest-asyncio

Validar:
- ambiente virtual instala as dependências
- imports críticos resolvem

## Etapa 3 - Bootstrap do backend
Objetivo:
Fazer o backend subir.

Implementar em `main.py`:
- bootstrap FastAPI
- rota de health
- startup hooks
- shutdown hooks
- subida do WebSocket

Validar:
- o processo sobe
- a rota de health responde
- o WebSocket aceita conexão

Critério de aceite local:
- backend rodando sem crash inicial

## Etapa 4 - Criar o protocolo base
Objetivo:
Definir a base do JSON/WebSocket.

Criar:
- `protocol/schemas.py`
- `protocol/actions.py`
- `protocol/events.py`

Implementar:
- schemas mínimos
- `sync_state`
- `action_response`
- `status`
- `message`
- `console`
- `system`

Validar:
- payloads são serializados corretamente
- erros inválidos geram resposta estruturada

Critério de aceite local:
- cliente de teste consegue conectar e receber `sync_state`

## Etapa 5 - Criar state_manager, session_store e history_store
Objetivo:
Dar memória operacional ao backend.

Implementar:
- estado atual do backend
- sessão ativa
- histórico persistido
- revisão do histórico

Persistir:
- `config.json`
- `session.json`
- banco SQLite quando aplicável

Validar:
- reiniciar backend mantém estado mínimo esperado
- reconectar devolve histórico

Critério de aceite local:
- `sync_state` reflete estado real

## Etapa 6 - Criar initial_rules.txt e carregar no boot
Objetivo:
Dar constituição inicial real ao produto.

Criar:
- `src/backend/product_config/initial_rules.txt`

Implementar:
- carregamento do arquivo no boot
- exposição do caminho em `sync_state`
- uso das regras no contexto do agent loop

Validar:
- alterar o arquivo e reiniciar o backend muda o comportamento esperado
- o caminho aparece no estado sincronizado

Critério de aceite local:
- o backend sabe onde estão suas regras iniciais

## Etapa 7 - Criar registry e router de modelos/providers
Objetivo:
Preparar a base multi-provider.

Criar:
- `models/registry.py`
- `models/router.py`

Implementar:
- catálogo builtin inicial
- mapeamento `model_id -> provider`
- validação de model id
- lookup por provider

Validar:
- modelo Gemini via API resolve para `google_ai`
- modelo Vertex resolve para `vertex_ai`

Critério de aceite local:
- o backend resolve corretamente o provider do modelo

## Etapa 8 - Implementar client Google AI API
Objetivo:
Fazer a primeira chamada real a modelos Gemini via API Key.

Criar:
- `models/providers/google_ai_client.py`

Implementar:
- leitura da credencial
- chamada simples ao modelo
- tratamento de erro de autenticação
- tratamento de rate limit
- tratamento de quota

Validar:
- uma pergunta simples responde corretamente
- erro de chave inválida é claro

Critério de aceite local:
- o backend consegue chamar o provider Google AI API

## Etapa 9 - Implementar client Vertex AI
Objetivo:
Fazer a primeira chamada real a modelos via Google Cloud.

Criar:
- `models/providers/vertex_ai_client.py`

Implementar:
- leitura de:
  - `GOOGLE_APPLICATION_CREDENTIALS`
  - `VERTEXAI_PROJECT`
  - `VERTEXAI_LOCATION`
- chamada simples ao modelo
- tratamento de autenticação
- tratamento de projeto/região
- tratamento de indisponibilidade do modelo

Validar:
- uma pergunta simples responde corretamente
- erro de região/projeto é claro

Critério de aceite local:
- o backend consegue chamar o provider Vertex AI

## Etapa 10 - Implementar provider_store e seleção de credencial
Objetivo:
Separar provider, modelo e credencial.

Criar:
- `models/credentials/key_manager.py`
- `models/credentials/vertex_credentials.py`
- `storage/provider_store.py`

Implementar:
- credencial ativa por provider
- leitura persistida de metadados
- troca manual da credencial ativa
- status seguro de credenciais

Validar:
- trocar credencial ativa não quebra o backend
- frontend ou cliente de teste consegue consultar status seguro

Critério de aceite local:
- o backend consegue escolher a credencial certa por provider

## Etapa 11 - Criar o motor agentic mínimo
Objetivo:
Fazer o backend pensar sem Open Interpreter.

Criar:
- `agent/engine.py`
- `agent/prompts.py`
- `agent/tool_router.py`

Implementar:
- contexto mínimo do agente
- regras iniciais + prompt de sistema
- saída estruturada em JSON
- dois caminhos:
  - `final_answer`
  - `use_tool`

Validar:
- o modelo retorna decisão previsível
- JSON inválido é tratado
- o loop não entra em alucinação infinita simples

Critério de aceite local:
- uma tarefa simples gera decisão estruturada

## Etapa 12 - Criar shell_tool
Objetivo:
Dar ação real ao agente.

Criar:
- `tools/shell_tool.py`
- `execution/process_manager.py`
- `execution/stream_manager.py`
- `execution/interrupt_manager.py`
- `execution/task_runner.py`

Implementar:
- execução de comando shell
- streaming stdout/stderr
- timeout
- rastreamento PID/PGID
- encerramento por interrupção

Validar:
- comando curto funciona
- comando mais longo streama saída
- interrupção funciona

Critério de aceite local:
- a shell tool é utilizável de forma segura

## Etapa 13 - Implementar execute_task
Objetivo:
Fechar o fluxo ponta a ponta.

Implementar:
- ação `execute_task`
- criação de task id
- eco `user`
- status START
- loop agentic
- uso de ferramenta quando necessário
- resposta final
- status END
- persistência de histórico

Validar:
- cliente recebe todos os eventos
- resposta final aparece
- histórico é persistido

Critério de aceite local:
- tarefa ponta a ponta funciona

## Etapa 14 - Implementar interrupt
Objetivo:
Dar controle real ao operador.

Implementar:
- ação `interrupt`
- localização da task ativa
- término do grupo de processos
- limpeza de estado
- evento de sistema
- atualização de `sync_state`

Validar:
- tarefa longa pode ser interrompida
- backend continua vivo
- próxima tarefa pode começar depois

Critério de aceite local:
- kill switch funcional

## Etapa 15 - Implementar logs básicos
Objetivo:
Tornar o backend observável.

Implementar:
- `backend.log`
- `events.log`
- `errors.log`

Registrar:
- start do backend
- fim do backend
- execute_task
- interrupt
- change_model
- change_provider
- fallback
- erro de provider
- erro de ferramenta

Validar:
- os logs são legíveis
- o operador consegue entender o fluxo da última tarefa

Critério de aceite local:
- há observabilidade mínima real

## Etapa 16 - Teste com cliente mínimo
Objetivo:
Provar o v2 sem depender do frontend imediatamente.

Implementar ou usar:
- cliente WebSocket simples de teste

Validar:
- connect
- sync_state
- get_status
- execute_task
- interrupt
- get_models
- get_providers

Critério de aceite local:
- o backend funciona mesmo sem o frontend final adaptado

## Etapa 17 - Adaptar o frontend atual ao mínimo do v2
Objetivo:
Reusar rapidamente o frontend já existente.

Implementar:
- leitura do novo `sync_state`
- leitura do catálogo de modelos/providers
- execute_task
- interrupt
- renderização da resposta final

Validar:
- frontend conversa com o novo backend
- o básico ponta a ponta funciona

Critério de aceite local:
- o novo core é utilizável pela UI existente

## Etapa 18 - Testes de smoke da Fase 1
Objetivo:
Validar a base entregue.

Checklist mínimo:
- backend sobe
- health responde
- WebSocket conecta
- sync_state chega
- get_status responde
- Google AI API responde
- Vertex AI responde
- execute_task responde
- shell tool funciona
- interrupt funciona
- sessão persiste
- histórico persiste
- logs são escritos

## Proibições Durante a Fase 1
1. Não reintroduzir Open Interpreter como motor central.
2. Não depender de wrappers genéricos opacos para esconder a lógica do produto.
3. Não começar pelo SSH antes do núcleo local estar validado.
4. Não expandir para multiagente antes do backend mínimo funcionar.
5. Não misturar provider, modelo e credencial como se fossem a mesma coisa.
6. Não deixar fallback entre providers implícito sem política.

## Critério Final da Fase 1
A Fase 1 só pode ser considerada pronta quando existir:
- backend v2 próprio
- dois providers Google funcionando
- session/history funcionando
- execute_task funcionando
- interrupt funcionando
- shell tool funcionando
- frontend conseguindo operar o núcleo mínimo
- logs suficientes para troubleshooting

## Regra Final
A Fase 1 não existe para entregar o sistema inteiro.
Ela existe para provar que o Mark Core v2 tem uma fundação própria, confiável e extensível, sem as fragilidades estruturais que motivaram o pivot.
