"""Creates the Home and Seguros content pages.

Both pages use the "Tokio Marine" master page and only Tokio Marine fragments
bound to CMS content: the Home slider lists the products flagged as "Destaque
na home", the categories carousel lists every Categoria de Seguro and the
Seguros catalog lists every product grouped by category. New content shows up
without editing the pages.

The default Home of a new site (welcome text) is replaced: it is deleted and
created again with the same friendly URL, as the first page of the site.
"""

import lr

BLOCO = "com.liferay.object.model.ObjectDefinition#H8R2"


def fragment(key, config=None):
	definition = {"fragment": {"key": key, "siteKey": "Guest"}}

	if config:
		definition["fragmentConfig"] = config

	return {"definition": definition, "type": "Fragment"}


def bloco(erc, estilo="banner"):
	entry = lr.get(
		f"/o/c/tmblocos/scopes/{lr.SPACE_KEY}/by-external-reference-code/{erc}")

	return {
		"bloco": {
			"className": BLOCO,
			"classPK": str(entry["id"]),
			"title": entry["title"],
		},
		"estilo": estilo,
	}


def page_definition(*elements):
	return {
		"pageElement": {"pageElements": list(elements), "type": "Root"},
		"settings": {"masterPage": {"key": "tokio-marine"}},
	}


PAGES = [
	(
		"/home", "Home",
		lambda: page_definition(
			fragment("tm-home-slider"),
			fragment(
				"tm-categorias-carrossel",
				{"bloco": bloco("TM_BLOCO_SEGUROS_MAIS_BUSCADOS")["bloco"]}),
			fragment("tm-bloco", bloco("TM_BLOCO_SUSTENTABILIDADE")))),
	(
		"/seguros", "Seguros",
		lambda: page_definition(
			fragment("tm-bloco", bloco("TM_BLOCO_SEGUROS_TOKIO_MARINE", "hero")),
			fragment("tm-catalogo-seguros"),
			fragment("tm-bloco", bloco("TM_BLOCO_SUSTENTABILIDADE")))),
]


def jsonws(path, **params):
	return lr.post(f"/api/jsonws{path}", data=params)


def main():
	pages = {
		page["friendlyUrlPath"]: page
		for page in lr.get_all(
			f"/o/headless-delivery/v1.0/sites/{lr.SITE_ID}/site-pages")
	}

	for priority, (friendly_url, title, build) in enumerate(PAGES):
		if friendly_url in pages:
			jsonws("/layout/delete-layout", plid=pages[friendly_url]["id"])

			print(f"deleted {friendly_url}")

		page = lr.post(
			f"/o/headless-delivery/v1.0/sites/{lr.SITE_ID}/site-pages",
			{
				"friendlyUrlPath": friendly_url,
				"pageDefinition": build(),
				"title": title,
			})

		jsonws("/layout/update-priority", plid=page["id"], priority=priority)

		print(f"page {friendly_url} -> {page['id']}")


if __name__ == "__main__":
	main()
