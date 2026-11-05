"""Makes new Marketing space content visible to site visitors.

The CMS keeps default permissions per space (and copies them to each folder
when the folder is created). Adding the Guest role to the defaults means every
entry the Marketing Manager publishes is public, with no manual permission
step. Existing entries are updated too, merging Guest into their current
permissions (PUT /permissions replaces the permissions of all roles).
"""

import json

import lr

GUEST_ACTIONS = {
	"L_CONTENTS": ["VIEW"],
	"L_FILES": ["DOWNLOAD_FILE", "VIEW"],
}

# Repeatable group items are entries of their own, with their own permissions

ENTRY_ENDPOINTS = [
	"/o/cms/basic-documents",
	"/o/c/tmblocoitems",
	"/o/c/tmblocos",
	"/o/c/tmcategorias",
	"/o/c/tmprodutofaqs",
	"/o/c/tmprodutos",
	"/o/c/tmprodutosecaoitems",
	"/o/c/tmprodutosecaos",
	"/o/c/tmprodutotabelalinhas",
	"/o/c/tmprodutotabelas",
]


def update_default_permissions():
	for record in lr.get_all("/o/cms/default-permissions"):
		if record.get("depotGroupId") != 53728:
			continue

		permissions = json.loads(record["defaultPermissions"])

		for key, actions in GUEST_ACTIONS.items():
			permissions.setdefault(key, {})["Guest"] = actions

		lr.patch(
			f"/o/cms/default-permissions/{record['id']}",
			{"defaultPermissions": json.dumps(permissions)})

		print(
			f"default permissions {record['className']} "
			f"{record['classExternalReferenceCode']}")


def grant_guest(path, actions):
	current = lr.get(f"{path}/permissions")["items"]

	merged = [
		{"actionIds": item["actionIds"], "roleName": item["roleName"]}
		for item in current
		if item["roleName"] != "Guest"
	]

	merged.append({"actionIds": actions, "roleName": "Guest"})

	lr.put(f"{path}/permissions", merged)


def update_existing_entries():
	for endpoint in ENTRY_ENDPOINTS:
		actions = GUEST_ACTIONS[
			"L_FILES" if "basic-documents" in endpoint else "L_CONTENTS"]

		for entry in lr.get_all(f"{endpoint}/scopes/{lr.SPACE_KEY}"):
			grant_guest(f"{endpoint}/{entry['id']}", actions)

			print(f"guest {endpoint}/{entry['id']}")


if __name__ == "__main__":
	update_default_permissions()
	update_existing_entries()
