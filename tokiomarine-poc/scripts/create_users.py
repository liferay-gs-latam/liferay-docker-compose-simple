"""Creates the two PoC personas and their roles.

- Frontend Developer: builds fragments, structures, master pages, display page
  templates, style books and pages. Site Administrator of the site and CMS
  Administrator (content structures).
- Marketing Manager: manages product content and images. Member of the
  Marketing space with the Asset Library Content Reviewer role; no access to
  the site design.

The "Frontend Developer" and "Marketing Manager" regular roles identify the
personas; their permissions come from the out-of-the-box site/space roles.
"""

import lr

SPACE_GROUP_ID = 53728

USERS = [
	{
		"email": "frontend@tokiomarine.com.br",
		"familyName": "Developer",
		"givenName": "Frontend",
		"regular_roles": ["Frontend Developer", "CMS Administrator"],
		"scoped_roles": [("Site Administrator", lr.SITE_ID)],
		"screenName": "frontend",
	},
	{
		"email": "marketing@tokiomarine.com.br",
		"familyName": "Manager",
		"givenName": "Marketing",
		"regular_roles": ["Marketing Manager"],
		"scoped_roles": [("Asset Library Content Reviewer", SPACE_GROUP_ID)],
		"screenName": "marketing",
	},
]


def roles_by_name():
	return {
		role["name"]: role["id"]
		for role in lr.get_all("/o/headless-admin-user/v1.0/roles")
	}


def user_id(spec):
	users = lr.get(
		"/o/headless-admin-user/v1.0/user-accounts?filter=emailAddress%20eq%20"
		f"'{spec['email']}'")["items"]

	if users:
		return users[0]["id"]

	user = lr.post(
		"/o/headless-admin-user/v1.0/user-accounts",
		{
			"alternateName": spec["screenName"],
			"emailAddress": spec["email"],
			"familyName": spec["familyName"],
			"givenName": spec["givenName"],
			"password": "test",
		})

	return user["id"]


def main():
	roles = roles_by_name()

	for spec in USERS:
		uid = user_id(spec)

		for role in spec["regular_roles"]:
			lr.call(
				"POST",
				f"/o/headless-admin-user/v1.0/roles/{roles[role]}/association/"
				f"user-account/{uid}",
				ok=(200, 204, 409))

		for role, group_id in spec["scoped_roles"]:

			# Site and space roles require membership of the group

			lr.post(
				"/api/jsonws/user/add-group-users",
				data={"groupId": group_id, "userIds": f"[{uid}]"})

			# The headless site role association rejects space (depot) roles

			lr.post(
				"/api/jsonws/usergrouprole/add-user-group-roles",
				data={
					"groupId": group_id,
					"roleIds": f"[{roles[role]}]",
					"userId": uid,
				})

		print(f"user {spec['email']} -> {uid}")


if __name__ == "__main__":
	main()
