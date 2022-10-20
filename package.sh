#!/usr/bin/env bash

readonly ADDON_NAME=learn_now
readonly ROOT_DIR=$(git rev-parse --show-toplevel)
readonly BRANCH=$(git branch --show-current)
readonly ZIP_NAME=${ADDON_NAME}_${BRANCH}.ankiaddon

cd -- "$ROOT_DIR" || exit 1

export ROOT_DIR BRANCH

git archive "$BRANCH" --format=zip --output "$ZIP_NAME"

# shellcheck disable=SC2016
git submodule foreach 'git archive main --prefix=$path/ --format=zip --output "$ROOT_DIR/${path}_${BRANCH}.zip"'

zipmerge "$ZIP_NAME" ./*.zip
rm -- ./*.zip
