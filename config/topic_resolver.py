_NAMESPACE = "factory"

def getRos2Topic(machine_id: str, param: str) -> str:
    return f"/{_NAMESPACE}/{machine_id}/{param}"

def getMqttTopic(machine_id: str, param: str) -> str:
    return f"{_NAMESPACE}/{machine_id}/{param}"

def getMqttSubscribePattern(machine_id: str) -> str:
    return f"{_NAMESPACE}/{machine_id}/+"

def getAllMachinesMqttPattern() -> str:
    return f"{_NAMESPACE}/#"

def parseMqttTopic(topic: str) -> tuple[str, str] | None:
    parts = topic.split("/")
    if len(parts) != 3 or parts[0] != _NAMESPACE:
        return None
    return parts[1], parts[2]

    
# Smoke Test
if __name__ == "__main__":
    machine_id = "machine_01"

    print(f"--- Subscribe pattern ---")
    print(f"\tSingle machine : {getMqttSubscribePattern(machine_id)}")
    print(f"\tAll machine : {getAllMachinesMqttPattern()}")

    print(f"--- Topic parse test --- ")
    test_topics = [
        "factory/machine_01/temperature"
        "factory/machine_02/vibration"
        "invalid/topic"
    ]

    for t in test_topics:
        result = parseMqttTopic(t)
        print(f"\t{t!r:45s} -> {result}")