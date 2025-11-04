# app.py
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
from db_utils import get_metrics
from utils import get_queue_depth, check_threshold
from config import QUEUES

# ---- Dash App ----
app = dash.Dash(__name__)
app.title = "RabbitMQ Queue Monitoring Dashboard"

# ---- Layout ----
def generate_layout():
    current_status_rows = []
    progress_bars = []

    for vhost, queue_name, max_length, threshold in QUEUES:
        depth = get_queue_depth(vhost, queue_name)
        percent, alert = check_threshold(depth, max_length, threshold)
        row_color = "#ff4d4d" if alert else "transparent"
        
        # Table row
        current_status_rows.append(
            html.Tr([
                html.Td(vhost),
                html.Td(queue_name),
                html.Td(depth),
                html.Td(max_length),
                html.Td(threshold),
                html.Td(f"{percent:.2f}%"),
                html.Td("ALERT" if alert else "")
            ], style={"backgroundColor": row_color, "color": "white" if alert else "black"})
        )

        # Progress bar
        progress_bars.append(
            html.Div([
                html.Div(f"{vhost}/{queue_name}", style={"width": "20%", "display": "inline-block"}),
                html.Div(
                    html.Div(style={
                        "width": f"{min(max(int(percent), 0), 100)}%",
                        "backgroundColor": "#ff4d4d" if alert else "#00cc96",
                        "height": "20px"
                    }),
                    style={"width": "75%", "backgroundColor": "#e0e0e0", "display": "inline-block"}
                ),
                html.Span(f" {percent:.2f}% | Threshold: {threshold}")
            ], style={"marginBottom": "10px"})
        )

    # Layout
    layout = html.Div([
        html.H1("RabbitMQ Queue Monitoring Dashboard"),
        html.H2("Current Queue Status"),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Vhost"), html.Th("Queue"), html.Th("Depth"),
                html.Th("Max Length"), html.Th("Threshold"),
                html.Th("Percent"), html.Th("Alert")
            ])),
            html.Tbody(current_status_rows)
        ], style={"width": "100%", "border": "1px solid black", "borderCollapse": "collapse", "marginBottom": "20px"}),
        html.H2("Queue Utilization"),
        html.Div(progress_bars),
        html.H2("Historical Trends (Last 24 Hours)"),
        html.Div([
            dcc.Graph(id=f"{vhost}_{queue_name}_trend") for vhost, queue_name, _, _ in QUEUES
        ])
    ])
    return layout

app.layout = generate_layout

# ---- Callbacks for historical trends ----
for vhost, queue_name, _, _ in QUEUES:
    def make_callback(vhost=vhost, queue_name=queue_name):
        def update_graph(n_intervals):
            data = get_metrics(vhost, queue_name, limit=288)  # last 24h
            if not data:
                return go.Figure()
            
            timestamps = [item[0] for item in data]
            depths = [item[1] for item in data]

            fig = go.Figure(
                data=[go.Scatter(x=timestamps, y=depths, mode='lines', name=f"{vhost}/{queue_name}")],
                layout=go.Layout(title=f"Queue Depth Trend: {vhost}/{queue_name}",
                                 xaxis_title="Time", yaxis_title="Depth")
            )
            return fig
        return update_graph

    app.callback(
        Output(f"{vhost}_{queue_name}_trend", "figure"),
        Input("interval-component", "n_intervals")
    )(make_callback())

# ---- Auto-refresh interval ----
app.layout = html.Div([
    dcc.Interval(id="interval-component", interval=2000, n_intervals=0),
    generate_layout()
])

# ---- Run App ----
if __name__ == "__main__":
    app.run_server(debug=True)
