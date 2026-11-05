"""Imports content/catalogo.json into the Marketing space.

- creates the CMS folders used by the Marketing Manager;
- downloads the reference images and uploads them as Basic Documents;
- creates/updates categories, content blocks and products (with their
  repeatable groups, category, Segmento categories and related products).

Every entry has a stable external reference code, so running the script again
updates the content instead of duplicating it.

Usage: import_catalog.py <download dir>
"""

import base64
import hashlib
import json
import os
import sys
import urllib.parse

import requests

import lr

CONTENT = os.path.join(os.path.dirname(__file__), "..", "content")

FOLDERS = [
	("TM_FILES_CATEGORIAS", "Categorias", "L_FILES"),
	("TM_FILES_ICONES", "Ícones", "L_FILES"),
	("TM_FILES_INSTITUCIONAL", "Institucional", "L_FILES"),
	("TM_FILES_PRODUTOS", "Produtos", "L_FILES"),
	("TM_CONTENTS_BLOCOS", "Blocos de Conteúdo", "L_CONTENTS"),
	("TM_CONTENTS_CATEGORIAS", "Categorias", "L_CONTENTS"),
	("TM_CONTENTS_PRODUTOS", "Produtos", "L_CONTENTS"),
]

SEGMENTOS = {
	"empresa": "TM_SEGMENTO_PARA_EMPRESA",
	"voce": "TM_SEGMENTO_PARA_VOCE",
}

SCOPE = f"/scopes/{lr.SPACE_KEY}"


def ensure_folders():
	for erc, title, parent in FOLDERS:
		folder = lr.call(
			"GET",
			f"/o/headless-object/v1.0{SCOPE}/object-entry-folder/"
			f"by-external-reference-code/{erc}",
			ok=(200, 404))

		if folder and folder.get("id"):
			continue

		lr.post(
			f"/o/headless-object/v1.0{SCOPE}/object-entry-folders",
			{
				"externalReferenceCode": erc,
				"parentObjectEntryFolderExternalReferenceCode": parent,
				"title": title,
			})

		print(f"folder {title}")


class Images:

	def __init__(self, download_dir):
		self._download_dir = download_dir
		self._ids = {}

	def id(self, url, folder):
		if not url:
			return 0

		if url in self._ids:
			return self._ids[url]

		name = urllib.parse.unquote(url.rsplit("/", 1)[-1])

		if "." not in name:
			name += ".png"

		erc = "TM_IMG_" + hashlib.sha1(url.encode()).hexdigest()[:16]

		path = os.path.join(self._download_dir, erc + "_" + name)

		if not os.path.exists(path):
			response = requests.get(url.replace(" ", "%20"), timeout=60)

			if response.status_code != 200:
				print(f"  missing image {url} ({response.status_code})")

				self._ids[url] = 0

				return 0

			with open(path, "wb") as file:
				file.write(response.content)

		with open(path, "rb") as file:
			data = base64.b64encode(file.read()).decode()

		title = os.path.splitext(name)[0].replace("-", " ").replace("_", " ")

		document = lr.put(
			f"/o/cms/basic-documents{SCOPE}/by-external-reference-code/{erc}",
			{
				"file": {"fileBase64": data, "name": name},
				"objectEntryFolderExternalReferenceCode": folder,
				"title": title.strip().capitalize(),
			})

		print(f"  image {name} -> {document['id']}")

		self._ids[url] = document["id"]

		return document["id"]


def taxonomy_category_ids():
	ids = {}

	for vocabulary in lr.get_all(
			"/o/headless-admin-taxonomy/v1.0/sites/34659/"
			"taxonomy-vocabularies"):

		if vocabulary["externalReferenceCode"] != "TM_SEGMENTO":
			continue

		for category in lr.get_all(
				"/o/headless-admin-taxonomy/v1.0/taxonomy-vocabularies/"
				f"{vocabulary['id']}/taxonomy-categories"):

			ids[category["externalReferenceCode"]] = int(category["id"])

	return ids


def upsert(endpoint, erc, entry):
	return lr.put(
		f"/o/c/{endpoint}{SCOPE}/by-external-reference-code/{erc}", entry)


def import_categorias(catalogo, images):
	ids = {}

	for categoria in catalogo["categorias"]:
		entry = upsert(
			"tmcategorias", f"TM_CAT_{categoria['slug'].upper()}",
			{
				"descricao": categoria["descricao"],
				"descricaoCurta": categoria["descricaoCurta"],
				"friendlyUrlPath": categoria["slug"],
				"objectEntryFolderExternalReferenceCode":
					"TM_CONTENTS_CATEGORIAS",
				"ordem": categoria["ordem"],
				"r_tmCategoriaIcone_l_cmsBasicDocumentId": images.id(
					categoria["icone"], "TM_FILES_ICONES"),
				"r_tmCategoriaImagem_l_cmsBasicDocumentId": images.id(
					categoria["imagem"], "TM_FILES_CATEGORIAS"),
				"rotulo": categoria["rotulo"],
				"title": categoria["title"],
			})

		ids[categoria["slug"]] = entry["id"]

		print(f"categoria {categoria['title']} -> {entry['id']}")

	return ids


def import_blocos(catalogo, images):
	for bloco in catalogo["blocos"]:
		entry = upsert(
			"tmblocos", f"TM_BLOCO_{bloco['slug'].upper().replace('-', '_')}",
			{
				"friendlyUrlPath": bloco["slug"],
				"linkBotao": bloco.get("linkBotao", ""),
				"objectEntryFolderExternalReferenceCode": "TM_CONTENTS_BLOCOS",
				"r_tmBlocoImagem_l_cmsBasicDocumentId": images.id(
					bloco.get("imagem"), "TM_FILES_INSTITUCIONAL"),
				"tag": bloco.get("tag", ""),
				"texto": bloco.get("texto", ""),
				"textoBotao": bloco.get("textoBotao", ""),
				"title": bloco["title"],
				"tmBlocoItens": [
					{"texto": texto} for texto in bloco.get("itens", [])],
			})

		print(f"bloco {bloco['title']} -> {entry['id']}")


def import_produtos(catalogo, images, categoria_ids):
	taxonomy_ids = taxonomy_category_ids()

	ids = {}

	for produto in catalogo["produtos"]:
		entry = upsert(
			"tmprodutos", f"TM_PROD_{produto['slug'].upper().replace('-', '_')}",
			{
				"aviso": produto["aviso"],
				"codigoProduto": produto["codigoProduto"],
				"destaqueHome": produto["destaqueHome"],
				"friendlyUrlPath": produto["slug"],
				"linkBotao": produto["linkBotao"],
				"objectEntryFolderExternalReferenceCode": "TM_CONTENTS_PRODUTOS",
				"ordem": produto["ordem"],
				"r_tmCategoriaProdutos_c_tmCategoriaId":
					categoria_ids[produto["categoria"]],
				"r_tmProdutoIcone_l_cmsBasicDocumentId": images.id(
					produto["icone"], "TM_FILES_ICONES"),
				"r_tmProdutoImagem_l_cmsBasicDocumentId": images.id(
					produto["imagem"], "TM_FILES_PRODUTOS"),
				"resumo": produto["resumo"],
				"rotulo": produto["rotulo"],
				"subtitulo": produto["subtitulo"],
				"taxonomyCategoryIds": [
					taxonomy_ids[SEGMENTOS[segmento]]
					for segmento in produto["segmentos"]
				],
				"textoBotao": produto["textoBotao"],
				"title": produto["title"],
				"tmProdutoFaqs": produto["faqs"],
				"tmProdutoSecoes": [
					{
						"subtitulo": secao["subtitulo"],
						"tag": secao["tag"],
						"titulo": secao["titulo"],
						"tmSecaoItens": [
							{
								"descricao": item["descricao"],
								"r_tmSecaoItemIcone_l_cmsBasicDocumentId":
									images.id(item["icone"], "TM_FILES_ICONES"),
								"titulo": item["titulo"],
							}
							for item in secao["itens"]
						],
					}
					for secao in produto["secoes"]
				],
				"tmProdutoTabelas": [
					{
						"nota": tabela["nota"],
						"planos": tabela["planos"],
						"subtitulo": tabela["subtitulo"],
						"tag": tabela["tag"],
						"titulo": tabela["titulo"],
						"tmTabelaLinhas": tabela["linhas"],
					}
					for tabela in produto["tabelas"]
				],
			})

		ids[produto["slug"]] = entry["id"]

		print(f"produto {produto['title']} -> {entry['id']}")

	for produto in catalogo["produtos"]:
		for slug in produto["relacionados"]:
			lr.put(
				f"/o/c/tmprodutos/{ids[produto['slug']]}/"
				f"tmProdutoRelacionados/{ids[slug]}")


# Repeatable group endpoint -> field that links an entry to its parent

GROUPS = [
	("tmblocoitems", "r_tmBlocoItens_c_tmBlocoId"),
	("tmprodutofaqs", "r_tmProdutoFaqs_c_tmProdutoId"),
	("tmprodutosecaos", "r_tmProdutoSecoes_c_tmProdutoId"),
	("tmprodutosecaoitems", "r_tmSecaoItens_c_tmProdutoSecaoId"),
	("tmprodutotabelas", "r_tmProdutoTabelas_c_tmProdutoId"),
	("tmprodutotabelalinhas", "r_tmTabelaLinhas_c_tmProdutoTabelaId"),
]


def delete_orphan_group_entries():

	# Updating an entry with nested group items links the new items to the
	# parent but keeps the previous ones, unlinked

	for endpoint, parent_field in GROUPS:
		for entry in lr.get_all(f"/o/c/{endpoint}{SCOPE}?fields=id,{parent_field}"):
			if not entry.get(parent_field):
				lr.delete(f"/o/c/{endpoint}/{entry['id']}")

				print(f"deleted orphan {endpoint}/{entry['id']}")


def main(download_dir):
	os.makedirs(download_dir, exist_ok=True)

	with open(os.path.join(CONTENT, "catalogo.json"), encoding="utf-8") as file:
		catalogo = json.load(file)

	ensure_folders()

	images = Images(download_dir)

	categoria_ids = import_categorias(catalogo, images)

	import_blocos(catalogo, images)
	import_produtos(catalogo, images, categoria_ids)

	delete_orphan_group_entries()


if __name__ == "__main__":
	main(sys.argv[1])
