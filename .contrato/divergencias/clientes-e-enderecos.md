# Divergências spec x código: Clientes e endereços

Uma linha por item. Formato: operação | o que a spec diz | o que o código faz | fonte.

- GET /customers | filtros `search`, `with_binding`, `without_binding` | o código aceita `searchName`, `withBinding`, `withoutBinding` (camelCase, chave do `AllowedFilter`) | `HolderManagement/.../B2bCustomerController.php:index`
- GET /customers | `Customer.cpf` ("não confirmado") | o Resource devolve `cpf_cnpj` e `document_type`; não existe `cpf` | `CustomerResource.php`
- GET /customers | `include=tagBindings,activeTagBindings` listados como úteis | o include é aceito mas o Resource não renderiza as Tags (efeito nenhum na resposta) | `CustomerResource.php`
- GET /customers | `per_page` | aceito sem teto; parâmetro `page` também vale e não está na spec como parâmetro próprio | `B2bCustomerController.php:index`
- GET /customers | spec lista 400, 401, 403 | também responde 429 (limite de chave de API), erro comum a qualquer rota | `ResolvesPartnerFromApiKey.php`
