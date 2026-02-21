# mdpi-2026_research-paper
Research paper for MDPI 2026 Publisher

## Description
This paper is formatted according to official TeX/LaTeX template from [Overleaf](https://www.overleaf.com/latex/templates/mdpi-article-template/fcpwsspfzsph) and [MDPI guidelines](https://www.mdpi.com/authors).

## Build from source
We are using Python scripts to build from source for conveniece rather than using Makefiles
```
docker build ... # prepare container with necessary utilities
python3 ./scripts/make.py -h # cli tool to build documents from TeX/LaTeX files and make other support operations
```
