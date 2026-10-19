# Fatos transversais confirmados no código (commit de produção `ff50d33`)

Interno. Quem escreve página de operação parte daqui e confere só o que é específico da rota. Cada item tem a fonte
no core (`apps/.worktrees/base-e24-main`). Se achar algo que contradiga este arquivo, avise no relatório final.

## Credenciais

> **Interno.** O login de usuário (token, filial por cabeçalho, papéis) é o fluxo do painel do parceiro e **não aparece em nenhuma página pública**
> (decisão de Sergio, 2026-10-19). Os fatos abaixo servem só para entender o código.

- Duas formas, na mesma rota, sem escolher por rota: **chave de API** (`X-Api-Key: ttk_...` ou `Authorization: Bearer ttk_...`)
  e **login humano** (`Authorization: Bearer <token>`, emitido por `POST /api/b2b/v1/auth/login`). O servidor tenta primeiro
  o token humano; se não for um, trata o valor como chave. Fonte: `PartnerManagement/.../ResolvesPartnerContext.php`
  e `ResolvesPartnerFromApiKey.php`.
- Chave: prefixo `ttk_` e 40 caracteres. Emitida pela equipe da ClubTrack (não há autoatendimento). O texto da chave só é
  mostrado na emissão. Chave equivale ao parceiro inteiro: não existe escopo por chave.
- Revogação ou expiração de chave leva **até 60 segundos** para valer (cache da resolução da chave).
- `X-Partner-Branch-Id`: só importa no login humano. Usuário com uma filial: ignorado. Com mais de uma: obrigatório,
  sem ele a resposta é 400 com `Usuário tem mais de uma filial — informe qual via header X-Partner-Branch-Id.` (o travessão
  é parte da mensagem real do código; em página pública escreva a mensagem num bloco de código, é a única exceção).
  Filial que não é do usuário: 403 `Filial informada não pertence a este usuário.`. Com chave de API o cabeçalho é ignorado.
- Mensagens 401 reais: `API key ausente.`, `API key inválida ou revogada.`, `Usuário inativo.` (inclui token expirado),
  `Usuário sem filial vinculada.`.
- Parceiro suspenso ou inativo (ou hub suspenso, que derruba as filiais): 403 `Parceiro inativo ou suspenso.` nas rotas com
  a trava de parceiro ativo. Confira rota a rota se a trava existe (grupo de rotas com `partner.active`).
- Limite: **1000 requisições por minuto por parceiro**, só no caminho de chave de API, compartilhado entre todas as rotas.
  Estourou: 429, corpo `{"message":"Limite de requisições atingido. Tente novamente em Ns."}`, cabeçalhos `Retry-After`
  (segundos) e `X-RateLimit-Limit: 1000`. Não há `X-RateLimit-Remaining`.

## Formato

- Todas as rotas respondem JSON, mesmo sem `Accept`. Recomende `Accept: application/json` e `Content-Type: application/json`
  nas chamadas com corpo.
- Objeto único: `{"data": {...}}`. Coleção paginada: `{"data": [...], "links": {...}, "meta": {...}}`.
  `links`: `first`, `last`, `prev`, `next` (URL completa, já com os filtros; `prev` e `next` são `null` nas pontas).
  `meta`: `current_page`, `from`, `last_page`, `links` (lista de botões para interface: `url`, `label`, `active`), `path`,
  `per_page`, `to`, `total`. Quando a lista está vazia, `from` e `to` são `null`.
- Datas e horas: ISO 8601 em UTC com `+00:00`, por exemplo `2026-10-19T17:32:10+00:00` (`app.timezone = UTC`).
- Identificadores: UUID (texto de 36 caracteres).
- Paginação: `per_page` (padrão 25, inteiro; sem teto na maioria das rotas, a localização por aparelho tem teto de 100 com 422 acima)
  e `page` (padrão 1).
- Ordenação: `sort=campo` ou `sort=-campo` (descendente), só campos permitidos por rota. Vários campos separados por vírgula.
- Inclusão: `include=a,b`, só os valores permitidos por rota.
- Filtros: `filter[nome]=valor`. Todos os filtros de uma chamada se combinam com **E**. Vírgula dentro de um valor vira lista
  com **OU** (`filter[status]=active,inactive`). Tipos: **exato** (igualdade, diferencia maiúscula de minúscula, aceita lista),
  **parcial** (contém o texto, ignora maiúscula e minúscula, trata `_` e `%` como texto comum) e **escopo** (filtro pronto da
  ClubTrack; o nome é o da chave no `AllowedFilter`, em camelCase quando o código está em camelCase, como `withBinding`).
  Filtro, ordenação ou inclusão fora da lista permitida: **400** com mensagem em inglês
  `Requested filter(s) \`x\` are not allowed. Allowed filter(s) are \`a, b\`.` (equivalente para `sort` e `include`).
  Fonte: `vendor/spatie/laravel-query-builder` + os `allowedFilters` de cada controller. **A spec erra nomes de filtro**
  (por exemplo `with_binding` onde o código aceita `withBinding`); o que vale é o `AllowedFilter` do controller.

## Erros

- Corpo base: `{"message": "..."}`. Validação (422): `{"message": "...", "errors": {"campo": ["mensagem"]}}`. A mensagem do
  framework sai **em inglês** (não há arquivos de tradução no core); mensagens escritas pelo código saem em português.
  Quando há mais de um erro de campo, o `message` do topo termina com `(and N more errors)`.
- Regras de negócio violadas (`DomainException`, `InvalidArgumentException`): 422 com `{"message": "..."}`.
- Recurso inexistente ou de outro parceiro: 404 `{"message": "Recurso não encontrado."}` (mesma resposta para os dois casos;
  a regra vale onde o E24.5 foi aplicado: confira por rota se um 403 de posse ainda existe).
- Erro de servidor: 500 `{"message": "Server Error"}`. Não há campo `code` ainda.
- Id fora do formato UUID no caminho de algumas rotas ainda dá 500 em vez de 404. **Não documente como comportamento.**
  Registre em divergências como "defeito conhecido" e siga.

## Webhook (alertas de cerca)

- O parceiro cadastra uma URL e um segredo com a equipe da ClubTrack (não há rota B2B para isso). Eventos: `geofence.enter`
  (aparelho entrou na cerca) e `geofence.exit` (saiu). Fonte: `Tracking/Application/Pipeline/GeofenceEvaluationService.php`.
- Chamada: `POST` na URL, corpo JSON `{event, geofence:{id,name,radius_meters}, device:{id,serial}, position:{latitude,longitude,distance_meters}, occurred_at}`.
- Cabeçalhos: `X-TagTrack-Event`, `X-TagTrack-Dispatch-Id` (identifica o envio; repete nas novas tentativas), `X-TagTrack-Timestamp`
  (ISO 8601 de quando a tentativa saiu) e, se há segredo cadastrado, `X-TagTrack-Signature-256: sha256=<hex>`, que é
  `HMAC-SHA256` do **corpo cru** (os bytes recebidos) com o segredo. Fonte: `Tracking/.../Webhook/WebhookRequest.php`.
- Entrega: qualquer 2xx é sucesso. Falha (não 2xx, tempo esgotado, erro de rede): até **5 tentativas**, com intervalos de
  2, 4, 8 e 16 minutos entre elas; depois o envio é abandonado. Sem URL cadastrada o envio é abandonado. Fonte: `WebhookDispatchService.php`.

## Caminho obsoleto

`/api/b2b/...` (sem `v1`) ainda responde igual e traz o cabeçalho `Deprecation`. As páginas só descrevem `/api/b2b/v1`.
