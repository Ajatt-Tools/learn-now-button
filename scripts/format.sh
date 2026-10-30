#!/bin/bash

set -euo pipefail

ROOT_DIR=$(git rev-parse --show-toplevel)
readonly ROOT_DIR

# Share Python scope between check and fix modes, excluding generated and third-party code.
# Adapted from https://github.com/Ajatt-Tools/mergenotes/blob/b83f34948238a79e8f7f08c3a1a256c0f51908d6/scripts/format.sh
"$ROOT_DIR/card_management/ajt_common/format.sh" \
	--include card_management \
	--include tests \
	--include playground \
	--exclude card_management/__about__.py \
	--exclude card_management/ajt_common \
	"$@"
