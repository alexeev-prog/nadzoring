#!/usr/bin/env bash

set -e

echo "🔧 Generating API documentation..."

mkdir -p docs/source/api

echo "🧹 Cleaning old API docs..."
rm -f docs/source/api/*.rst

echo "📚 Running sphinx-apidoc..."
sphinx-apidoc \
    -o docs/source/api/ \
    src/nadzoring/ \
    --force \
    --separate \
    --module-first \
    --no-toc \
    --maxdepth 4

cat > docs/source/api/index.rst << 'EOF'
API Reference
=============

.. toctree::
   :maxdepth: 2
   :glob:

   nadzoring*
EOF

echo "✅ API documentation generated successfully!"
