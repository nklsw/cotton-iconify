# cotton-iconify

CLI tool to generate [iconify](https://iconify.design/) icons as [django-cotton](https://django-cotton.com/) components

Generate full icon-sets or single icons into your Django project as ready-to-use cotton components. See [iconify](https://icon-sets.iconify.design/) for available icons and icon-sets.

## Installation
Install via pip:
```
pip install cotton-iconify
```

Or via uv as development dependency:
```
uv add cotton-iconify --dev
```

## Get started
Generate an icon-set

```
cotton-iconify heroicons
```

Generate a single icon
```
cotton-iconify heroicons:check-circle
```

Use as cotton component in Django templates:
```
<c-heroicons.check-circle />
```

## Usage

By default, icons will be created in the `templates/cotton/<icon_set>` directory with filenames in snake_case, but they are used in Django templates with kebab-case. 
```html
<!-- example output in templates/cotton/heroicons/check_circle.html -->

<c-vars width="1000" height="1000" viewBox="0 0 1000 1000" />

<svg {{ attrs }} xmlns="http://www.w3.org/2000/svg" width="{{ width }}" height="{{ height }}" viewBox="{{ viewBox }}">
  <path fill="currentColor" d="M0 791.667h694.444L1000 208.333H333.334z"/>
</svg>
```

Basic usage in Django templates:
```html
<c-heroicons.check-circle />
```

Pass attributes
```html
<c-heroicons.check-circle class="icon foo" bar />
```

Modify width/height/viewBox attributes of svg:
```html
<c-heroicons.check-circle width="16" height="16" viewBox="0 0 16 16" />
```

### Generation Options
```
usage: cotton-iconify [-h] [--all] [--output OUTPUT] [--source SOURCE] [--force] [--file-prefix FILE_PREFIX] [--kebab] icon_reference

Generate Django component SVG files from Iconify JSON files.

positional arguments:
  icon_reference        Icon set prefix (e.g., "brandico") or full reference with icon (e.g. "brandico:facebook")

options:
  -h, --help            show this help message and exit
  --all, -a             Generate all icons from the set
  --output OUTPUT, -o OUTPUT
                        Output directory for SVG files (if not specified, uses templates/cotton/<icon-set>)
  --source SOURCE, -s SOURCE
                        Source URL for JSON files
  --force, -f           Overwrite existing files without asking
  --file-prefix FILE_PREFIX, -p FILE_PREFIX
                        Prefix to add to generated filenames (e.g., "icon" for icon-name.html)
  --kebab, -k           Use kebab-case for filenames (default is snake_case)
```

#### Specify Output directory
Provide a directory path with -o or --output
```
cotton-iconify heroicons -o templates/cotton/icons
```
Usage in Template:
```
<c-icons.check-circle />
```

#### Use kebab-case filenames (original iconify format)
Use the -k or --kebab flag to generate filenames with hyphens instead of underscores:
```
cotton-iconify heroicons --kebab
```
Usage in Template:
```
<c-heroicons.check-circle />
```

#### Specify prefix for output files
Provide a file prefix with -p or --file-prefix. This option is useful for generating icons from multiple icon-sets into one output folder.
```
cotton-iconify heroicons -p hero -o templates/cotton/icons
```
Usage in Template:
```
<c-icons.hero-check-circle />
```

## Acknowledgement
cotton-iconify is built upon the incredible work of [Iconify](https://iconify.design/) and [django-cotton](https://django-cotton.com/). While cotton-iconify is not officially affiliated with Iconify or django-cotton, we deeply appreciate their contributions to the open-source community, which made this tool possible.

## License
cotton-iconify is licensed under the MIT license.

This license does not apply to icons. Icons are released under different licenses, see each icon set for details.