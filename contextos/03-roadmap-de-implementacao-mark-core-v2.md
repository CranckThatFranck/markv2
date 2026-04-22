# Roadmap de Implementação do Mark Core v2

## Objetivo
Este documento define a ordem oficial de implementação do novo backend/core dos agentes Mark, refeito do zero para substituir o núcleo baseado em Open Interpreter e já nascer com suporte a Google AI API e Vertex AI.

## Regra-Mãe
O Mark Core v2 não deve nascer em modo cowboy.
Toda etapa estrutural deve nascer em Plan, ser validada, e só então ser executada em Agent.

## Resultado Esperado do Primeiro Marco
Ao final do primeiro marco do Mark Core v2, o projeto deve entregar:
- backend daemon Linux funcional
- WebSocket funcional
- protocolo JSON estável
- `sync_state`
- `execute_task`
- `interrupt`
- histórico de sessão persistido
- cliente Google AI API funcional
- cliente Vertex AI funcional
- uma ferramenta shell funcional
- kill switch real
- logs básicos
- frontend atual conectado ao novo backend

## Premissas Obrigatórias
1. O novo core não depende do Open Interpreter no centro da arquitetura.
2. O backend deve nascer em Python.
3. O backend deve rodar via systemd.
4. O frontend atual será reaproveitado e adaptado.
5. O projeto deve continuar atendendo Fedora e Ubuntu.
6. O trabalho deve continuar protegido por TODO, logs e versionamento.
7. O núcleo deve tratar provider como capacidade de base, não addon tardio.

## Ordem Oficial de Execução

### Fase 0 - Congelamento do Mark Alfa
Objetivo:
Preservar a referência operacional e visual já construída.

Ações:
- congelar o Mark Alfa atual como referência histórica
- registrar que o pivot ocorrerá apenas no backend/core
- preservar frontend, empacotamento e documentação útil

Entregáveis:
- referência estável do Mark Alfa
- decisão de pivot documentada

Critério para avançar:
A base antiga deve estar preservada, sem confusão sobre o que será refeito.

### Fase 1 - Preparação documental do v2
Objetivo:
Dar ao agente contrato suficiente para construir sem improviso.

Ações:
- criar arquitetura do Mark Core v2
- criar contrato operacional do Mark Core v2
- criar este roadmap
- criar TODO inicial do v2

Entregáveis:
- documentos-base do pivot
- direção oficial do novo núcleo

Critério para avançar:
A fundação documental do v2 deve existir e ser coerente.

### Fase 2 - Definição oficial da stack
Objetivo:
Fechar a stack técnica do novo backend.

Ações:
- declarar Python + FastAPI + WebSocket + asyncio
- declarar persistência inicial
- declarar stack de testes
- declarar stack de providers
- declarar Google AI API e Vertex AI como providers oficiais de primeira linha

Entregáveis:
- stack oficial definida
- dependências-base decididas

Critério para avançar:
Nenhuma incerteza estrutural crítica deve restar sobre a tecnologia do backend.

### Fase 3 - Estrutura-base do repositório
Objetivo:
Preparar a árvore mínima do novo backend.

Ações:
- criar a estrutura de diretórios do novo core em `src/backend`
- criar módulos-base
- criar `requirements-backend.txt`
- criar arquivos vazios e esqueleto mínimo dos módulos

Entregáveis:
- árvore inicial do backend v2
- requisitos-base do backend

Critério para avançar:
O repositório deve conter a estrutura real do novo core.

### Fase 4 - Bootstrap do backend
Objetivo:
Fazer o backend subir limpo.

Ações:
- criar `src/backend/main.py`
- inicializar FastAPI/Uvicorn
- subir endpoint de health
- subir WebSocket base
- inicializar configuração e logs

Entregáveis:
- backend sobe
- health responde
- WebSocket aceita conexão

Critério para avançar:
O processo deve subir de forma previsível.

### Fase 5 - Protocolo v2
Objetivo:
Definir o contrato mínimo utilizável.

Ações:
- criar `protocol/schemas.py`
- criar tipos de eventos
- criar tipos de ações
- implementar `sync_state`
- implementar `get_status`

Entregáveis:
- protocolo mínimo operacional
- `sync_state` funcionando ao conectar

Critério para avançar:
O frontend ou um cliente de teste deve conseguir sincronizar estado.

### Fase 6 - Estado e sessão
Objetivo:
Dar memória operacional ao novo backend.

Ações:
- criar `state_manager`
- criar `session_store`
- criar `history_store`
- persistir estado atual
- persistir histórico da sessão

Entregáveis:
- sessão ativa persistida
- histórico persistido
- revisão do histórico

Critério para avançar:
Reconectar no backend deve devolver estado e histórico.

### Fase 7 - Regras iniciais do produto
Objetivo:
Dar constituição real ao novo core.

Ações:
- criar `product_config/initial_rules.txt`
- criar carregamento das regras no boot
- tornar as regras disponíveis ao motor agentic
- expor o caminho no estado sincronizado

Entregáveis:
- regras iniciais reais
- caminho da regra disponível ao produto

Critério para avançar:
O backend deve iniciar com regras iniciais carregadas.

### Fase 8 - Registro de providers e catálogo de modelos
Objetivo:
Criar a camada base que permite múltiplos providers.

Ações:
- criar `models/registry.py`
- criar `models/router.py`
- declarar model ids suportados
- declarar provider por model id
- declarar política de compatibilidade por model id

Entregáveis:
- catálogo unificado de modelos
- roteador de provider funcional

Critério para avançar:
O backend deve conseguir identificar provider e política de um model id.

### Fase 9 - Cliente Google AI API
Objetivo:
Ter um cliente simples e confiável para Gemini via API Key.

Ações:
- criar `models/providers/google_ai_client.py`
- implementar chamada básica ao Gemini
- validar `GOOGLE_API_KEY`
- tratar erros básicos do provider

Entregáveis:
- chamada ao modelo funcional por Google AI API
- resposta simples obtida com sucesso

Critério para avançar:
O backend deve conseguir pedir resposta ao modelo via API Key.

### Fase 10 - Cliente Vertex AI
Objetivo:
Ter um cliente simples e confiável para modelos do Google Cloud.

Ações:
- criar `models/providers/vertex_ai_client.py`
- implementar autenticação por service account
- validar:
  - `GOOGLE_APPLICATION_CREDENTIALS`
  - `VERTEXAI_PROJECT`
  - `VERTEXAI_LOCATION`
- implementar chamada básica ao modelo
- tratar erros de autenticação, projeto e região

Entregáveis:
- chamada ao modelo funcional por Vertex AI
- resposta simples obtida com sucesso

Critério para avançar:
O backend deve conseguir pedir resposta ao modelo via Vertex AI.

### Fase 11 - Gestão de credenciais e seleção de provider
Objetivo:
Preparar o terreno para continuidade operacional.

Ações:
- criar `key_manager.py`
- criar `vertex_credentials.py`
- selecionar credencial ativa por provider
- persistir metadados de credenciais
- suportar seleção manual de credencial

Entregáveis:
- credencial ativa selecionável
- backend capaz de operar com os dois providers

Critério para avançar:
O backend deve conseguir escolher provider, modelo e credencial de forma controlada.

### Fase 12 - Motor agentic mínimo
Objetivo:
Criar o primeiro loop cognitivo próprio.

Ações:
- criar `agent/engine.py`
- criar `agent/prompts.py`
- definir formato estruturado de decisão
- suportar:
  - resposta final
  - pedido de ferramenta
- manter limites de iteração e segurança

Entregáveis:
- primeiro loop agentic funcional
- decisão estruturada previsível

Critério para avançar:
Uma tarefa simples deve ser processada pelo motor próprio.

### Fase 13 - Ferramenta shell
Objetivo:
Dar ação real ao agente.

Ações:
- criar `tools/shell_tool.py`
- criar `execution/process_manager.py`
- criar `task_runner.py`
- executar comandos shell com streaming
- rastrear PID/PGID

Entregáveis:
- shell tool funcional
- streaming stdout/stderr funcional
- rastreamento de processo funcional

Critério para avançar:
O agente deve conseguir rodar uma tarefa shell simples e streamar a saída.

### Fase 14 - execute_task
Objetivo:
Fechar o primeiro fluxo ponta a ponta.

Ações:
- implementar `execute_task`
- enviar eventos:
  - user
  - status
  - message
  - code
  - console
  - system
- persistir o histórico correspondente

Entregáveis:
- execução ponta a ponta do novo core
- stream coerente de eventos

Critério para avançar:
O frontend ou cliente de teste deve ver a tarefa acontecendo.

### Fase 15 - interrupt
Objetivo:
Dar controle real ao usuário.

Ações:
- implementar `interrupt`
- encerrar grupo de processos
- limpar estado da task
- registrar interrupção
- voltar a estado seguro

Entregáveis:
- kill switch funcional
- backend pronto para nova ordem após interrupção

Critério para avançar:
Uma tarefa longa deve poder ser interrompida sem reiniciar o backend.

### Fase 16 - Modo Plan e Modo Agent
Objetivo:
Implantar formalmente os dois estados cognitivos.

Ações:
- implementar `change_mode`
- aplicar restrições do Plan
- aplicar execução do Agent
- refletir estado no protocolo
- retornar ao estado esperado após a tarefa

Entregáveis:
- plan/agent funcionais
- estado coerente entre backend e frontend

Critério para avançar:
O backend deve respeitar o modo solicitado.

### Fase 17 - Logs e observabilidade
Objetivo:
Tornar o sistema operável de verdade.

Ações:
- criar `backend.log`
- criar `events.log`
- criar `errors.log`
- logar tarefas
- logar falhas
- logar fallback
- logar troca de modelo
- logar troca de provider
- logar troca de credencial

Entregáveis:
- observabilidade mínima real

Critério para avançar:
O operador deve conseguir entender o que aconteceu sem adivinhar.

### Fase 18 - Ferramentas complementares
Objetivo:
Ampliar utilidade do agente sem destruir simplicidade.

Ações:
- criar `file_tool.py`
- criar `python_tool.py`
- criar `system_tool.py`

Entregáveis:
- leitura/escrita de arquivo controlada
- execução Python controlada
- inspeção de sistema

Critério para avançar:
O agente deve conseguir resolver tarefas mais ricas sem shell puro o tempo todo.

### Fase 19 - Fallback e rotação
Objetivo:
Dar robustez operacional ao uso dos modelos.

Ações:
- fallback automático entre modelos do mesmo provider
- fallback entre providers quando política permitir
- rotação manual de chave
- rotação automática quando aplicável
- registro de fallback no log
- retorno visível ao frontend

Entregáveis:
- fallback funcional
- rotação funcional

Critério para avançar:
O backend deve sobreviver melhor a falhas de quota, região ou provider.

### Fase 20 - Integração com frontend atual
Objetivo:
Reaproveitar o frontend do Mark Alfa.

Ações:
- adaptar o frontend atual ao protocolo v2
- validar:
  - conexão
  - histórico
  - execução
  - interrupção
  - troca de modelo
  - troca de provider
  - host remoto/local

Entregáveis:
- frontend controlando o novo backend

Critério para avançar:
O novo core deve ser utilizável sem esperar um novo frontend.

### Fase 21 - systemd e empacotamento
Objetivo:
Formalizar o novo backend como produto.

Ações:
- criar ou atualizar unit file
- atualizar empacotamento `.deb`
- atualizar empacotamento `.rpm`
- documentar instalação e operação
- validar em Fedora e Ubuntu

Entregáveis:
- backend instalável
- serviço via systemd previsível

Critério para avançar:
O backend deve poder ser instalado fora da máquina de desenvolvimento.

### Fase 22 - Testes locais
Objetivo:
Validar a fundação do v2.

Ações:
- executar testes unitários
- executar testes de smoke
- validar:
  - sync_state
  - execute_task
  - interrupt
  - sessão
  - histórico
  - troca de modelo
  - troca de provider
  - rotação de credencial
  - chamadas por Google AI API
  - chamadas por Vertex AI

Entregáveis:
- checklist mínimo de validação aprovado

Critério para avançar:
O v2 deve estar confiável localmente.

### Fase 23 - Teste remoto
Objetivo:
Validar o uso real em outra máquina.

Ações:
- instalar em host remoto
- validar serviço
- validar operação remota
- validar persistência
- validar reconexão
- validar provider Google AI API
- validar provider Vertex AI

Entregáveis:
- teste remoto aprovado

Critério para avançar:
O núcleo deve funcionar fora da máquina original.

### Fase 24 - Fechamento do primeiro marco
Objetivo:
Concluir o primeiro milestone real do v2.

Ações:
- revisar TODO
- revisar docs
- revisar logs
- revisar empacotamento
- registrar marco
- commit/push final do milestone

Entregáveis:
- primeiro marco do Mark Core v2 concluído
- base pronta para evolução posterior

## Regras de Execução
1. Não avançar fase sem validar a anterior.
2. Não inventar recursos novos no meio sem registrar.
3. Não expandir para multiagente antes do núcleo local estar estável.
4. Não começar por SSH antes do núcleo local funcionar bem.
5. Não trocar de stack no meio sem nova decisão arquitetural.
6. Não tratar Vertex AI como apêndice improvisado; ele faz parte da fundação do v2.

## Sprints Recomendadas

### Sprint 1
- Fases 0 a 15
- objetivo: backend mínimo ponta a ponta com Google AI API e Vertex AI já ligados

### Sprint 2
- Fases 16 a 19
- objetivo: robustez operacional e fallback

### Sprint 3
- Fases 20 a 24
- objetivo: integração, empacotamento e validação remota

## Regra Final
O Mark Core v2 deve crescer em camadas, com confiança acumulada.
Primeiro ele precisa funcionar bem localmente como agente confiável.
Só depois ele escala para remoto, multiagente e Jarvis Master.
Mas o suporte a múltiplos providers do Google deve nascer na base, não ser enxertado depois.

