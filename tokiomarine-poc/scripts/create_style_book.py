"""Creates the "Tokio Marine" style book and makes it the site default.

Token values come from the current site theme (main-css): primary green
#006551, dark green #004d3a, gold accent #C7800B, Montserrat, 30px pill
buttons and a 1320px container.

Usage: create_style_book.py <frontend-token-definition.json of Classic theme>
"""

import io
import json
import sys
import zipfile

import lr

ERC = "TM_STYLE_BOOK"

VALUES = {
	"bodyColor": "#232a2a",
	"borderRadius": "0.75rem",
	"borderRadiusLg": "1rem",
	"borderRadiusSm": "0.5rem",
	"brandColor1": "#006551",
	"brandColor2": "#C7800B",
	"brandColor3": "#004d3a",
	"brandColor4": "#101828",
	"btnLinkColor": "#006551",
	"btnLinkHoverColor": "#004d3a",
	"btnOutlinePrimaryBorderColor": "#006551",
	"btnOutlinePrimaryColor": "#006551",
	"btnOutlinePrimaryHoverBackgroundColor": "#0065510f",
	"btnOutlinePrimaryHoverBorderColor": "#004d3a",
	"btnOutlinePrimaryHoverColor": "#004d3a",
	"btnPrimaryBackgroundColor": "#006551",
	"btnPrimaryBorderColor": "#006551",
	"btnPrimaryColor": "#fff",
	"btnPrimaryHoverBackgroundColor": "#004d3a",
	"btnPrimaryHoverBorderColor": "#004d3a",
	"btnPrimaryHoverColor": "#fff",
	"btnSecondaryBackgroundColor": "#fff",
	"btnSecondaryBorderColor": "#006551",
	"btnSecondaryColor": "#006551",
	"btnSecondaryHoverBackgroundColor": "#f5f5f5",
	"btnSecondaryHoverBorderColor": "#004d3a",
	"btnSecondaryHoverColor": "#004d3a",
	"containerMaxXl": "1320px",
	"fontFamilyBase": "'Montserrat', system-ui, -apple-system, sans-serif",
	"fontFamilySansSerif": "'Montserrat', system-ui, -apple-system, sans-serif",
	"fontSizeBase": "1rem",
	"fontSizeLg": "1.125rem",
	"fontSizeSm": "0.875rem",
	"h1FontSize": "2.75rem",
	"h2FontSize": "2rem",
	"h3FontSize": "1.25rem",
	"h4FontSize": "1.125rem",
	"lightColor": "#f5f5f5",
	"lighterColor": "#f7f7f7",
	"primaryColor": "#006551",
	"secondaryColor": "#C7800B",
	"textMuted": "#849394",
}


def css_variable_mappings(definition_path):
	with open(definition_path, encoding="utf-8") as file:
		definition = json.load(file)

	mappings = {}

	for category in definition["frontendTokenCategories"]:
		for token_set in category["frontendTokenSets"]:
			for token in token_set["frontendTokens"]:
				for mapping in token.get("mappings", []):
					if mapping["type"] == "cssVariable":
						mappings[token["name"]] = mapping["value"]

	return mappings


def main(definition_path):
	mappings = css_variable_mappings(definition_path)

	values = {
		name: {"cssVariableMapping": mappings[name], "value": value}
		for name, value in VALUES.items()
	}

	# The style book headless API is behind feature flag LPD-56718, so the
	# style book is imported as a ZIP, like the Style Books admin does

	buffer = io.BytesIO()

	with zipfile.ZipFile(buffer, "w") as zip_file:
		zip_file.writestr(
			"tokio-marine/style-book.json",
			json.dumps(
				{
					"defaultStyleBookEntry": True,
					"frontendTokensValuesPath": "frontend-tokens-values.json",
					"name": "Tokio Marine",
					"themeId": "classic_WAR_classictheme",
				}))
		zip_file.writestr(
			"tokio-marine/frontend-tokens-values.json", json.dumps(values))

	lr.portlet_action(
		"com_liferay_style_book_web_internal_portlet_StyleBookPortlet",
		"/style_book/import_style_book_entries", data={"overwrite": "true"},
		files={"file": ("tokio-marine-style-book.zip", buffer.getvalue())})

	print("style book Tokio Marine imported")


if __name__ == "__main__":
	main(sys.argv[1])
