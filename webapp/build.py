"""
Build the pages that compare each example with its vignette. It is run by Quarto
before each render (`pre-render` in `_quarto.yml`), and writes two files:

    webapp/index.qmd    Every model: the original and the Starsim version side by side
    _scorecard.md       One row per model: lines of code, run time, and agreement

Both are made from `examples/<framework>/<model>` and `vignettes/<framework>/<model>`,
so neither is edited by hand or committed.

    python webapp/build.py
"""
import os
import re
import sciris as sc

root = sc.thispath(__file__).parent
skip = ['.xlsx', '.pyc', '.ipynb', '.gz'] # Not shown: binary files, and notebooks that are also there as a script
languages = {'.py':'python', '.R':'r', '.yaml':'yaml', '.yml':'yaml'} # Anything else is shown as plain text
header = '''---
title: "Compare models"
page-layout: full
toc: false
include-after-body: _picker.html
---

Each model in [examples](/examples/index.qmd) as its framework's authors wrote it, next to its translation in [vignettes](/vignettes/README.md). Pick a model:
'''


def read(path):
    """ Read a text file, without the newline at the end """
    return sc.loadtext(path).rstrip('\n')


def code_files(folder, exclude=()):
    """ The source files in a folder and its subfolders, as paths relative to it, with those at the top first """
    paths = []
    for path in sc.getfilelist(folder, recursive=True, nopath=False):
        path = sc.path(path)
        if path.is_file() and path.suffix not in skip and path.name not in exclude and '__pycache__' not in path.parts:
            paths.append(path.relative_to(folder))
    return sorted(paths, key=lambda path: (len(path.parts), str(path)))


def code_block(path):
    """ A file as a fenced code block (with tildes, since the file may contain backticks) """
    lang = languages.get(path.suffix, 'default')
    return f'~~~~~{{.{lang}}}\n{read(path)}\n~~~~~'


def code_pane(title, folder, files):
    """ One side of the comparison: a single file, or a tab for each of several """
    out = [f'::::: {{.pane}}\n\n**{title}**\n']
    if len(files) == 1:
        out += [f'`{files[0]}`\n', code_block(folder / files[0])]
    elif len(files) > 1:
        out += [':::::: {.panel-tabset}\n']
        for file in files:
            out += [f'#### {file.name}\n', code_block(folder / file), '']
        out += ['::::::']
    else:
        out += ['*Not written yet.*']
    out += ['\n:::::']
    return '\n'.join(out)


def fix_links(text, folder):
    """ Make the relative links in a file from another folder work from anywhere in the site """
    def fix(match):
        target, hash, anchor = match.group(1).partition('#')
        if not target or target.startswith(('http', 'mailto:', '/')):
            return match.group(0)
        path = os.path.normpath(folder / target)
        if os.path.isdir(path):
            path = os.path.join(path, 'README.md')
        return f'](/{os.path.relpath(path, root)}{hash}{anchor})'
    return re.sub(r'\]\(([^)\s]+)\)', fix, text)


def sections(text):
    """ Split a Markdown file into its title, its opening text, and `{heading: text}` for each second-level section """
    parts = re.split(r'^## +(.*)$', text, flags=re.MULTILINE)
    title, hash, intro = parts[0].partition('# ')[2].partition('\n')
    body = {heading.strip(): content.strip() for heading, content in zip(parts[1::2], parts[2::2])}
    return title.strip(), intro.strip(), body


def table_rows(text):
    """ The rows of the first Markdown table in a text, as lists of cells, without the header """
    rows = [line.strip().strip('|').split('|') for line in text.splitlines() if line.startswith('|')]
    return [[cell.strip() for cell in row] for row in rows[2:]]


def load_model(folder):
    """ Everything known about one example and its vignette """
    meta = sc.objdict(sc.loadyaml(folder / 'meta.yaml'))
    key = f"{folder.parent.name}/{folder.name}"
    vfolder = root / 'vignettes' / key
    title, intro, body = sections(read(folder / 'README.md'))
    vtitle, vintro, vbody = sections(fix_links(read(vfolder / 'README.md'), vfolder))
    model = sc.objdict(
        key      = key,
        id       = 'm-' + key.replace('/', '-'),
        meta     = meta,
        title    = title,
        intro    = intro.split('\n\n')[0],
        vintro   = vintro,
        table    = vbody.pop('Comparison', ''),
        notes    = vbody,
        folder   = folder / 'original',
        vfolder  = vfolder,
        original = code_files(folder / 'original'),
        starsim  = code_files(vfolder, exclude=['README.md', 'compare.py']),
    )
    return model


def model_page(model):
    """ The section of the page for one model """
    meta = model.meta
    source = re.sub(r'(https?://[^\s,)]+)', r'<\1>', str(meta.source))
    out = [
        f'::: {{#{model.id} .model}}\n',
        f'## {model.title}\n',
        f'{model.intro}\n',
        f'- **Framework:** {meta.framework} {meta.version} ({meta.license})',
        f'- **Language:** {meta.language}',
        f'- **Source:** {source}',
        f'- **Full detail:** [the example](/examples/{model.key}/README.md) and [the vignette](/vignettes/{model.key}/README.md)\n',
    ]
    if model.table:
        out += [model.table, '']
    else: # There is no comparison yet, so say why
        out += [model.vintro.split('\n\n')[0].partition('. ')[2], '']
    out += [
        ':::: {.compare}\n',
        code_pane(f'Original ({meta.framework})', model.folder, model.original), '',
        code_pane('Starsim', model.vfolder, model.starsim), '',
        '::::\n',
    ]
    for heading, text in model.notes.items():
        out += [f'### {heading}\n', text, '']
    out += [':::\n']
    return '\n'.join(out)


def scorecard_row(model):
    """ The row of the scorecard for one model: lines, time, and whether the results agree """
    link = f'[{model.meta.framework}: {model.folder.parent.name}](/webapp/index.qmd#{model.id})'
    rows = table_rows(model.table)
    if not rows:
        return f'| {link} | {model.meta.language} | | *Not written yet* | | | |'
    lines, time = rows[0], rows[1]
    results = '; '.join(row[3] for row in rows[2:])
    return f'| {link} | {model.meta.language} | {lines[1]} | {lines[2]} | {time[1]} | {time[2]} | {results} |'


if __name__ == '__main__':
    folders = sorted(path.parent for path in (root / 'examples').glob('*/*/meta.yaml'))
    models = [load_model(folder) for folder in folders]

    picker = ' '.join(f'[{model.meta.framework}]({"#" + model.id}){{.model-link}}' for model in models)
    page = [header, f'::: {{.model-picker}}\n{picker}\n:::\n'] + [model_page(model) for model in models]
    sc.savetext(root / 'webapp' / 'index.qmd', '\n'.join(page))

    scorecard = [
        '| Model | Language | Lines: original | Lines: Starsim | Time: original | Time: Starsim | Results |',
        '|---|---|---|---|---|---|---|',
    ] + [scorecard_row(model) for model in models]
    sc.savetext(root / '_scorecard.md', '\n'.join(scorecard) + '\n')

    print(f'Wrote webapp/index.qmd and _scorecard.md for {len(models)} models')
