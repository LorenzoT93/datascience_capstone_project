# Import required libraries
import pandas as pd
import dash
from dash import html, callback
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        #{'label': 'site1', 'value': 'site1'},
                                    ] + [{'label':x, 'value':x} for x in spacex_df["Launch Site"].unique()],
                                    value='ALL',
                                    placeholder="Select a launch site",
                                    searchable=True
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider', 
                                    min=0, max=10000, step=1000,
                                    marks={
                                        k: str(k) for k in range(0, 10001, 1000)},
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

print(spacex_df.columns)

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value")
)
def pie_chart(entered_site):
    if entered_site == 'ALL':
        df_plot = spacex_df.groupby("Launch Site", as_index=False)["class"].mean()
        fig = px.pie(
            df_plot, values='class', 
            names='Launch Site', 
            title='Total Successes Launches by Site')
        return fig
    else:
        df_plot = spacex_df[spacex_df["Launch Site"] == entered_site]#("class", as_index=False)["class"].mean()
        ntot = df_plot.shape[0]
        df_plot= df_plot['class'].astype('object').value_counts().reset_index()
        df_plot['count'] /= ntot 
        #print(df_plot.reset_index())
        fig = px.pie(
            df_plot, values='count', 
            names='class', 
            title=f'Total Successes Launches for site {entered_site}')
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'), 
        Input(component_id="payload-slider", component_property="value")
    ]
    
)
def scatter_plot_selection(entered_site, payload_slider):
    if entered_site == 'ALL':
        bool_payload = (
            (payload_slider[0] <= spacex_df["Payload Mass (kg)"]) 
            & (spacex_df["Payload Mass (kg)"] <= payload_slider[1]))
        df_plot = spacex_df[bool_payload]
        fig = px.scatter(
            df_plot, x ='Payload Mass (kg)', y='class', 
            color = 'Booster Version Category', 
            title='Correlation between Payload and Success for all sites')
        return fig
    else:
        bool_payload =  (
            (payload_slider[0] <= spacex_df["Payload Mass (kg)"]) 
            & (spacex_df["Payload Mass (kg)"] <= payload_slider[1]))
        bool_site = spacex_df["Launch Site"] == entered_site
        df_plot = spacex_df[bool_payload & bool_site]#("class", as_index=False)["class"].mean()
        
        fig = px.scatter(
            df_plot, 
            x ='Payload Mass (kg)', y ='class', 
            color = 'Booster Version Category',
            title=f'Correlation between Payload and Success for site {entered_site}')
        return fig


# Run the app
if __name__ == '__main__':
    app.run(port="8051")


