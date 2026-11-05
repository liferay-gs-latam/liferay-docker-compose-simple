# PoC Portal Tokio Marine com o Liferay CMS

PoC da nova versão do site Tokio Marine (referência:
`http://www.tokiomarine.com.br:8080`) na instância `dev.tokiomarine:8080`,
usando o novo Liferay CMS (Liferay DXP 2026.q1.13).

O objetivo é mostrar como o conteúdo dos produtos fica estruturado uma única vez
no CMS e é reaproveitado, de forma dinâmica e padronizada, em todas as páginas:
o Marketing Manager cadastra um produto e ele aparece automaticamente no menu,
no catálogo, na página da categoria, no comparador dos produtos irmãos e, se
marcado como destaque, no slider da home, sempre com o mesmo layout.

## Páginas

| Página | URL | Como é montada |
|---|---|---|
| Home | `/` | Página de conteúdo: slider dos produtos com "Destaque na home", carrossel de categorias, bloco ESG |
| Seguros | `/web/guest/seguros` | Página de conteúdo: hero (bloco), catálogo por categoria com filtro por Segmento, bloco ESG |
| Categoria | `/web/guest/categoria/marketing/<categoria>` | Display Page Template "Categoria de Seguro" (uma página por categoria, automática) |
| Produto | `/web/guest/seguro/marketing/<produto>` | Display Page Template "Produto de Seguro" (uma página por produto, automática) |

Exemplos: `/web/guest/seguro/marketing/seguro-auto`,
`/web/guest/categoria/marketing/vida`. As URLs também funcionam sem
`/web/guest`.

Todas as páginas usam a master page **Tokio Marine** (estilos base, header e
footer) e o style book **Tokio Marine** (verde #006551, dourado #C7800B,
Montserrat, botões em pílula).

## Modelo de conteúdo (space Marketing)

Estruturas criadas no formato do construtor de estruturas do CMS (editáveis pela
interface do CMS):

- **Produto de Seguro** (`TmProduto`): nome, rótulo, subtítulo, resumo (para
  quem é), texto/link de contratação, código do produto, destaque na home,
  ordem, aviso legal, imagem principal e ícone (Basic Documents).
  - Categoria: conteúdo relacionado (uma **Categoria de Seguro**).
  - Produtos relacionados: conteúdo relacionado múltiplo (outros produtos).
  - Grupos repetíveis:
    - **Seções de destaques** (tag, título, subtítulo) com **Itens** (ícone,
      título, descrição) — coberturas, diferenciais, benefícios.
    - **Tabelas de planos** (título, planos separados por `|`, nota) com
      **Linhas** (serviço, planos que incluem o serviço).
    - **Perguntas frequentes** (pergunta, resposta).
- **Categoria de Seguro** (`TmCategoria`): nome, rótulo, descrições, ordem,
  imagem e ícone.
- **Bloco de Conteúdo** (`TmBloco`): conteúdo compartilhado entre páginas
  (ESG, canais de atendimento, hero da página Seguros, chamada da home), com
  itens repetíveis.

Categorização: vocabulário global **Segmento** (Para Você, Para sua Empresa),
usado no filtro do catálogo. Um produto pode ter os dois segmentos.

Pastas do CMS: `Contents/{Produtos, Categorias, Blocos de Conteúdo}` e
`Files/{Produtos, Categorias, Ícones, Institucional}`.

## Fragmentos (coleção "Tokio Marine")

| Fragmento | Uso |
|---|---|
| Estilos Base, Header, Footer | Master page. O menu "Seguros" e a coluna Seguros do rodapé vêm do catálogo; atalhos, canais de atendimento e colunas do rodapé vêm dos Navigation Menus `Tokio - *` |
| Produto: Hero, Seções de Destaques, Tabelas de Planos, Comparador da Categoria, Perguntas Frequentes, Chamada para Contratação, Produtos Relacionados, Aviso Legal | Display Page Template de Produto |
| Categoria: Hero, Categoria: Produtos | Display Page Template de Categoria |
| Home: Slider de Produtos em Destaque, Home: Carrossel de Categorias, Catálogo de Seguros, Bloco de Conteúdo | Páginas de conteúdo |

Os fragmentos de produto/categoria têm um campo de seleção de item: na display
page ele é preenchido automaticamente com o item exibido; em uma página de
conteúdo o Frontend Developer escolhe o item. Os dados são lidos dos headless
APIs do CMS com `restClient`, com as permissões do visitante.

Seções sem conteúdo não aparecem (ex.: produto sem FAQ ou sem tabela de planos).

## Papéis

| Papel | Responsabilidade | Acesso |
|---|---|---|
| Frontend Developer (`frontend@tokiomarine.com.br` / `test`) | Fragmentos, estruturas, master pages, display page templates, style book, páginas e menus | Site Administrator do site + CMS Administrator |
| Marketing Manager (`marketing@tokiomarine.com.br` / `test`) | Conteúdos e imagens dos produtos, categorias e blocos | Membro do space Marketing com Asset Library Content Reviewer |

## Fluxo do Marketing Manager

1. No CMS (space Marketing), criar um **Produto de Seguro** em
   `Contents/Produtos`, escolher a categoria, o segmento, as imagens (em
   `Files`) e preencher seções, tabelas e FAQ.
2. Publicar. O produto passa a aparecer no menu Seguros, no rodapé (via
   categoria), no catálogo, na página da categoria, no comparador dos produtos
   da mesma categoria e, se "Destaque na home" estiver marcado, no slider da
   home. A página do produto é criada pelo Display Page Template.

## Estrutura deste diretório

```
content/catalogo.json      conteúdo da PoC (categorias, produtos, blocos)
fragments/                 ZIP de deploy: fragmentos, master page, DPTs
scripts/                   automação (headless APIs)
```

Ordem de execução para recriar a PoC numa instância com o CMS ativo e o space
Marketing conectado ao site:

```bash
cd scripts
python3 create_structures.py
python3 build_catalog.py <pasta com os outlines do site de referência>   # opcional, regenera content/catalogo.json
python3 import_catalog.py <pasta temporária para imagens>
python3 set_default_permissions.py
python3 create_style_book.py <frontend-token-definition.json do tema Classic>
python3 create_navigation_menus.py
./deploy.sh                                   # fragmentos, master page, DPTs
python3 create_pages.py
python3 create_users.py
```

Depois do primeiro deploy, marcar os dois Display Page Templates como padrão.

## Permissões de visitante

`scripts/set_default_permissions.py` adiciona VIEW para Guest nas permissões
padrão do space Marketing (e das pastas) e nas entradas existentes, incluindo
os itens dos grupos repetíveis, que têm permissões próprias. Com isso, todo
conteúdo publicado pelo Marketing Manager fica visível no site sem nenhum passo
manual de permissão.

## Observações técnicas

- Os `itemType` dos fragmentos (`com.liferay.object.model.ObjectDefinition#U6J3`,
  `#M1H3`, `#H8R2`) e as URLs padrão dos logos são desta instância; em outro
  ambiente precisam ser ajustados.
- O separador de URL amigável das estruturas é explícito (`seguro`,
  `categoria`, `bloco`): o portal rejeita separadores que sejam prefixo de
  outro, como os gerados por padrão para grupos repetíveis.
- Atualizar uma entrada com grupos repetíveis aninhados (PUT) cria novos itens
  e deixa os antigos órfãos; `import_catalog.py` remove os órfãos no final.
- Filtrar entradas por campo de relacionamento no headless não é suportado;
  os fragmentos leem os produtos pelo lado da categoria.
- A API de style books depende do feature flag `LPD-56718`; o style book é
  importado por ZIP, como na tela de Style Books.
- Header e footer do tema Classic são desligados nas configurações da master
  page.
- A importação do conteúdo partiu do site atual e herdou algumas lacunas dele
  (ex.: Seguro Moto e Vida Mulher sem FAQ, Seguro Aluguel com poucas seções).
