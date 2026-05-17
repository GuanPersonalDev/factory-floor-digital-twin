_NAMESPACE = "factory"

def get_ros2_topic(machine_id: str, param: str) -> str:
    return f"/{_NAMESPACE}/{machine_id}/{param}"

def get_mqtt_topic(machine_id: str, param: str) -> str:
    return f"{_NAMESPACE}/{machine_id}/{param}"

def get_mqtt_subscribe_pattern(machine_id: str) -> str:
    return f"{_NAMESPACE}/{machine_id}/+"

def get_all_machines_mqtt_pattern() -> str:
    return f"{_NAMESPACE}/#"

def parse_mqtt_topic(topic: str) -> tuple[str, str] | None:
    parts = topic.split("/")
    if len(parts) != 3 or parts[0] != _NAMESPACE:
        return None
    return parts[1], parts[2]

    
# Smoke Test
if __name__ == "__main__":
    machine_id = "machine_01"

    print(f"--- Subscribe pattern ---")
    print(f"\tSingle machine : {get_mqtt_subscribe_pattern(machine_id)}")
    print(f"\tAll machine : {get_all_machines_mqtt_pattern()}")

    print(f"--- Topic parse test --- ")
    test_topics = [
        "factory/machine_01/temperature",
        "factory/machine_02/vibration",
        "invalid/topic"
    ]

    for t in test_topics:
        result = parse_mqtt_topic(t)
        print(f"\t{t!r:45s} -> {result}")