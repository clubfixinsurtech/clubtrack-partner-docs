# Divergências spec x código: Tags, dispositivos e posições (páginas de Tags e de posições)

Uma linha por item. Formato: operação | o que a spec diz | o que o código faz | fonte.
Escopo deste arquivo: `listar-tags`, `consultar-trajeto`, `consultar-distancia`, `listar-posicoes`, `ultima-posicao`.
As páginas de dispositivos (`listar-dispositivos`, `consultar-dispositivo`) têm outro redator.

## GET /tags

- GET /tags | `meta` sem esquema descrito | `meta` traz as chaves do paginador mais `generated_at` e `online_threshold_minutes` (60) | `B2bTagCollection.php` (construtor), `config/clubtrack.php:80`
- GET /tags | resposta 4xx lista 400, 401, 403, 422, 500 | também responde 429 (limite de chave de API), erro comum a qualquer rota; e 400 de filial ausente (`X-Partner-Branch-Id`) no login humano | `ResolvesPartnerFromApiKey.php`, `ResolvesPartnerContext.php`
- GET /tags | `device.serial` e `device.status` como strings obrigatórias | o Resource lê `device?->serial` e `device?->status->value`; ficam `null` se o aparelho não existir mais (caso raro, não coberto por teste) | `TagRow.php`
- GET /tags | `filter[nickname]` "Contém, sem diferenciar caixa" | o filtro é o parcial do Spatie sem `delimiter('')`: a vírgula divide o valor em alternativas (OU), então um apelido com vírgula não se acha por texto exato. `category` e `custom_fields` desligam a divisão | `B2bTagController.php:61-63`
- GET /tags | `filter[nickname]` sem diferenciar caixa | a dobra de caixa é `LOWER(coluna)` do banco com o valor já minúsculo no PHP; para letra acentuada em maiúscula o resultado depende da collation do banco (a categoria foi corrigida para `pg_c_utf8`, o apelido não) | `vendor/spatie/laravel-query-builder/src/Filters/FiltersPartial.php`, `CategoryFilter.php`
- GET /tags | `sort` não existe na spec | `sort=qualquer` responde 400 (`allowedSorts()` vazio); a ordem é fixa: `-bound_at`, desempate por id decrescente | `B2bTagController.php:65-69`
- GET /tags | `filter[custom_fields]` e `include=custom_fields` sem menção ao interruptor | sem o recurso de campos personalizados ligado para o hub do parceiro, `include` devolve `custom_fields: []` em toda linha e o filtro responde 400 (chave desconhecida) | `EloquentTagAssetFieldsAdapter.php`, `EloquentTagAssetFilterAdapter.php`
- GET /tags | `include=custom_fields`, erro 500 | confere: mensagem fixa `Não foi possível ler os campos agora.` e a página inteira falha | `B2bTagController.php`, `TagFieldsReadFailedException.php`

## GET /tags/{id}/track

- GET /tags/{id}/track | `tag` reutiliza `PartnerTag`, que inclui `asset.custom_fields` | o cabeçalho do trajeto nunca traz `custom_fields` (a chave não existe) | `TagRow::of`, chamado sem o quarto argumento em `B2bTagTrackController.php`
- GET /tags/{id}/track | resposta 4xx lista 400, 401, 403, 404, 422 | também responde 429 e, no login humano, 400 de filial ausente | `ResolvesPartnerFromApiKey.php`, `ResolvesPartnerContext.php`
- GET /tags/{id}/track | `404` genérico | `Tag não encontrada.` para vínculo inexistente, alheio, encerrado, de outra filial ou escondido pelo modelo de cobrança; `id` fora do formato UUID não chega ao controller (`whereUuid`) e dá 404 da rota, com mensagem do framework, outro texto | `TagNotFound.php`, `routes.php:73`
- GET /tags/{id}/track | `sort` e `include` | recusados com 400 que cita o próprio nome do parâmetro (`` `sort` ``, `` `include` ``) como valor não permitido; filtro desconhecido lista `from, to` como permitidos | `ReadsTrackPeriod.php:25-37`
- GET /tags/{id}/track | `filter[from]` e `filter[to]` obrigatórios | ausência dá 422 com texto do framework em inglês (`The filter.from field is required.`); formato, ordem e teto de 90 dias dão 422 com texto em português escrito pelo código | `ReadsTrackPeriod.php:40-85`
- GET /tags/{id}/track | `period.from`/`period.to` | saem em UTC sem frações de segundo (`Y-m-d\TH:i:sP`), mesmo que o pedido tenha frações; o cursor guarda o período com microssegundos | `B2bTagTrackController.php`, `ReadsTrackPeriod.php:periodKey`
- GET /tags/{id}/track | `per_page` "de 1 a 1000" | confere (padrão 100, 422 fora do intervalo) | `TagTrackRequest.php`
- GET /tags/{id}/track | trajeto de uma Tag | segue o bem (`asset`): inclui posições de vínculos anteriores do mesmo bem em cliente do parceiro, cada uma dentro da janela do vínculo; `positions[].device_id` pode mudar | `TagTrackQuery.php:windows`, `EloquentTagBindingLineageAdapter.php`

## GET /tags/{id}/distance

- GET /tags/{id}/distance | `tag` reutiliza `PartnerTag`, que inclui `asset.custom_fields` | o cabeçalho da distância nunca traz `custom_fields` | `B2bTagDistanceController.php`
- GET /tags/{id}/distance | resposta 4xx lista 400, 401, 403, 404, 422 | também responde 429 e, no login humano, 400 de filial ausente | `ResolvesPartnerFromApiKey.php`, `ResolvesPartnerContext.php`
- GET /tags/{id}/distance | `meters` "uma casa", `kilometers` "três casas" | confere: `round(m, 1)` e `round(m / 1000, 3)`; Haversine com raio 6.371.008,8 m, por janela, sem ligar janelas | `B2bTagDistanceController.php`, `TagTrackQuery.php:distance`

## GET /devices/{deviceId}/locations

- GET /devices/{deviceId}/locations | descrição: "Somente API Key (`partner.api_key`): não aceita login humano" | a rota usa `partner.access`, que aceita chave de API e login humano (correção de 22/09/2026 registrada no comentário da rota) | `Tracking/Infrastructure/Http/routes.php:58-84`
- GET /devices/{deviceId}/locations | `GpsLocation` sem `estimated_speed_kmh`, `battery_level`, `battery_percent`, `battery_level_updated_at` | o Resource devolve essas quatro chaves em toda posição; a bateria é do aparelho (última leitura conhecida), repetida em todas as linhas | `GpsLocationResource.php`, teste `GpsLocationBindingWindowTest` (I11)
- GET /devices/{deviceId}/locations | `satellites` `integer nullable` | a coluna é `NOT NULL DEFAULT 0`; nunca vem `null` | `2026_08_21_000003_partition_gps_locations_by_time.php:50`
- GET /devices/{deviceId}/locations | `include=device` | aceito, mas o Resource não renderiza o `device` (só os campos de bateria, que já vêm sempre): efeito nenhum na resposta | `GpsLocationController.php:47`, `GpsLocationResource.php`
- GET /devices/{deviceId}/locations | `filter[moving]` e `filter[stopped]`: "default do scope: 3.0 quando a chave está presente sem valor útil" | o Spatie repassa o valor enviado como limite; sem valor o filtro é ignorado (não se aplica o 3.0). Para ser verificado: comportamento com valor vazio não coberto por teste | `GpsLocationModel.php:scopeMoving`, `FiltersScope.php`
- GET /devices/{deviceId}/locations | `filter[from]`/`filter[to]` como `date-time` | o texto é repassado ao banco sem conversão de fuso (coluna `timestamp` sem fuso, em UTC); os testes só usam UTC. Deslocamento diferente de UTC não é coberto por teste | `GpsLocationModel.php:scopeRecordedAfter`, `GpsLocationFilterTest.php`
- GET /devices/{deviceId}/locations | defeito conhecido (provável, não verificado por teste): valor impossível em `filter[from]`, `filter[to]`, `filter[min_speed]`, `filter[max_speed]`, `filter[min_satellites]`, `filter[moving]` ou `filter[stopped]` não é validado pela requisição e chega ao banco; a falha de conversão tende a dar 500 | `GpsLocationController.php:34-40`
- GET /devices/{deviceId}/locations | defeito conhecido (provável, não verificado por teste): `deviceId` fora do formato UUID não passa por `whereUuid` nem por validação e chega ao banco; tende a dar 500 em vez de 404. A página não descreve isso como comportamento | `routes.php:81-84`, `VerifyDeviceOwnershipAction.php`
- GET /devices/{deviceId}/locations | a lista devolve todos os registros do aparelho na janela, inclusive `gps_valid = false` e coordenada (0, 0); o Resource não traz o indicador de validade. O trajeto da Tag filtra pelo ponto válido (C3). A decidir com o produto se a lista deve filtrar ou expor a validade | `GpsLocationController.php:27-31`, `GpsLocationResource.php`, `TagTrackQuery.php:branch`
- GET /devices/{deviceId}/locations | a janela de visibilidade não aplica o modelo de cobrança do parceiro (`PartnerTagVisibility`): por assinatura ou consolidado, vale só a união dos vínculos de cliente do parceiro com o aparelho (a spec afirma a mesma regra para os dois modelos). Difere de `GET /tags`, trajeto e distância, que escondem a Tag sem assinatura ativa. Registrado para decisão, a página descreve o que o código faz | `GpsLocationModel.php:scopeWithinPartnerBindingWindows`, `PartnerTagVisibility.php`
- GET /devices/{deviceId}/locations | resposta 4xx lista 400, 401, 403, 404, 422 | também responde 429; o 400 de filial ausente só vale no login humano | `ResolvesPartnerFromApiKey.php`, `ResolvesPartnerContext.php`
- GET /devices/{deviceId}/locations | `per_page` | padrão 100 e teto 100 (422 acima), confere com a spec; `page` não é parâmetro próprio na spec | `ListDeviceLocationsRequest.php`
- GET /devices/{deviceId}/locations | `404` "Dispositivo inexistente ou de outro parceiro" | confere: `Dispositivo não encontrado.` nos dois casos; aparelho do parceiro sem posição na janela devolve 200 com `data: []` | `VerifyDeviceOwnershipAction.php`

## GET /devices/{deviceId}/locations/latest

- GET /devices/{deviceId}/locations/latest | descrição: "Somente API Key" | aceita chave de API e login humano (`partner.access`) | `routes.php:80-83`
- GET /devices/{deviceId}/locations/latest | `GpsLocationEnvelope` sem `estimated_speed_kmh` e sem os três campos de bateria; `satellites` `nullable` | o Resource devolve as quatro chaves; `satellites` nunca é `null` | `GpsLocationResource.php`
- GET /devices/{deviceId}/locations/latest | 404 único "Dispositivo inexistente ou de outro parceiro, ou aparelho do parceiro sem nenhuma posição" | dois textos distintos: `Dispositivo não encontrado.` e `Nenhuma posição encontrada para este dispositivo.` | `GpsLocationController.php:75`, `VerifyDeviceOwnershipAction.php`
- GET /devices/{deviceId}/locations/latest | a "última posição" | é o registro de maior `recorded_at` (desempate pelo maior `id`) dentro da janela de vínculo do parceiro, sem filtro de ponto válido | `GpsLocationController.php:60-76`
- GET /devices/{deviceId}/locations/latest | resposta 4xx lista 401, 403, 404 | também responde 429 e, no login humano, 400 de filial ausente; defeito conhecido provável com `deviceId` fora do formato UUID (ver acima) | `ResolvesPartnerFromApiKey.php`, `ResolvesPartnerContext.php`
