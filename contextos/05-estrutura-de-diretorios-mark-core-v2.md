# Estrutura de Diretórios do Mark Core v2

## Objetivo
Definir a estrutura oficial de diretórios e arquivos do projeto durante o pivot do Mark Core v2, separando claramente o novo backend/core do legado do Mark Alfa e preparando o produto para crescer com segurança.

## Regra Geral
1. O repositório deve continuar separando backend, frontend, empacotamento, documentação, testes e scripts.
2. O backend novo deve nascer de forma modular.
3. O frontend atual pode ser reaproveitado, mas o novo core não deve nascer misturado ao legado.
4. Nenhum arquivo estrutural novo deve surgir “em qualquer lugar”.
5. Toda expansão estrutural relevante deve ser documentada.

## Raízes Externas ao Repositório

### 1. Repositório de desenvolvimento
`/home/francisco/Documentos/repos/mark`

Função:
- código-fonte
- documentação
- testes
- empacotamento
- TODOList
- pivotagem
- DevJarvis

### 2. Instalação do produto
`/opt/jarvis`

Função:
- código instalado
- arquivos executáveis
- frontend instalado
- backend instalado
- venv do produto

### 3. Estado persistente do produto
`/var/lib/jarvis-mark`

Função:
- configuração persistida
- histórico de sessão
- catálogo persistido
- metadados de provider
- estado de tasks

### 4. Logs do produto
`/var/log/jarvis`

Função:
- trilha de eventos
- erros
- logs do backend

## Estrutura Oficial do Repositório

### Raiz
Arquivos esperados:
- `README.md`
- `TODOList.md`
- `.gitignore`
- `.env.example`
- `requirements-backend.txt`
- `requirements-frontend.txt`
- `build_deb.sh`
- `build_rpm.sh`

Pastas esperadas:
- `src`
- `tests`
- `docs`
- `scripts`
- `packaging`
- `pivotagem`
- `AgentContext`
- `DevJarvis`

## Diretório `src`
Função:
Conter exclusivamente o código-fonte do produto.

Estrutura:
- `src/backend`
- `src/frontend`

## Diretório `src/backend`
Função:
Conter o novo backend/core do Mark Core v2.

Estrutura oficial:
```text
src/backend/
├── main.py
├── api/
├── protocol/
├── session/
├── agent/
├── models/
├── tools/
├── execution/
├── storage/
├── security/
├── logging/
└── product_config/
src/backend/main.py

Função:
Ponto de entrada do novo backend.

Responsabilidades:

bootstrap do serviço
inicialização de config
inicialização dos stores
subida da API e WebSocket
src/backend/api

Função:
Camada de transporte HTTP e WebSocket.

Pode conter:

websocket.py
health.py
routes.py se necessário

Responsabilidades:

aceitar conexão
emitir sync_state
despachar ações
manter o canal de comunicação vivo
src/backend/protocol

Função:
Centralizar o contrato JSON/WebSocket.

Pode conter:

schemas.py
actions.py
events.py

Responsabilidades:

definir entrada e saída
validar payloads
padronizar respostas
src/backend/session

Função:
Gerenciar sessão, histórico e estado atual.

Pode conter:

state_manager.py
session_store.py
history_store.py

Responsabilidades:

manter sessão ativa
manter histórico
manter revisão do histórico
reconstruir sync_state
src/backend/agent

Função:
Conter o motor agentic próprio.

Pode conter:

engine.py
planner.py
prompts.py
tool_router.py

Responsabilidades:

construir contexto do agente
montar prompt
decidir próximo passo
chamar ferramentas
consolidar resposta final
src/backend/models

Função:
Camada de provider, catálogo, fallback e credenciais.

Estrutura sugerida:

src/backend/models/
├── router.py
├── registry.py
├── fallback.py
├── providers/
│   ├── google_ai_client.py
│   └── vertex_ai_client.py
├── credentials/
│   ├── key_manager.py
│   ├── vertex_credentials.py
│   └── provider_store.py
└── policies/
    ├── provider_policy.py
    └── model_policy.py

Responsabilidades:

mapear model id para provider
validar catálogo de modelos
chamar provider correto
trocar credencial ativa
aplicar fallback de modelo/provider
src/backend/tools

Função:
Conter as ferramentas do agente.

Arquivos sugeridos:

shell_tool.py
python_tool.py
file_tool.py
ssh_tool.py
system_tool.py

Responsabilidades:

executar ação real
padronizar entrada e saída
streamar resultado quando necessário
src/backend/execution

Função:
Gerenciar execução real de processos e tasks.

Arquivos sugeridos:

process_manager.py
stream_manager.py
interrupt_manager.py
task_runner.py

Responsabilidades:

execução assíncrona
rastreamento PID/PGID
interrupção
timeout
isolamento de processo
src/backend/storage

Função:
Centralizar persistência.

Arquivos sugeridos:

db.py
config_store.py
rules_store.py
provider_store.py

Responsabilidades:

SQLite
JSONs persistentes
regras iniciais
configuração do produto
estado de provider
src/backend/security

Função:
Conter políticas e guardrails.

Arquivos sugeridos:

policies.py
command_guard.py
confirmations.py

Responsabilidades:

bloquear ações perigosas
separar plan/agent
validar comandos
validar host remoto
src/backend/logging

Função:
Observabilidade e auditoria.

Arquivos sugeridos:

logger.py
audit.py

Responsabilidades:

backend.log
events.log
errors.log
trilha de auditoria
src/backend/product_config

Função:
Guardar configuração inicial do produto instalada junto ao backend.

Arquivos esperados:

initial_rules.txt

Responsabilidades:

regras globais iniciais do agente
base do comportamento do backend no boot
Diretório src/frontend

Função:
Manter o frontend atual do produto, adaptando-o ao novo backend.

Regra:
O frontend pode ser reaproveitado, mas não deve conter lógica que pertença ao backend.

Responsabilidades:

UI
conexão WebSocket
visualização de histórico
controle de host local/remoto
configuração visual
escolha de modelo/provider
gestão operacional de credenciais em nível seguro
Diretório tests

Função:
Conter testes automatizados e assistidos.

Estrutura sugerida:

tests/backend
tests/frontend
tests/integration
tests/manual
tests/backend

Exemplos:

validação de protocolo
validação do registry de modelos
fallback
rotação de credenciais
kill switch
sessão/histórico
tests/frontend

Exemplos:

conexão
sync_state
autoscroll
renderização
persistência visual
tests/integration

Exemplos:

frontend conectando no backend
execute_task
interrupt
change_model
change_provider
reconexão
fallback
tests/manual

Exemplos:

checklist de instalação
checklist de operação remota
checklist de provider
Diretório docs

Função:
Guardar documentação do produto, separada do AgentContext.

Arquivos sugeridos:

architecture.md
backend.md
frontend.md
protocol.md
providers.md
operations.md
packaging.md
troubleshooting.md
Diretório scripts

Função:
Guardar scripts operacionais de desenvolvimento e build.

Arquivos sugeridos:

run_backend_local.sh
run_frontend_local.sh
check_env.sh
build_backend_package.sh
build_frontend_package.sh
smoke_test.sh
Diretório packaging

Função:
Conter a estrutura de empacotamento do produto.

Estrutura:

packaging/deb
packaging/rpm
packaging/systemd
packaging/frontend/desktop

Responsabilidades:

backend .deb
backend .rpm
frontend .deb
frontend .rpm
unit file
.desktop
ícone e artefatos de integração com o SO
Diretório AgentContext

Função:
Orientar a construção do produto por humanos e agentes.

Regra:
Documenta como construir.

Diretório DevJarvis

Função:
Documentação técnica voltada à integração remota e evolução futura.

Regra:
Explica como integrar e operar tecnicamente.

Arquivo TODOList.md

Função:
Ser a trilha operacional do pivot e da implementação.

Estrutura oficial:

## Feito
## Fazendo
## A fazer
Arquivo README.md

Função:
Explicar como o produto funciona para humanos.

Deve conter:

visão geral
requisitos
providers suportados
credenciais esperadas
instalação backend
instalação frontend
operação local
operação remota
troubleshooting
Regra de Convivência com o Legado
O Mark Alfa deve ser tratado como legado controlado.
O novo backend deve nascer limpo em src/backend.
O frontend atual pode ser adaptado progressivamente.
Não deve haver mistura confusa entre motor legado e core novo.
Toda ponte temporária com o legado deve ser explícita e removível.
Convenções de Nomes
Pastas técnicas do produto preferencialmente em inglês.
Documentos operacionais do AgentContext podem continuar em português.
Nomes de arquivo devem refletir responsabilidade real.
Provider e modelo devem ser conceitos separados em nomes e estruturas.
Regra Final

A estrutura do Mark Core v2 deve reduzir ambiguidade, facilitar evolução e impedir que o novo backend herde a bagunça estrutural do núcleo antigo.
