#!/bin/bash
# Packages tokiomarine-poc/fragments (fragments, master page, display page
# templates) and drops it in the Liferay auto-deploy folder, then waits for
# the deploy result in the container log.

set -e

POC_DIR=$(cd "$(dirname "$0")/.." && pwd)
DEPLOY_DIR="$POC_DIR/../liferay-deploy"
CONTAINER=${LIFERAY_CONTAINER:-liferay-docker-compose-simple-liferay-1}
ZIP_NAME=tokiomarine-poc.zip

TMP_ZIP=$(mktemp -u --suffix=.zip)

(cd "$POC_DIR/fragments" && zip -q -r "$TMP_ZIP" .)

SINCE=$(date +%s)

cp "$TMP_ZIP" "$DEPLOY_DIR/$ZIP_NAME"
rm -f "$TMP_ZIP"

for _ in $(seq 1 60); do
	LOG=$(docker logs --since "$SINCE" "$CONTAINER" 2>&1 | grep -E "$ZIP_NAME|FragmentFileInstaller|LayoutsImporter" || true)

	if echo "$LOG" | grep -qE "Deployed $ZIP_NAME|Unable to deploy|rror"; then
		echo "$LOG" | tail -5

		docker logs --since "$SINCE" "$CONTAINER" 2>&1 | grep -E "WARN|ERROR" | grep -iE "fragment|layout|import" | tail -10 || true

		exit 0
	fi

	sleep 3
done

echo "Timed out waiting for $ZIP_NAME deploy"

exit 1
