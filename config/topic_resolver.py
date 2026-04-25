_NAMESPACE = "factory"

PARAMS = ["temperature", "vibration", "operation_mode"]

def getRos2Topic(machine_id: str, param: str) -> str:
    return f"/{_NAMESPACE}/{machine_id}/{param}"

def getMqttTopic(machine_id: str, param: str) -> str:
    return f"{_NAMESPACE}/{machine_id}/{param}"

def getAllRos2Topics(machine_id: str) -> dict[str, str]:
    return {param: getRos2Topic(machine_id, param) for param in PARAMS}

def getAllMqttTopics(machine_id: str) -> dict[str, str]:
    return {param: getMqttTopic(machine_id, param) for param in PARAMS}

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

    print(f"--- {machine_id} topic list --- ")
    for param in PARAMS:
        print(f"\tROS2 : {getRos2Topic(machine_id, param)}")
        print(f"\tMQTT : {getMqttTopic(machine_id, param)}")

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