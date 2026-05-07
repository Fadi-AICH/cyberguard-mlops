# CyberGuard MLOps - Overleaf package

Upload these LaTeX files to Overleaf, and upload the project `screenshots/` folder at the same level as `main.tex`.

Recommended Overleaf structure:

```text
main.tex
preamble.tex
titlepage.tex
references.bib
chapters/
  00_resume.tex
  01_introduction.tex
  ...
  11_conclusion.tex
appendices/
  a_screenshots.tex
  b_commandes.tex
screenshots/
  01_environment_versions.png
  ...
  22_mlflow_run_details_metrics_artifacts.png
  architecture.jpeg
  cover_background.png
  ismagilogo.png
```

Compiler:

- `pdfLaTeX`
- Bibliography tool: `Biber`

Compile order if Overleaf asks:

```text
pdflatex -> biber -> pdflatex -> pdflatex
```

If images are uploaded in a sibling folder instead of inside this report folder, the report also supports `../screenshots/` because `preamble.tex` defines both image paths.
