# sys and config
from config.config_loader import FactoryConfig

def get_machine_prim_path(machine_id: str) -> str:
    config = FactoryConfig()
    machine_config = config.get_machine_by_id(machine_id)
    if not machine_config:
        raise ValueError(f"Machine id {machine_id} not found in config")
    return machine_config.usd_prim_path
    