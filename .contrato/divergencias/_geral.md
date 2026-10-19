# Divergências gerais spec x código (commit ff50d33)

- As 4 operações de cerca da spec (`GET/POST /geofences`, `GET/DELETE /geofences/{id}`) **não existem no código**: a Story 20.3 removeu as rotas B2B de cerca (`src/Tracking/Infrastructure/Http/routes.php`, comentário "Story 20.3"). A cerca é criada pelo cliente final, pela API B2C. Sem página de operação; o webhook de cerca segue valendo para as cercas dos clientes do parceiro.
- Rotas que existem e **não estão na spec**: `POST /auth/forgot-password`, `GET /partner`, `POST /partner/logo`, `POST /subscriptions/{id}/resend-payment-link`. Documentadas como operações fora da spec (`spec: false` no manifesto).
- `locations` e `locations/latest`: a spec diz "somente API Key"; o código usa `partner.access` (aceita chave e login de usuário).
- Spec declara `servers` de desenvolvimento e texto de implantação ("NÃO EXISTE AINDA") que não vale mais; a normalização é da E24.8.
