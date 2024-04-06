from bokeh.plotting import figure, show, curdoc
from bokeh.models import HoverTool
from datetime import datetime
from pandas import read_json

def plot_graph():
    logs = read_json("Log.json")

    logs["time"] = logs["time"].map(lambda x: datetime.fromtimestamp(x))

    fig = figure(tools='wheel_zoom, xwheel_zoom, pan', x_axis_type = "datetime", sizing_mode = "stretch_both", active_scroll = "xwheel_zoom")
    curdoc().theme = "dark_minimal"
    render = fig.line(logs["time"], logs["percent"], color = "green", line_width=3)
    fig.add_tools(HoverTool(tooltips = [("Percent", "@y"), ("Date", '@x{%D}'), ("Time", '@x{%R}')], formatters={'@x': 'datetime'}, renderers = [render], mode = "vline"))

    show(fig)

if __name__ == "__main__":
    plot_graph()
