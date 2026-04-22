# Política de Providers, Modelos e Credenciais do Mark Core v2

## Objetivo
Definir como o Mark Core v2 deve tratar providers de modelo, catálogo de modelos, autenticação, credenciais, fallback e rotação operacional.

## Regra-Mãe
O backend deve tratar provider, modelo e credencial como camadas distintas.
Não pode existir mistura confusa entre:
- qual modelo foi escolhido
- por qual provider ele será executado
- qual credencial será usada

## Providers Oficiais da Primeira Versão

### 1. Google AI API
Uso:
Modelos Gemini acessados por API Key simples.

Credencial esperada:
- `GOOGLE_API_KEY`

Exemplos de modelos:
- `gemini/gemini-3-flash-preview`
- `gemini/gemini-3.1-pro-preview`
- `gemini/gemini-3.1-pro-preview-customtools`
- `gemini/gemini-2.5-flash`
- `gemini/gemini-2.5-pro`

### 2. Vertex AI
Uso:
Modelos acessados pelo Google Cloud.

Credenciais esperadas:
- `GOOGLE_APPLICATION_CREDENTIALS`
- `VERTEXAI_PROJECT`
- `VERTEXAI_LOCATION`

Exemplos de modelos:
- `vertex_ai/gemini-2.5-flash`
- `vertex_ai/gemini-2.5-pro`
- `vertex_ai/gemini-3.1-pro-preview`
- `vertex_ai/gemini-3.1-pro-preview-customtools`
- modelos oficialmente habilitados no projeto GCP

## Catálogo de Modelos
O backend deve manter um catálogo unificado com:
- modelos builtin
- modelos customizados
- provider associado
- capabilities conhecidas
- política de fallback

Cada entrada do catálogo deve conter pelo menos:
- `model_id`
- `provider`
- `enabled`
- `builtin`
- `supports_tools`
- `supports_plan`
- `supports_agent`
- `priority`

## Resolução de Provider
O backend deve resolver o provider a partir de uma destas fontes, nesta ordem:

1. model id informado explicitamente
2. configuração persistida do backend
3. política de provider padrão do produto

Exemplos:
- `gemini/gemini-3.1-pro-preview` -> `google_ai`
- `vertex_ai/gemini-2.5-pro` -> `vertex_ai`

## Regras de Credenciais

### Google AI API
As credenciais podem vir de:
- variável de ambiente
- cadastro persistido do produto
- troca operacional via frontend, se permitido pela política

Cada credencial cadastrada deve ter:
- `credential_id`
- `provider = google_ai`
- rótulo humano opcional
- segredo armazenado com acesso restrito
- flag de ativa/inativa

### Vertex AI
As credenciais podem vir de:
- variáveis de ambiente
- configuração persistida do produto
- caminhos explicitamente configurados pelo operador

Metadados mínimos:
- `credential_id`
- `provider = vertex_ai`
- caminho do JSON de service account
- projeto
- região padrão
- ativa/inativa

## Regra de Segurança de Credenciais
1. O frontend nunca deve receber segredos completos de volta.
2. O backend só pode expor metadados seguros.
3. Logs nunca devem imprimir tokens, API keys ou conteúdo de JSON sensível.
4. Arquivos persistidos de credenciais devem ter permissões restritas.
5. O produto deve permitir rotação sem reinício completo sempre que tecnicamente possível.

## Seleção da Credencial Ativa
O backend deve suportar:
- uma credencial ativa por provider
- troca manual da credencial ativa
- persistência da credencial ativa
- leitura de estado seguro das credenciais

## Fallback

### Fallback entre modelos do mesmo provider
Permitido por padrão quando a política do produto habilitar.

Exemplo:
- `gemini/gemini-3.1-pro-preview` -> `gemini/gemini-2.5-pro`

### Fallback entre credenciais do mesmo provider
Permitido quando:
- houver múltiplas credenciais válidas
- a política do produto permitir rotação automática
- a falha for compatível com nova tentativa

Exemplo:
- quota esgotada na `google_ai_key_1`
- tentar `google_ai_key_2`

### Fallback entre providers diferentes
Não deve ser implícito por padrão.
Só pode ocorrer quando:
- a política do produto permitir explicitamente
- existir mapeamento compatível entre modelos
- o operador aceitar esse comportamento como esperado

## Tipos de Falha que Devem Ser Diferenciados
O backend deve diferenciar pelo menos:
- erro de autenticação
- credencial ausente
- credencial inválida
- rate limit
- quota excedida
- modelo indisponível
- provider indisponível
- região inválida
- modelo não habilitado naquele provider
- erro transitório de rede
- erro fatal não recuperável

## Regras de Rotação de Credenciais
1. O backend deve permitir rotação manual sempre.
2. A rotação automática só deve ocorrer sob política explícita.
3. Troca automática deve ser logada.
4. O frontend deve ser notificado de fallback ou rotação.
5. A sessão não deve perder contexto por simples troca de credencial.

## Regras de Região para Vertex AI
1. `VERTEXAI_LOCATION` deve ser tratada como configuração de provider ou credencial.
2. Modelos que exigirem região específica devem poder declarar isso no catálogo.
3. O backend deve validar coerência entre:
   - modelo
   - projeto
   - região
   - credencial
4. Erros de região devem ser claros e diferenciados de quota.

## Cadastro de Modelos Customizados
O backend deve permitir cadastro de modelos customizados, desde que:
- o provider seja conhecido
- a política do produto permita
- o model id seja persistido
- o frontend mostre esse modelo de forma clara

Cada modelo customizado deve guardar:
- `model_id`
- `provider`
- `enabled`
- `created_by`
- `created_at`

## Provider Padrão e Modelo Padrão
O produto pode ter:
- provider padrão
- modelo padrão
- credencial ativa padrão por provider

Mas isso não deve impedir:
- troca de provider
- troca de modelo
- fallback
- rotação de credencial

## Regras de Frontend
O frontend deve poder:
- listar providers suportados
- listar modelos por provider
- mostrar provider ativo
- mostrar modelo ativo
- mostrar estado seguro das credenciais
- trocar provider
- trocar modelo
- trocar credencial ativa
- cadastrar modelo customizado permitido

O frontend não deve:
- conhecer segredo completo
- decidir fallback por conta própria
- reimplementar política de provider

## Persistência Recomendada
O backend deve persistir em arquivo ou banco pelo menos:
- providers conhecidos
- modelos builtin
- modelos customizados
- credencial ativa por provider
- metadados seguros de credenciais
- política de fallback

## Logs Obrigatórios
Deve registrar:
- troca de provider
- troca de modelo
- troca de credencial ativa
- fallback de credencial
- fallback de modelo
- falha de autenticação
- falha de região
- falha de quota
- provider indisponível

## Critério de Sucesso
A política estará correta quando:
- o backend conseguir usar Google AI API e Vertex AI de forma limpa
- provider, modelo e credencial estiverem claramente separados
- o frontend puder operar isso sem ver segredos
- fallback e rotação funcionarem sem bagunçar o estado
- a evolução para novos modelos do Google não exigir refazer a fundação

## Regra Final
O suporte a múltiplos providers do Google deve nascer como política oficial do produto, não como remendo posterior.
