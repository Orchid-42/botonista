# Edição especial (not in the game yet)

Parked until the first special-edition art is uploaded.

- `Botonista_Edicao_Especial.psd`: artboards `2`–`11` (1024², round face, number painted in) and `GK` (1960×680).
  Export > Artboards to Files with the team prefix, e.g. `FLA_` → `FLA_2.png … FLA_11.png, FLA_GK.png`.
- `Botonista_Caixa_Botoes.glb`: the box model (tray, 10 buttons, keeper, black box). The team frame is drawn in code as a
  cardboard sleeve: team colour (secondary if the main is white), thin tracked team name on top, BOTONISTA below.
- `box_renderer.js`: WebGL renderer for the box with team art, sleeve and materials.
- `unboxing_preview.html`: unlock animation — maple chest with a team-colour inlay stripe and slim brass latch; lid opens,
  camera tilts to a higher view, the team box rises out, confetti in the team colours, caption "Edição especial desbloqueada".
- Plan: special boxes unlock with achievements such as winning a cup with that team; special buttons use the art as painted
  (the game adds no number on top).

## Corinthians (first special edition)
`Botonista_COR_Edicao_Especial.psd`: artboards named by game position (1 = goalkeeper card). Shirt numbers baked in:
1→12, 2→2, 3→13, 4→3, 5→8, 6→6, 7→23, 8→5, 9→9, 10→20, 11→11. Export as `COR_1.png … COR_11.png`.
