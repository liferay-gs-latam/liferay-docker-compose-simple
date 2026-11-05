"""Builds content/catalogo.json from the reference site outlines.

The generated catalog is the editable source of the PoC content: categories,
products (with sections, plan tables and FAQ parsed from the current pages)
and shared content blocks. Image values are URLs of the reference site; the
import script uploads them to the CMS as Basic Documents.

Usage: build_catalog.py <outlines dir>
"""

import json
import os
import sys

from parse_outline import parse

REF = "http://www.tokiomarine.com.br:8080"
ICONS = REF + "/documents/6797060/6819004/"

AVISO = (
	"O registro deste produto na Susep não representa aprovação ou "
	"recomendação pela autarquia.")

CATEGORIAS = [
	{
		"descricao": (
			"A Tokio Marine tem uma opção para cada perfil de motorista. "
			"Encontre o seu seguro em segundos."),
		"descricaoCurta": "Proteção para o seu carro, moto ou caminhão.",
		"icone": ICONS + "icone-carro.svg",
		"imagem": REF + "/documents/6797060/0/Seguro Auto Tokio Marine "
			"Seguradora (2).png",
		"ordem": 1,
		"rotulo": "SEGUROS DE AUTOMÓVEIS",
		"slug": "automoveis",
		"title": "Seguros Automóveis",
	},
	{
		"descricao": (
			"Proteção para o seu lar, do jeito certo para o seu momento. "
			"Soluções completas para proprietários, inquilinos e "
			"imobiliárias."),
		"descricaoCurta": "Soluções para proprietários, inquilinos e imobiliárias.",
		"icone": ICONS + "icone-casa.svg",
		"imagem": REF + "/documents/6797060/0/Seguros Residenciais Tokio "
			"Marine.png",
		"ordem": 2,
		"rotulo": "SEGUROS RESIDENCIAIS",
		"slug": "residenciais",
		"title": "Seguros Residenciais",
	},
	{
		"descricao": (
			"Proteção para quem você ama. Para cada momento da vida. Cobertura "
			"financeira para sua família ou planejamento completo para o "
			"futuro."),
		"descricaoCurta": "Proteção para quem você ama, em cada momento da vida.",
		"icone": ICONS + "icone-coracao.svg",
		"imagem": REF + "/documents/6797060/0/hero-vida.jpg",
		"ordem": 3,
		"rotulo": "SEGUROS DE VIDA",
		"slug": "vida",
		"title": "Seguros Vida",
	},
]

# slug: (outline, categoria, title, segmentos, destaque, icone, resumo,
#        codigo, relacionados)

PRODUTOS = [
	(
		"seguro-auto", "seguros-automoveis__seguro-auto", "automoveis",
		"Seguro Auto", ["voce"], True, "icone-carro.svg",
		"Cobertura completa com isenção de franquia sem culpa e indenização "
		"em até 5 dias úteis.",
		"AUTO, AUPP",
		["seguro-residencial-premiado", "seguro-vida", "seguro-moto"]),
	(
		"seguro-auto-classico", "seguros-automoveis__seguro-auto-classico",
		"automoveis", "Seguro Auto Clássico", ["voce"], False,
		"icone-carro.svg",
		"Cobertura completa para colisão, roubo e terceiros com preço "
		"acessível.",
		"AUTO",
		["seguro-auto", "seguro-residencial-premiado", "seguro-vida"]),
	(
		"seguro-moto", "seguros-automoveis__seguro-moto", "automoveis",
		"Seguro Moto", ["voce"], True, "icone-moto.svg",
		"Proteção e assistência 24h para motociclistas com facilidade de "
		"pagamento.",
		"MOTO",
		["seguro-auto", "seguro-vida", "seguro-residencial-premiado"]),
	(
		"seguro-caminhao", "seguros__seguro-caminhao", "automoveis",
		"Seguro Caminhão", ["voce", "empresa"], False, "icone-van.svg",
		"Proteção completa para o seu caminhão, com assistência 24h para "
		"manter a operação em movimento.",
		"CAMINHAO",
		["seguro-auto", "seguro-vida", "seguro-imobiliario"]),
	(
		"seguro-aluguel", "seguros-residenciais__seguro-fianca",
		"residenciais", "Seguro Aluguel", ["voce", "empresa"], True,
		"icone-casa.svg",
		"Alugue sem fiador: garantia locatícia para inquilinos, "
		"proprietários e imobiliárias.",
		"FIANCA",
		["seguro-imobiliario", "seguro-residencial-premiado", "seguro-vida"]),
	(
		"seguro-imobiliario", "seguros-residenciais__seguro-imobiliario",
		"residenciais", "Seguro Imobiliário", ["voce", "empresa"], False,
		"icone-casa.svg",
		"Seguro incêndio para imóveis alugados, obrigatório pela Lei do "
		"Inquilinato, com assistência 24h.",
		"IMOBILIARIO",
		["seguro-aluguel", "seguro-residencial-premiado", "seguro-auto"]),
	(
		"seguro-residencial-premiado",
		"seguros-residenciais__seguro-residencial", "residenciais",
		"Seguro Residencial Premiado", ["voce"], True, "icone-casa.svg",
		"Coberturas personalizadas contra incêndio, danos elétricos e roubo, "
		"com assistência 24h e sorteio mensal de R$ 10 mil.",
		"RESIDENCIAL",
		["seguro-auto", "seguro-vida", "seguro-aluguel"]),
	(
		"seguro-vida", "seguros-vida__seguro-vida", "vida", "Seguro Vida",
		["voce"], True, "icone-coracao.svg",
		"Coberturas abrangentes com benefícios que você pode usar em vida.",
		"VIDA",
		["seguro-funeral", "seguro-residencial-premiado", "seguro-auto"]),
	(
		"seguro-vida-homem", "seguro-vida-homem1", "vida", "Seguro Vida Homem",
		["voce"], False, "icone-coracao.svg",
		"Proteção pensada para a saúde do homem, com telemedicina para você "
		"e mais duas pessoas.",
		"VIDA",
		["seguro-vida", "seguro-funeral", "seguro-auto"]),
	(
		"seguro-funeral", "seguros-vida__seguro-funeral", "vida",
		"Seguro Funeral", ["voce"], False, "icone-coracao.svg",
		"Planeje agora e proteja sua família quando ela mais precisar.",
		"FUNERAL",
		["seguro-vida", "seguro-residencial-premiado", "seguro-auto"]),
	(
		"seguro-vida-mulher", "lp__seguro-vida-mulher", "vida",
		"Seguro Vida Mulher", ["voce"], False, "icone-coracao.svg",
		"Proteção para a mulher em todas as fases da vida, com telemedicina "
		"e coberturas para doenças graves.",
		"VIDA",
		["seguro-vida", "seguro-funeral", "seguro-residencial-premiado"]),
	(
		"seguro-vida-senior", "seguro-vida-senior", "vida",
		"Seguro Vida Sênior", ["voce"], False, "icone-coracao.svg",
		"No melhor momento da vida, você e sua família protegidos, com "
		"telemedicina e benefícios exclusivos.",
		"VIDA",
		["seguro-vida", "seguro-funeral", "seguro-residencial-premiado"]),
]

BLOCOS = [
	{
		"imagem": REF + "/documents/6797060/0/banner-sustentabilidade-auto.webp",
		"itens": [
			"Apólice digital disponível no Super App",
			"Programa de compensação de carbono ativo",
			"Relatórios ESG publicados anualmente",
			"Projetos sociais e ambientais em curso",
		],
		"linkBotao": "https://www.tokiomarine.com.br/empresa/esg",
		"slug": "sustentabilidade",
		"tag": "Sustentabilidade",
		"texto": (
			"A Tokio Marine integra práticas ESG em toda a sua operação: do "
			"produto ao atendimento, do sinistro ao impacto na comunidade."),
		"textoBotao": "Conheça nossa agenda ESG",
		"title": "Comprometidos com um futuro mais seguro.",
	},
	{
		"itens": [
			"Fale com a Marina pelo WhatsApp|https://wa.me/5511995786546",
			"Acesse o Chat Online|https://www.tokiomarine.com.br/chat-cliente",
		],
		"slug": "atendimento",
		"tag": "Atendimento",
		"texto": "Prefere falar com alguém agora?",
		"title": "Canais de atendimento",
	},
	{
		"imagem": REF + "/documents/6797060/0/Seguros Tokio Marine "
			"Seguradora.png",
		"linkBotao": "https://www.tokiomarine.com.br/cotacoes",
		"slug": "seguros-tokio-marine",
		"tag": "SEGUROS",
		"texto": (
			"Conheça os Seguros Tokio Marine. Planos completos para sua casa, "
			"família, carro e empresa. Cote seu seguro online com facilidade."),
		"textoBotao": "Cotar agora",
		"title": "Seguros Tokio Marine",
	},
	{
		"linkBotao": "/web/guest/seguros",
		"slug": "seguros-mais-buscados",
		"texto": (
			"Seguros flexíveis para você, sua família e seus bens. Simule "
			"agora e descubra como é fácil viver mais tranquilo."),
		"textoBotao": "Ver todos os seguros",
		"title": "Nossos seguros mais buscados",
	},
]

# Sections that only make sense on the old static pages: cross links to sibling
# products (now generated from the catalog) or empty headers

SKIPPED_SECTIONS = ("Qual o Seguro Vida Individual ideal",)

# The current pages use inconsistent eyebrows ("AUTO" on Caminhão, none on
# Vida Mulher); the catalog normalizes them

ROTULOS = {
	"seguro-auto-classico": "SEGUROS DE AUTOMÓVEIS",
	"seguro-caminhao": "SEGUROS DE AUTOMÓVEIS",
	"seguro-imobiliario": "SEGUROS RESIDENCIAIS",
	"seguro-residencial-premiado": "SEGUROS RESIDENCIAIS",
	"seguro-vida-mulher": "SEGUROS DE VIDA",
}


def _short_url(url):

	# Text fields hold up to 280 characters; drop tracking parameters

	if len(url) > 280:
		return url.split("?")[0]

	return url


def build_produto(outlines, spec, ordem):
	(
		slug, outline, categoria, title, segmentos, destaque, icone, resumo,
		codigo, relacionados) = spec

	parsed = parse(os.path.join(outlines, outline + ".main"))

	hero = parsed["hero"]

	secoes = [
		{
			"itens": [
				{
					"descricao": item["descricao"],
					"icone": item.get("icone"),
					"titulo": item["titulo"],
				}
				for item in section["itens"]
			],
			"subtitulo": section.get("subtitulo", ""),
			"tag": section.get("tag", ""),
			"titulo": section.get("titulo") or "Destaques",
		}
		for section in parsed["secoes"]
		if not (section.get("titulo") or "").startswith(SKIPPED_SECTIONS)
	]

	tabelas = [
		{
			"linhas": [
				{
					"incluidoEm": " | ".join(row["incluidoEm"]),
					"servico": row["servico"],
				}
				for row in table["linhas"]
			],
			"nota": table.get("nota", ""),
			"planos": " | ".join(table["planos"]),
			"subtitulo": table.get("subtitulo", ""),
			"tag": table.get("tag", ""),
			"titulo": table.get("titulo") or "Compare os planos",
		}
		for table in parsed["tabelas"]
	]

	return {
		"aviso": AVISO,
		"categoria": categoria,
		"codigoProduto": codigo,
		"destaqueHome": destaque,
		"faqs": parsed["faqs"],
		"icone": ICONS + icone,
		"imagem": hero.get("imagem"),
		"linkBotao": _short_url(
			hero.get("ctaLink") or "https://www.tokiomarine.com.br/cotacoes"),
		"ordem": ordem,
		"relacionados": relacionados,
		"resumo": resumo,
		"rotulo": ROTULOS.get(slug) or (hero.get("rotulo") or "").upper(),
		"secoes": secoes,
		"segmentos": segmentos,
		"slug": slug,
		"subtitulo": hero.get("subtitulo", ""),
		"tabelas": tabelas,
		"textoBotao": hero.get("ctaTexto") or "Cotar agora",
		"title": title,
	}


def main(outlines):
	catalogo = {
		"blocos": BLOCOS,
		"categorias": CATEGORIAS,
		"produtos": [
			build_produto(outlines, spec, index + 1)
			for index, spec in enumerate(PRODUTOS)
		],
	}

	target = os.path.join(
		os.path.dirname(__file__), "..", "content", "catalogo.json")

	os.makedirs(os.path.dirname(target), exist_ok=True)

	with open(target, "w", encoding="utf-8") as file:
		json.dump(catalogo, file, ensure_ascii=False, indent="\t")

	print(f"wrote {os.path.normpath(target)}")


if __name__ == "__main__":
	main(sys.argv[1])
