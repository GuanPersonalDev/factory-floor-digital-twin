import omni.ui as ui
from omni.ui import color

class FactoryStyleSheet:
    # Keyword
    __RECTANGLE = "Rectangle"
    __LABEL = "Label"

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
    bg_panel = color("161B22")

    border_default = color("#30363D")

    text_primary = color("#E6EDF3")
    text_secondary = color("#8B949E")
    
    col_warning = color("#D29922")
    col_error = color("#F85149")


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
            __FONT_SIZE: 11,
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