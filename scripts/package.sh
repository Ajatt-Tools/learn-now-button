#!/bin/bash

set -euo pipefail

./card_management/ajt_common/package.sh \
	--package "Card Management" \
	--name "AJT Card Management" \
	--root "card_management" \
	"$@"
