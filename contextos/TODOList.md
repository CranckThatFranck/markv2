### Instruções de leitura e movimentação do documento:
**Inicie a leitura dos itens em A fazer**: esta será a lista operacional oficial do Mark Core v2. Cada work item deve existir em uma única linha iniciada por `-`.
**No ## Fazendo**: mova para cá apenas o item que estiver realmente em execução no momento.
**No ## Feito**: mova para cá apenas o item que estiver realmente concluído, validado e com commit/push realizados.
**Regra de versionamento**: ao concluir cada item real e movê-lo para `## Feito`, executar imediatamente `git add . && git commit -m "mensagem curta e objetiva do item concluído" && git push origin <branch_atual>`.
**Regra de escopo**: não inventar requisito novo no meio sem registrar no TODO e, se for estrutural, também registrar em `pivotagem`.
**Regra de validação**: nenhum item pode ser marcado como concluído sem evidência concreta local de que funcionou.

## Feito
- Congelar o Mark Alfa atual como referência operacional e visual.
- Decidir o pivot para um backend/core próprio sem Open Interpreter.
- Definir a arquitetura inicial do Mark Core v2.
- Definir o contrato operacional inicial do Mark Core v2.
- Definir o roadmap inicial do Mark Core v2.
- Definir o contrato JSON do Mark Core v2.
- Definir a estrutura de diretórios do Mark Core v2.
- Definir a política de providers, modelos e credenciais do Mark Core v2.
- Definir o guia de implementação da Fase 1 do Mark Core v2.
- Criar a estrutura inicial de diretórios do novo backend em `src/backend`.
- Criar `requirements-backend.txt` do Mark Core v2.
- Criar `src/backend/main.py`.
- Criar `src/backend/api/health.py`.
- Criar `src/backend/api/websocket.py`.
- Criar `src/backend/protocol/schemas.py`.

## Fazendo
- Criar `src/backend/protocol/actions.py`.

## A fazer

### Preparação e coerência documental do v2
- Revisar os documentos 01 a 07 do Mark Core v2 e confirmar consistência final entre arquitetura, contrato operacional, contrato JSON, estrutura, providers, credenciais e roadmap.
- Atualizar o README.md do repositório para registrar oficialmente o pivot do backend para o Mark Core v2.
- Registrar no README.md que o Mark Alfa permanece como referência histórica/operacional e que o novo núcleo é o Mark Core v2.
- Revisar o DevJarvis atual e confirmar o que continua válido para o novo backend.
- Revisar o TODOList.md antigo e garantir que ele agora reflita apenas o trabalho do Mark Core v2.
- Criar pivotagem formal do abandono do núcleo baseado em Open Interpreter como motor central do produto.

### Estrutura inicial do novo backend
- Criar `src/backend/api/websocket.py`.
- Criar `src/backend/protocol/schemas.py`.
- Criar `src/backend/protocol/actions.py`.
- Criar `src/backend/protocol/events.py`.
- Criar `src/backend/session/state_manager.py`.
- Criar `src/backend/session/session_store.py`.
- Criar `src/backend/session/history_store.py`.
- Criar `src/backend/agent/engine.py`.
- Criar `src/backend/agent/planner.py`.
- Criar `src/backend/agent/prompts.py`.
- Criar `src/backend/agent/tool_router.py`.
- Criar `src/backend/models/router.py`.
- Criar `src/backend/models/registry.py`.
- Criar `src/backend/models/fallback.py`.
- Criar `src/backend/models/providers/google_ai_client.py`.
- Criar `src/backend/models/providers/vertex_ai_client.py`.
- Criar `src/backend/models/credentials/key_manager.py`.
- Criar `src/backend/models/credentials/vertex_credentials.py`.
- Criar `src/backend/models/credentials/provider_store.py`.
- Criar `src/backend/models/policies/provider_policy.py`.
- Criar `src/backend/models/policies/model_policy.py`.
- Criar `src/backend/tools/shell_tool.py`.
- Criar `src/backend/tools/python_tool.py`.
- Criar `src/backend/tools/file_tool.py`.
- Criar `src/backend/tools/system_tool.py`.
- Criar `src/backend/tools/ssh_tool.py`.
- Criar `src/backend/execution/process_manager.py`.
- Criar `src/backend/execution/stream_manager.py`.
- Criar `src/backend/execution/interrupt_manager.py`.
- Criar `src/backend/execution/task_runner.py`.
- Criar `src/backend/storage/db.py`.
- Criar `src/backend/storage/config_store.py`.
- Criar `src/backend/storage/rules_store.py`.
- Criar `src/backend/storage/provider_store.py`.
- Criar `src/backend/security/policies.py`.
- Criar `src/backend/security/command_guard.py`.
- Criar `src/backend/security/confirmations.py`.
- Criar `src/backend/logging/logger.py`.
- Criar `src/backend/logging/audit.py`.
- Criar `src/backend/product_config/initial_rules.txt`.

### Bootstrap mínimo do backend
- Implementar o bootstrap FastAPI/Uvicorn em `src/backend/main.py`.
- Implementar endpoint de healthcheck HTTP.
- Implementar subida do WebSocket principal.
- Implementar startup hooks do backend.
- Implementar shutdown hooks do backend.
- Validar que o backend sobe localmente sem crash.
- Validar que a rota de health responde.
- Validar que o WebSocket aceita conexão.

### Protocolo JSON/WebSocket v2
- Implementar schema base do protocolo JSON do Mark Core v2.
- Implementar envelope de entrada com `protocol_version`, `action` e `payload`.
- Implementar envelope de saída com `action_response`.
- Implementar tipos de evento `sync_state`, `status`, `system`, `user`, `message`, `code`, `console` e `provider_event`.
- Implementar ação `healthcheck`.
- Implementar ação `get_status`.
- Implementar ação `get_config`.
- Implementar ação `update_config`.
- Implementar ação `get_models`.
- Implementar ação `get_providers`.
- Implementar ação `change_model`.
- Implementar ação `change_provider`.
- Implementar ação `get_credentials_status`.
- Implementar ação `set_active_credential`.
- Implementar ação `add_custom_model`.
- Implementar ação `remove_custom_model`.
- Implementar ação `get_history`.
- Implementar ação `clear_session`.
- Implementar ação `execute_task`.
- Implementar ação `interrupt`.
- Implementar ação `shutdown_backend`.
- Implementar respostas de erro estruturadas com `error_code` e `message`.
- Validar que payload inválido gera erro estruturado.
- Validar que ação desconhecida gera erro estruturado.

### Estado, sessão e histórico
- Implementar o `state_manager` do novo backend.
- Implementar persistência do estado atual do backend.
- Implementar `session_store` da sessão ativa.
- Implementar `history_store` do histórico da sessão.
- Persistir estado em `config.json`.
- Persistir sessão em `session.json`.
- Persistir dados mais estruturados em SQLite quando aplicável.
- Implementar `history_revision`.
- Implementar `sync_state` com estado, catálogo de modelos, providers, credenciais seguras e histórico.
- Validar reconexão com reidratação de histórico.
- Validar persistência de sessão entre reinícios do backend.

### Regras iniciais do produto
- Criar o conteúdo inicial de `product_config/initial_rules.txt` para o Mark Core v2.
- Implementar carregamento de `initial_rules.txt` no boot do backend.
- Implementar exposição do caminho de `initial_rules.txt` dentro do `sync_state`.
- Garantir que o backend use o conteúdo de `initial_rules.txt` como referência global inicial do agente.
- Validar que alterar `initial_rules.txt` e reiniciar o serviço altera o comportamento esperado do backend.

### Registry de modelos e providers
- Implementar o registry unificado de modelos builtin.
- Implementar a distinção explícita entre provider, modelo e credencial.
- Declarar catálogo inicial de modelos Google AI API.
- Declarar catálogo inicial de modelos Vertex AI.
- Implementar mapeamento de `model_id -> provider`.
- Implementar lookup por provider.
- Implementar validação de model id.
- Implementar suporte a modelos customizados permitidos pela política.
- Persistir modelos customizados.
- Expor catálogo de modelos builtin, custom e total no protocolo.
- Validar que o backend resolve corretamente o provider a partir do model id.

### Provider Google AI API
- Implementar `google_ai_client.py`.
- Implementar leitura da credencial `GOOGLE_API_KEY`.
- Implementar chamada básica ao Gemini via Google AI API.
- Implementar tratamento de erro de autenticação Google AI API.
- Implementar tratamento de rate limit Google AI API.
- Implementar tratamento de quota excedida Google AI API.
- Implementar retorno normalizado para o agent loop.
- Validar uma pergunta simples via Google AI API.
- Validar erro claro quando `GOOGLE_API_KEY` estiver ausente ou inválida.

### Provider Vertex AI
- Implementar `vertex_ai_client.py`.
- Implementar leitura de `GOOGLE_APPLICATION_CREDENTIALS`.
- Implementar leitura de `VERTEXAI_PROJECT`.
- Implementar leitura de `VERTEXAI_LOCATION`.
- Implementar chamada básica ao modelo via Vertex AI.
- Implementar tratamento de erro de autenticação Vertex AI.
- Implementar tratamento de erro de projeto inválido no Vertex AI.
- Implementar tratamento de erro de região inválida no Vertex AI.
- Implementar tratamento de indisponibilidade de modelo no Vertex AI.
- Implementar retorno normalizado para o agent loop.
- Validar uma pergunta simples via Vertex AI.
- Validar erro claro quando credenciais ou região estiverem incorretas.

### Credenciais, rotação e estado seguro
- Implementar `key_manager.py` para credenciais do provider `google_ai`.
- Implementar `vertex_credentials.py` para metadados e seleção de credencial do provider `vertex_ai`.
- Implementar `provider_store.py` para persistir metadados de credenciais e provider ativo.
- Implementar seleção da credencial ativa por provider.
- Implementar leitura de status seguro das credenciais.
- Garantir que o frontend nunca receba segredos completos.
- Implementar troca manual da credencial ativa.
- Implementar rotação manual de credenciais via backend.
- Implementar persistência da credencial ativa por provider.
- Validar troca manual de credencial sem reiniciar o backend.
- Validar que o backend não vaza segredos em logs ou respostas WebSocket.

### Política de fallback
- Implementar fallback entre modelos do mesmo provider.
- Implementar fallback entre credenciais do mesmo provider.
- Implementar política explícita de fallback entre providers, desabilitada por padrão.
- Implementar registro em log de fallback de modelo.
- Implementar registro em log de fallback de credencial.
- Implementar evento `provider_event` para fallback.
- Validar fallback por quota/rate limit no `google_ai`.
- Validar fallback por falha de região/modelo no `vertex_ai`.
- Validar que o backend diferencia claramente falha de autenticação, falha de quota, falha de região e falha de modelo.

### Motor agentic próprio
- Implementar o `agent/engine.py`.
- Definir o formato estruturado de decisão do agente em JSON.
- Implementar suporte às decisões `final_answer` e `use_tool`.
- Implementar `planner.py` para modo Plan.
- Implementar `tool_router.py`.
- Implementar construção do contexto da tarefa.
- Implementar aplicação das regras iniciais ao agent loop.
- Implementar limites de iteração.
- Implementar tratamento de JSON inválido vindo do modelo.
- Implementar retorno legível de falha do agent loop.
- Validar uma tarefa simples em modo Plan.
- Validar uma tarefa simples em modo Agent.

### Ferramenta shell e execução real
- Implementar `shell_tool.py`.
- Implementar execução shell com streaming de stdout.
- Implementar execução shell com streaming de stderr.
- Implementar timeout na shell tool.
- Implementar rastreamento PID/PGID.
- Implementar `process_manager.py`.
- Implementar `stream_manager.py`.
- Implementar `task_runner.py`.
- Validar comando curto via shell tool.
- Validar comando mais longo com streaming progressivo.
- Validar comando com stderr.
- Validar que o backend permanece responsivo durante execução longa.

### Interrupt e kill switch
- Implementar `interrupt_manager.py`.
- Implementar ação `interrupt`.
- Implementar localização da task ativa.
- Implementar interrupção real do grupo de processos.
- Implementar limpeza do estado da tarefa interrompida.
- Implementar evento de sistema para interrupção.
- Implementar atualização de `sync_state` após interrupção.
- Validar interrupção de tarefa longa sem reiniciar o backend.
- Validar que nova tarefa pode começar após o interrupt.

### execute_task ponta a ponta
- Implementar ação `execute_task`.
- Implementar criação de `task_id`.
- Implementar emissão de evento `user`.
- Implementar emissão de `status START`.
- Implementar integração do agent loop com tool execution.
- Implementar emissão de `message`, `code`, `console` e `system`.
- Implementar emissão de `status END`.
- Persistir histórico completo da tarefa.
- Validar tarefa ponta a ponta com resposta final visível.
- Validar tarefa ponta a ponta com uso de shell tool.

### Segurança e guardrails
- Implementar `security/policies.py`.
- Implementar `command_guard.py`.
- Implementar bloqueio inicial de comandos destrutivos explícitos.
- Implementar distinção comportamental entre Plan e Agent.
- Implementar bloqueio de ferramentas sensíveis em Plan.
- Implementar política inicial para operações SSH e hosts remotos.
- Validar que comandos de risco não passam silenciosamente.
- Validar que o modo Plan não executa ação sensível.

### Logs e observabilidade
- Implementar `backend.log`.
- Implementar `events.log`.
- Implementar `errors.log`.
- Implementar trilha de auditoria mínima.
- Registrar start e stop do backend.
- Registrar execute_task.
- Registrar interrupt.
- Registrar change_model.
- Registrar change_provider.
- Registrar troca de credencial ativa.
- Registrar fallback de modelo.
- Registrar fallback de credencial.
- Registrar falhas de autenticação.
- Registrar falhas de quota.
- Registrar falhas de região do Vertex AI.
- Validar que os logs ficam em `/var/log/jarvis/`.
- Validar que os logs são legíveis e úteis para troubleshooting.

### Cliente mínimo de teste do backend
- Criar cliente mínimo WebSocket para validar o v2 sem depender imediatamente do frontend.
- Validar `connect`.
- Validar `sync_state`.
- Validar `get_status`.
- Validar `get_models`.
- Validar `get_providers`.
- Validar `get_credentials_status`.
- Validar `execute_task`.
- Validar `interrupt`.

### Adaptação do frontend atual ao v2
- Adaptar o frontend atual ao `sync_state` do Mark Core v2.
- Adaptar o frontend atual ao catálogo de providers e modelos do v2.
- Adaptar o frontend atual à troca de provider.
- Adaptar o frontend atual à troca de modelo.
- Adaptar o frontend atual à leitura de status seguro de credenciais.
- Adaptar o frontend atual ao novo histórico persistido.
- Validar `execute_task` via frontend.
- Validar `interrupt` via frontend.
- Validar reconexão e reidratação de sessão via frontend.
- Validar Google AI API via frontend.
- Validar Vertex AI via frontend.

### Empacotamento e instalação
- Atualizar empacotamento `.deb` do backend para o novo core.
- Atualizar empacotamento `.rpm` do backend para o novo core.
- Atualizar unit file do systemd do novo backend.
- Garantir instalação em `/opt/jarvis/backend`.
- Garantir persistência em `/var/lib/jarvis-mark`.
- Garantir logs em `/var/log/jarvis`.
- Garantir `initial_rules.txt` instalado em `/opt/jarvis/backend/product_config/`.
- Atualizar scripts de pós-instalação quando necessário.
- Validar instalação local do backend novo por `.deb`.
- Validar instalação local do backend novo por `.rpm`.

### Testes do Mark Core v2
- Criar testes unitários do protocolo.
- Criar testes unitários do registry de modelos/providers.
- Criar testes unitários do fallback.
- Criar testes unitários do key manager.
- Criar testes unitários do vertex credentials manager.
- Criar testes unitários do session/history store.
- Criar smoke test do backend.
- Criar smoke test do frontend contra o backend v2.
- Validar healthcheck.
- Validar `sync_state`.
- Validar `execute_task`.
- Validar `interrupt`.
- Validar sessão persistida.
- Validar histórico persistido.
- Validar Google AI API.
- Validar Vertex AI.
- Validar fallback e rotação de credencial.
- Validar reconexão do frontend.

### Documentação final do primeiro marco
- Atualizar README.md do produto para o Mark Core v2.
- Documentar providers suportados.
- Documentar credenciais esperadas.
- Documentar Google AI API.
- Documentar Vertex AI.
- Documentar fallback e rotação de credenciais.
- Documentar instalação backend.
- Documentar operação backend.
- Documentar troubleshooting básico.
- Atualizar DevJarvis com o protocolo v2 se necessário.
- Revisar AgentContext final do primeiro marco do v2.

### Teste remoto e fechamento do primeiro marco
- Instalar o novo backend em outra máquina de teste.
- Validar healthcheck remoto.
- Validar execute_task remoto.
- Validar interrupt remoto.
- Validar Google AI API em máquina remota.
- Validar Vertex AI em máquina remota.
- Validar persistência e logs na máquina remota.
- Revisar TODOList.md antes do fechamento do primeiro marco.
- Revisar pivotagens antes do fechamento do primeiro marco.
- Fechar o primeiro marco do Mark Core v2.