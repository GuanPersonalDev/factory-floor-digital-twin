from pxr import Usd, UsdShade, Sdf, Gf

def createMaterial(stage: Usd.Stage, material_root_path: str, material_name: str, color: tuple[float, float, float, float]) -> UsdShade.Material:
    mat_path = f"{material_root_path}/{material_name}"
    material = UsdShade.Material.Define(stage, mat_path)

    shader_path = f"{mat_path}/Shader"
    shader = UsdShade.Shader.Define(stage, shader_path)
    shader.CreateIdAttr("UsdPreviewSurface")

    diffuse_color = (color[0], color[1], color[2])
    opacity = color[3]
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*diffuse_color))
    shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(opacity)

    material.CreateSurfaceOutput().ConnectToSource(
        shader.ConnectableAPI(), "surface"
    )
    return material

def removeMaterial(stage: Usd.Stage, material_root_path: str):
    material_root = stage.GetPrimAtPath(material_root_path)
    if material_root.IsValid():
        stage.RemovePrim(material_root_path)
