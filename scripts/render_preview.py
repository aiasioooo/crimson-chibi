"""Render the repository front preview from the open .blend file."""

from pathlib import Path
import bpy

project = Path(bpy.data.filepath).resolve().parent
scene = bpy.data.scenes["CRIMSON • Origami Chibi"]
bpy.context.window.scene = scene
scene.camera = bpy.data.objects["Camera • FRONT"]
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.render.resolution_x = 1400
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(project / "renders" / "crimson_chibi_front.png")
bpy.ops.render.render(write_still=True)
