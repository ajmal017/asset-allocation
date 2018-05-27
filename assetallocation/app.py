import dash
import requests
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from generate_portfolios import get_graph_data
from frontend import timeperiod_input
from frontend import riskreturn_graph
from frontend import datasets

app = dash.Dash()
app.config['suppress_callback_exceptions'] = True

app.title = 'Asset Allocation'
app.css.append_css({'external_url': 'https://codepen.io/accsgs/pen/pVMmQM.css'})
app.layout = html.Div(children=[
    html.H1(children='Asset allocation',
            style={'margin': '0',
                   'padding': '10px',
                   'padding-left': '5px',
                   'background-color': '#354545',
                   'color': '#e5e5e5'}),
    html.Div(dcc.Tabs(
        tabs=[
            {'label': 'Introduction', 'value': 1},
            {'label': 'Porfolios', 'value': 2},
            {'label': 'Datasets', 'value': 3},
        ],
        value=1,
        id='tabs',
        vertical=True,
        style={
            'height': '100vh',
            'padding': '10px',
            'borderRight': 'thin lightgrey solid',
            'textAlign': 'left',
        }
    ),
        style={'width': '20%', 'float': 'left'}
    ),
    html.Div(id='tab-output', style={'width': '80%-50px', 'padding':
                                     '25px', 'margin-left': '20%'})
])


@app.callback(
    Output(component_id='riskreturn_graph', component_property='figure'),
    [Input(component_id='timeperiod_input', component_property='value')]
)
def update_timeperiod(value):
    print(value)
    return riskreturn_graph.get_params(*get_graph_data(*value))


cached_readme = requests.get('https://raw.githubusercontent.com/viv-r/asset-allocation/master/doc/Design.md').text


@app.callback(Output('tab-output', 'children'), [Input('tabs', 'value')])
def display_content(value):
    if value == 1:
        return dcc.Markdown(cached_readme)
    elif value == 2:
        return html.Div(children=[
            riskreturn_graph.get_component(*get_graph_data()),
            timeperiod_input.get_component()
        ])
    elif value == 3:
        return datasets.get_component()


@app.callback(
    dash.dependencies.Output('datasets-container', 'children'),
    [dash.dependencies.Input('datasets-dropdown', 'value')])
def update_output(value):
    return datasets.update_graph(value)


if __name__ == '__main__':
    app.run_server(debug=True)
