#!/usr/bin/env bash
# Download wheel files for requirements.txt into wheelhouse/ using Tsinghua mirror
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
mkdir -p wheelhouse
python3 -m pip download -r requirements.txt -d wheelhouse -i https://pypi.tuna.tsinghua.edu.cn/simple/ --prefer-binary
echo "Downloaded wheels into $REPO_ROOT/wheelhouse"
