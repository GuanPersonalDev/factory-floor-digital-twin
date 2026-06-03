import omni.kit.commands
import omni.usd
import omni.kit.viewport.utility
from pxr import UsdGeom, Usd

def jump_to_prim(prim_path: str) -> bool:
    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.IsValid():
        return False

    viewport_api = omni.kit.viewport.utility.get_active_viewport()
    resolution = viewport_api.resolution

    
    omni.kit.commands.execute(
        "FramePrimsCommand",
        prim_to_move=viewport_api.camera_path,
        prims_to_frame=[prim_path],
        time_code=viewport_api.time,
        usd_context_name=viewport_api.usd_context_name,
        aspect_ratio=resolution[0] / resolution[1],
    )
    return True