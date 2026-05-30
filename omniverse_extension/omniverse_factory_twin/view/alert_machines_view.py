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
    def __init__(self) -> None:
        self.plot_half_data_count = 30

    def set_plot_half_count(self, value: int):
        self.plot_half_data_count = value 

    def get_data(self) -> list[UnitAlertMachine]:
        import random
        def _dummy_log(middle: float, y_min: float, y_max: float) -> list[tuple[int, float]]:
            l = []
            start = -30
            i = start
            while i <= self.plot_half_data_count:
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
    def __init__(self, config: FactoryConfig):
        self.plot_data_expect_half_count = 90 # 90 second in past, 90 second in future
        self._data = AlertMachinesData()
        self._data.set_plot_half_count(self.plot_data_expect_half_count)
        self._config = config
        self._root_stack = None
        self._card_cache: list[MachineCard] = []

    def build(self):
        with ui.VStack():
            FactoryStyle.draw_section_title("Alarms:")
            ui.Spacer(height=4)
            self._root_stack = ui.VStack()

    def binding_alert_machins_data(self, data: AlertMachinesData):
        expect_half_count = self._data.plot_half_data_count
        self._data = data
        self._data.set_plot_half_count(expect_half_count)

    def redraw(self):
        self._build_content()

    def _build_content(self):
        card_index = 0
        for unit_alert_machine in self._data.get_data():
            card = self._get_card(card_index)
            card.redraw(unit_alert_machine)
            card_index += 1

        # set useless card visible false
        while card_index < len(self._card_cache):
            card = self._card_cache[card_index]
            card.disable()
            card_index += 1

    def _get_card(self, index: int):
        if index < len(self._card_cache):
            return self._card_cache[index]
        with self._root_stack:
            result = MachineCard(self.plot_data_expect_half_count, self._config)
            result.build_widget()
        self._card_cache.append(result)
        return result

class MachineCard:
    _PLOT_H = 72 # plot height
    _CARD_INNER_MARGIN = 8
    _COLOR_STRIP_W = 3
    _CARD_NAME_H = 18
    _SPACE_NAME_PLOT = 4
    _SPACE_PLOT_SUMMARY = 14
    _SPACE_PLOT_PLOT = 6
    _PLOT_MARGIN = 4


    def __init__(self, plot_data_expect_half_count: int, config: FactoryConfig):
        self.plot_data_expect_half_count = plot_data_expect_half_count
        self._config = config
        self._root_stack = None
        self._bg = None
        self._name_label = None
        self._severity_bar = None
        self._main_stack = None
        self._param_plot_cache = []

    def set_plot_data_expect_half_count(self, count: int):
        self.plot_data_expect_half_count = count

    def build_widget(self):
        self._root_stack = ui.ZStack()
        with self._root_stack:
            self._bg = FactoryStyle.alert_card_bg(FactoryStyle.col_idle, FactoryStyle.col_offline)
            with ui.HStack(spacing=0):
                self._severity_bar = FactoryStyle.get_row_severity_bar(FactoryStyle.col_idle)
                with ui.VStack(spacing=0, style=FactoryStyle.alert_card_context(self._CARD_INNER_MARGIN)):
                    with ui.HStack(height=self._CARD_NAME_H):
                        self._name_label = ui.Label("name", style=FactoryStyle.alert_card_name, alignment=ui.Alignment.CENTER)
                    ui.Spacer(height=self._SPACE_NAME_PLOT)
                    self._main_stack = ui.VStack()
                    ui.Spacer(height=self._SPACE_PLOT_PLOT)
                    self._build_export_button()
                    ui.Spacer(height=self._CARD_INNER_MARGIN)

    def _build_export_button(self):
        pass

      
    def disable(self):
        self._root_stack.visible = False

    def redraw(self, unit_alert: UnitAlertMachine):
        main_color, secondary_color = MachineCard.get_severity_colors(unit_alert.severity)
        card_height = self._calc_card_height(len(unit_alert.alert_param_info))
        self._root_stack.height = ui.Pixel(card_height)
        self._bg.style = FactoryStyle.alert_card_bg_style(main_color, secondary_color)
        self._severity_bar.style = FactoryStyle.row_severity_bar_style(main_color)
        self._name_label.text = unit_alert.machine_id

        plot_index = 0
        for (param, param_info) in unit_alert.alert_param_info.items():
            param_x_y = unit_alert.alert_param_plot.get(param)
            self._build_param_plot(plot_index, param, param_info, param_x_y)
            plot_index += 1

        while plot_index < len(self._param_plot_cache):
            self._param_plot_cache[plot_index].disable()
            plot_index += 1

        self._root_stack.visible = True
                        
    @staticmethod
    def get_severity_colors(severity: str) -> tuple:
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

    def _build_param_plot(self, plot_index: int, param: str, param_info: tuple, data_x_y: list[tuple[int, float]]):
        plot = self._get_plot_stack(plot_index)
        plot.draw(param, param_info, data_x_y)

    def _get_plot_stack(self, index: int) -> "PlotView":
        if index < len(self._param_plot_cache):
            return self._param_plot_cache[index]

        h = self._calc_single_plot_h()
        with self._main_stack:
            result = PlotView(h, self.plot_data_expect_half_count, self._config)
            result.build(self._SPACE_PLOT_SUMMARY, self._PLOT_H, self._PLOT_MARGIN)
            self._param_plot_cache.append(result)
        return result

class PlotView:
    def __init__(self, height: float, plot_half_count: int, config: FactoryConfig):
        self.plot_data_expect_half_count = plot_half_count
        self._config = config
        self._total_height = height
        self._root_stack  = None
        self._main_stack = None
        self._front_space = None
        self._back_space = None
        self._severity_plot_cache = []
        self._summary_label = None

    def build(self, space_plot_summary, plot_height, plot_margin):
        inner_h = plot_height - plot_margin*2
        self._root_stack = ui.VStack(height=self._total_height, style={"VStack":{"margin":plot_margin}})
        with self._root_stack:
            with ui.ZStack(height=plot_height):
                ui.Rectangle(style=FactoryStyle.alert_plot_bg)
                with ui.ZStack(height=inner_h):
                    with ui.HStack():
                        self._front_space = ui.Rectangle(style=FactoryStyle.empty_plot_space, width=ui.Fraction(0))
                        self._main_stack = ui.HStack()
                        self._back_space = ui.Rectangle(style=FactoryStyle.empty_plot_space, width=ui.Fraction(0))
            ui.Spacer(height=4)
            self._summary_label = ui.Label("SUMMARY", height=space_plot_summary, style=FactoryStyle.alert_card_param_summary(FactoryStyle.col_idle),alignment=ui.Alignment.CENTER, word_warp=False)
    
    def disable(self):
        self._root_stack.visible = False
            

    def draw(self, param: str, param_info: tuple, data_x_y: list[tuple[int, float]]):
        (alert_time, value, severity, unit) = param_info
        summary_text = f"{param[0].upper()} {value:.1f}{unit} {alert_time:.0f}-second passed"
        (main_color, second_color) = MachineCard.get_severity_colors(severity)

        (y_min ,y_max) = self._get_value_range(param, data_x_y)
        x_min = data_x_y[0][0]
        x_max = data_x_y[-1][0]
        front_space = x_min -(-self.plot_data_expect_half_count)
        back_space = self.plot_data_expect_half_count - x_max
        total_length = 2 * self.plot_data_expect_half_count

        self._front_space.width = ui.Fraction(front_space/total_length)

        with self._main_stack:
            plot_index = 0
            for severity_plot_data in self._separate_line_with_severity(param, data_x_y):
                self._draw_severity_plot(plot_index, y_max, y_min, severity_plot_data, total_length)
                plot_index += 1
            while plot_index < len(self._severity_plot_cache):
                self._severity_plot_cache[plot_index].visible = False
                plot_index += 1

        self._back_space.width = ui.Fraction(back_space/total_length)
        self._summary_label.text = summary_text
        self._summary_label.style = FactoryStyle.alert_card_param_summary(main_color)
        self._root_stack.visible = True

    @dataclass
    class SeverityPlotData:
        severity: str
        data_x_y: list[tuple[float, float]]

    def _separate_line_with_severity(self, param: str, data_x_y: list[tuple[int, float]]) -> list[SeverityPlotData]:
        result = []
        current_data : self.SeverityPlotData= None
        current_data_severity_level = 0
        last_x = 0
        last_y = 0
        for (x, y) in data_x_y:
            (severity, severity_level) = self._config.compute_severity(param, y)

            if last_x <= 0 and x > 0 and current_data != None:
                current_data_severity_level = severity_level
                current_data = self.SeverityPlotData(
                    severity=severity,
                    data_x_y=[]
                )
                current_data.data_x_y.append((last_x, last_y))
                result.append(current_data)

            if current_data == None:
                current_data_severity_level = severity_level
                current_data = self.SeverityPlotData(
                    severity=severity,
                    data_x_y=[]
                )
                result.append(current_data)

            # 補齊安全等級轉變過程的資料
            if severity_level != current_data_severity_level:
                step = 1 if severity_level > current_data_severity_level else -1
                severity_keys = self._config.severity_keys
                crossings = []
                l = current_data_severity_level
                while l != severity_level:
                    next_l = l + step
                    threshold_level = max(next_l, l)
                    threshold_str = severity_keys[threshold_level]
                    threshold_value = self._config.get_threshold_value(param, threshold_str)
                    crossings.append((threshold_str, threshold_value, threshold_level))
                    l = next_l
                crossing_count = len(crossings)
                x_step = (x - last_x)/(crossing_count+1)
                last_x += x_step
                current_data.data_x_y.append((last_x, crossings[0][1]))
                for i in range(len(crossings) - 1):
                    (start_severity, start, start_level) = crossings[i]
                    (end_severity, end, end_level) = crossings[i + 1]
                    s = start_severity if start_level < end_level else end_severity
                    inter_data = self.SeverityPlotData(severity=s, data_x_y=[])
                    inter_data.data_x_y.append((last_x, start))
                    last_x += x_step
                    inter_data.data_x_y.append((last_x, end))
                    result.append(inter_data)
                # next severity data
                current_data_severity_level = severity_level
                current_data = self.SeverityPlotData(
                    severity=severity,
                    data_x_y=[]
                )
                current_data.data_x_y.append((last_x, crossings[-1][1]))
                result.append(current_data)
                
            current_data.data_x_y.append((x, y))
            last_x = x
            last_y = y
        return result

    def _get_value_range(self, param: str, data_x_y: list[tuple[int, float]]) -> tuple[float, float]:
        match param:
            case FactoryConfig.TEMPERATURE_PARAM_KEY:
                return (0, 100)
            case FactoryConfig.VIBRATION_PARAM_KEY:
                return (0, 15)
        y_values = [y for _, y in data_x_y]
        data_min = min(y_values)
        data_max = max(y_values)
        padding = max((data_max - data_min) * 0.1, 1)
        y_min = data_min - padding
        y_max = data_max + padding
        return (y_min, y_max)
            

    def _draw_severity_plot(self, index: int, y_max, y_min, severity_plot_data: SeverityPlotData, total_length):
        plot = self._get_plot_stack(index)
        part_length = severity_plot_data.data_x_y[-1][0] - severity_plot_data.data_x_y[0][0]
        ratio = part_length / total_length
        (main_color, secondary_color) = MachineCard.get_severity_colors(severity_plot_data.severity)

        if severity_plot_data.data_x_y[-1][0] > 0:
            main_color = FactoryStyle.change_alpha(main_color, int(255*0.3))

        plot.scale_min = y_min
        plot.scale_max = y_max
        plot.width = ui.Fraction(ratio)
        plot.style = FactoryStyle.plot_with_color(main_color)
        plot.set_xy_data(severity_plot_data.data_x_y)       
        plot.visible = True
    
    def _get_plot_stack(self, index: int):
        if index < len(self._severity_plot_cache):
            return self._severity_plot_cache[index]
        result = ui.Plot(ui.Type.LINE2D, 0, 100, width=ui.Fraction(0), style=FactoryStyle.plot_with_color(FactoryStyle.col_idle))
        self._severity_plot_cache.append(result)
        return result

    def _draw_threshold(self, param:str, inner_h, y_min, y_max):
        with ui.ZStack(height=inner_h):
            FactoryStyle.mouse_event_blocker()
            self._build_threshold_plot(param, FactoryConfig.WARNING_STATE_KEY, y_min, y_max)
            self._build_threshold_plot(param, FactoryConfig.ERROR_STATE_KEY, y_min, y_max)

    
    def _build_threshold_plot(self, param: str, severity: str, y_min, y_max):
        threshold_value = self._config.get_threshold_value(param, severity)
        data_x_y=[(0, threshold_value),(1, threshold_value)]

        plot = ui.Plot(ui.Type.LINE2D, y_min, y_max, style=FactoryStyle.plot_with_color(FactoryStyle.col_idle))
        plot.set_xy_data(data_x_y)
 