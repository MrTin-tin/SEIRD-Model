# Presentation slides

Each module has its own folder with its Beamer frames, a standalone file to preview them, the compiled preview, and only the figures its slides use.

| Folder | Frames | Figures |
|---|---|---|
| `module1/` | Why β(t); published models (text only); phase plane and thresholds (3 frames) | `m1_phase_space.png` (copy of the report figure) |
| `module2/` | R0 and stability; final size; sensitivity (3 frames) | `m2_final_size.png`, `m2_prcc.png` (copies of the report figures) |
| `module5/` | E5 held-out forecast; E7 rolling forecasts; what the PINN adds (3 frames) | `e5_cases.png`, `e5_deaths.png`, `e5_rt.png`, `e7_rolling.png` |

**Preview one module:** compile `moduleN/moduleN_standalone.tex` with pdflatex from inside its folder.

**Main deck:** use the preamble of a standalone file, add `\graphicspath{{module1/}{module2/}{module5/}}`, and `\input{module1/module1_frames}`, `\input{module2/module2_frames}`, `\input{module5/module5_frames}`. Module 1 also needs `\usepackage{tikz}` and `\usetikzlibrary{arrows.meta,positioning}`.

All numbers on the slides come from `report/main.tex` (final Colab run).
