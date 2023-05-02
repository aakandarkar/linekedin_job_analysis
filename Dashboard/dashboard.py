import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import dcc #Dash Core component
from dash import html

data_dir = {Enter directory path here}

# Read in the data
df = pd.read_csv(data_dir+'all_data.csv')

# Define the app
app = dash.Dash(__name__)

# Define the dropdown options
domain_options = [{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in df['domain'].unique()]
avg_sal_exp_loc_domain_options = [{'label': i, 'value': i} for i in df['domain'].unique()]
job_type_options = [{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in df['job_type'].unique()]
axis_options = [{'label': 'Work Method', 'value': 'work_method'},
                {'label': 'State', 'value': 'state'}]


# Define the layout
app.layout = html.Div([
    html.H1('Select Job Domain'),
    dcc.Dropdown(
        id='domain-dropdown',
        options=domain_options,
        value='All'
    ),
    dcc.Graph(id='salary-bar-chart', style={'height': '700px'}),
    html.H1('Average Salaries in states based on domain'),
    dcc.Graph(id='salary-heatmap', style={'height': '700px'}),

    html.H1('Job Salaries by Experience Level and Location'),
    dcc.Graph(id='salary-scatter-plot'),


    html.H1('Average Salaries by Experience Level and Domain'),
    dcc.Dropdown(
        id='avg_sal_exp_loc_domain_dropdown',
        options=avg_sal_exp_loc_domain_options,
        value=avg_sal_exp_loc_domain_options[0]['value']
    ),
    dcc.Graph(id='salary-stacked-bar-chart'),

    html.H1('Work Method VS Number of Jobs / States VS Number of Jobs'),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='x-axis-dropdown',
                options=axis_options,
                value='work_method'
            )
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='y-axis-dropdown',
                options=axis_options,
                value='state'
            )
        ], style={'width': '50%', 'display': 'inline-block'})
    ]),
    dcc.Graph(id='work-method-bar-chart')
])

# Define the callback
@app.callback(
    [dash.dependencies.Output('salary-bar-chart', 'figure'),
     dash.dependencies.Output('salary-heatmap', 'figure'),
     dash.dependencies.Output('salary-scatter-plot', 'figure'),
     dash.dependencies.Output('salary-stacked-bar-chart', 'figure'),
     dash.dependencies.Output('work-method-bar-chart', 'figure')],
    [dash.dependencies.Input('domain-dropdown', 'value'),
     dash.dependencies.Input('avg_sal_exp_loc_domain_dropdown', 'value'),
     dash.dependencies.Input('x-axis-dropdown', 'value'),
     dash.dependencies.Input('y-axis-dropdown', 'value')
     ]
)
def update_bar_chart(domain,avg_sal_exp_loc_domain_options,y_axis,x_axis):
    # Filter the data based on the selected domain
    if domain == 'All':
        filtered_df = df
    else:
        filtered_df = df[df['domain'] == domain]

    # Sort the data by salary in descending order
    sorted_df = filtered_df.sort_values('salary', ascending=False)

    # Take the top 10 jobs
    top_10_jobs = sorted_df.head(10)

    # Create the bar chart
    top_salary_bar_chart_ = px.bar(top_10_jobs, x='salary', y='job_title',
                 title=f'Top 10 Highest Salary Jobs in {domain if domain != "All" else "All Domains"}',
                 labels={'job_title': 'Job Title', 'salary': 'Salary'},
                 orientation='h')

    # Group the data by state and calculate the average salary
    avg_salary_by_state = filtered_df.groupby('state', as_index=False).agg({'salary': 'mean'})

    # Create the heat map
    heat_map_avg_sal = px.choropleth(avg_salary_by_state, locations='state', locationmode='USA-states', color='salary',
                        scope='usa', title=f'Average Salary by State in {domain if domain != "All" else "All Domains"}',
                        color_continuous_scale='Viridis', range_color=(min(avg_salary_by_state['salary']), max(avg_salary_by_state['salary'])))


    # Create the scatter plot
    scatter_data = []
    for exp_level in filtered_df['experience_level'].unique():
        temp_df = filtered_df[filtered_df['experience_level'] == exp_level]
        scatter_data.append(go.Scatter(x=temp_df['salary'], y=temp_df['company_location'], mode='markers',
                                       name=exp_level, hovertext=temp_df['job_title']))

    scatter_layout = go.Layout(title=f'Job Salaries by Experience Level and Location in {domain if domain != "All" else "All Domains"}',
                               xaxis={'title': 'Salary'}, yaxis={'title': 'Company Location'})

    sal_by_exp = go.Figure(data=scatter_data, layout=scatter_layout)

    filtered_df_av_sal = df[df['domain'] == avg_sal_exp_loc_domain_options]

    # Create the stacked bar chart data
    exp_levels = filtered_df_av_sal['experience_level'].unique()
    bar_data = []
    for i, exp_level in enumerate(exp_levels):
        temp_df = filtered_df_av_sal[filtered_df_av_sal['experience_level'] == exp_level]
        bar_data.append(go.Bar(x=[exp_level], y=[temp_df['salary'].mean()],
                               name=exp_level, marker_color=f'rgba(0,0,{i * 50 + 50},1)'))

    bar_layout = go.Layout(title=f'Average Salaries by Experience Level for {avg_sal_exp_loc_domain_options} Positions',
                           xaxis={'title': 'Experience Level'},
                           yaxis={'title': 'Average Salary'},
                           barmode='stack')

    avg_sal_exp_loc = go.Figure(data=bar_data, layout=bar_layout)

    pivot_df = df.pivot_table(index=y_axis, columns=x_axis, values='company_name', aggfunc=len, fill_value=0)

    # Create the bar chart
    work_method_bar_chart = px.bar(pivot_df,
                 x=pivot_df.index,
                 y=pivot_df.columns,
                 labels=dict(x=y_axis.title(), y='Number of Companies'),
                 barmode='group')


    return top_salary_bar_chart_,heat_map_avg_sal,sal_by_exp,avg_sal_exp_loc,work_method_bar_chart

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
