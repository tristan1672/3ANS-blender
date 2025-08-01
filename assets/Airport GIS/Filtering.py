import re
from qgis.core import QgsProject, QgsLayerTreeLayer, QgsLayerTreeGroup

project = QgsProject.instance()
root = project.layerTreeRoot()

# Updated regex to allow optional _c_ prefix
pattern = re.compile(r'^(_c_)?_T(\d+)(L[A-Za-z0-9]+)_')

# Cache for group references
group_cache = {}

def get_or_create_group(parent: QgsLayerTreeGroup, name: str) -> QgsLayerTreeGroup:
    key = (parent.name(), name)
    if key in group_cache:
        return group_cache[key]

    # Search existing groups
    for child in parent.children():
        if isinstance(child, QgsLayerTreeGroup) and child.name() == name:
            group_cache[key] = child
            return child

    # Create if not found
    group = parent.addGroup(name)
    group_cache[key] = group
    return group

# Collect layers to delete
layers_to_delete = []

for layer in project.mapLayers().values():
    layer_name = layer.name()

    # Skip and mark for deletion if not ending in _4326
    if not layer_name.endswith('_4326'):
        layers_to_delete.append(layer)
        continue

    match = pattern.search(layer_name)
    if not match:
        continue

    t_part = f"T{match.group(2)}"
    l_part = match.group(3)

    main_group = get_or_create_group(root, t_part)
    sub_group = get_or_create_group(main_group, l_part)

    # Find the existing node in the layer tree
    existing_node = root.findLayer(layer.id())
    if existing_node:
        current_parent = existing_node.parent()
        if current_parent != sub_group:
            # Remove from old group and add to correct group
            cloned_node = existing_node.clone()
            current_parent.removeChildNode(existing_node)
            sub_group.insertChildNode(0, cloned_node)

# Actually remove the outdated layers
for layer in layers_to_delete:
    node = root.findLayer(layer.id())
    if node:
        node.parent().removeChildNode(node)
    project.removeMapLayer(layer)

print("✅ Layers moved. ❌ Old layers removed.")
