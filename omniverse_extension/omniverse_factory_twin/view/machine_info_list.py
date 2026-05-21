# system
from dataclasses import dataclass

from config.config_loader import FactoryConfig

# omniverse lib
import omni.ui as ui

# Factory
from .style_sheet import FactoryStyleSheet as FactoryStyle

@dataclass
class UnitRowInfo:
    severity: str
    operation_mode: str
    machine_id: str
    param_data: list[tuple[str, float, str, str]]

class MachineInfoListData:
    def get_row_info_list(self) -> list[UnitRowInfo]:
        result = []
        result.append(UnitRowInfo(
            severity=FactoryConfig.NORMAL_STATE_KEY,
            operation_mode=FactoryConfig.RUNNING_MODE_KEY,
            machine_id="dummy_001",
            param_data = [
                (FactoryConfig.TEMPERATURE_PARAM_KEY, 25, "°C", FactoryConfig.NORMAL_STATE_KEY),
                (FactoryConfig.VIBRATION_PARAM_KEY, 2, "mm/s", FactoryConfig.NORMAL_STATE_KEY),
            ]
        ))
        result.append(UnitRowInfo(
            severity=FactoryConfig.ERROR_STATE_KEY,
            operation_mode=FactoryConfig.RUNNING_MODE_KEY,
            machine_id="dummy_002",
            param_data = [
                (FactoryConfig.TEMPERATURE_PARAM_KEY, 100, "°C", FactoryConfig.ERROR_STATE_KEY),
                (FactoryConfig.VIBRATION_PARAM_KEY, 7, "mm/s", FactoryConfig.WARNING_STATE_KEY),
            ]
        ))
        for i in range(0, 40):
            result.append(UnitRowInfo(
                severity=FactoryConfig.NORMAL_STATE_KEY,
                operation_mode=FactoryConfig.RUNNING_MODE_KEY,
                machine_id=f"dummy_scroll_{i}",
                param_data = [
                    (FactoryConfig.TEMPERATURE_PARAM_KEY, 0, "°C", FactoryConfig.NORMAL_STATE_KEY),
                    (FactoryConfig.VIBRATION_PARAM_KEY, 0, "mm/s", FactoryConfig.NORMAL_STATE_KEY),
                ]
            ))

        return result
    

class MachineInfoList:

    def __init__(self):
        self._list_data = MachineInfoListData()

    def bind_list_data(self, data: MachineInfoListData):
        self._list_data = data

    def redraw(self):
        ui.Label("Machine List:", height=32, style=FactoryStyle.section_title, alignment=ui.Alignment.LEFT_CENTER)
        with ui.ScrollingFrame(
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
        ):
            with ui.VStack(height=0, spacing=2):
                for unit_row_info in self._list_data.get_row_info_list():
                    self._render_one_raw(unit_row_info)

    def _render_one_raw(self, row_info: UnitRowInfo):
        (main_color, badge_style) = self._color_and_badge(row_info)

        with ui.ZStack(height=32):
            ui.Rectangle(style=FactoryStyle.machine_row_bg)
            with ui.HStack(spacing=6):
                self._severity_color_bar(main_color)
                ui.Spacer(width=4)
                ui.Label(row_info.machine_id, width=90, height=32, style=FactoryStyle.machine_name, alignment=ui.Alignment.LEFT_CENTER)
                with ui.VStack():
                    ui.Spacer()
                    ui.Button(row_info.operation_mode, width=68, height=20, style=badge_style, enabled=False, alignment=ui.Alignment.LEFT_CENTER)
                    ui.Spacer()
                ui.Spacer(width=4)
                for (param_str, value, unit, severity) in row_info.param_data:
                    style = self._get_param_style(severity)
                    str = f"{param_str[0].upper()} {value:.1f}{unit}"
                    ui.Label(str, width=75, style=style, alignment=ui.Alignment.LEFT_CENTER)
        pass

    def _color_and_badge(self, raw_info: UnitRowInfo):
        if raw_info.operation_mode == FactoryConfig.OFFLINE_MODE_KEY:
            return (FactoryStyle.col_offline, FactoryStyle.badge_offline)

        if raw_info.operation_mode == FactoryConfig.SHUTDOWN_MODE_KEY:
            return (FactoryStyle.col_error, FactoryStyle.badge_shutdown)

        match raw_info.severity:
            case FactoryConfig.NORMAL_STATE_KEY:
                return (FactoryStyle.col_normal, FactoryStyle.badge_running)
            case FactoryConfig.WARNING_STATE_KEY:
                return (FactoryStyle.col_warning, FactoryStyle.badge_running)
            case FactoryConfig.ERROR_STATE_KEY:
                return (FactoryStyle.col_error, FactoryStyle.badge_running)
        return (FactoryStyle.col_idle, FactoryStyle.badge_idle)

    def _get_param_style(self, severity: str):
        match severity:
            case FactoryConfig.WARNING_STATE_KEY:
                return FactoryStyle.machine_param_warning
            case FactoryConfig.ERROR_STATE_KEY:
                return FactoryStyle.machine_param_error
        return FactoryStyle.machine_param_normal
        

    def _severity_color_bar(self, color):
        with ui.ZStack(width=3):
            ui.Rectangle(style=FactoryStyle.get_row_severity_bar(color))
