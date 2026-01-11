# Markdown helpers

import traceback


def mdCallout(type, message, title=None):
    titleInsert = ""
    if title:
        titleInsert = f'title="{title}"'
    return f"""
::: {{.callout-{type} {titleInsert}}}
{message}
:::
"""


def mdCallouts(callouts):
    markdown = ""
    for calloutType, calloutMessage in callouts:
        markdown += mdCallout(calloutType, calloutMessage)
    return markdown


def mdH1(text):
    return f"\n# {text}\n"


def mdH2(text):
    return f"\n## {text}\n"


def mdH3(text):
    return f"\n### {text}\n"


def mdCodeBlock(code, language='default', lineNumbers=False, copyButton=False):
    attribs = ""
    if lineNumbers:
        attribs += ' code-line-numbers="true"'
    if copyButton:
        attribs += ' code-copy="true"'

    return f"\n```{{.{language} {attribs}}}\n{code}\n```\n"
    # return "\n```{." + language + " " + attribs + "}\n{" + code + "}\n```\n"


def mdErrorBlock(error):
    return mdCallout('important', f"Error:\n```\n{error}\n```\n")


def mdErrorTraceback(error):
    trace = traceback.format_exception(type(error), error, error.__traceback__)
    trace = ''.join(trace)
    return mdErrorBlock(trace)


def mdColumns(column1, column2):
    return f"""
:::: {{.columns}}
::: {{.column width="50%"}}
{column1}
:::
::: {{.column width="50%"}}
{column2}
:::
::::
"""


def qmd(markdown, title="AutoGrader Report"):
    return f"""\
---
format:
  html:
    title: {title}
    embed-resources: true
    anchor-sections: false
    toc: true
    toc-expand: 1
    code-fold: true
    code-overflow: wrap
    smooth-scroll: true
    page-layout: full
    fig-align: center
    theme:
      light:
        - sandstone
      dark:
        - darkly
    grid:
      body-width: 1800px
---

{markdown}
"""
