import omni.ui as ui
from omni.ui import color

class FactoryStyleSheet:
    # Keyword
    __RECTANGLE = "Rectangle"
    __LABEL = "Label"
    __BUTTON = "Button"
    __BUTTON_LABEL = "Button.Label"

    __FONT_SIZE = "font_size"
    __FONT_WEIGHT = "font_weight"
    __FONT_WEIGHT_BOLD = "bold"
    __COLOR = "color"

    __BG_COLOR = "background_color"
    __BORDER_RADIUS = "border_radius"
    __BORDER_WIDTH = "border_width"
    __BORDER_COLOR = "border_color"


    # Color
    bg_deep = color("#0D1117")
    bg_panel = color("#161B22")
    bg_card = color("#1C2128")

    border_default = color("#30363D")

    text_primary = color("#E6EDF3")
    text_secondary = color("#8B949E")
    
    col_normal = color("#3FB950")
    col_warning = color("#D29922")
    col_error = color("#F85149")
    col_offline = color("#6E7681")
    col_idle = color("#58A6FF")

    # Common
    section_title = {
        __LABEL: {
            __COLOR: text_primary,
            __FONT_SIZE: 16
        }
    }

    @staticmethod
    def draw_section_title(title: str):
        return ui.Label(title, height=32, style=FactoryStyleSheet.section_title, alignment=ui.Alignment.LEFT_CENTER)

    @staticmethod
    def get_row_severity_bar(color):
        return {FactoryStyleSheet.__RECTANGLE: {FactoryStyleSheet.__BG_COLOR: color}}


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
            __COLOR: text_secondary,
            __FONT_SIZE: 14,
        }   
    }

    overview_context_normal = {
        __LABEL: {
            __COLOR: text_secondary,
            __FONT_SIZE: 18,
            __FONT_WEIGHT: __FONT_WEIGHT_BOLD
        }
    }

    overview_context_warning = {
        __LABEL: {
            __COLOR: col_warning,
            __FONT_SIZE: 18,
            __FONT_WEIGHT: __FONT_WEIGHT_BOLD
        }
    }    
    
    overview_context_error = {
        __LABEL: {
            __COLOR: col_error,
            __FONT_SIZE: 18,
            __FONT_WEIGHT: __FONT_WEIGHT_BOLD
        }
    }

    # Machine info row
    machine_row_bg = {
        __RECTANGLE:{
            __BG_COLOR: bg_card,
            __BORDER_RADIUS: 0,
            __BORDER_WIDTH: 0
        }
    }

    machine_name = {
        __LABEL: {
            __COLOR: text_primary,
            __FONT_SIZE: 12,
            __FONT_WEIGHT: __FONT_WEIGHT_BOLD
        }
    }

    machine_param_normal = {
        __LABEL: {
            __COLOR: text_secondary,
            __FONT_SIZE: 11
        }
    }

    machine_param_warning = {
        __LABEL: {
            __COLOR: col_warning,
            __FONT_SIZE: 11,
            __FONT_WEIGHT: __FONT_WEIGHT_BOLD
        }
    }

    machine_param_error = {
        __LABEL: {
            __COLOR: col_error,
            __FONT_SIZE: 11,
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
            __FONT_SIZE: 10
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
            __FONT_SIZE: 10
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
            __COLOR: text_secondary,
            __FONT_SIZE: 10
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
            __FONT_SIZE: 10
        }
    }