from qgis import processing
from qgis.core import QgsProject, QgsPointXY, QgsCoordinateTransform, QgsCoordinateReferenceSystem

rotation_deg = -67.08  # clockwise fix
center_lon = 103.9860286
center_lat = 1.3613794

project = QgsProject.instance()
wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")

for layer in project.mapLayers().values():
    if layer.type() == layer.VectorLayer:
        # Transform rotation center to layer CRS
        transform = QgsCoordinateTransform(wgs84, layer.crs(), project)
        center_point = transform.transform(QgsPointXY(center_lon, center_lat))

        # Fix invalid geometries in-memory
        fixed_layer = processing.run(
            "native:fixgeometries",
            {"INPUT": layer, "OUTPUT": "memory:"}
        )["OUTPUT"]

        output_path = rf"C:\Users\tqwda\OneDrive\Desktop\3ANS-blender\assets\Airport_QGIS_Rotated\{layer.name()}_rotated.shp"

        params = {
            "INPUT": fixed_layer,
            "ANGLE": rotation_deg,              # rotation angle in degrees
            "ANCHOR": f"{center_point.x()},{center_point.y()}",  # rotation center
            "OUTPUT": output_path
        }

        processing.run("native:rotatefeatures", params)
        print(f"Rotated {layer.name()} → {output_path}")
