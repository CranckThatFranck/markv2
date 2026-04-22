# Contrato JSON do Mark Core v2

## Objetivo
Padronizar toda a comunicação entre frontend, backend e futuros clientes remotos do Mark Core v2.

## Regra Geral
1. Toda comunicação trafega em JSON.
2. Toda mensagem enviada ao backend deve conter `action`.
3. Toda resposta estruturada do backend deve conter `type`.
4. Toda resposta final de ação deve indicar sucesso ou erro.
5. O protocolo deve ser tolerante à expansão futura.
6. Clientes devem ignorar campos desconhecidos sem quebrar.

## Versão do Protocolo
Campo recomendado em todas as mensagens:
`"protocol_version": "2.0"`

## Conceitos Centrais
O protocolo v2 precisa representar explicitamente:
- estado atual do backend
- modo atual
- provider atual
- modelo atual
- catálogo de modelos
- catálogo de providers
- sessão ativa
- histórico
- tarefa ativa
- eventos de stream
- interrupção
- atualização de configuração
- estado das credenciais em nível seguro, sem expor segredos

## Envelope de Entrada
Formato geral:
```json
{
  "protocol_version": "2.0",
  "action": "nome_da_acao",
  "payload": {}
}
Envelope de Saída

Formato geral de resposta estruturada:

{
  "type": "action_response",
  "protocol_version": "2.0",
  "action": "nome_da_acao",
  "success": true,
  "data": {}
}

Formato geral de erro:

{
  "type": "action_response",
  "protocol_version": "2.0",
  "action": "nome_da_acao",
  "success": false,
  "error_code": "CODIGO_DO_ERRO",
  "message": "Mensagem legível"
}
Ações de Entrada
1. execute_task

Uso:
Executar uma tarefa real no backend.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "execute_task",
  "payload": {
    "prompt": "Verifique o status do serviço jarvis-backend",
    "mode": "agent"
  }
}

Regras:

prompt é obrigatório
mode aceita plan ou agent
se mode não vier, usar o modo atual do backend
se já houver tarefa ativa, deve responder erro estruturado
2. interrupt

Uso:
Interromper imediatamente a tarefa atual.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "interrupt"
}
3. get_status

Uso:
Consultar estado atual do backend.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "get_status"
}
4. healthcheck

Uso:
Validar se o backend está vivo e responsivo.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "healthcheck"
}
5. get_config

Uso:
Ler a configuração persistida do agente.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "get_config"
}
6. update_config

Uso:
Atualizar configuração persistida do backend.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "update_config",
  "payload": {
    "config": {
      "agent_name": "Mark 1",
      "default_mode": "agent",
      "provider": "google_ai",
      "model": "gemini/gemini-3.1-pro-preview",
      "allow_cross_provider_fallback": false
    }
  }
}

Regras:

só pode atualizar campos aceitos pela política do backend
configurações inválidas devem gerar erro estruturado
atualização de credenciais não deve trafegar junto com update_config
7. get_models

Uso:
Listar catálogo completo de modelos suportados.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "get_models"
}
8. get_providers

Uso:
Listar providers suportados e seus estados seguros.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "get_providers"
}
9. change_model

Uso:
Trocar o modelo ativo sem reiniciar o backend.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "change_model",
  "payload": {
    "model": "vertex_ai/gemini-2.5-pro"
  }
}

Regras:

o backend resolve automaticamente o provider a partir do model id
se o model id for novo e permitido pela política, pode ser registrado como customizado
se o model id for inválido, responder erro estruturado
10. change_provider

Uso:
Trocar explicitamente o provider ativo.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "change_provider",
  "payload": {
    "provider": "vertex_ai"
  }
}

Regras:

não deve trocar provider para estado impossível
se não houver credencial válida para o provider, retornar erro
11. get_credentials_status

Uso:
Ler apenas o estado seguro das credenciais por provider.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "get_credentials_status"
}

Regras:

nunca retornar segredo
só retornar metadados seguros, como:
provider
credencial ativa
quantidade de credenciais cadastradas
status: configurado/não configurado
12. set_active_credential

Uso:
Trocar a credencial ativa de um provider.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "set_active_credential",
  "payload": {
    "provider": "google_ai",
    "credential_id": "google_ai_key_2"
  }
}
13. add_custom_model

Uso:
Cadastrar um model id adicional permitido pela política.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "add_custom_model",
  "payload": {
    "model": "vertex_ai/gemini-custom-preview",
    "provider": "vertex_ai"
  }
}
14. remove_custom_model

Uso:
Remover um model id customizado cadastrado anteriormente.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "remove_custom_model",
  "payload": {
    "model": "vertex_ai/gemini-custom-preview"
  }
}
15. get_history

Uso:
Ler o histórico completo ou parcial da sessão ativa.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "get_history"
}
16. clear_session

Uso:
Limpar a sessão/histórico atual.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "clear_session"
}

Regras:

ação sensível
deve ser registrada no log
pode exigir confirmação futura, conforme política
17. shutdown_backend

Uso:
Solicitar desligamento gracioso do backend.

Exemplo:

{
  "protocol_version": "2.0",
  "action": "shutdown_backend"
}
Tipos de Saída
sync_state

Enviado ao conectar no WebSocket e após mudanças de estado relevantes.

Exemplo:

{
  "type": "sync_state",
  "protocol_version": "2.0",
  "state": {
    "agent_name": "Mark 1",
    "mode": "agent",
    "status": "idle",
    "provider": "google_ai",
    "model": "gemini/gemini-3-flash-preview",
    "active_task_id": null,
    "history_revision": 12,
    "paths": {
      "base_dir": "/var/lib/jarvis-mark",
      "rules_file": "/opt/jarvis/backend/product_config/initial_rules.txt",
      "rules_dir": "/opt/jarvis/backend/product_config"
    }
  },
  "providers": {
    "available": [
      "google_ai",
      "vertex_ai"
    ],
    "active": "google_ai"
  },
  "models": {
    "builtin": [
      "gemini/gemini-3-flash-preview",
      "gemini/gemini-3.1-pro-preview",
      "vertex_ai/gemini-2.5-pro"
    ],
    "custom": [],
    "all": [
      "gemini/gemini-3-flash-preview",
      "gemini/gemini-3.1-pro-preview",
      "vertex_ai/gemini-2.5-pro"
    ]
  },
  "credentials_status": {
    "google_ai": {
      "configured": true,
      "active_credential_id": "google_ai_key_1",
      "credential_count": 2
    },
    "vertex_ai": {
      "configured": true,
      "active_credential_id": "vertex_sa_default",
      "credential_count": 1
    }
  },
  "history": []
}
system

Mensagens de sistema.

Exemplo:

{
  "type": "system",
  "message": "Conexão estabelecida com sucesso."
}
status

Atualizações de ciclo de vida.

Exemplo:

{
  "type": "status",
  "phase": "START",
  "action": "execute_task",
  "task_id": "task_001"
}

Exemplo de fim:

{
  "type": "status",
  "phase": "END",
  "action": "execute_task",
  "task_id": "task_001"
}
user

Eco da mensagem do usuário.

Exemplo:

{
  "type": "user",
  "content": "Verifique o status do serviço jarvis-backend"
}
message

Mensagem natural do agente.

Exemplo:

{
  "type": "message",
  "content": "O serviço está ativo e sem falhas críticas."
}
code

Código que o agente gerou ou pretende executar.

Exemplo:

{
  "type": "code",
  "language": "bash",
  "content": "systemctl status jarvis-backend"
}
console

Saída de execução.

Exemplo:

{
  "type": "console",
  "stream": "stdout",
  "content": "active (running)"
}
provider_event

Evento relacionado a provider, credencial, modelo ou fallback.

Exemplo:

{
  "type": "provider_event",
  "event": "fallback_model",
  "from_model": "gemini/gemini-3.1-pro-preview",
  "to_model": "gemini/gemini-2.5-pro",
  "provider": "google_ai",
  "reason": "rate_limit"
}

Exemplo de troca de provider:

{
  "type": "provider_event",
  "event": "change_provider",
  "from_provider": "google_ai",
  "to_provider": "vertex_ai"
}
action_response

Resposta final estruturada de uma ação.

Exemplo de sucesso:

{
  "type": "action_response",
  "protocol_version": "2.0",
  "action": "change_model",
  "success": true,
  "data": {
    "provider": "vertex_ai",
    "model": "vertex_ai/gemini-2.5-pro"
  }
}

Exemplo de erro:

{
  "type": "action_response",
  "protocol_version": "2.0",
  "action": "change_provider",
  "success": false,
  "error_code": "PROVIDER_NOT_CONFIGURED",
  "message": "O provider vertex_ai não possui credencial válida configurada."
}
Regras de Erro
Todo erro estruturado deve usar type = action_response.
Todo erro deve conter:
success = false
error_code
message
Códigos de Erro Sugeridos
INVALID_ACTION
INVALID_PAYLOAD
TASK_ALREADY_RUNNING
TASK_NOT_FOUND
INTERRUPT_FAILED
MODEL_NOT_FOUND
PROVIDER_NOT_FOUND
PROVIDER_NOT_CONFIGURED
CREDENTIAL_NOT_FOUND
CREDENTIAL_NOT_CONFIGURED
REGION_INVALID
AUTHENTICATION_FAILED
RATE_LIMIT
QUOTA_EXCEEDED
TOOL_EXECUTION_FAILED
CONFIG_INVALID
Regras de Compatibilidade
Campos novos podem ser adicionados no futuro sem quebrar clientes antigos.
Clientes devem ignorar campos desconhecidos.
Campos obrigatórios não podem ser removidos sem nova versão de protocolo.
O frontend não deve assumir que só existe um provider.
Regra Final

O protocolo do Mark Core v2 deve ser simples, explícito, extensível e previsível.
Toda ambiguidade removida aqui economiza bugs no backend, no frontend e no futuro Jarvis Master.
