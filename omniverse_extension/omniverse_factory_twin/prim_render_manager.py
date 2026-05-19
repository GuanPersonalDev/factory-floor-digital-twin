# sys and config
import sys
from pathlib import Path 
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent)) # add root to Python search path due to I wanna load config.config_loader
from config.config_loader import FactoryConfig

# omniverse lib
import omni.kit.app
from pxr import Sdf, Usd, UsdShade
import omni.usd

# tools
from omniverse_extension.tool.debug import DebugLogger
from omniverse_extension.tool.generate_material import create_material, remove_material

# factory project
from .factory_log import FactoryLog
from .model.machine_model import MachineModel



class PrimRenderManager:
    MATERIAL_ROOT = "/World/StatusMaterials"
    def __init__(self, config: FactoryConfig):
        self._material_map: dict[tuple, UsdShade.Material] = {}
        self._collection_map: dict[str, Usd.CollectionAPI] = {}
        self._logger = DebugLogger()
        self._config = config
        self._logger.enable = config.ENABLE_LOG
        self.is_building = False

    def init_source(self):
        self.is_building = True
        stage = omni.usd.get_context().get_stage()
        remove_material(stage, self.MATERIAL_ROOT)
        self._material_map = {}
        self._collection_map = {}

        try:
            self.build_materials()
            self._logger.log(f"[Factory Twin] Material map count: {len(self._material_map)}")
            self.build_collections()
            self._logger.log(f"[Factory Twin] Collection map count: {len(self._collection_map)}")
        finally:
            self.is_building = False

    def build_materials(self):
        stage = omni.usd.get_context().get_stage()
        self._logger.log(f"[Factory Twin] building materials stage: {stage}")

        for operation_mode in self._config.operation_mode:
            for severity in self._config.severity_keys:
                color = self._config.resolve_color(operation_mode, severity)
                if color in self._material_map:
                    continue
                mat_name = f"Mat_{operation_mode}_{severity}"
                self._logger.log(f"[Factory Twin] Ready to create material: {mat_name} color={color}")
                mat = create_material(stage, self.MATERIAL_ROOT, mat_name, color)
                self._logger.log(f"[Factory Twin] Created material: {mat}")
                self._material_map[color] = mat
        self._logger.log(f"[Factory Twin] Created {len(self._material_map)} materials")
    
    def build_collections(self):
        stage = omni.usd.get_context().get_stage()

        for machine in self._config.machines:
            prim_path = machine.usd_prim_path
            root_prim = stage.GetPrimAtPath(prim_path)
            if not root_prim.IsValid():
                self._logger.log(f"[Factory Twin] Build collection fail, not found prim : {prim_path}")
                continue
            collection_api = Usd.CollectionAPI.Apply(root_prim, "statusOverride")
            collection_api.CreateIncludesRel().SetTargets([Sdf.Path(prim_path)])
            collection_api.CreateExpansionRuleAttr().Set("expandPrims")

            self._collection_map[machine.machine_id] = collection_api
            self._logger.log(f"[Factory Twin] Build collection end : {prim_path}")

    def remove_collections(self):
        stage = omni.usd.get_context().get_stage()
        if not stage:
            return
        for machine in self._config.machines:
            root_prim = stage.GetPrimAtPath(machine.usd_prim_path)
            if not root_prim.IsValid():
                continue
            binding_api = UsdShade.MaterialBindingAPI(root_prim)
            binding_api.UnbindCollectionBinding("statusOverride")

            root_prim.RemoveAPI(Usd.CollectionAPI, "statusOverride")

    def update_machine_color(self, machine_id:str, color: tuple):
        try:
            collection_api = self._collection_map[machine_id]
            if collection_api is None:
                self._logger.log(f"[Factory Twin] Not found collection : {machine_id}")
                return
            material = self._material_map.get(color)
            if material is None:
                self._logger.log(f"[Factory Twin] Not found material : {color}")
                return
            root_prim = collection_api.GetPrim()
            binding_api = UsdShade.MaterialBindingAPI.Apply(root_prim)
            binding_rel = binding_api.GetCollectionBindingRel("statusOverride")
            binding_rel.SetTargets([
                collection_api.GetCollectionPath(),
                material.GetPath()
            ])

            UsdShade.MaterialBindingAPI.SetMaterialBindingStrength(
                binding_rel,
                UsdShade.Tokens.strongerThanDescendants
            )

            self._logger.log(f"[Factory Twin] {machine_id} -> Material {color}")
        except Exception as e:
            self._logger.log(f"[Factory Twin] Update color error: {machine_id} -> {e}")
            pass

    def dispose(self):
        stage = omni.usd.get_context().get_stage()
        if stage:
            self.remove_collections()
            remove_material(stage, self.MATERIAL_ROOT)
