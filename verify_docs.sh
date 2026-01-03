#!/bin/bash
# Documentation Verification Script
# Verifies that all documentation is present and accessible

echo "=========================================="
echo "Documentation Verification"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "ERROR: Please run this script from the test-gui directory"
    exit 1
fi

echo "✓ Running from project root"
echo ""

# Check documentation files
echo "Checking documentation files..."
docs=(
    "README.md"
    "PROJECT_STATUS.md"
    "CHANGELOG.md"
    "PHASE_7_SUMMARY.md"
    "QUICK_REFERENCE.md"
    "docs/index.html"
    "docs/THEORY.md"
    "docs/TUTORIAL.md"
    "docs/PLATFORM_GUIDE.md"
)

missing=0
for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        size=$(stat -f%z "$doc" 2>/dev/null || stat -c%s "$doc" 2>/dev/null)
        echo "  ✓ $doc (${size} bytes)"
    else
        echo "  ✗ $doc - MISSING"
        missing=$((missing + 1))
    fi
done

echo ""

if [ $missing -gt 0 ]; then
    echo "ERROR: $missing documentation file(s) missing"
    exit 1
fi

echo "✓ All documentation files present"
echo ""

# Check for HTTP server
echo "Checking documentation server..."
if lsof -i :8000 >/dev/null 2>&1; then
    echo "  ✓ HTTP server running on port 8000"

    # Test accessibility
    if curl -s http://localhost:8000/ | head -1 | grep -q "<!DOCTYPE html>"; then
        echo "  ✓ Website accessible at http://localhost:8000/"
    else
        echo "  ✗ Website not responding correctly"
        exit 1
    fi

    # Test THEORY.md
    if curl -s http://localhost:8000/THEORY.md | head -1 | grep -q "# Test Bench"; then
        echo "  ✓ THEORY.md accessible"
    else
        echo "  ✗ THEORY.md not accessible"
        exit 1
    fi
else
    echo "  ℹ HTTP server not running"
    echo "  Start with: cd docs && python3 -m http.server 8000"
fi

echo ""

# Check for LaTeX equations in THEORY.md
echo "Checking LaTeX equations..."
latex_count=$(grep -c '\$\$' docs/THEORY.md)
if [ $latex_count -gt 0 ]; then
    echo "  ✓ Found $latex_count LaTeX equation delimiters in THEORY.md"
else
    echo "  ✗ No LaTeX equations found"
    exit 1
fi

echo ""

# Check MathJax configuration in index.html
echo "Checking MathJax configuration..."
if grep -q "MathJax" docs/index.html && grep -q "tex-svg.js" docs/index.html; then
    echo "  ✓ MathJax library configured in index.html"
else
    echo "  ✗ MathJax not properly configured"
    exit 1
fi

echo ""

# Summary
echo "=========================================="
echo "✅ Documentation verification complete!"
echo "=========================================="
echo ""
echo "Documentation website: http://localhost:8000/index.html"
echo "README: README.md"
echo "Project Status: PROJECT_STATUS.md"
echo "Quick Reference: QUICK_REFERENCE.md"
echo ""
echo "All systems ready! ✨"
