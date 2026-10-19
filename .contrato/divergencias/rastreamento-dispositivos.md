# Divergências: dispositivos (escritas por Bernardo)

- GET /devices | filtros `registered_after`, `registered_before`, `assigned_to_partner` (snake_case) | o código aceita `registeredAfter`, `registeredBefore`, `assignedToPartner` (camelCase); teste do core usa `filter[assignedToPartner]` | `B2bDeviceController.php:index`, `tests/Feature/B2b/DeviceInventoryTest.php`
- GET /devices | `active_tag_binding_id` | o campo existe na resposta B2B (id do vínculo ativo do parceiro, ou null) | `DeviceResource.php`, `B2bDeviceController::attachActiveTagBindingIds`
- GET /devices/{id} | 404 com mensagem "Dispositivo não encontrado." (específica, não "Recurso não encontrado.") | `B2bDeviceController.php:show`
- GET /devices/{id} | id que não é UUID responde 500 hoje (a rota não tem whereUuid); a E24.11 troca por 404. A página descreve o alvo (404) | `src/DeviceManagement/Infrastructure/Http/routes.php`
- GET /devices | erro 400 também para `include` ou `sort` inválido; `status_histories` só traz o histórico a partir da entrada do aparelho no parceiro | `B2bDeviceController::statusHistoriesSinceEntry`
- GET /devices | `filter[search]` não consta na spec | o código aceita `search` (serial, apelido do bem ou nome do cliente) | `B2bDeviceController.php:index`
