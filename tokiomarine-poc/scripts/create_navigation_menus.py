"""Creates the site navigation menus read by the header and footer fragments.

The insurance products menu is not here: the header builds it from the CMS
catalog (categories and products), so a new product shows up in the menu as
soon as it is published.
"""

import lr

TM = "https://www.tokiomarine.com.br"


def item(name, link, children=()):
	return {
		"name": name,
		"navigationMenuItems": list(children),
		"type": "url",
		"typeSettings": {"name": name, "url": link, "useNewTab": "false"},
	}


MENUS = {
	"Tokio - Atalhos": [
		item("Portal do Corretor", "https://corretor.tokiomarine.com.br"),
		item("Portal de Parceiros", TM + "/parceiro-de-negocios"),
		item(
			"Portal do Cliente",
			"https://autoatendimento.tokiomarine.com.br/superapp"),
	],
	"Tokio - Canais de Atendimento": [
		item("Fale Conosco", TM + "/fale-conosco"),
		item("Sinistros", TM + "/sinistros"),
		item("Alterações de Cadastro", TM + "/alteracoes-de-cadastro"),
		item("Telefones Úteis", TM + "/telefones-uteis"),
		item("Oficinas e Prestadores", TM + "/localizacoes"),
		item("Chat Online", TM + "/chat-cliente"),
	],
	"Tokio - Rodapé": [
		item(
			"Sobre Nós", "#",
			[
				item("Nossa História", TM + "/empresa/nossa-historia"),
				item("Instituto", "https://instituto.tokiomarine.com.br"),
				item("Sustentabilidade", TM + "/empresa/esg"),
				item("Imprensa", TM + "/sala-de-imprensa"),
				item("Trabalhe Conosco", "https://tokiomarine.gupy.io"),
			]),
		item(
			"Ajuda", "#",
			[
				item("Perguntas Frequentes", TM + "/perguntas-frequentes"),
				item("Canais de Atendimento", TM + "/canais-de-atendimento"),
				item("Ouvidoria", TM + "/ouvidoria"),
				item("Encontrar Corretor", TM + "/localizacoes?categoria=corretores"),
				item("Condições Gerais", TM + "/condicoes-gerais"),
			]),
		item(
			"Blog", "https://newblog.tokiomarine.com.br",
			[
				item("Auto", "https://newblog.tokiomarine.com.br/auto"),
				item("Empresas", "https://newblog.tokiomarine.com.br/empresas"),
				item(
					"Institucional",
					"https://newblog.tokiomarine.com.br/institucional"),
			]),
	],
	"Tokio - Legal": [
		item("Política de Privacidade e Cookies", TM + "/privacidade"),
		item("Mapa do Site", TM + "/mapa-do-site"),
	],
}


def main():
	existing = {
		menu["name"]: menu["id"]
		for menu in lr.get_all(
			f"/o/headless-delivery/v1.0/sites/{lr.SITE_ID}/navigation-menus")
	}

	for name, items in MENUS.items():
		body = {"name": name, "navigationMenuItems": items}

		if name in existing:
			menu = lr.put(
				f"/o/headless-delivery/v1.0/navigation-menus/{existing[name]}",
				body)
		else:
			menu = lr.post(
				f"/o/headless-delivery/v1.0/sites/{lr.SITE_ID}/navigation-menus",
				body)

		print(f"menu {menu['name']} -> {menu['id']}")


if __name__ == "__main__":
	main()
