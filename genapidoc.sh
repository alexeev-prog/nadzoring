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

if [ -f docs/source/api/modules.rst ]; then
    echo "📝 Keeping modules.rst"
fi

cat > docs/source/api/index.rst << EOF
API Reference
=============

This section contains automatically generated API documentation from docstrings.

.. toctree::
   :maxdepth: 2
   :glob:

   modules
   nadzoring*
EOF

echo "✅ API documentation generated successfully!"
echo ""
echo "Next steps:"
echo "  - Run 'make html' in docs/ directory to build HTML"
echo "  - Or use 'sphinx-build -b html docs/source docs/build'"
