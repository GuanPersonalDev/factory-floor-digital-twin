from dataclasses import dataclass, field
import omni.kit.viewport.utility as vp_util
import omni.ui as ui


from .style_sheet import FactoryStyleSheet as FactoryStyle


@dataclass
class MiniMapRect:
    x: float
    y: float
    width: float
    height: float   

    def __str__(self) -> str:
        return f"x: {self.x}, y: {self.y}, width: {self.width}, height: {self.height}"
        pass

@dataclass
class MachineRect:
    machine_id: str
    rect: MiniMapRect

@dataclass
class ZoneRect:
    zone_id: str
    rect: MiniMapRect
    machines: list[MachineRect] = field(default_factory=list)

@dataclass
class FactoryRect:
    rect: MiniMapRect
    zones: dict[str, ZoneRect] = field(default_factory=dict)


class FactoryMiniMapData:

    def __init__(self):
        self.factory_rect = FactoryRect(
            rect=MiniMapRect(
                x=0,
                y=0,
                width=750,
                height=750
            ),
            zones={"Test Zone": ZoneRect(
                zone_id="Test Zone",
                rect=MiniMapRect(x=30, y=30, width=250, height=250),
                machines=[MachineRect(
                    machine_id="Name",
                    rect=MiniMapRect(x=150, y=150, width=100, height=100)
                )]
            )}
        )

    def get_data(self):
        pass

class RectWidgets:
    def __init__(self):
        self.placer = None
        self.rect = None
        self.bg = None
        self.label = None
        self.label_width = 0

    def generate_rect(self, id: str, relative_rect: MiniMapRect, color):
        self.placer = ui.Placer(offset_x=relative_rect.x, offset_y=relative_rect.y)
        with self.placer:
            print(f"[Mini Map Rect] Draw rect : {relative_rect.width}x{relative_rect.height}")
            self.rect = ui.ZStack(width=ui.Pixel(relative_rect.width), height=ui.Pixel(relative_rect.height))
            with self.rect:
                self.bg = ui.Rectangle(style=FactoryStyle.mini_map_rect_bg_style(color))
                self.label = ui.Label(id, alignment=ui.Alignment.CENTER_TOP, style=FactoryStyle.mini_map_label)

                self.label_width = len(id) * FactoryStyle.text_context_size * 0.6
                self._check_label_display(relative_rect.width)

    def _check_label_display(self, width):
        self.label.visible = self.label_width <= width

    def redraw(self, relative_rect: MiniMapRect, display: bool):
        if not display:
            self.rect.visible = False
            return
        
        self.placer.offset_x = relative_rect.x
        self.placer.offset_y = relative_rect.y
        self.rect.width = ui.Pixel(relative_rect.width)
        self.rect.height = ui.Pixel(relative_rect.height)
        self._check_label_display(relative_rect.width)
        self.rect.visible = True
   

class FactoryMiniMapView:

    CANVAS_W = 300
    CANVAS_H = 600
    SCALE_MIN = 0.3
    SCALE_MAX = 5.0
    LOD_MACHINE_THRESHOLD = 0.8
    LOD_ZONE_THRESHOLD = 0.3   

    def __init__(self):
        self._viewport_window = None
        self._overlay_frame = None
        self._data: FactoryMiniMapData = FactoryMiniMapData()

        self._canvas_placer = None
        self._zone_widget_collection: dict[str, RectWidgets] = {}
        self._machine_widget_collection: dict[str, RectWidgets] = {}

        self._ratio_3d_to_canvas :float = 1
        self._mouse_x = 0.0
        self._mouse_y = 0.0
        self._scale = 1
        self._drag_start = None
        self._canvas_placer_offset_x = 0
        self._canvas_placer_offset_y = 0

    def bind_mini_map_data(self, data: FactoryMiniMapData):
        self._data = data

    def build(self):
        self._compute_ratio_3d_to_canvas()
        self._viewport_window = vp_util.get_active_viewport_window()
        self._overlay_frame = self._viewport_window.get_frame("factory_minimap")
        with self._overlay_frame:
            with ui.ZStack():
                with ui.VStack():
                    ui.Spacer()
                    with ui.HStack(height=ui.Pixel(self.CANVAS_H)):
                        with ui.Frame(
                            width=ui.Pixel(self.CANVAS_W),
                            height=ui.Pixel(self.CANVAS_H),
                            horizontal_clipping=True,
                            vertical_clipping=True,
                            mouse_pressed_fn=self._on_mouse_pressed,
                            mouse_moved_fn=self._on_mouse_moved,
                            mouse_released_fn=self._on_mouse_released,
                            # mouse_wheel_fn=self._on_scroll
                        ):
                            with ui.ZStack():
                                ui.Rectangle(style=FactoryStyle.mini_map_bg)
                                self._canvas_placer = ui.Placer(offset_x=0, offset_y=0)
                                with self._canvas_placer:
                                    with ui.ZStack():
                                        self._build_zones()
                                        self._build_machines()
                        ui.Spacer()
    
    def _compute_ratio_3d_to_canvas(self):
        factory_rect = self._data.factory_rect
        sw = factory_rect.rect.width
        sh = factory_rect.rect.height
        rw = self.CANVAS_W / sw
        rh = self.CANVAS_H / sh
        self._ratio_3d_to_canvas = min(rw, rh)

    def _build_zones(self):
        for zone_id, zone in self._data.factory_rect.zones.items():
            zone_relative_rect = self._to_pixel(zone.rect)
            rect = self._build_rect_widget(zone_id, zone_relative_rect, FactoryStyle.col_mini_map_bg)
            self._zone_widget_collection[zone_id] = rect

    def _build_machines(self):
        for _, zone in self._data.factory_rect.zones.items():
            for machine in zone.machines:
                machine_relative_rect = self._to_pixel(machine.rect)
                rect = self._build_rect_widget(machine.machine_id, machine_relative_rect, FactoryStyle.col_mini_map_bg)
                self._machine_widget_collection[machine.machine_id] = rect

    def _build_rect_widget(self, id: str, relative_rect: MiniMapRect, color) -> RectWidgets:
        rect = RectWidgets()
        rect.generate_rect(id, relative_rect, color)
        return rect

    def _to_pixel(self, rect: MiniMapRect):
        uniform_scale = self._ratio_3d_to_canvas * self._scale

        pixel_x = rect.x * uniform_scale
        pixel_y = rect.y * uniform_scale
        pixel_width = rect.width * uniform_scale
        pixel_height = rect.height * uniform_scale
        return MiniMapRect(
            x=pixel_x,
            y=pixel_y,
            width=pixel_width,
            height=pixel_height
        )
    
    def _update_layout(self):
        self._canvas_placer.offset_x = self._canvas_placer_offset_x
        self._canvas_placer.offset_y = self._canvas_placer_offset_y

        for zone_id, zone in self._data.factory_rect.zones.items():
            zone_pixel_rect = self._to_pixel(zone.rect)
            display_zone = self._scale >= self.LOD_ZONE_THRESHOLD
            self._zone_widget_collection[zone_id].redraw(zone_pixel_rect, display_zone)

            for machine in zone.machines:
                machine_pixel_rect = self._to_pixel(machine.rect)
                show_machine = self._scale >= self.LOD_MACHINE_THRESHOLD
                self._machine_widget_collection[machine.machine_id].redraw(machine_pixel_rect, show_machine)
            
                        
    def _on_mouse_pressed(self, x, y, button, modifier):
        if button == 0:
            self._drag_start = (x, y)

    def _on_mouse_moved(self, x, y, modifier, dragging):
        self._mouse_x = x
        self._mouse_y = y
        if dragging and self._drag_start:
            dx = x - self._drag_start[0]
            dy = y - self._drag_start[1]
            self._canvas_placer_offset_x += dx
            self._canvas_placer_offset_y += dy
            self._drag_start = (x, y)
            self._update_layout()

    def _on_mouse_released(self, x, y, button, modifier):
        self._drag_start = None

    def _on_scroll(self, dx, dy, modifier):
        scale_old = self._scale
        zoom_factor = 1.1 if dy > 0 else 0.9
        new_scale = max(self.SCALE_MIN, min(self.SCALE_MAX, scale_old * zoom_factor))

        x = self._mouse_x
        y = self._mouse_y
        self._canvas_placer_offset_x = x - (x - self._canvas_placer_offset_x)/scale_old * new_scale
        self._canvas_placer_offset_y = y - (y - self._canvas_placer_offset_y)/scale_old * new_scale
        self._scale = new_scale
        self._update_layout()

    def destroy(self):
        self._canvas_placer = None
        self._zone_widget_collection = None
        self._machine_widget_collection = None
        try:
            if self._overlay_frame:
                self._overlay_frame.clear()
        except:
            pass
        self._overlay_frame = None
        self._viewport_window = None
        