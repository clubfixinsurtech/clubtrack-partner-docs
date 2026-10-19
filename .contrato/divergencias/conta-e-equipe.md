# Divergências spec x código: Conta e equipe

Uma linha por item. Formato: operação | o que a spec diz | o que o código faz | fonte.

## Spec x código

- POST /auth/login | spec afirma "sem nenhum middleware, inclusive sem o rate limit de 1000 req/min" | confere: a rota não tem middleware nem limite próprio (nem de tentativas por e-mail). Página não afirma nada sobre limite de tentativas; ver "Para decidir" abaixo | `PartnerManagement/Infrastructure/Http/routes.php` (bloco `auth/login`)
- POST /auth/login | spec lista só 401 e 422 | confere. A página não lista 400, 403 nem 429 (a rota não passa por resolução de filial, trava de parceiro ativo nem limite da chave) | `PartnerAuthController.php:login`
- POST /auth/login | spec descreve `user` sem `status`/`created_at` | confere: o controller monta `user` à mão com `id, partner_id, name, email, role` | `PartnerAuthController.php:31-37`
- POST /auth/login | nada diz sobre acesso com data de validade | o login só confere `status`; um usuário com `expires_at` no passado recebe 200 e token, e a primeira chamada com o token responde 401 `Usuário inativo.` (a página registra isso em "Detalhes que ajudam") | `PartnerAuthController.php:login` x `ResolvesPartnerContext.php:34`
- POST /auth/login | nada diz sobre a situação do parceiro | o login não consulta o parceiro: usuário de parceiro suspenso recebe token e as chamadas seguintes dão 403 | `PartnerAuthController.php:login`
- POST /auth/forgot-password | operação fora da spec (`spec: false`) | existe: sempre 200 com `Se o e-mail informado tiver uma conta ativa, enviamos um link de recuperação.`; só envia para usuário `active`; link de 24 horas; 422 só para `email` ausente ou malformado | `PartnerAuthController.php:forgotPassword`, `PartnerUserPasswordReset.php`
- POST /auth/forgot-password | fora da spec | sem middleware e sem limite de envio por e-mail ou IP: cada chamada para conta ativa enfileira um e-mail | `routes.php` (bloco `auth/forgot-password`)
- GET /partner | operação fora da spec | existe com `partner.access` + `partner.active`; resposta `{data: {id, name, logo_url, is_hub, billing_model}}`; o Resource é enxuto de propósito e NÃO traz webhook, segredo, `payout_day`, `commission_rate` nem `billing_cutoff_day`; nada sensível a conferir | `PartnerProfileController.php:show`, `B2b/PartnerProfileResource.php`
- GET /partner | fora da spec | `billing_model` aceita `per_subscription` (padrão) e `consolidated_postpaid` (check no banco) | `PartnerBillingModel.php`, migration `2026_09_25_000001`
- GET /partner | fora da spec | `logo_url` é `Storage::disk('public')->url(...)`, ou seja `APP_URL/storage/partner-logos/<hash>.<ext>`; o host real em produção depende de `APP_URL` e o exemplo da página usa o host da API. A conferir | `PartnerProfileResource.php`, `config/filesystems.php:44`
- POST /partner/logo | operação fora da spec | existe: campo `logo` (multipart), regras `required|image|max:2048`; `image` aceita jpg, jpeg, png, gif, bmp, webp, avif, heic, heif (SVG fora); 200 com o perfil; apaga o arquivo anterior | `UpdatePartnerLogoRequest.php`, `UpdatePartnerLogoHandler.php`, `ValidatesAttributes.php:validateImage` (vendor)
- POST /partner/logo | fora da spec | 403 `Papel 'operator' não pode alterar a logo do parceiro.` (só login de operator; chave de API não tem papel); 422 `Só o hub pode ter logo própria — filial herda a do hub.` para credencial de filial (o travessão é parte da mensagem real do código) | `PartnerProfileController.php:updateLogo`, `UpdatePartnerLogoHandler.php`
- POST /partner/logo | fora da spec | a pasta de destino e o nome do arquivo (`partner-logos/<hash>`) são aleatórios; o endereço muda a cada envio | `UpdatePartnerLogoHandler.php`
- GET /branches | spec lista 401 e 403 | também responde 400 (login de usuário com mais de uma filial sem `X-Partner-Branch-Id`) e 429 (limite de chave de API), erros comuns às rotas com resolução de parceiro | `ResolvesPartnerContext.php`
- GET /branches | spec exemplifica `cnpj` com máscara ("00.000.000/0001-00") | o cadastro grava só dígitos (`preg_replace('/\D/', '')`), então a página mostra 14 dígitos sem máscara. Parceiros cadastrados por outro caminho podem ter outro formato: a conferir | `CreatePartnerHandler.php:42`
- GET /branches | spec diz que o hub vem primeiro e as filiais por nome | confere. A lista inclui filiais suspensas e filiais a que o usuário logado não tem acesso (não filtra por status nem por acesso do usuário) | `B2bBranchController.php:index`
- GET /branches | fora da spec: query `filter[parent_partner_id]` | a rota não usa query builder; o filtro é ignorado (teste `PartnerBranchListTest`) | `B2bBranchController.php`, `tests/Feature/B2b/PartnerBranchListTest.php:67`
- GET /partner-users | spec lista 401 e 403 | também responde 400 e 429 (mesmo motivo de GET /branches) | `ResolvesPartnerContext.php`
- GET /partner-users | spec: "usuários do próprio parceiro" | o filtro é `where partner_id = resolved_partner_id` (FK de origem), não a tabela de acessos por filial: um usuário criado no hub não aparece na consulta em nome de uma filial, mesmo que tenha acesso a ela | `PartnerUserController.php:index`
- POST /partner-users | spec lista 401, 403, 422 | também responde 400 e 429 | `ResolvesPartnerContext.php`
- POST /partner-users | spec: "sem cadência de convite por e-mail nesta rota" | confere. O handler não envia notificação; o usuário nasce `active` e com acesso só ao parceiro resolvido (`branches()->attach`). A página avisa que, apesar do nome da operação, não há convite | `CreatePartnerUserHandler.php`
- POST /partner-users | spec: 403 inclui "Parceiro inativo" | confere; mensagem do papel é `Papel 'operator' não pode gerenciar outros usuários do parceiro.` | `PartnerUserController.php:store`
- POST /partner-users | spec: 422 genérico | e-mail repetido responde 422 com `{"message": "E-mail '<email>' já está em uso."}` sem `errors`; a checagem é global (qualquer parceiro) e exata (distingue maiúscula de minúscula) | `CreatePartnerUserHandler.php:14`
- POST /partner-users | spec: `password` "só tamanho mínimo 8" | confere (`Password::min(8)`); mensagem em inglês `The password field must be at least 8 characters.` | `CreatePartnerUserRequest.php`
- POST /partner-users | a validação do corpo roda antes da checagem de papel: `operator` com corpo inválido recebe 422, não 403 | ordem FormRequest -> `abort_if` | `PartnerUserController.php:store`
- POST /partner-users/{id}/password | spec: 403 "assinatura inválida ou expirada" | confere: `Invalid signature.` (framework, em inglês) para link adulterado ou vencido | `routes.php` (`->middleware('signed')`)
- POST /partner-users/{id}/password | spec: 404 | confere; a mensagem é `Recurso não encontrado.` (mapeamento global) | `PartnerUserController.php:setPassword`, `bootstrap/app.php`
- POST /partner-users/{id}/password | spec diz "reutilizável enquanto a assinatura não expirar" | confere; a página registra de forma neutra que cada chamada dentro do prazo troca a senha de novo | `PartnerUserController.php:setPassword`
- POST /partner-users/{id}/password | spec: parâmetros `expires` (inteiro) e `signature` | confere; `expires` é timestamp Unix em segundos; `signature` é hex de 64 caracteres. Validade: 24 h no link de recuperação, 7 dias no convite enviado pela equipe | `PartnerSetPasswordUrl.php`, `PartnerUserInvitation.php`, `PartnerUserPasswordReset.php`
- POST /partner-users/{id}/password | o link do e-mail não é o endereço da API: é a página `/definir-senha` do Portal do Parceiro com o endereço assinado no parâmetro `url` (clicar é GET e a rota só aceita POST) | `PartnerSetPasswordUrl.php`

## Divergência com o guia de autenticação (não editado)

Registrado também em `conta-e-equipe-guia.md`.

## Defeito conhecido / a conferir

- Login com `expires_at` vencido devolve 200 e token; a recusa vem só na chamada seguinte (`PartnerAuthController::login` não chama `isExpired()`). Defeito de pouca gravidade; a página descreve o comportamento atual.
- Definir senha não revoga tokens já emitidos do usuário nem invalida o link usado; o mesmo link troca a senha de novo até vencer. A conferir se é intencional.
- `forgot-password` e `auth/login` não têm limite de tentativas nem de envio (sem `throttle`). Não há limite próprio de nenhum tipo nas duas rotas.
- Cada login emite token novo sem revogar os anteriores; Sanctum com `expiration => null`, então tokens nunca expiram sozinhos.
- `POST /partner-users`: mensagens de validação do framework saem em inglês (efeito conhecido, normalização em português já pronta e não publicada).
