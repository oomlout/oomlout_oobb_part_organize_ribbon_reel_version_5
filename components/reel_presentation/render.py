"""Render the production meshes and assembled instances in Blender's OOBB studio."""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

jobs = json.loads(Path(sys.argv[-1]).read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 12
scene.cycles.use_denoising = True
prefs = bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for device in prefs.devices:
        device.use = device.type == 'OPTIX'
    if any(d.use for d in prefs.devices):
        scene.cycles.device = 'GPU'
except (ValueError, RuntimeError):
    pass
scene.render.film_transparent = True
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "AgX"
scene.world = bpy.data.worlds.new("Soft studio")
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.7
materials = {}
for name, rgb in {"teal":(0,177,183),"black":(32,32,32),"steel":(145,148,150)}.items():
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    srgb = [v/255 for v in rgb]
    bsdf.inputs['Base Color'].default_value = (*[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in srgb],1)
    bsdf.inputs["Metallic"].default_value = 0.68 if name=="steel" else 0
    bsdf.inputs["Roughness"].default_value = 0.4
    materials[name] = material
camera = bpy.data.cameras.new("Orthographic")
cam = bpy.data.objects.new("Camera",camera)
scene.collection.objects.link(cam)
scene.camera = cam
camera.type = "ORTHO"
camera.clip_start = 0.00001
lights = []
for offset,power in [((-2,-3,5),2),((3,-1,3),1),((0,4,4),2)]:
    lamp = bpy.data.lights.new("Softbox","AREA")
    lamp.shape = "DISK"
    obj = bpy.data.objects.new("Softbox",lamp)
    scene.collection.objects.link(obj)
    lights.append((obj,Vector(offset),power))
meshes = {}
for job in jobs:
    rotation = Vector(job["eye"]).to_track_quat("Z","Y")
    objects, points = [], []
    for path,role,xyz,angles in job["objects"]:
        if path not in meshes:
            bpy.ops.wm.stl_import(filepath=path)
            obj = bpy.context.object
            meshes[path] = obj.data
        else:
            obj = bpy.data.objects.new(Path(path).stem,meshes[path])
            scene.collection.objects.link(obj)
        if not obj.data.materials:
            obj.data.materials.append(materials[role])
        obj.scale = (0.001,)*3
        obj.location = Vector(xyz)*0.001
        obj.rotation_euler = [math.radians(v) for v in angles]
        objects.append(obj)
    bpy.context.view_layer.update()
    for obj in objects:
        points.extend(rotation.inverted() @ (obj.matrix_world @ Vector(c)) for c in obj.bound_box)
    lo = Vector([min(p[i] for p in points) for i in range(3)])
    hi = Vector([max(p[i] for p in points) for i in range(3)])
    target = rotation @ ((hi+lo)/2)
    span = max((hi-lo)[:2])
    cam.location = target + rotation @ Vector((0,0,span*6))
    cam.rotation_euler = rotation.to_euler()
    camera.ortho_scale = span*1.1
    for lamp,offset,power in lights:
        lamp.location = target+offset*span
        lamp.rotation_euler = (-offset).to_track_quat("-Z","Y").to_euler()
        lamp.data.energy = power*(span/.1)**2
        lamp.data.size = span*3
    scene.render.resolution_x = scene.render.resolution_y = job.get("size",820)
    scene.render.resolution_percentage = 100
    scene.render.filepath = job["target"]
    bpy.ops.render.render(write_still=True)
    for obj in objects:
        bpy.data.objects.remove(obj,do_unlink=True)

