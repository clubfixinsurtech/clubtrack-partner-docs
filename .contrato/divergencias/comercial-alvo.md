# Comportamento alvo ainda não em produção: Pedidos, assinaturas e planos

Uma linha por item. Formato: operação | o que a página documenta (alvo) | o que a produção faz hoje | decisão e fonte.

- Alvo ainda não em produção: `recipient_type` na resposta de POST /device-orders e GET /device-orders | as páginas `criar-pedido-de-dispositivo` e `listar-pedidos-de-dispositivo` documentam os valores `partner` e `customer` e usam `"recipient_type": "partner"` nos exemplos | hoje a produção devolve o nome interno de uma classe no campo (defeito conhecido, não descrito nas páginas) | decisão já tomada: devolver `customer` ou `partner` na resposta B2B; a normalização da spec fará isso. Fonte do estado atual: `DeviceOrderResource.php` (devolve `recipient_type` cru, sem `Relation::morphMap`), `CreateDeviceOrderTest.php:34`
