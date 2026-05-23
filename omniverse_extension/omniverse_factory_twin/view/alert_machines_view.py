# system
from dataclasses import dataclass
from datetime import time
from config.config_loader import FactoryConfig

# omniverse lib
import omni.ui as ui

# Factory
from .style_sheet import FactoryStyleSheet as FactoryStyle

@dataclass
class UnitAlertMachine:
    machine_id: str
    severity: str
    # param_name, (relative_second, value, severity)
    param_info: dict[str, tuple[float, float, str]]
    alert_params: list[str]

class AlertMachinesData:
    def get_data(self) -> list[UnitAlertMachine]:
        result = []
        result.append(UnitAlertMachine(
            machine_id="machine_002",
            severity=FactoryConfig.ERROR_STATE_KEY,
            param_info={
                FactoryConfig.TEMPERATURE_PARAM_KEY: (0, 100, FactoryConfig.ERROR_STATE_KEY),
                FactoryConfig.VIBRATION_PARAM_KEY: (0, 9, FactoryConfig.WARNING_STATE_KEY)
            },
            alert_params=[FactoryConfig.TEMPERATURE_PARAM_KEY, FactoryConfig.VIBRATION_PARAM_KEY]
        ))
        result.append(UnitAlertMachine(
            machine_id="machine_001",
            severity=FactoryConfig.WARNING_STATE_KEY,
            param_info={
                FactoryConfig.TEMPERATURE_PARAM_KEY: (0, 25, FactoryConfig.NORMAL_STATE_KEY),
                FactoryConfig.VIBRATION_PARAM_KEY: (0, 8, FactoryConfig.WARNING_STATE_KEY)
            },
            alert_params=[FactoryConfig.VIBRATION_PARAM_KEY]
        ))
        return result

class AlertMachinesView:
    _PLOT_H = 72 # plot height
    _CARD_INNER_MARGIN = 8
    _COLOR_STRIP_W = 3
    _CARD_NAME_H = 18
    _SPACE_NAME_SUMMARY = 4
    _SPACE_SUMMARY_PLOT = 8
    _SPACE_PLOT_PLOT = 6

    def __init__(self):
        self._data = AlertMachinesData()

    def binding_alert_machins_data(self, data: AlertMachinesData):
        self._data = data

    def redraw(self):
        FactoryStyle.draw_section_title("Alarms:")
        ui.Spacer(height=4)
        for unit_alert_machine in self._data.get_data():
            self._build_machine_card(unit_alert_machine)

    def _build_machine_card(self, unit_alert: UnitAlertMachine):
        main_color, secondary_color = self._get_severity_colors(unit_alert.severity)
        card_height = self._calc_card_height(len(unit_alert.alert_params))
        with ui.ZStack(height=card_height):
            FactoryStyle.alert_card_bg(main_color, secondary_color)
            with ui.HStack(spacing=0):
                FactoryStyle.get_row_severity_bar(main_color)
                with ui.VStack(spacing=0, style=FactoryStyle.alert_card_context(self._CARD_INNER_MARGIN)):
                    self._build_card_header(unit_alert.machine_id)
                    ui.Spacer(height=self._SPACE_NAME_SUMMARY)

                    self._build_summary()
                    ui.Spacer(height=self._SPACE_SUMMARY_PLOT)

                    for param in unit_alert.alert_params:
                        param_info = unit_alert.param_info.get(param)
                        self._build_param_plot(param, param_info)
                        ui.Spacer(height=self._SPACE_PLOT_PLOT)
                    
                    self._build_export_button()
                    ui.Spacer(height=self._CARD_INNER_MARGIN)
                        

    def _get_severity_colors(self, severity: str) -> tuple:
        match severity:
            case FactoryConfig.WARNING_STATE_KEY:
                return (FactoryStyle.col_warning, FactoryStyle.col_warning_secondary)
            case FactoryConfig.ERROR_STATE_KEY:
                return (FactoryStyle.col_error, FactoryStyle.col_error_secondary)
        return (FactoryStyle.col_idle, FactoryStyle.col_offline)

    def _calc_card_height(self, plot_count: int):
        result = (self._CARD_INNER_MARGIN
            + self._CARD_NAME_H # name
            + self._SPACE_NAME_SUMMARY # space
            + 14 # param summary
            + self._SPACE_SUMMARY_PLOT # space
            + (self._PLOT_H + self._SPACE_PLOT_PLOT) * plot_count # plot
            + self._CARD_INNER_MARGIN
            + 24 # output button
            + self._CARD_INNER_MARGIN
        )
        return result
        
    def _build_card_header(self, machine_id: str):
        with ui.HStack(height=self._CARD_NAME_H):
            ui.Label(machine_id, style=FactoryStyle.alert_card_name, alignment=ui.Alignment.CENTER)

    def _build_summary(self):
        pass

    def _build_param_plot(self, param: str, info: tuple):
        pass

    def _build_export_button(self):
        pass