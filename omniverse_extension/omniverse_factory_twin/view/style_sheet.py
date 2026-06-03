import omni.ui as ui
from omni.ui import color

class FactoryStyleSheet:
    # Keyword
    __RECTANGLE = "Rectangle"
    __LABEL = "Label"
    __BUTTON = "Button"
    __BUTTON_LABEL = "Button.Label"
    __V_STACK = "VStack"
    __PLOT = "Plot"

    __FONT_SIZE = "font_size"
    __FONT_WEIGHT = "font_weight"
    __FONT_WEIGHT_BOLD = "bold"
    __COLOR = "color"

    __BG_COLOR = "background_color"
    __BORDER_RADIUS = "border_radius"
    __BORDER_WIDTH = "border_width"
    __BORDER_COLOR = "border_color"
    __MARGIN_LEFT = "margin_left"
    __MARGIN_RIGHT = "margin_right"
    __MARGIN_TOP = "margin_top"

    __PADDING = "padding"
    __MARGIN = "margin"

    # Color
    bg_deep = color("#0D1117")
    bg_panel = color("#161B22")
    bg_card = color("#1C2128")

    border_default = color("#30363D")

    text_col_primary = color("#E6EDF3")
    text_col_secondary = color("#8B949E")
    
    col_normal = color("#3FB950")
    COL_WARNING_HEX = "#D29922"
    col_warning = color("#D29922")
    col_warning_secondary = color("#2A1E08")
    COL_ERROR_HEX = "#F85149"
    col_error = color("#F85149")
    col_error_secondary = color("#2A1010")
    col_offline = color("#6E7681")
    col_idle = color("#58A6FF")
    col_mini_map_bg = color(26, 26, 26, 128)
    
    # Text Size
    text_title_size = 18
    text_header_size = 16
    text_context_size = 14

    col_transparent = color(0, 0, 0, 0)


    # Common
    section_title = {
        __LABEL: {
            __COLOR: text_col_primary,
            __FONT_SIZE: text_header_size 
        }
    }

    @staticmethod
    def mouse_event_blocker():
        return ui.Rectangle(style={
            FactoryStyleSheet.__RECTANGLE:{FactoryStyleSheet.__BG_COLOR: FactoryStyleSheet.col_transparent}
        }, opaque_for_mouse_events=True)

    @staticmethod
    def draw_section_title(title: str):
        return ui.Label(title, height=32, style=FactoryStyleSheet.section_title, alignment=ui.Alignment.LEFT_CENTER)

    @staticmethod
    def get_row_severity_bar(color):
        return ui.Rectangle(
            width=3,
            style=FactoryStyleSheet.row_severity_bar_style(color)
        )

    @staticmethod
    def row_severity_bar_style(color):
        return {
                    FactoryStyleSheet.__RECTANGLE:{
                    FactoryStyleSheet.__BG_COLOR: color,
                    FactoryStyleSheet.__BORDER_RADIUS: 0,
                    FactoryStyleSheet.__BORDER_WIDTH: 0
                    }
               }

    @staticmethod
    def change_alpha(ori_color: color, alpha: int) -> color:
        value = int(ori_color)
        r = value & 0xFF
        g = (value >> 8) & 0xFF
        b = (value >> 16) & 0xFF
        return color(r, g, b, alpha)


    # Overview
    overview_bar_bg = {
        __RECTANGLE: {
            __BG_COLOR: bg_panel,
            __BORDER_RADIUS: 6,
            __BORDER_WIDTH: 1,
            __BORDER_COLOR: border_default
        }
    }

    overview_bar_divider = {
        __RECTANGLE: {
            __BG_COLOR: border_default
        }
    }

    overview_bar_label = {
        __LABEL: {
            __COLOR: text_col_secondary,
            __FONT_SIZE: text_context_size,
        }   
    }

    overview_context_normal = {
        __LABEL: {
            __COLOR: text_col_secondary,
            __FONT_SIZE: text_title_size,
            __FONT_WEIGHT: __FONT_WEIGHT_BOLD
        }
    }

    overview_context_warning = {
        __LABEL: {
            __COLOR: col_warning,
            __FONT_SIZE: text_title_size,
            __FONT_WEIGHT: __FONT_WEIGHT_BOLD
        }
    }    
    
    overview_context_error = {
        __LABEL: {
            __COLOR: col_error,
            __FONT_SIZE: text_title_size,
            __FONT_WEIGHT: __FONT_WEIGHT_BOLD
        }
    }

    # Alert
    @staticmethod
    def alert_card_bg(main_color, secondary_color):
        return ui.Rectangle(style=FactoryStyleSheet.alert_card_bg_style(main_color, secondary_color))

    @staticmethod
    def alert_card_bg_style(main_color, secondary_color):
        return {
            FactoryStyleSheet.__RECTANGLE:{
                FactoryStyleSheet.__BG_COLOR: secondary_color,
                FactoryStyleSheet.__BORDER_RADIUS: 5,
                FactoryStyleSheet.__BORDER_WIDTH: 1,
                FactoryStyleSheet.__BORDER_COLOR: main_color
            }
        }

    @staticmethod
    def alert_card_context(margin):
        return {
            FactoryStyleSheet.__V_STACK:{
                FactoryStyleSheet.__MARGIN_LEFT: margin,
                FactoryStyleSheet.__MARGIN_RIGHT: margin,
                FactoryStyleSheet.__MARGIN_TOP: margin
            }
        }

    alert_card_name = {
        __LABEL:{
            __COLOR: text_col_primary,
            __FONT_SIZE: text_context_size,
            __FONT_WEIGHT: __FONT_WEIGHT_BOLD
        }
    }

    @staticmethod
    def alert_card_param_summary(color):
        return {
            FactoryStyleSheet.__LABEL:{
                FactoryStyleSheet.__COLOR: color,
                FactoryStyleSheet.__FONT_SIZE: FactoryStyleSheet.text_context_size
            }
        }

    alert_plot_bg = {
        __RECTANGLE:{
            __BG_COLOR: color("#0A0A12"),
            __BORDER_RADIUS: 4,
            __BORDER_WIDTH: 1,
            __BORDER_COLOR: border_default
        }
    }

    empty_plot_space = {
        __RECTANGLE: {
            __BG_COLOR: col_transparent,
            __PADDING: 0,
            __MARGIN: 0
        }
    }

    @staticmethod
    def plot_with_color(color):
        return {
            FactoryStyleSheet.__PLOT: {
                FactoryStyleSheet.__COLOR: color,
                FactoryStyleSheet.__BG_COLOR: FactoryStyleSheet.col_transparent,
                FactoryStyleSheet.__PADDING: 0,
                FactoryStyleSheet.__MARGIN: 0
            }
        }

    # Machine info row
    machine_row_bg = {
        __BUTTON:{
            __BG_COLOR: bg_card,
            __BORDER_RADIUS: 0,
            __BORDER_WIDTH: 0,
            __MARGIN: 0
        },
        "Button.hovered": {
            __BG_COLOR: col_warning
        },
        "Button.pressed": {
            __BG_COLOR: col_normal
        }
    }

    machine_name = {
        __LABEL: {
            __COLOR: text_col_primary,
            __FONT_SIZE: text_context_size,
            __FONT_WEIGHT: __FONT_WEIGHT_BOLD
        }
    }

    machine_param_normal = {
        __LABEL: {
            __COLOR: text_col_secondary,
            __FONT_SIZE: text_context_size
        }
    }

    machine_param_warning = {
        __LABEL: {
            __COLOR: col_warning,
            __FONT_SIZE: text_context_size,
            __FONT_WEIGHT: __FONT_WEIGHT_BOLD
        }
    }

    machine_param_error = {
        __LABEL: {
            __COLOR: col_error,
            __FONT_SIZE: text_context_size,
            __FONT_WEIGHT: __FONT_WEIGHT_BOLD
        }
    }

    badge_running = {
        __BUTTON: {
            __BG_COLOR: color("#0D2A1A"),
            __BORDER_RADIUS: 3,
            __BORDER_WIDTH: 1,
            __BORDER_COLOR: col_normal,
        },
        __BUTTON_LABEL: {
            __COLOR: col_normal,
            __FONT_SIZE: text_context_size
        }
    }

    badge_idle = {
        __BUTTON: {
            __BG_COLOR: color("#0D1A2E"),
            __BORDER_RADIUS: 3,
            __BORDER_WIDTH: 1,
            __BORDER_COLOR: col_idle,
        },
        __BUTTON_LABEL: {
            __COLOR: col_idle,
            __FONT_SIZE: text_context_size
        }
    }

    badge_shutdown = {
        __BUTTON: {
            __BG_COLOR: color("#1A1A1A"),
            __BORDER_RADIUS: 3,
            __BORDER_WIDTH: 1,
            __BORDER_COLOR: border_default,
        },
        __BUTTON_LABEL: {
            __COLOR: text_col_secondary,
            __FONT_SIZE: text_context_size
        }
    }

    badge_offline = {
        __BUTTON: {
            __BG_COLOR: color("#1A1010"),
            __BORDER_RADIUS: 3,
            __BORDER_WIDTH: 1,
            __BORDER_COLOR: col_error,
        },
        __BUTTON_LABEL: {
            __COLOR: col_offline,
            __FONT_SIZE: text_context_size
        }
    }

    # Mini map
    mini_map_bg = {
        __RECTANGLE:{
            __BG_COLOR: col_mini_map_bg,
            __BORDER_RADIUS: 10,
        }
    }

    @staticmethod
    def mini_map_rect_bg_style(color):
        return {
            FactoryStyleSheet.__RECTANGLE:{
                FactoryStyleSheet.__BG_COLOR: color,
                FactoryStyleSheet.__BORDER_RADIUS: 5
            }
        }

    mini_map_label = {
        __LABEL: {
            __COLOR: text_col_primary,
            __FONT_SIZE: text_context_size,
        }   
    }