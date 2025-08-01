import processing
from qgis.core import QgsProject, QgsCoordinateReferenceSystem

# === CONFIG ===
group_name = "BM (visible layers)"
output_crs = "EPSG:4326"

# Use the correct method to find group
layer_tree = QgsProject.instance().layerTreeRoot()
target_group = layer_tree.findGroup(group_name)

if target_group is None:
    print(f"Group '{group_name}' not found.")
else:
    for node in target_group.children():
        if not hasattr(node, "layer") or node.layer() is None:
            continue

        layer = node.layer()
        if not layer.isValid():
            continue

        output_path = rf"C:\Users\tqwda\OneDrive\Desktop\3ANS-blender\assets\Airport GIS\{layer.name()}_4326.shp"

        # Run reprojection
        params = {
            "INPUT": layer,
            "TARGET_CRS": QgsCoordinateReferenceSystem(output_crs),
            "OUTPUT": output_path
        }
        result = processing.run("native:reprojectlayer", params)

        # Load and name the reprojected layer
        output_path = result["OUTPUT"]
        output_layer = QgsVectorLayer(output_path, f"{layer.name()}_4326", "ogr")
        if output_layer.isValid():
            QgsProject.instance().addMapLayer(output_layer)
            print(f"Reprojected and added: {layer.name()}")
        else:
            print(f"Failed to load reprojected layer for: {layer.name()}")
