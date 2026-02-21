#!/bin/bash

set -euo pipefail

readonly ROOT_DIR=$(git rev-parse --show-toplevel)

"$ROOT_DIR/card_management/ajt_common/format.sh" \
	--include card_management \
	--include tests \
	--exclude card_management/ajt_common
