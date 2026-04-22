# Contrato Operacional do Mark Core v2

## Objetivo
Este documento define as regras operacionais obrigatórias para a implementação, execução e evolução do novo backend/core dos agentes Mark.

## Escopo
O Mark Core v2 é o núcleo operacional dos Marks de nova geração.
Ele substitui a dependência estrutural do Open Interpreter como motor central e passa a operar com backend próprio.

## Missão do Produto
O Mark Core v2 deve:
- receber tarefas
- decidir e executar ações com segurança
- transmitir progresso em tempo real
- manter contexto de sessão
- permitir interrupção imediata
- operar em Linux local e remoto
- sustentar o futuro ecossistema multiagente
- suportar mais de um provider de modelo sem redesenho estrutural

## Regras Arquiteturais Obrigatórias
1. O núcleo do backend não deve depender do Open Interpreter como motor central.
2. O loop agentic deve ser implementado no próprio produto.
3. O backend deve rodar como daemon controlado por systemd.
4. O frontend continua sendo cliente do backend, nunca dono da lógica.
5. Backend e frontend continuam separados.
6. Backend e frontend continuam tendo pacotes separados.
7. O sistema deve suportar Fedora e Ubuntu.
8. O produto deve continuar prevendo `.rpm` e `.deb`.
9. O suporte a providers de modelo deve existir desde a fundação do v2.
10. O produto não deve ser acoplado a um único método de autenticação de modelo.

## Linguagem e Stack Base
1. O novo core deve ser implementado em Python.
2. A stack base oficial é FastAPI + WebSocket + asyncio.
3. A execução do backend deve ser compatível com Python 3.12 ou superior compatível definido pelo projeto.
4. O backend deve ser empacotável e instalável fora da máquina de desenvolvimento.

## Providers e Modelos

### Provider 1 - Google AI API
O sistema deve suportar modelos Gemini acessados por API Key simples.

Credencial esperada:
- `GOOGLE_API_KEY`

### Provider 2 - Vertex AI
O sistema deve suportar modelos acessados pelo Google Cloud via Vertex AI.

Credenciais esperadas:
- `GOOGLE_APPLICATION_CREDENTIALS`
- `VERTEXAI_PROJECT`
- `VERTEXAI_LOCATION`

### Regras de provider
1. O provider deve ser resolvido pelo backend, não pelo frontend.
2. O frontend deve operar sobre um catálogo lógico de modelos.
3. O backend deve saber como um model id mapeia para um provider.
4. O backend deve conseguir diferenciar falha de credencial, falha de região, falha de quota e falha de modelo.
5. A política de fallback deve ser explícita e documentada.

## Modos Cognitivos
O Mark Core v2 deve operar formalmente em dois modos:

### Plan
- analisa
- propõe
- quebra etapas
- não executa ações sensíveis
- não altera sistema por padrão

### Agent
- executa ferramentas
- testa
- corrige
- registra andamento
- conclui ou interrompe

## Regras de Ferramentas
1. Toda ferramenta deve ter contrato claro de entrada e saída.
2. Toda ferramenta deve ser registrada pelo backend.
3. Toda ferramenta deve poder ser logada.
4. Ferramentas perigosas devem ser mediadas por política.
5. O agente não pode usar ferramentas inexistentes, implícitas ou opacas.

## Regras de Execução
1. O backend deve ser responsivo mesmo durante tarefas longas.
2. Tarefas devem ter rastreamento de PID/PGID quando aplicável.
3. O kill switch deve ser real.
4. O agente deve poder continuar emitindo eventos durante execução.
5. O backend deve diferenciar:
   - tarefa em execução
   - tarefa concluída
   - tarefa interrompida
   - falha recuperável
   - falha fatal

## Regras de Provider e Credencial
1. Credenciais não devem ser hardcoded no código.
2. Credenciais podem vir de ambiente, arquivo persistido ou cadastro operacional permitido pelo produto.
3. O backend nunca deve devolver segredos completos ao frontend.
4. O frontend pode exibir apenas metadados seguros, como:
   - provider configurado
   - id lógico da credencial
   - status de disponibilidade
   - modelo ativo
5. O backend deve suportar seleção da credencial ativa por provider.
6. O backend deve suportar fallback entre credenciais do mesmo provider quando a política permitir.
7. O backend deve suportar fallback entre modelos quando a política permitir.
8. Fallback entre providers diferentes só deve ocorrer se estiver explicitamente habilitado na política do produto.

## Protocolo de Comunicação
1. Toda comunicação entre frontend e backend deve trafegar em JSON.
2. O backend deve emitir `sync_state` ao conectar.
3. O backend deve transmitir histórico e estado atual ao reconectar.
4. Toda resposta estruturada deve ser explícita.
5. O contrato deve ser tolerante a expansão futura.
6. O contrato deve comportar:
   - provider atual
   - modelo atual
   - catálogo de modelos
   - modo atual
   - estado da tarefa
   - caminhos relevantes
   - histórico da sessão

## Persistência
O backend deve persistir pelo menos:
- configuração do agente
- modo atual
- provider atual
- modelo atual
- sessão ativa
- histórico da sessão
- catálogo de modelos e credenciais
- metadados necessários à retomada

## Regras de Segurança
1. O Mark Core v2 deve nascer com política de segurança explícita.
2. Ações destrutivas não devem ser executadas implicitamente.
3. Modo Plan não executa.
4. Comandos de alto risco exigem política clara.
5. Operações remotas exigem validação de host/alvo.
6. Logs de auditoria são obrigatórios para ações relevantes.
7. Credenciais de provider devem ter armazenamento minimamente seguro e acesso restrito.

## Política de Logs
O sistema deve manter observabilidade suficiente em:
- `/var/log/jarvis/backend.log`
- `/var/log/jarvis/events.log`
- `/var/log/jarvis/errors.log`

Esses logs devem registrar:
- início e fim de tarefa
- falhas
- interrupções
- troca de modelo
- troca de provider
- troca de credencial ativa
- fallback
- erros de ferramenta
- eventos relevantes de conexão
- falhas de autenticação por provider
- falhas de região no Vertex AI

## Regras de Recuperação
1. Se o frontend cair, o backend deve continuar vivo.
2. Se o frontend reconectar, deve receber `sync_state` + histórico.
3. Se uma tarefa for interrompida, o backend deve voltar a estado seguro.
4. O backend não pode continuar uma tarefa interrompida como se nada tivesse acontecido.
5. Após reboot, o backend deve conseguir retomar estado suficiente.

## Relação com o Mark Alfa
1. O Mark Alfa deve ser tratado como referência histórica e operacional.
2. O frontend atual pode ser reutilizado e adaptado.
3. O novo backend não deve herdar as fragilidades do antigo motor.
4. Reaproveitamento não autoriza manter dependência estrutural incorreta.

## Política de Planejamento
1. Toda mudança estrutural deve nascer em Plan.
2. Agent não deve inventar novos requisitos sem necessidade real.
3. Se o escopo mudar de forma relevante, registrar pivotagem.
4. Toda mudança estrutural deve atualizar TODO e documentação.

## Política de Versionamento
1. Cada item realmente concluído deve gerar commit claro.
2. Marcos relevantes devem ser enviados ao GitHub sem esperar o projeto inteiro terminar.
3. O TODO deve refletir o estado real do trabalho.
4. Mudanças estruturais novas devem ser registradas em pivotagem quando necessário.

## Resultado Esperado
Ao final da primeira fase do Mark Core v2, deve existir:
- backend daemon funcional
- loop agentic próprio
- suporte a uma tarefa por vez
- ferramenta shell funcional
- sessão persistida
- kill switch funcional
- frontend capaz de controlar o novo backend
- suporte funcional a Google AI API
- suporte funcional a Vertex AI
- documentação suficiente para evolução segura

## Critério de Qualidade
Nenhuma funcionalidade existe apenas porque parece funcionar.
Tudo deve ser:
- reproduzível
- rastreável
- testável
- interrompível
- recuperável
- documentado

## Regra Final
O Mark Core v2 não deve improvisar a fundação do produto.
Ele deve nascer como um núcleo confiável, simples e extensível, capaz de sustentar os próximos agentes Marks e o futuro Jarvis Master, com suporte limpo e previsível a múltiplos providers do Google desde o início.
