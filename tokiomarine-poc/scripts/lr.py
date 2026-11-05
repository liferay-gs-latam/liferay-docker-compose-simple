"""Small helper around the Liferay headless APIs used by the PoC scripts."""

import os
import re
import sys

import requests

HOST = os.environ.get("LR_HOST", "http://dev.tokiomarine:8080")
AUTH = (
	os.environ.get("LR_USER", "test@liferay.com"),
	os.environ.get("LR_PASSWORD", "test"),
)

SITE_ERC = "L_GUEST"
SITE_ID = 34657
SPACE_ERC = "cee3817a-34a5-4fcc-c295-9d5ca14a0d9a"
SPACE_KEY = "Marketing"

_session = requests.Session()
_session.auth = AUTH


def call(method, path, json=None, ok=(200, 201, 204), **kwargs):
	response = _session.request(method, HOST + path, json=json, **kwargs)

	if response.status_code not in ok:
		print(
			f"ERROR {method} {path} -> {response.status_code}\n{response.text[:2000]}",
			file=sys.stderr)

		response.raise_for_status()

	if not response.text:
		return None

	try:
		return response.json()
	except ValueError:
		return response.text


def get(path, **kwargs):
	return call("GET", path, **kwargs)


def get_all(path, page_size=200):
	items = []
	page = 1

	while True:
		separator = "&" if "?" in path else "?"

		data = get(f"{path}{separator}page={page}&pageSize={page_size}")

		items.extend(data["items"])

		if page >= data.get("lastPage", 1):
			return items

		page += 1


def post(path, json=None, **kwargs):
	return call("POST", path, json=json, **kwargs)


def put(path, json=None, **kwargs):
	return call("PUT", path, json=json, **kwargs)


def patch(path, json=None, **kwargs):
	return call("PATCH", path, json=json, **kwargs)


def delete(path, **kwargs):
	return call("DELETE", path, ok=(200, 204, 404), **kwargs)


def portal_session():
	"""Returns (session, p_auth) logged in through the portal login, for
	portlet actions that have no headless API."""

	session = requests.Session()

	def auth_token():
		match = re.search(
			r"authToken: '([^']+)'", session.get(HOST + "/").text)

		return match.group(1)

	session.post(
		f"{HOST}/c/portal/login?p_auth={auth_token()}",
		data={"login": AUTH[0], "password": AUTH[1]})

	return session, auth_token()


def portlet_action(portlet_id, action, data=None, files=None):
	session, p_auth = portal_session()

	namespace = f"_{portlet_id}_"

	response = session.post(
		f"{HOST}/group/guest/~/control_panel/manage",
		data={
			f"{namespace}{key}": value for key, value in (data or {}).items()},
		files={
			f"{namespace}{key}": value
			for key, value in (files or {}).items()
		},
		params={
			f"{namespace}jakarta.portlet.action": action,
			f"{namespace}javax.portlet.action": action,
			"p_auth": p_auth,
			"p_p_id": portlet_id,
			"p_p_lifecycle": "1",
		})

	response.raise_for_status()

	return response
