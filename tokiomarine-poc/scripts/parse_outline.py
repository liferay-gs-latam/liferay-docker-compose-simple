"""Turns a page outline of the current Tokio Marine site into product JSON.

The outlines were extracted from the reference site
(http://www.tokiomarine.com.br:8080) one fragment at a time. This parser maps
the repeating fragments to the Produto de Seguro structure:

- slide--hero- -> hero fields
- tag + section-title + cards (card-simple, benefits-cards...) -> secoes
- tag + section-title + products-0 -> tabelas
- faq-accordion -> faqs

Usage: parse_outline.py <outline.main> [<outline.main>...]
"""

import json
import re
import sys

LINE = re.compile(r"^(\s*)(.*)$")
TAG_LINE = re.compile(r"^<(\w+)> (.*)$")
IMG_LINE = re.compile(r"^IMG: (.+?)(?: alt='(.*)')?$")
LINK_TEXT = re.compile(r"^(.*?) -> (\S+)$")


def clean_url(url):
	return url.split("?")[0]


def parse(path):
	product = {
		"faqs": [],
		"hero": {},
		"secoes": [],
		"tabelas": [],
	}

	block = None
	pending = {}
	current_item = None
	current_section = None
	table = None
	faq_question = None
	faq_title = None

	def take_pending():
		header = dict(pending)

		pending.clear()

		return header

	for raw in open(path, encoding="utf-8"):
		match = LINE.match(raw.rstrip("\n"))
		indent, text = len(match.group(1)), match.group(2)

		if not text:
			continue

		if text.startswith("[") and text.endswith("]"):
			name = text[1:-1]

			if name in ("card-simple", "benefits-cards", "cards-carousel"):
				block = "cards"

				if indent == 0 or current_section is None or (
						current_section.get("_closed")):

					current_section = {"itens": [], **take_pending()}

					product["secoes"].append(current_section)

				current_item = None
			elif name == "products-0":
				block = "table"

				table = {
					"linhas": [],
					"planos": [],
					**take_pending(),
				}

				product["tabelas"].append(table)
			elif name in (
					"grid-to-carousel--card-simple-", "flex-grid",
					"cards-carousel"):

				block = "cards-container"
				current_section = {"itens": [], **take_pending()}

				product["secoes"].append(current_section)
				current_item = None
			else:
				block = name

				if current_section is not None and indent == 0:
					current_section["_closed"] = True

			continue

		if text.startswith("BG:") or text.startswith("ROW:") is False and (
				text.startswith("IMG:") and block not in (
					"slide--hero-", "cards", "cards-container",
					"benefits-cards")):

			if block == "tag":
				pending["tagIcone"] = clean_url(text.split()[1])

			continue

		if block == "slide--hero-":
			hero = product["hero"]

			img = IMG_LINE.match(text)

			if img:
				hero.setdefault("imagem", clean_url(img.group(1)))
				hero.setdefault("alt", img.group(2) or "")

				continue

			tag = TAG_LINE.match(text)

			if not tag:
				continue

			element, value = tag.groups()

			if element == "h1":
				hero["titulo"] = value
			elif element == "p":
				key = "rotulo" if "titulo" not in hero else "subtitulo"

				if key == "subtitulo" and "subtitulo" in hero:
					key = "apoio"

				hero.setdefault(key, value)
			elif element == "a":
				link = LINK_TEXT.match(value)

				if link and "ctaLink" not in hero:
					hero["ctaTexto"], hero["ctaLink"] = link.groups()

			continue

		if block == "tag":
			tag = TAG_LINE.match(text)

			if tag and tag.group(1) == "span":
				pending["tag"] = tag.group(2)

				continue

			if not (tag and tag.group(1) == "h2"):
				continue

			block = "section-title"

		if block == "section-title" or (
				block in (None, "button", "text", "section-bg") and
				TAG_LINE.match(text) and
				TAG_LINE.match(text).group(1) in ("h2",)):

			tag = TAG_LINE.match(text)

			if not tag:
				continue

			element, value = tag.groups()

			if element == "h2":
				pending["titulo"] = value
				pending.pop("subtitulo", None)
				block = "section-title"
			elif element == "p" and "titulo" in pending:
				pending["subtitulo"] = value

			continue

		if block in ("cards", "cards-container", "benefits-cards"):
			if current_section is None:
				current_section = {"itens": [], **take_pending()}

				product["secoes"].append(current_section)

			img = IMG_LINE.match(text)

			if img:
				current_item = {
					"descricao": "",
					"icone": clean_url(img.group(1)),
					"titulo": "",
				}

				current_section["itens"].append(current_item)

				continue

			tag = TAG_LINE.match(text)

			if not tag:
				continue

			element, value = tag.groups()

			if element in ("h3", "h4", "h5"):
				if current_item is None or current_item["titulo"]:
					current_item = {"descricao": "", "titulo": ""}

					current_section["itens"].append(current_item)

				current_item["titulo"] = value
			elif element in ("p", "li") and current_item is not None:
				value = "• " + value if element == "li" else value

				current_item["descricao"] = (
					current_item["descricao"] + "\n" + value).strip()

			continue

		if block == "table":
			if text.startswith("ROW:"):
				cells = [cell.strip() for cell in text[4:].split("|")]

				included = [
					plan
					for plan, cell in zip(table["planos"], cells[1:])
					if "✓" in cell or cell.strip("[] ").lower() in (
						"sim", "yes")
				]

				table["linhas"].append(
					{"incluidoEm": included, "servico": cells[0]})

				continue

			tag = TAG_LINE.match(text)

			if not tag:
				continue

			element, value = tag.groups()

			if element == "div" and not table["linhas"]:
				if value.lower() not in ("serviço", "servico", "cobertura"):
					table["planos"].append(value)
			elif element == "p":
				table["nota"] = value

			continue

		if block == "faq-accordion":
			tag = TAG_LINE.match(text)

			if not tag:
				continue

			element, value = tag.groups()

			if element == "h2":
				faq_title = value
			elif element == "button":
				faq_question = value
			elif element == "p" and faq_question:
				product["faqs"].append(
					{"pergunta": faq_question, "resposta": value})

				faq_question = None

	product["secoes"] = [
		{key: value for key, value in section.items() if key != "_closed"}
		for section in product["secoes"]
		if [item for item in section["itens"] if item["titulo"]]
	]

	for section in product["secoes"]:
		section["itens"] = [
			item for item in section["itens"] if item["titulo"]]

	product["tabelas"] = [
		table for table in product["tabelas"] if table["linhas"]]

	if faq_title:
		product["faqTitulo"] = faq_title

	return product


if __name__ == "__main__":
	json.dump(
		{path: parse(path) for path in sys.argv[1:]}, sys.stdout,
		ensure_ascii=False, indent="\t")
