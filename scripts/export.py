"""Export the character and its twelve components from the open .blend file."""

from pathlib import Path
import json
import bpy

PROJECT = Path(bpy.data.filepath).resolve().parent
ROOT_NAME = "CRIMSON • character root"


def descendants(obj):
    for child in obj.children:
        yield child
        yield from descendants(child)


def export(path, objects):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
    )
    print(f"Exported {path}")


root = bpy.data.objects.get(ROOT_NAME)
if root is None:
    raise RuntimeError(f"Missing object: {ROOT_NAME}")

main_scene = next((scene for scene in bpy.data.scenes if root.name in scene.objects), None)
if main_scene is None:
    raise RuntimeError(f"{ROOT_NAME} is not linked to a scene")
bpy.context.window.scene = main_scene

controllers = {obj.name: obj for obj in root.children if obj.name.startswith("PART • ")}
if len(controllers) != 12:
    raise RuntimeError(f"Expected 12 PART controllers, found {len(controllers)}")

export(PROJECT / "crimson_chibi.glb", [root, *descendants(root)])

components = json.loads((PROJECT / "parts" / "components.json").read_text(encoding="utf-8"))
if len(components) != 12:
    raise RuntimeError(f"Expected 12 manifest entries, found {len(components)}")
component_meshes = set()
for component in components:
    controller = controllers.get(component["controller"])
    if controller is None:
        raise RuntimeError(f"Missing controller: {component['controller']}")
    meshes = sorted((obj for obj in controller.children if obj.type == "MESH"), key=lambda obj: obj.name)
    if not meshes:
        raise RuntimeError(f"Empty component: {component['id']}")
    component["mesh_count"] = len(meshes)
    component["meshes"] = [obj.name for obj in meshes]
    component_meshes.update(meshes)
    path = PROJECT / component["export"]
    path.parent.mkdir(parents=True, exist_ok=True)
    export(path, [controller, *meshes])

all_meshes = {obj for obj in descendants(root) if obj.type == "MESH"}
if component_meshes != all_meshes:
    raise RuntimeError("Some character meshes are missing from the components")
(PROJECT / "parts" / "components.json").write_text(
    json.dumps(components, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
bpy.ops.object.select_all(action="DESELECT")
