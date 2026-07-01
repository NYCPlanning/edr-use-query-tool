#!/bin/bash
#
# Build the WASM app (marimo -> static site) for local preview or deployment.
# Runs the marimo export, then post-processes the output (see patch_wasm_site.py).
# Used both locally and by CI (.github/workflows/deploy.yml) so the deployed site
# and what you preview locally are built the same way.
#
# Usage:
#   ./build_site.sh [OUTPUT_DIR]        # default OUTPUT_DIR: _site_directory
#   python -m http.server --directory _site_directory   # then preview
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${1:-_site_directory}"

echo "📄 Exporting WASM app to ${OUTPUT_DIR}"
uvx --verbose marimo export html-wasm --mode run query_app.py --output "${OUTPUT_DIR}"

echo "🔕 Post-processing (disable browser notifications)"
python3 "${SCRIPT_DIR}/patch_wasm_site.py" "${OUTPUT_DIR}"

echo "✅ Build complete: ${OUTPUT_DIR}"
echo "   Preview with: python -m http.server --directory ${OUTPUT_DIR}"
