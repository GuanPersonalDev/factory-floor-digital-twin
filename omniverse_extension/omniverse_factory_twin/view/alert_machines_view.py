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
    # param_name, (alert_time, value, severity, unit)
    alert_param_info: dict[str, tuple[float, float, str, str]]
    # param_name, (relative_second, value)
    alert_param_plot: dict[str, list[tuple[int, float]]]

class AlertMachinesData:
    def get_data(self) -> list[UnitAlertMachine]:
        import random
        def _dummy_log(middle: float, y_min: float, y_max: float) -> list[tuple[int, float]]:
            l = []
            half = 10 
            i = -half
            while i <= half:
                v = random.uniform(y_min, y_max) if i != 0 else middle
                l.append((i, v))
                i += 1
            return l


        result = []
        machine_002_temp_log = _dummy_log(90, 25, 100)
        machine_002_vib_log = _dummy_log(8, 2, 12)
        result.append(UnitAlertMachine(
            machine_id="machine_002",
            severity=FactoryConfig.ERROR_STATE_KEY,
            alert_param_info={
                FactoryConfig.TEMPERATURE_PARAM_KEY: (45, 90, FactoryConfig.ERROR_STATE_KEY, "°C"),
                FactoryConfig.VIBRATION_PARAM_KEY: (70, 8, FactoryConfig.WARNING_STATE_KEY, "mm/s")
            },
            alert_param_plot={
                FactoryConfig.TEMPERATURE_PARAM_KEY: machine_002_temp_log,
                FactoryConfig.VIBRATION_PARAM_KEY: machine_002_vib_log
            }
        ))

        machine_001_vib_log = _dummy_log(7, 2, 12)
        result.append(UnitAlertMachine(
            machine_id="machine_001",
            severity=FactoryConfig.WARNING_STATE_KEY,
            alert_param_info={
                FactoryConfig.VIBRATION_PARAM_KEY: (80, 7, FactoryConfig.WARNING_STATE_KEY, "mm/s")
            },
            alert_param_plot={
                FactoryConfig.VIBRATION_PARAM_KEY: machine_001_vib_log
            }
        ))
        return result

class AlertMachinesView:
    _PLOT_H = 72 # plot height
    _CARD_INNER_MARGIN = 8
    _COLOR_STRIP_W = 3
    _CARD_NAME_H = 18
    _SPACE_NAME_PLOT = 4
    _SPACE_PLOT_SUMMARY = 14
    _SPACE_PLOT_PLOT = 6

    def __init__(self, config: FactoryConfig):
        self._data = AlertMachinesData()
        self._config = config

    def binding_alert_machins_data(self, data: AlertMachinesData):
        self._data = data

    def redraw(self):
        FactoryStyle.draw_section_title("Alarms:")
        ui.Spacer(height=4)
        for unit_alert_machine in self._data.get_data():
            self._build_machine_card(unit_alert_machine)

    def _build_machine_card(self, unit_alert: UnitAlertMachine):
        main_color, secondary_color = self._get_severity_colors(unit_alert.severity)
        card_height = self._calc_card_height(len(unit_alert.alert_param_info))
        with ui.ZStack(height=card_height):
            FactoryStyle.alert_card_bg(main_color, secondary_color)
            with ui.HStack(spacing=0):
                FactoryStyle.get_row_severity_bar(main_color)
                with ui.VStack(spacing=0, style=FactoryStyle.alert_card_context(self._CARD_INNER_MARGIN)):
                    self._build_card_header(unit_alert.machine_id)
                    ui.Spacer(height=self._SPACE_NAME_PLOT)

                    for (param, param_info) in unit_alert.alert_param_info.items():
                        param_x_y = unit_alert.alert_param_plot.get(param)
                        self._build_param_plot(param, param_info, param_x_y)
                        ui.Spacer(height=self._SPACE_PLOT_PLOT)
                    
                    self._build_export_button()
                    ui.Spacer(height=self._CARD_INNER_MARGIN)
                        

    def _get_severity_colors(self, severity: str) -> tuple:
        match severity:
            case FactoryConfig.WARNING_STATE_KEY:
                return (FactoryStyle.col_warning, FactoryStyle.col_warning_secondary)
            case FactoryConfig.ERROR_STATE_KEY:
                return (FactoryStyle.col_error, FactoryStyle.col_error_secondary)
        return (FactoryStyle.col_normal, FactoryStyle.col_offline)

    def _calc_card_height(self, plot_count: int):
        result = (self._CARD_INNER_MARGIN
            + self._CARD_NAME_H # name
            + self._SPACE_NAME_PLOT # space
            + self._calc_single_plot_h() * plot_count # plot
            + self._CARD_INNER_MARGIN
            + 24 # output button
            + self._CARD_INNER_MARGIN
        )
        return result

    def _calc_single_plot_h(self):
        return self._PLOT_H + self._SPACE_PLOT_SUMMARY + self._SPACE_PLOT_PLOT
        
    def _build_card_header(self, machine_id: str):
        with ui.HStack(height=self._CARD_NAME_H):
            ui.Label(machine_id, style=FactoryStyle.alert_card_name, alignment=ui.Alignment.CENTER)

    def _build_param_plot(self, param: str, info: tuple, data_x_y: list[tuple[int, float]]):
        (alert_time, value, severity, unit) = info
        str = f"{param[0].upper()} {value:.1f}{unit} {alert_time}-second passed"
        (main_color, second_color) = self._get_severity_colors(severity)

        y_values = [y for _, y in data_x_y]
        data_min = min(y_values)
        data_max = max(y_values)
        padding = max((data_max - data_min) * 0.1, 1)
        y_min = data_min - padding
        y_max = data_max + padding
        y_range = y_max - y_min

        def y_pixel(value: float) -> float:
            return self._PLOT_H * ( 1 - (value - y_min) / y_range)

        plot_margin = 4
        inner_h = self._PLOT_H - plot_margin*2

        h = self._calc_single_plot_h()
        with ui.VStack(height=h, style={"VStack":{"margin":plot_margin}}):
            # ui.Spacer()
            # plot
            with ui.ZStack(height=self._PLOT_H):
                ui.Rectangle(style=FactoryStyle.alert_plot_bg)
                with ui.ZStack():
                    with ui.HStack(height=inner_h):
                        for severity_plot_data in self._separate_line_with_severity(param, data_x_y):
                            self._build_severity_plot(y_max, y_min, severity_plot_data)
                       # last_plot.title = param
                    # plot = ui.Plot(ui.Type.LINE2D, height=inner_h, style=FactoryStyle.plot_with_color(FactoryStyle.col_normal), visibleMax=y_max, visibleMin=y_min)
                    # plot.set_xy_data(data_x_y)

            # threshold
            with ui.ZStack(width=38):
                pass
            
            ui.Spacer(height=4)
            # current value
            ui.Label(str, height=self._SPACE_PLOT_SUMMARY, style=FactoryStyle.alert_card_param_summary(main_color),alignment=ui.Alignment.CENTER, word_warp=False)

    @dataclass
    class SeverityPlotData:
        severity: str
        data_x_y: list[tuple[float, float]]
    
    def _separate_line_with_severity(self, param: str, data_x_y: list[tuple[int, float]]) -> list[SeverityPlotData]:
        result = []
        current_data : self.SeverityPlotData= None
        current_data_severity_level = 0
        last_x = 0
        for (x, y) in data_x_y:
            (severity, severity_level) = self._config.compute_severity(param, y)

            if current_data == None:
                current_data_severity_level = severity_level
                current_data = self.SeverityPlotData(
                    severity=severity,
                    data_x_y=[]
                )
                result.append(current_data)

            # 補齊安全等級轉變過程的資料
            if severity_level != current_data_severity_level:
                threshold_str = current_data.severity if current_data_severity_level > severity_level else severity
                threshold_value = self._config.get_threshold_value(param, threshold_str)
                current_data.data_x_y.append((x, threshold_value))
                # next severity data
                current_data_severity_level = severity_level
                current_data = self.SeverityPlotData(
                    severity=severity,
                    data_x_y=[]
                )
                current_data.data_x_y.append((last_x, threshold_value))
                result.append(current_data)
                
            current_data.data_x_y.append((x, y))
            last_x = x
        return result

    def _build_severity_plot(self, y_max, y_min, severity_plot_data: SeverityPlotData) -> ui.Plot:
        data_count = len(severity_plot_data.data_x_y)
        for (x, y) in severity_plot_data.data_x_y:
            print(f"({x}, {y})")
        (main_color, secondary_color) = self._get_severity_colors(severity_plot_data.severity)
        plot = ui.Plot(ui.Type.LINE2D, y_min, y_max, width=ui.Fraction(data_count), style=FactoryStyle.plot_with_color(main_color))
        plot.set_xy_data(severity_plot_data.data_x_y)       
        return plot
    

    def _build_export_button(self):
        pass