# Documentation Guide

This guide explains how to view and work with the Test Bench GUI documentation.

---

## 📖 Viewing Documentation

### Option 1: GitHub Pages (Recommended)

The documentation is automatically deployed and available online:

**Live Documentation**: https://anandvks.github.io/test-hub/

- No installation required
- Always up-to-date with the `main` branch
- Professional MkDocs Material theme
- Dark/light mode support
- Full search functionality

### Option 2: Local Development Server

For editing or previewing documentation locally:

#### Prerequisites

```bash
# Install MkDocs and Material theme
pip install mkdocs mkdocs-material
```

#### Serve Locally

```bash
# Start development server
mkdocs serve

# Server will start at http://127.0.0.1:8000/
# Documentation auto-reloads when you edit files
```

Open your browser and navigate to: **http://127.0.0.1:8000/**

### Option 3: Build Static Site

Build the documentation as static HTML files:

```bash
# Build site to site/ directory
mkdocs build

# Output will be in site/
# Open site/index.html in your browser
```

---

## 📝 Editing Documentation

### Documentation Structure

```
docs/
├── index.md                      # Homepage
├── getting-started/
│   ├── quick-start.md           # Quick start guide
│   └── installation.md          # Installation instructions
├── user-guide/
│   ├── tutorial.md              # Complete tutorial
│   ├── hardware-setup.md        # Hardware setup guide
│   └── gui-overview.md          # GUI documentation
├── technical/
│   ├── theory.md                # Engineering theory
│   ├── platform-guide.md        # Platform porting guide
│   └── test-protocols.md        # Test protocol details
├── development/
│   ├── contributing.md          # Contribution guidelines
│   ├── testing.md               # Testing guide
│   └── api.md                   # API reference
└── about/
    ├── changelog.md             # Version history
    └── license.md               # License information
```

### Making Changes

1. **Edit markdown files** in `docs/` directory
2. **Preview changes** with `mkdocs serve`
3. **Commit changes** to git
4. **Deploy** (see below)

### Markdown Features

MkDocs supports extended markdown:

#### Code Blocks

```python
def example():
    """Example code with syntax highlighting."""
    return "Hello, World!"
```

#### Admonitions

```markdown
!!! note "Note Title"
    This is a note block

!!! warning "Warning"
    This is a warning block

!!! tip "Pro Tip"
    This is a tip block
```

#### Tabbed Content

```markdown
=== "Python"
    ```python
    print("Hello")
    ```

=== "Bash"
    ```bash
    echo "Hello"
    ```
```

#### Math Equations

```markdown
$$
E = mc^2
$$

Inline math: $F = ma$
```

---

## 🚀 Deploying Documentation

### Automatic Deployment

Documentation is automatically deployed when you push to the `main` branch:

```bash
git add docs/
git commit -m "Update documentation"
git push origin main
```

GitHub Pages will rebuild and deploy automatically.

### Manual Deployment

To manually deploy documentation to GitHub Pages:

```bash
# Build and deploy to gh-pages branch
mkdocs gh-deploy

# With force update (overwrites gh-pages branch)
mkdocs gh-deploy --force
```

This command:
1. Builds the documentation
2. Pushes to `gh-pages` branch
3. Updates GitHub Pages automatically

---

## 🛠️ Configuration

### mkdocs.yml

Main configuration file for MkDocs:

```yaml
site_name: Test Bench GUI
site_url: https://anandvks.github.io/test-hub/

theme:
  name: material
  palette:
    - scheme: default      # Light mode
    - scheme: slate        # Dark mode
  features:
    - navigation.instant
    - navigation.tabs
    - search.suggest
    - content.code.copy

nav:
  - Home: index.md
  - Getting Started: ...
  - User Guide: ...
```

### Adding New Pages

1. **Create markdown file** in appropriate `docs/` subdirectory
2. **Add to navigation** in `mkdocs.yml`:

```yaml
nav:
  - Home: index.md
  - Your Section:
      - New Page: section/new-page.md
```

3. **Preview** with `mkdocs serve`
4. **Deploy** with `mkdocs gh-deploy`

---

## 🔍 Search Functionality

Search is automatically enabled and indexes:
- All page titles
- All headings
- All content text

No configuration needed - just start typing in the search box!

---

## 📱 Responsive Design

The documentation automatically adapts to:
- **Desktop** - Full navigation sidebar
- **Tablet** - Collapsible navigation
- **Mobile** - Hamburger menu

---

## 🎨 Theme Customization

### Colors

Edit `mkdocs.yml` to change colors:

```yaml
theme:
  palette:
    primary: blue        # Header color
    accent: light blue   # Link color
```

Available colors: red, pink, purple, deep purple, indigo, blue, light blue, cyan, teal, green, light green, lime, yellow, amber, orange, deep orange

### Features

Enable/disable features in `mkdocs.yml`:

```yaml
theme:
  features:
    - navigation.instant  # Instant loading
    - navigation.tabs     # Top-level tabs
    - navigation.sections # Expandable sections
    - navigation.expand   # Expand all sections
    - navigation.top      # Back to top button
    - search.suggest      # Search suggestions
    - search.highlight    # Highlight search terms
    - content.code.copy   # Copy code button
```

---

## 🐛 Troubleshooting

### "mkdocs: command not found"

```bash
# Install MkDocs
pip install mkdocs mkdocs-material
```

### "WARNING: Excluding 'index.html'"

This is normal - `docs/index.html` conflicts with `docs/index.md` and is ignored.

### Broken Links

Run the build to check for broken links:

```bash
mkdocs build --strict
```

This will fail if there are any broken internal links.

### Port Already in Use

If port 8000 is already in use:

```bash
# Use different port
mkdocs serve --dev-addr=127.0.0.1:8001
```

---

## 📚 Resources

- **MkDocs Documentation**: https://www.mkdocs.org/
- **Material Theme**: https://squidfunk.github.io/mkdocs-material/
- **Markdown Guide**: https://www.markdownguide.org/
- **Live Site**: https://anandvks.github.io/test-hub/

---

## 🤝 Contributing to Docs

See [Contributing Guide](docs/development/contributing.md) for:
- Documentation style guide
- Writing guidelines
- Review process

---

## 📞 Support

For documentation issues:
- Open an issue on GitHub
- Check existing documentation
- Review MkDocs Material documentation
