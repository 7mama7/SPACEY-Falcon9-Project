import dash
from dash import html, dcc, no_update
from dash.dependencies import Output, Input
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

space_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
min_payload = space_df['Payload Mass (kg)'].max()
max_payload = space_df['Payload Mass (kg)'].min()

app = dash.Dash(__name__)
app.layout = html.Div(children=[html.H1('SpaceX Falcon9 Launch Dashboard',
                                        style={'textAlign':'center',
                                                'color':'#503D36',
                                                'fontsize': 40}),
                                dcc.Dropdown(id='site_dropdown', 
                                             options=[{'label': 'All Sites', 'value': 'ALL'},
                                                      {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'}, 
                                                      {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                      {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                      {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}],
                                             value='ALL', 
                                             placeholder='Select a location',
                                             style={'width' : '80%',
                                                    'padding':'3px',
                                                    'fontsize':'20px',
                                                    'textAlign':'center'}),
                                html.Div(
                                    dcc.Graph(id='success-pie-graph',
                                              style={'display':'flex'})
                                ),
                                html.Br(),
                                html.P('Select Payload (Kg):'),
                                dcc.RangeSlider(id='payload-slider', 
                                                step= 1000, 
                                                min=0, 
                                                max=10000,
                                                marks={},
                                                value=[min_payload, max_payload]),
                                html.Div(
                                    dcc.Graph(id='success-scatter-graph',
                                              style={'display':'flex'})
                                )])

@app.callback(Output(component_id='success-pie-graph', component_property='figure'), 
          Input(component_id='site_dropdown', component_property='value'))

def get_pie_graph(entered_site):
    df1 = space_df.groupby('Launch Site')['class'].mean()
    if entered_site == 'ALL':
        figure1 = px.pie(values=df1.values, names=df1.index, title='Success Rate of Launch Sites', color_discrete_sequence=['gold', 'red', 'blue', 'pink'])
    else:
        filtered_df = space_df[space_df['Launch Site'] == entered_site]
        success_rate = filtered_df['class'].mean()
        failure_rate = 1 - success_rate
        figure1 = go.Figure(data=[go.Pie(labels=['Success', 'Failure'], 
                                         values=[success_rate, failure_rate],
                                         marker=dict(colors=['blue', 'red']))])
        
    return figure1
    
@app.callback(Output(component_id='success-scatter-graph', component_property='figure'), 
              [Input(component_id='site_dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def update_scatter_chart(entered_site, payload_range):
    if entered_site == 'ALL':
        filtered_df = space_df[(space_df['Payload Mass (kg)'] >= payload_range[0]) & (space_df['Payload Mass (kg)'] <= payload_range[1])]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category', title='Payload Mass vs. Launch Outcome for All Sites')
    else:
        filtered_df = space_df[(space_df['Launch Site'] == entered_site) & (space_df['Payload Mass (kg)'] >= payload_range[0]) & (space_df['Payload Mass (kg)'] <= payload_range[1])]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category', title=f'Payload Mass vs. Launch Outcome for {entered_site}')
    
    fig.update_layout(xaxis_title='Payload Mass (kg)', yaxis_title='Launch Outcome')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
    