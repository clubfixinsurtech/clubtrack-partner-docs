#!/usr/bin/env python3
"""Confere páginas de operação contra o manifesto e a spec congelada.

Uso:
  python3 scripts/verificar-contrato.py --grupo rastreamento
  python3 scripts/verificar-contrato.py --tudo
  python3 scripts/verificar-contrato.py --final      # tudo + navegação, links e guias

ERRO derruba a execução (código 1). AVISO precisa ser resolvido na página ou registrado em
.contrato/divergencias/<grupo>.md citando o nome do parâmetro ou do status.
"""
import argparse, json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SPEC = json.loads((RAIZ / '.contrato/openapi-b2b.json').read_text(encoding='utf-8'))
OPS = json.loads((RAIZ / '.contrato/operacoes.json').read_text(encoding='utf-8'))

SECOES = ['Quando usar', 'Autenticação e permissões', 'Parâmetros', 'Resposta', 'Erros', 'Exemplos']
PROIBIDOS = [
    r'src/', r'\bStory\b', r'\bEpic\b', r'\bE24\b', r'middleware', r'Sanctum', r'Spatie', r'Laravel', r'Saloon',
    r'Horizon', r'Forge', r'tagtrack', r'api/admin', r'partner\.access', r'partner\.active', r'\bcore\b(?!\.clubtrack)',
    r'ModelNotFound', r'Src\\', r'\bPartnerModel\b', r'\bRESOLVES', r'clubfix', r'seguradora',
]
# Vocabulário que a marca evita (DNA): aviso, não erro
EVITAR = [r'\broubo', r'\bfurto', r'\bperigo', r'\bblindagem', r'\brevolucion', r'\binovador', r'\bdisruptiv',
          r'solução completa', r'tecnologia de ponta', r'\bvigilância']
IDIOMAS = [('bash', 'cURL'), ('javascript', 'JavaScript'), ('python', 'Python'), ('php', 'PHP')]


def resolver(x):
    while isinstance(x, dict) and '$ref' in x:
        y = SPEC
        for k in x['$ref'].lstrip('#/').split('/'):
            y = y[k]
        x = y
    return x


def spec_op(o):
    return SPEC['paths'][o['path']][o['method'].lower()]


def params_spec(o):
    if o.get('spec') is False:
        return None
    op = spec_op(o)
    comuns = SPEC['paths'][o['path']].get('parameters', [])
    saida = set()
    for p in comuns + op.get('parameters', []):
        p = resolver(p)
        sch = resolver(p.get('schema') or {})
        if p['in'] == 'query' and sch.get('type') == 'object' and sch.get('properties'):
            for prop in sch['properties']:
                saida.add(('query', f"{p['name']}[{prop}]"))
        else:
            saida.add((p['in'], p['name']))
    rb = op.get('requestBody')
    if rb:
        sch = resolver(rb['content']['application/json']['schema'])
        for k in (sch.get('properties') or {}):
            saida.add(('body', k))
    return saida


def tirar_codigo(txt):
    return re.sub(r'```.*?```', '', txt, flags=re.S)


def frontmatter(txt):
    m = re.match(r'---\n(.*?)\n---\n', txt, flags=re.S)
    if not m:
        return None, txt
    fm = {}
    for linha in m.group(1).splitlines():
        k, _, v = linha.partition(':')
        fm[k.strip()] = v.strip().strip('"')
    return fm, txt[m.end():]


def secao(corpo, nome):
    m = re.search(r'^## ' + re.escape(nome) + r'\s*$(.*?)(?=^## |\Z)', corpo, flags=re.S | re.M)
    return m.group(1) if m else None


def checar_texto_publico(rel, txt, erros, avisos):
    sem_codigo = re.sub(r'X-TagTrack-[\w-]*', '', tirar_codigo(txt))
    for padrao in PROIBIDOS:
        # Story, Epic, E24 e nomes de classe são sensíveis a maiúsculas; o resto, não
        flags = 0 if padrao in (r'\bStory\b', r'\bEpic\b', r'\bE24\b', r'\bPartnerModel\b', r'\bRESOLVES') else re.I
        m = re.search(padrao, sem_codigo, flags=flags)
        if m:
            erros.append(f'{rel}: termo interno proibido "{m.group(0)}"')
    for padrao in EVITAR:
        m = re.search(padrao, sem_codigo, flags=re.I)
        if m:
            avisos.append(f'{rel}: vocabulário que a marca evita: "{m.group(0)}"')
    for tracos in ('—', '–'):
        if tracos in sem_codigo:
            erros.append(f'{rel}: travessão ({tracos}) fora de bloco de código')
    for em in re.findall(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+', txt):
        if not em.endswith('.example'):
            erros.append(f'{rel}: e-mail que não é fictício: {em}')
    if re.search(r'não é [^.\n]{1,50}, (é|mas)', sem_codigo, flags=re.I):
        avisos.append(f'{rel}: padrão "não é X, é Y"')
    for bloco in re.findall(r'```json[^\n]*\n(.*?)```', txt, flags=re.S):
        try:
            json.loads(bloco)
        except Exception as e:  # noqa: BLE001
            erros.append(f'{rel}: JSON inválido em exemplo ({e})')


def checar_operacao(o, erros, avisos, infos):
    rel = o['page']
    arq = RAIZ / rel
    if not arq.exists():
        erros.append(f'{rel}: página não existe')
        return
    txt = arq.read_text(encoding='utf-8')
    fm, corpo = frontmatter(txt)
    if fm is None:
        erros.append(f'{rel}: sem frontmatter')
        return
    esperado = f"{o['method']} {o['path']}"
    if fm.get('api') != esperado:
        erros.append(f'{rel}: api="{fm.get("api")}" deveria ser "{esperado}"')
    if not fm.get('title'):
        erros.append(f'{rel}: sem title')
    d = fm.get('description', '')
    if not d:
        erros.append(f'{rel}: sem description')
    elif len(d) > 160:
        avisos.append(f'{rel}: description com {len(d)} caracteres (máximo 160)')

    ultimo = -1
    for s in SECOES:
        m = re.search(r'^## ' + re.escape(s) + r'\s*$', corpo, flags=re.M)
        if not m:
            erros.append(f'{rel}: falta a seção "## {s}"')
        else:
            if m.start() < ultimo:
                erros.append(f'{rel}: seção "{s}" fora de ordem')
            ultimo = m.start()

    diverg = ''
    for dv in sorted((RAIZ / '.contrato/divergencias').glob(f"{o['group']}*.md")) + [RAIZ / '.contrato/divergencias/_geral.md']:
        if dv.exists():
            diverg += dv.read_text(encoding='utf-8').lower() + '\n'

    pagina = set()
    for loc, nome in re.findall(r'<ParamField\s+(header|path|query|body)="([^"]+)"', txt):
        pagina.add((loc, nome))
    esp = params_spec(o)
    fora_da_spec = esp is None
    if fora_da_spec:
        esp = set()
    GLOBAIS = {('header', 'X-Api-Key'), ('header', 'Authorization'), ('query', 'page')}

    def registrado(nome):
        interno = re.sub(r'^.*\[(.*)\]$', r'\1', nome).lower()
        return nome.lower() in diverg or interno in diverg

    for loc, nome in sorted(esp - pagina):
        (infos if registrado(nome) else avisos).append(f'{rel}: spec tem {loc} "{nome}" e a página não')
    for loc, nome in sorted(() if fora_da_spec else pagina - esp - GLOBAIS):
        (infos if registrado(nome) else avisos).append(f'{rel}: página tem {loc} "{nome}" que a spec não tem')

    for tipo, tag in (('ParamField', 'ParamField'), ('ResponseField', 'ResponseField')):
        for m in re.finditer(r'<%s\s+[^>]*>(.*?)</%s>' % (tag, tag), txt, flags=re.S):
            if len(re.sub(r'\s+', ' ', m.group(1)).strip()) < 25:
                avisos.append(f'{rel}: {tipo} com explicação curta demais: {m.group(0)[:70]!r}')

    sec_erros = secao(corpo, 'Erros') or ''
    codigos_pagina = set(re.findall(r'^\|\s*(\d{3})\s*\|', sec_erros, flags=re.M))
    codigos_spec = set() if fora_da_spec else {c for c in spec_op(o)['responses'] if c.startswith(('4', '5'))}
    for c in sorted(codigos_spec - codigos_pagina):
        (infos if c in diverg else avisos).append(f'{rel}: spec lista erro {c} e a tabela de erros não')
    for c in sorted(() if fora_da_spec else codigos_pagina - codigos_spec - {'429'}):
        (infos if c in diverg else avisos).append(f'{rel}: tabela de erros tem {c}, que a spec não lista')

    sec_ex = secao(corpo, 'Exemplos') or ''
    for lang, nome in IDIOMAS:
        if not re.search(r'```' + lang + r'\b', sec_ex):
            erros.append(f'{rel}: exemplo de requisição em {nome} ausente')
    if '<RequestExample>' not in sec_ex or '<ResponseExample>' not in sec_ex:
        erros.append(f'{rel}: faltam <RequestExample> e/ou <ResponseExample> na seção Exemplos')

    checar_texto_publico(rel, txt, erros, avisos)


def checar_guias(erros, avisos):
    for arq in sorted(list((RAIZ / 'guias').glob('*.mdx')) + [RAIZ / 'index.mdx', RAIZ / 'primeira-chamada.mdx', RAIZ / 'historico-de-mudancas.mdx']):
        if not arq.exists():
            erros.append(f'{arq.relative_to(RAIZ)}: guia não existe')
            continue
        txt = arq.read_text(encoding='utf-8')
        fm, _ = frontmatter(txt)
        rel = str(arq.relative_to(RAIZ))
        if not fm or not fm.get('title') or not fm.get('description'):
            erros.append(f'{rel}: frontmatter sem title ou description')
        checar_texto_publico(rel, txt, erros, avisos)


def checar_navegacao(erros):
    docs = json.loads((RAIZ / 'docs.json').read_text(encoding='utf-8'))
    paginas = []

    def varrer(n):
        if isinstance(n, str):
            paginas.append(n)
        elif isinstance(n, dict):
            for k in ('pages', 'groups', 'tabs'):
                for x in n.get(k, []):
                    varrer(x)
        elif isinstance(n, list):
            for x in n:
                varrer(x)
    varrer(docs['navigation'])
    for p in paginas:
        if not (RAIZ / (p + '.mdx')).exists():
            erros.append(f'docs.json aponta para {p}.mdx que não existe')
    todos = {str(a.relative_to(RAIZ))[:-4] for a in RAIZ.rglob('*.mdx')}
    for t in sorted(todos - set(paginas)):
        erros.append(f'{t}.mdx existe e não está no menu')
    for a in RAIZ.rglob('*.mdx'):
        for alvo in re.findall(r'\]\((/[^)#\s]+)', a.read_text(encoding='utf-8')):
            if alvo.startswith(('/logo', '/images', '/favicon')):
                continue
            if not (RAIZ / (alvo.lstrip('/') + '.mdx')).exists() and not (RAIZ / alvo.lstrip('/')).exists():
                erros.append(f'{a.relative_to(RAIZ)}: link interno quebrado {alvo}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--grupo')
    ap.add_argument('--tudo', action='store_true')
    ap.add_argument('--final', action='store_true')
    a = ap.parse_args()
    erros, avisos, infos = [], [], []
    ops = OPS if (a.tudo or a.final) else [o for o in OPS if o['group'] == a.grupo]
    if not ops:
        print('Nada a conferir: informe --grupo, --tudo ou --final.')
        return 2
    for o in ops:
        checar_operacao(o, erros, avisos, infos)
    if a.final:
        checar_guias(erros, avisos)
        checar_navegacao(erros)
    for i in infos:
        print('INFO  ', i)
    for w in avisos:
        print('AVISO ', w)
    for e in erros:
        print('ERRO  ', e)
    print(f'\n{len(ops)} operação(ões) conferida(s): {len(erros)} erro(s), {len(avisos)} aviso(s), {len(infos)} divergência(s) registrada(s).')
    return 1 if erros else 0


if __name__ == '__main__':
    sys.exit(main())
