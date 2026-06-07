from enum import IntEnum
import carb.events
import omni.kit.app

class FactoryEventType(IntEnum):
    """Factory event types."""
    CAMERA_JUMPED = carb.events.type_from_string("omni.factory.twin.camera_jumped")

def get_event_stream():
    """Get the event stream for factory events."""
    return omni.kit.app.get_app().get_message_bus_event_stream()

def emit_camera_jumped(machine_id: str):
    get_event_stream().push(int(FactoryEventType.CAMERA_JUMPED), 
                       sender=0, 
                       payload={"machine_id": machine_id}
                       )