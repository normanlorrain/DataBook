# DataBookBinder

DataBookBinder is a Python (3.6+) CLI application for generating a "project data book" from a collection of Markdown files and PDF documents.

> The project data book is the bound collection of documents which provide the client with a full definition of the 'as built' plant. [(link)](https://books.google.ca/books?id=1ad4NZEz8d8C&lpg=PA116&dq=project%20%22data%20book%22&pg=PA116#v=onepage&q=%22data%20book%22&f=false)

The output is a single PDF with bookmarks, attachements, and watermarks.

## Basic setup

### Install the requirements:
```
$ pip install -r requirements.txt
```

### Install the external tools

* [Pandoc](https://github.com/jgm/pandoc/releases)
* [pdftk (server)](https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/pdftk_server-2.02-win-setup.exe)


## Usage

```
$ python ..\databook.py {input directory} {output pdf file name}
```

## Example

In the doc/ directory of this project, run the application to generate example documentation:
```
$ python ..\databook.py . databookbinder.pdf
```

