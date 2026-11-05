"""Creates the Tokio Marine content structures in the Liferay CMS.

The payloads mirror what the CMS structure builder sends
(site-cms-site-initializer/.../structure_builder), so the structures stay
editable from the CMS UI:

- repeatable groups are published first, as object definitions in the
  L_CMS_STRUCTURE_REPEATABLE_GROUPS folder, linked to their parent with a
  oneToMany "cascade" relationship;
- the main structure is published in L_CMS_CONTENT_STRUCTURES, scoped to the
  Marketing space;
- single "related content" fields (images, the product category) are oneToMany
  "disassociate" relationships owned by the related structure;
- multiple "related content" fields are manyToMany relationships.

The script is idempotent for creation: structures that already exist are
skipped.
"""

import lr

BASIC_DOCUMENT = "L_CMS_BASIC_DOCUMENT"

BOOLEAN = ("Boolean", "Boolean")
INTEGER = ("Integer", "Integer")
LONG_TEXT = ("LongText", "Clob")
RICH_TEXT = ("RichText", "Clob")
TEXT = ("Text", "String")


# Fields of repeatable groups are never required: the CMS editor always shows
# one instance of each group, so a required field there would force every
# entry to have at least one item

def field(name, label, field_type=TEXT, required=False):
	business_type, db_type = field_type

	localized = business_type in ("LongText", "RichText", "Text")

	object_field = {
		"DBType": db_type,
		"businessType": business_type,
		"externalReferenceCode": f"TM_FIELD_{name.upper()}",
		"indexed": True,
		"indexedAsKeyword": False,
		"label": {"pt_BR": label},
		"localized": localized,
		"name": name,
		"required": required,
		"system": False,
	}

	if localized:
		object_field["indexedLanguageId"] = ""

	return object_field


def title_field(label):
	object_field = field("title", label, required=True)

	object_field["system"] = True

	return object_field


# Each structure: erc, name, label, separator, fields, groups and related
# content. "images" are single related Basic Documents (relationship name ->
# label).

STRUCTURES = [
	{
		"erc": "TM_BLOCO",
		"fields": [
			title_field("Título"),
			field("tag", "Tag"),
			field("texto", "Texto", LONG_TEXT),
			field("textoBotao", "Texto do botão"),
			field("linkBotao", "Link do botão"),
		],
		"groups": [
			{
				"erc": "TM_BLOCO_ITEM",
				"fields": [field("texto", "Texto")],
				"label": "Itens",
				"name": "TmBlocoItem",
				"relationship": "tmBlocoItens",
			},
		],
		"images": {"tmBlocoImagem": "Imagem de fundo"},
		"label": "Bloco de Conteúdo",
		"name": "TmBloco",
		"separator": "bloco",
	},
	{
		"erc": "TM_CATEGORIA",
		"fields": [
			title_field("Nome"),
			field("rotulo", "Rótulo"),
			field("descricaoCurta", "Descrição curta"),
			field("descricao", "Descrição", LONG_TEXT),
			field("ordem", "Ordem", INTEGER),
		],
		"groups": [],
		"images": {
			"tmCategoriaIcone": "Ícone",
			"tmCategoriaImagem": "Imagem",
		},
		"label": "Categoria de Seguro",
		"name": "TmCategoria",
		"separator": "categoria",
	},
	{
		"erc": "TM_PRODUTO",
		"fields": [
			title_field("Nome"),
			field("rotulo", "Rótulo"),
			field("subtitulo", "Subtítulo"),
			field("resumo", "Resumo (para quem é)", LONG_TEXT),
			field("textoBotao", "Texto do botão de contratação"),
			field("linkBotao", "Link de contratação"),
			field("codigoProduto", "Código do produto"),
			field("destaqueHome", "Destaque na home", BOOLEAN),
			field("ordem", "Ordem", INTEGER),
			field("aviso", "Aviso legal", LONG_TEXT),
		],
		"groups": [
			{
				"erc": "TM_PRODUTO_SECAO",
				"fields": [
					field("tag", "Tag"),
					field("titulo", "Título"),
					field("subtitulo", "Subtítulo", LONG_TEXT),
				],
				"groups": [
					{
						"erc": "TM_PRODUTO_SECAO_ITEM",
						"fields": [
							field("titulo", "Título"),
							field("descricao", "Descrição", LONG_TEXT),
						],
						"images": {"tmSecaoItemIcone": "Ícone"},
						"label": "Itens",
						"name": "TmProdutoSecaoItem",
						"relationship": "tmSecaoItens",
					},
				],
				"label": "Seções de destaques",
				"name": "TmProdutoSecao",
				"relationship": "tmProdutoSecoes",
			},
			{
				"erc": "TM_PRODUTO_TABELA",
				"fields": [
					field("tag", "Tag"),
					field("titulo", "Título"),
					field("subtitulo", "Subtítulo", LONG_TEXT),
					field("planos", "Planos (separados por |)"),
					field("nota", "Nota de rodapé", LONG_TEXT),
				],
				"groups": [
					{
						"erc": "TM_PRODUTO_TABELA_LINHA",
						"fields": [
							field("servico", "Serviço"),
							field(
								"incluidoEm",
								"Incluído nos planos (separados por |)"),
						],
						"label": "Linhas",
						"name": "TmProdutoTabelaLinha",
						"relationship": "tmTabelaLinhas",
					},
				],
				"label": "Tabelas de planos",
				"name": "TmProdutoTabela",
				"relationship": "tmProdutoTabelas",
			},
			{
				"erc": "TM_PRODUTO_FAQ",
				"fields": [
					field("pergunta", "Pergunta"),
					field("resposta", "Resposta", LONG_TEXT),
				],
				"label": "Perguntas frequentes",
				"name": "TmProdutoFaq",
				"relationship": "tmProdutoFaqs",
			},
		],
		"images": {
			"tmProdutoIcone": "Ícone",
			"tmProdutoImagem": "Imagem principal",
		},
		"label": "Produto de Seguro",
		"many_to_many": {
			"tmProdutoRelacionados": ("TM_PRODUTO", "Produtos relacionados"),
		},
		"name": "TmProduto",
		"related": {
			"tmCategoriaProdutos": ("TM_CATEGORIA", "Categoria"),
		},
		"separator": "seguro",
	},
]


def object_definition(
		erc, name, label, fields, relationships, folder, group_settings):

	definition = {
		"enableComments": True,
		"enableFriendlyURLCustomization": True,
		"enableIndexSearch": True,
		"enableLocalization": True,
		"enableObjectEntryDraft": True,
		"enableObjectEntryHistory": True,
		"enableObjectEntrySchedule": True,
		"enableObjectEntryVersioning": True,
		"externalReferenceCode": erc,
		"label": {"pt_BR": label},
		"name": name,
		"objectDefinitionSettings": group_settings,
		"objectFields": fields,
		"objectFolderExternalReferenceCode": folder,
		"objectRelationships": relationships,
		"pluralLabel": {"pt_BR": label},
		"scope": "depot",
		"status": {"code": 0},
		"titleObjectFieldName": "title",
	}

	return definition


def cascade_relationships(parent_erc, groups):
	return [
		{
			"deletionType": "cascade",
			"externalReferenceCode": f"{group['erc']}_REL",
			"label": {"pt_BR": group["label"]},
			"name": group["relationship"],
			"objectDefinitionExternalReferenceCode1": parent_erc,
			"objectDefinitionExternalReferenceCode2": group["erc"],
			"type": "oneToMany",
		}
		for group in groups
	]


def publish_groups(groups):
	for group in groups:
		publish_groups(group.get("groups", []))

		definition = object_definition(
			group["erc"], group["name"], group["label"], group["fields"],
			cascade_relationships(group["erc"], group.get("groups", [])),
			"L_CMS_STRUCTURE_REPEATABLE_GROUPS",
			[{"name": "acceptAllGroups", "value": "true"}])

		definition["enableIndexSearch"] = False

		# The default separator is derived from the name and the portal rejects
		# separators that prefix each other (TmProdutoSecao vs
		# TmProdutoSecaoItem)

		definition["friendlyURLSeparator"] = group["name"].lower() + "-grupo"

		lr.put(
			"/o/object-admin/v1.0/object-definitions/by-external-reference-code/"
			+ group["erc"],
			definition)

		print(f"  group {group['name']}")


def single_relationship(owner_erc, target_erc, name, label):
	lr.post(
		"/o/object-admin/v1.0/object-definitions/by-external-reference-code/"
		f"{owner_erc}/object-relationships",
		{
			"deletionType": "disassociate",
			"externalReferenceCode": f"TM_REL_{name.upper()}",
			"label": {"pt_BR": label},
			"name": name,
			"objectDefinitionExternalReferenceCode1": owner_erc,
			"objectDefinitionExternalReferenceCode2": target_erc,
			"type": "oneToMany",
		})

	print(f"  related {name} ({owner_erc} -> {target_erc})")


def publish_images(erc, spec):
	for name, label in spec.get("images", {}).items():
		single_relationship(BASIC_DOCUMENT, erc, name, label)

	for group in spec.get("groups", []):
		publish_images(group["erc"], group)


def existing_ercs():
	return {
		definition["externalReferenceCode"]
		for definition in lr.get_all("/o/object-admin/v1.0/object-definitions")
	}


def main():
	existing = existing_ercs()

	for spec in STRUCTURES:
		if spec["erc"] in existing:
			print(f"skip {spec['name']} (already exists)")

			continue

		print(f"structure {spec['name']}")

		publish_groups(spec["groups"])

		definition = object_definition(
			spec["erc"], spec["name"], spec["label"], spec["fields"],
			cascade_relationships(spec["erc"], spec["groups"]),
			"L_CMS_CONTENT_STRUCTURES",
			[
				{
					"name": "acceptedGroupExternalReferenceCodes",
					"value": lr.SPACE_ERC,
				}
			])

		definition["friendlyURLSeparator"] = spec["separator"]

		lr.post("/o/object-admin/v1.0/object-definitions", definition)

		publish_images(spec["erc"], spec)

		for name, (target_erc, label) in spec.get("related", {}).items():
			single_relationship(target_erc, spec["erc"], name, label)

		for name, (target_erc, label) in spec.get(
				"many_to_many", {}).items():

			lr.post(
				"/o/object-admin/v1.0/object-definitions/"
				f"by-external-reference-code/{spec['erc']}/"
				"object-relationships",
				{
					"deletionType": "disassociate",
					"externalReferenceCode": f"TM_REL_{name.upper()}",
					"label": {"pt_BR": label},
					"name": name,
					"objectDefinitionExternalReferenceCode1": spec["erc"],
					"objectDefinitionExternalReferenceCode2": target_erc,
					"type": "manyToMany",
				})

			print(f"  related {name} (manyToMany -> {target_erc})")


if __name__ == "__main__":
	main()
