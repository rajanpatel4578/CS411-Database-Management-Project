import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import Dash, dcc, html, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from pandas import DataFrame

from myapp_utils import getTop5Faculties, getTopPubsListForUser, prepareMyDashboardWidget, getMyFavoriteKeywords, \
    getMyFavoritePublications, getMyFavoriteFaculties, prepareSearchByKeywordResult, preparePublicationDetailsPane, \
    prepareMyFavouritesWidget, prepareMyCollaborationsWidget, getMyAffiliations, getMyConnections, getMyWorks, \
    getDynamicHeaderForTopPubsRecos, getDynamicHeaderForTopFaculties, getTop5Universities, \
    getDynamicHeaderForTopUniversities, getTopKeywords, prepareUniversityTrendsGraph, prepareConnectionFinderInputWidget
from mysql_utils import queryUserByName, createuserByName, addToFavoritePublications, addToFavoriteAuthors, \
    addToFavoriteKeywords, deleteFromFavoriteKeywords, deleteFromFavoritePublications, deleteFromFavoriteFaculty, \
    queryKeywordID, queryUniversityID, addToUserAffiliations, deleteFromUserAffiliations, queryFacultyID, \
    addToUserConnections, deleteFromUserConnections, queryUserWorkTitle, addToUserWorks, deleteFromUsersWork, \
    updateUserWorks, queryUniversities, queryPublicationYears, queryKeywords, queryTopTrendingKeywordsLast5Years, \
    queryUserByID, deleteUserProfile
from mongodb_utils import queryPublicationAndFacultyForKeyword, getTopUniversitiesByKeywords
from neo4j_utils import getConnectionsToFaculty, getConnectionsForKeywordByFac, getConnectionsForKeywordByUni

# Instantiate the Dash
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.SLATE])

app.layout = html.Div(children=
[
    # Title/Header of the app
    dbc.Row(
        dbc.Col(
            html.Div(
                'My Academic World', className='h-15',
                style={'font-family': 'Georgia', 'text-align': 'center',
                       'font-size': '2.5em', 'margin-top': '10px', 'font-weight': 100,
                       'letter-spacing': '1px'}
            )
        )
    ),
    # Row defining the "My dashboard login" along with top trends and top faculties in columns
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Label(
                                'My Dashboard', className='h2', style={'font-family': 'Georgia',
                                                                       'color': '#52BE80', 'margin-left': '10px'}
                            ),
                            html.Br(),
                            html.Div(
                                [
                                    dcc.Input(
                                        id='user_name_input',
                                        className='inputBox',
                                        placeholder='Enter Username',
                                        type='text',
                                        style={'color': 'white', 'backgroundColor': '#34495E'}
                                    ),
                                    html.Button(
                                        'Load', id='user_load_create', n_clicks=0, disabled=True,
                                        className='buttonStyle', style={'height': '45px'}
                                    ),
                                    html.Button(
                                        '↻', id='user_reload_profile', n_clicks=0, hidden=True,
                                        title='Reload your profile', className='buttonStyle',
                                        style={'font-size': '2.0em', 'font-weight': '100', 'border-radius': '25px',
                                               'background-image': 'linear-gradient(#0d47a1, #4285F4)'}
                                    ),
                                    dcc.ConfirmDialog(
                                        id='confirm_profile_deletion',
                                        message='Deleted account cannot be recovered, Are you sure you want to '
                                                'continue?',
                                    ),
                                    html.Button(
                                        '×', id='user_delete_profile', n_clicks=0, hidden=True,
                                        title='Delete your profile', className='buttonStyle',
                                        style={'font-size': '2.0em', 'font-weight': '100', 'border-radius': '90px',
                                               'background-image': 'linear-gradient(#ff0000, #b30000)'}
                                    ),
                                    dcc.Loading(id='user_profile_status_loader',
                                                parent_style={'margin-top': '35px', 'margin-left': '300px'},
                                                type='default', color='orange')
                                ]),
                            dcc.Store(id='user_id'),
                            html.P(id='user_profile_response', style={'margin-left': '10px'}),
                            html.Div(id='user_dashboard_plane', style={'margin-left': '10px'}),
                            html.Br()
                        ]
                    ),
                    html.Hr(),
                    # Row defining the Top recommendations based on user's saved data in profile
                    dbc.Row(
                        [
                            dbc.Col(id='top_pub_recommendations_res',
                                    children=[
                                        getDynamicHeaderForTopPubsRecos(0),
                                        dbc.Spinner(id='pub_recos_loader',
                                                    size='lg',
                                                    fullscreen=True,
                                                    color='#52BE80',
                                                    fullscreen_style={
                                                        'backgroundColor': 'transparent'},
                                                    spinner_style={
                                                        "width": "3rem",
                                                        "height": "3rem",
                                                        "top": "225px",
                                                        "position": "absolute",
                                                        "left": "400px"})],
                                    width={'size': 12, 'order': 'first'}
                                    )], justify='between'),
                    html.Hr(),
                    dbc.Row(
                        [
                            dbc.Col(
                                id='top_univ_recos_res',
                                children=[
                                    getDynamicHeaderForTopUniversities(0),
                                    dbc.Spinner(id='univ-recos-loader',
                                                size='lg',
                                                fullscreen=False,
                                                color='#52BE80',
                                                fullscreen_style={
                                                    'backgroundColor': 'transparent'},
                                                spinner_style={
                                                    "width": "3rem",
                                                    "height": "3rem",
                                                    "position": "right"})])], justify='between')]
                , width={'size': 4, 'order': 'first'}
            ),
            # This is a middle column meant for graphs and other details we wish to display
            dbc.Col([dbc.Row(id='university_research_trend_widget', children=[
                html.Label('University Research Trends by keyword', className='h2',
                           style={'font-family': 'Georgia', 'color': '#52BE80', 'text-align': 'center',
                                  'margin-top': '10px'}),
                html.Br(),
                dcc.Graph(id='graph-content',
                          figure=prepareUniversityTrendsGraph(list(getTopUniversitiesByKeywords()['University']),
                                                              queryTopTrendingKeywordsLast5Years(1)['Keyword'][0])),
                dcc.Loading(id='loading_trends_plot',
                            parent_style={'position': 'absolute', 'align-self': 'left',
                                          'margin-top': '25px', 'margin-left': '150px'},
                            style={'align-self': 'left', 'margin-top': '50px', 'margin-left': '200px'},
                            type='default'),
                html.Div(children=[html.Label('Select University', className='h3',
                                              style={'font-family': 'Georgia', 'color': '#F4D03F',
                                                     'text-align': 'left', 'margin-top': '5px'}),
                                   dcc.Dropdown(queryUniversities(), id='university_selection', multi=True,
                                                style={'margin-left': '5px', 'width': '80%', 'border': '#AEB6BF'})],
                         style={'margin-left': '15px', 'display': 'flex'}),
                html.Div(children=[html.Label('Select Keyword', className='h3',
                                              style={'font-family': 'Georgia', 'color': '#F4D03F',
                                                     'text-align': 'left', 'margin-top': '5px',
                                                     'margin-bottom': '10px'}),
                                   dcc.Dropdown(queryKeywords(), id='keyword_selection',
                                                style={'margin-left': '10px', 'margin-bottom': '10px', 'width': '70%',
                                                       'border': '#AEB6BF'})],
                         style={'margin-left': '15px', 'display': 'flex'}),
                html.Br(),
                html.Hr()]),
                     dbc.Row(children=[
                         html.Label('Academic Connections Finder', className='h2',
                                    style={'font-family': 'Georgia', 'color': '#52BE80', 'text-align': 'center',
                                           'margin-top': '10px'}),
                         html.Br(),
                         dbc.Row(id='connection_finder_widget', children=[
                             prepareConnectionFinderInputWidget(0)]),
                         dbc.Row([html.Div(id="faculty_relation_path")])
                     ], style={'margin-left': '15px'})
                     ], width={'size': 4}),
            # This is a last column meant for top faculties and research trends for keywords we wish to display
            dbc.Col([dbc.Row(id='top_faculty_recos_res',
                             children=[
                                 getDynamicHeaderForTopFaculties(0),
                                 dbc.Spinner(id='fac_recos_loader', size='lg', fullscreen=True, color='#52BE80',
                                             spinner_style={"width": "3rem", "height": "3rem", "left": "10px",
                                                            "position": "right"})], style={'margin-left': '15px'}),
                     html.Hr(),
                     dbc.Row(
                         id='trending_keyword_widget',
                         children=[html.Label('Trending Keywords', className='h2',
                                              style={'font-family': 'Georgia', 'color': '#52BE80',
                                                     'text-align': 'left', 'margin-top': '10px'}),
                                   html.Br(),
                                   dbc.Row([dbc.Col(
                                       children=[html.Label('Year', className='h3',
                                                            style={'font-family': 'Georgia', 'color': '#F4D03F',
                                                                   'display': 'block',
                                                                   'text-align': 'center', 'margin-top': '10px'}),
                                                 dcc.Dropdown(queryPublicationYears(),
                                                              value=max(queryPublicationYears()), id="year-selection",
                                                              style={'width': '80%', 'border': '#AEB6BF'})],
                                       width={'size': 4, 'order': 'first'}),
                                       dbc.Col([html.Label('Number of Top Keywords', className='h3',
                                                           style={'font-family': 'Georgia', 'color': '#F4D03F',
                                                                  'display': 'block',
                                                                  'text-align': 'center', 'margin-top': '10px'}),
                                                dcc.Slider(id='keyword_count_slider', min=5, max=25, step=5,
                                                           value=10)],
                                               width={'size': 8, 'order': 'last'})]),

                                   html.Br(),
                                   html.Div(id='top_keywords_table')])
                     ],
                    width={'size': 4, 'order': 'last'})
        ], className='h-40', justify='between'
    )
]
)


# Callback for reloading the widgets based on user data
@app.callback(Output(component_id='user_reload_profile', component_property='n_clicks'),
              Output(component_id='connection_finder_widget', component_property='children', allow_duplicate=True),
              Output(component_id='top_faculty_recos_res', component_property='children', allow_duplicate=True),
              Output(component_id='top_pub_recommendations_res', component_property='children', allow_duplicate=True),
              Output(component_id='top_univ_recos_res', component_property='children', allow_duplicate=True),
              Output(component_id='user_profile_status_loader', component_property='parent_style', allow_duplicate=True),
              Input(component_id='user_reload_profile', component_property='n_clicks'),
              Input(component_id='user_id', component_property='data'), prevent_initial_call='initial_duplicate')
def reload_user_profile(n_clicks, userID):
    if n_clicks == 0:
        return dash.no_update
    else:
        return 0, prepareConnectionFinderInputWidget(userID), getTop5Faculties(userID), getTopPubsListForUser(
            userID), getTop5Universities(userID), {'margin-top': '35px', 'margin-left': '300px'}


# Callback for confirming the user account/profile deletion
@app.callback(Output(component_id='confirm_profile_deletion', component_property='displayed', allow_duplicate=True),
              Output(component_id='user_delete_profile', component_property='n_clicks', allow_duplicate=True),
              Output(component_id='user_profile_response', component_property='children', allow_duplicate=True),
              Input(component_id='user_delete_profile', component_property='n_clicks'),
              Input(component_id='user_name_input', component_property='value'), prevent_initial_call='initial_duplicate')
def confirm_delete_user_profile(n_clicks, userName):
    if n_clicks == 0:
        return dash.no_update
    else:
        return True, 0, html.Label('User account \"{user}\" is being deleted.'.format(user=userName),
                                              className='h3', style={'font-family': 'Georgia', 'color': '#ff1a1a'})


# Callback for deleting the user account/profile
@app.callback(Output(component_id='user_delete_profile', component_property='n_clicks', allow_duplicate=True),
              Output(component_id='user_id', component_property='data', allow_duplicate=True),
              Output(component_id='confirm_profile_deletion', component_property='submit_n_clicks',
                     allow_duplicate=True),
              Output(component_id='confirm_profile_deletion', component_property='displayed', allow_duplicate=True),
              Output(component_id='user_profile_response', component_property='children', allow_duplicate=True),
              Output(component_id='user_dashboard_plane', component_property='children', allow_duplicate=True),
              Output(component_id='user_name_input', component_property='value', allow_duplicate=True),
              Output(component_id='connection_finder_widget', component_property='children', allow_duplicate=True),
              Output(component_id='top_faculty_recos_res', component_property='children', allow_duplicate=True),
              Output(component_id='top_pub_recommendations_res', component_property='children', allow_duplicate=True),
              Output(component_id='top_univ_recos_res', component_property='children', allow_duplicate=True),
              Output(component_id='user_profile_status_loader', component_property='parent_style', allow_duplicate=True),
              Input(component_id='confirm_profile_deletion', component_property='submit_n_clicks'),
              Input(component_id='user_id', component_property='data'), prevent_initial_call='initial_duplicate')
def delete_user_profile(submit_n_clicks, userID):
    if submit_n_clicks is None:
        raise PreventUpdate
    if submit_n_clicks > 0:
        userName = queryUserByID(userID)
        if userName is None or userName.empty:
            return 0, userID, 0, False, "User name not found.", dash.no_update, dash.no_update, dash.no_update, \
                dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        else:
            userName = userName['Name'][0]
            deleteUserProfile(userName)
            return 0, 0, 0, False, html.Label('User account \"{user}\" deleted successfully.'.format(user=userName),
                                              className='h3', style={'font-family': 'Georgia', 'color': '#2ECC71'}), \
                html.Div([]), "", prepareConnectionFinderInputWidget(0), getTop5Faculties(0), getTopPubsListForUser(0), \
                getTop5Universities(0), {'margin-top': '35px', 'margin-left': '300px'}
    else:
        return dash.no_update


# Callback for populating top faculties recommendations based on favorite keywords
@app.callback(
    Output(component_id='top_faculty_recos_res', component_property='children', allow_duplicate=True),
    Input(component_id='user_id', component_property='data'), prevent_initial_call='initial_duplicate')
def get_top_faculties_recommendation(userID):
    if userID == 0:
        return getTop5Faculties(0)
    elif userID is None:
        return getTop5Faculties(0)
    else:
        return getTop5Faculties(userID)


# Callback for populating top universities recommendations based on favorite keywords
@app.callback(
    Output(component_id='top_univ_recos_res', component_property='children', allow_duplicate=True),
    Input(component_id='user_id', component_property='data'), prevent_initial_call='initial_duplicate')
def get_top_universities_recommendation(userID):
    if userID == 0:
        return getTop5Universities(0)
    elif userID is None:
        return getTop5Universities(0)
    else:
        return getTop5Universities(userID)


# Callback for populating publications recommendations
@app.callback(
    Output(component_id='top_pub_recommendations_res', component_property='children', allow_duplicate=True),
    Input(component_id='user_id', component_property='data'), prevent_initial_call='initial_duplicate')
def get_top_publications_recommendation(userID):
    if userID == 0:
        raise PreventUpdate
    elif userID is None:
        return getTopPubsListForUser(0)
    else:
        return getTopPubsListForUser(userID)


# Callback for user input based loading dashboard
@app.callback(Output(component_id='user_name_input', component_property='value', allow_duplicate=True),
              Output(component_id='user_load_create', component_property='n_clicks'),
              Output(component_id='user_load_create', component_property='disabled'),
              Output(component_id='user_reload_profile', component_property='hidden'),
              Output(component_id='user_delete_profile', component_property='hidden'),
              Output(component_id='user_load_create', component_property='children'),
              Output(component_id='user_profile_response', component_property='children', allow_duplicate=True),
              Output(component_id='user_id', component_property='data', allow_duplicate=True),
              Output(component_id='user_dashboard_plane', component_property='children', allow_duplicate=True),
              Output(component_id='connection_finder_widget', component_property='children', allow_duplicate=True),
              Input(component_id='user_load_create', component_property='n_clicks'),
              Input(component_id='user_load_create', component_property='children'),
              Input(component_id='user_name_input', component_property='value'), prevent_initial_call=True)
def load_or_create_user_profile(n_clicks, operation, userName):
    dashboardPlane = html.Div([])
    if n_clicks == 0:
        return userName, 0, False, True, True, 'Load', '', 0, dashboardPlane, dash.no_update
    elif userName is None or not userName.strip():
        return userName, 0, False, True, True, 'Load', html.Label(
            'Invalid user name. User name cannot be an empty string', className='h3',
            style={'font-family': 'Georgia', 'color': 'red'}), 0, dashboardPlane, dash.no_update
    else:
        userName = userName.strip()
        if operation == 'Load':
            user = queryUserByName(userName)
            if user.empty:
                return userName, 0, False, True, True, 'Create', html.Label(
                    'User "{}" does not exist, Click Create button to add new user ' \
                    'profile'.format(userName), className='h3',
                    style={'font-family': 'Georgia', 'color': '#F5B041'}), 0, dashboardPlane, dash.no_update
            else:
                # prepare the user dashboard plane to load
                dashboardPlane = prepareMyDashboardWidget()
                return user.get('username')[0], 0, True, False, False, 'Load', html.Label(
                    'Profile for user "{}" loaded successfully.'.format(
                        userName), className='h3',
                    style={'font-family': 'Georgia', 'color': '#2ECC71'}), user.get('id')[
                    0], dashboardPlane, prepareConnectionFinderInputWidget(user.get('id')[0])
        elif operation == 'Create':
            createuserByName(userName)
            return userName, 0, False, True, True, 'Load', html.Label(
                'User "{}" created successfully. Click "Load" button to '
                'load the dashboard.'.format(userName),
                className='h3', style={'font-family': 'Georgia',
                                       'color': '#5DADE2'}), 0, dashboardPlane, dash.no_update
        else:
            return userName, 0, False, True, True, 'Create', html.Label(
                'User "{}" does not exist, Click Create button to add new user ' \
                'profile'.format(userName), className='h3', style={'font-family': 'Georgia',
                                                                   'color': '#F4D03F'}), 0, dashboardPlane, dash.no_update


# Render the dashboard tabs
@app.callback(
    Output(component_id='my_dashboard_content', component_property='children'),
    Input(component_id='my_dashboard_tabs', component_property='value'))
def render_my_dashboard_content(tab):
    if tab is None:
        return dash.no_update

    if tab == 'myFavouritesTab':
        return prepareMyFavouritesWidget()
    elif tab == 'myCollabsTab':
        return prepareMyCollaborationsWidget()


# Render my favorite tabs
@app.callback(
    Output(component_id='my_favorite_content', component_property='children'),
    Input(component_id='my_favorites_tabs', component_property='value'),
    Input(component_id='user_id', component_property='data'))
def render_my_favorite_tab_content(tab, userName):
    if userName is None:
        return dash.no_update

    if tab == 'myFavKeywords':
        return getMyFavoriteKeywords(userName)
    elif tab == 'myFavPublications':
        return getMyFavoritePublications(userName)
    elif tab == 'myFavFaculties':
        return getMyFavoriteFaculties(userName)


# Render my collaborations tabs
@app.callback(
    Output(component_id='my_collab_content', component_property='children'),
    Output(component_id='collab_query_result', component_property='data'),
    Input(component_id='my_collab_tabs', component_property='value'),
    Input(component_id='user_id', component_property='data'))
def render_my_collaborations_tab_content(tab, userID):
    if userID is None:
        return dash.no_update

    if tab == 'myAffiliations':
        return getMyAffiliations(userID)
    elif tab == 'myWorks':
        return getMyWorks(userID)
    elif tab == 'myConnections':
        return getMyConnections(userID)


# Callback for deletion from favorite keywords
@app.callback(Output(component_id='fav_keyword_delete_msg', component_property='children'),
              [Input(component_id='user_id', component_property='data'),
               Input(component_id='fav_keyword_table', component_property='data_previous')],
              [State('fav_keyword_table', 'data')])
def delete_fav_keyword(user_id, previous, current):
    if previous is None:
        raise PreventUpdate
    else:
        msg = ''
        for row in previous:
            if row not in current:
                deleteFromFavoriteKeywords(user_id, row['Keyword'])
                msg = html.Label('Successfully removed keyword "{keyword}"'.format(keyword=row['Keyword']),
                                 className='h3',
                                 style={'font-family': 'Georgia', 'color': '#007E33'})
        return msg


# Callback for deletion from favorite publications
@app.callback(Output(component_id='fav_pubs_delete_msg', component_property='children'),
              [Input(component_id='user_id', component_property='data'),
               Input(component_id='fav_pubs_table', component_property='data_previous')],
              [State('fav_pubs_table', 'data')])
def delete_fav_publication(user_id, previous, current):
    if previous is None:
        raise PreventUpdate
    else:
        msg = ''
        for row in previous:
            if row not in current:
                msg = html.Label('Successfully removed publication "{pubID}"'.format(pubID=row['ID']),
                                 className='h3', style={'font-family': 'Georgia', 'color': '#007E33'})
                deleteFromFavoritePublications(user_id, row['ID'])

        return msg


# Callback for deletion from favorite faculty
@app.callback(Output(component_id='fav_faculty_delete_msg', component_property='children'),
              [Input(component_id='user_id', component_property='data'),
               Input(component_id='fav_faculty_table', component_property='data_previous')],
              [State('fav_faculty_table', 'data')])
def delete_fav_faculty(user_id, previous, current):
    if previous is None:
        raise PreventUpdate
    else:
        msg = ''
        for row in previous:
            if row not in current:
                deleteFromFavoriteFaculty(user_id, row['Name'])
                msg = html.Label('Successfully removed faculty "{facID}"'.format(facID=row['Name']), className='h3',
                                 style={'font-family': 'Georgia', 'color': '#007E33'})
        return msg


# Search by keyword callback routine
@app.callback(
    Output(component_id='publication_search_res', component_property='children'),
    Output(component_id='keyword_search_result', component_property='data'),
    Output(component_id='loading_search_res', component_property='parent_style'),
    Input(component_id='keyword_search', component_property='n_clicks'),
    Input(component_id='keywordSearch', component_property='value'), prevent_initial_call=True)
def searchByKeywords(n_clicks, keyword):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        if keyword is None:
            raise PreventUpdate
        elif ctx.triggered_id == 'keyword_search':
            searchRes = queryPublicationAndFacultyForKeyword(keyword)
            resList = list(searchRes)
            searchResDF = DataFrame(resList)
            if searchResDF.empty:
                return html.H3('No match found for "{word}"'.format(word=keyword),
                               className='h3', style={'font-family': 'Georgia', 'text-align': 'left',
                                                      'color': '#CC0000'}), 'None', {'position': 'absolute',
                                                                                     'align-self': 'center'}
            else:
                topPubsDF = searchResDF.loc[:, ['ID', 'Title']]
                return prepareSearchByKeywordResult(topPubsDF), searchResDF.to_dict(), {'position': 'absolute',
                                                                                        'align-self': 'center'}
        else:
            raise PreventUpdate


# Callback for highlighting the selected publication row details.
@app.callback(
    Output(component_id='publication_details_res', component_property='children'),
    Output(component_id='selected_publication_details', component_property='data'),
    Input(component_id='keyword_search_res_table', component_property='selected_rows'),
    Input(component_id='keyword_search_result', component_property='data'), prevent_initial_call=True)
def populate_publication_details(selected_rows, searchRes):
    if not selected_rows:
        raise PreventUpdate
    else:
        return preparePublicationDetailsPane(selected_rows, searchRes)


# Callback for highlighting the selected works row details.
@app.callback(
    Output(component_id='work_id', component_property='value'),
    Output(component_id='work_title', component_property='value'),
    Output(component_id='work_cit_pub_id', component_property='value'),
    Output(component_id='work_reference_keywords', component_property='value'),
    Output(component_id='add_work_button', component_property='children'),
    Input(component_id='user_current_works_table', component_property='selected_rows'),
    Input(component_id='collab_query_result', component_property='data'), prevent_initial_call=True)
def populate_selected_work_details(selected_row, workRes):
    if not selected_row:
        raise PreventUpdate
    else:
        workResDF = DataFrame.from_dict(workRes)
        workD = workResDF.loc[:, ['ID', 'Title', 'Citations', 'Keywords']].iloc[selected_row[0]]

        return workD['ID'], workD['Title'], workD['Citations'], workD['Keywords'], "Update work"


# Callback for add to favorites button
@app.callback(
    Output(component_id='add_favorite_status_msg', component_property='children'),
    Output(component_id='add_to_favorite_button', component_property='disabled'),
    Input(component_id='add_to_favorite_button', component_property='n_clicks'),
    Input(component_id='user_id', component_property='data'),
    Input(component_id='selected_publication_details', component_property='data'), prevent_initial_call=True)
def add_publication_to_my_favorites(n_clicks, userID, toSaveDF):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        for key in toSaveDF.keys():
            if key == 'pub_id':
                addToFavoritePublications(userID, toSaveDF[key][0])
            elif key == 'author_ids':
                addToFavoriteAuthors(userID, toSaveDF[key])
            else:
                print('Unknown key ', key)
    return html.Div(children=[html.Br(), html.Label('Added to favorites successfully.', className='h3',
                                                    style={'font-family': 'Georgia', 'color': '#007E33'})]), True


# Add to favorite keywords
@app.callback(
    Output(component_id='add_keyword_to_fav_msg', component_property='children', allow_duplicate=True),
    Output(component_id='add_keyword_fav_button', component_property='disabled'),
    Input(component_id='add_keyword_fav_button', component_property='n_clicks'),
    Input(component_id='keywordSearch', component_property='value'),
    Input('user_id', 'data'), prevent_initial_call=True)
def addToMyFavoriteKeywords(n_clicks, keyword, userID):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        if keyword is None:
            raise PreventUpdate
        elif ctx.triggered_id == 'add_keyword_fav_button':
            keyIdDF = queryKeywordID(keyword)
            if keyIdDF.empty:
                return html.H3('Ignoring: Unknown keyword "{word}" with no references.'.format(word=keyword),
                               className='h3', style={'font-family': 'Georgia', 'text-align': 'left',
                                                      'color': '#FF8800'}), False
            else:
                addToFavoriteKeywords(userID, keyword)
            return html.H3('Successfully added "{word}" to favorite keyword'.format(word=keyword),
                           className='h3', style={'font-family': 'Georgia', 'text-align': 'left',
                                                  'color': '#2ECC71'}), True
        else:
            raise PreventUpdate


# Callback for add affiliation button
@app.callback(
    Output(component_id='add_affiliation_status_msg', component_property='children'),
    Output(component_id='add_affiliation_button', component_property='disabled'),
    Input(component_id='add_affiliation_button', component_property='n_clicks'),
    Input(component_id='user_id', component_property='data'),
    Input(component_id='affiliation_univ_dropdown', component_property='value'), prevent_initial_call=True)
def add_user_affiliation(n_clicks, userID, univName):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        if univName is None:
            raise PreventUpdate
        elif ctx.triggered_id == 'add_affiliation_button':
            univIdDF = queryUniversityID(univName)
            if univIdDF.empty:
                return html.H3('Ignoring: Unknown university name "{word}".'.format(word=univName),
                               className='h3', style={'font-family': 'Georgia', 'text-align': 'left',
                                                      'color': '#FF8800'}), False
            else:
                addToUserAffiliations(userID, univName)
            return html.H3('Added affiliation successfully',
                           className='h3', style={'font-family': 'Georgia', 'text-align': 'left',
                                                  'color': '#2ECC71'}), True
        else:
            raise PreventUpdate


# Callback for deletion from user affiliation
@app.callback(Output(component_id='affiliation_delete_msg', component_property='children'),
              [Input(component_id='user_id', component_property='data'),
               Input(component_id='user_affiliations_table', component_property='data_previous')],
              [State('user_affiliations_table', 'data')])
def delete_user_affiliation(user_id, previous, current):
    if previous is None:
        raise PreventUpdate
    else:
        msg = ''
        for row in previous:
            if row not in current:
                deleteFromUserAffiliations(user_id, row['University'])
                msg = html.Label('Successfully removed affiliation to "{univ}"'.format(univ=row['University']),
                                 className='h3',
                                 style={'font-family': 'Georgia', 'color': '#007E33'})
        return msg


# Callback for deletion from user connection
@app.callback(Output(component_id='connection_delete_msg', component_property='children'),
              [Input(component_id='user_id', component_property='data'),
               Input(component_id='user_connections_table', component_property='data_previous')],
              [State('user_connections_table', 'data')])
def delete_user_connection(user_id, previous, current):
    if previous is None:
        raise PreventUpdate
    else:
        msg = ''
        for row in previous:
            if row not in current:
                deleteFromUserConnections(user_id, row['Name'])
                msg = html.Label('Successfully removed connection "{conn}"'.format(conn=row['Name']),
                                 className='h3',
                                 style={'font-family': 'Georgia', 'color': '#007E33'})
        return msg


# Callback for deletion from user works
@app.callback(Output(component_id='delete_work_msg', component_property='children'),
              [Input(component_id='user_id', component_property='data'),
               Input(component_id='user_current_works_table', component_property='data_previous')],
              [State('user_current_works_table', 'data')])
def delete_users_work(user_id, previous, current):
    if previous is None:
        raise PreventUpdate
    else:
        msg = ''
        for row in previous:
            if row not in current:
                deleteFromUsersWork(user_id, row['ID'])
                msg = html.Label('Successfully removed work ID {id}:"{title}"'.format(id=row['ID'], title=row['Title']),
                                 className='h3',
                                 style={'font-family': 'Georgia', 'color': '#007E33'})
        return msg


# Callback for add connection button
@app.callback(
    Output(component_id='add_connection_status_msg', component_property='children'),
    Output(component_id='add_connection_button', component_property='disabled'),
    Input(component_id='add_connection_button', component_property='n_clicks'),
    Input(component_id='user_id', component_property='data'),
    Input(component_id='connection_names_dropdown', component_property='value'))
def add_user_connection(n_clicks, userID, conName):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        if conName is None:
            raise PreventUpdate
        elif ctx.triggered_id == 'add_connection_button':
            facIDF = queryFacultyID(conName)
            if facIDF.empty:
                return html.H3('Ignoring: Unknown faculty name "{word}".'.format(word=conName),
                               className='h3', style={'font-family': 'Georgia', 'text-align': 'left',
                                                      'color': '#FF8800'}), False
            else:
                addToUserConnections(userID, conName)
            return html.H3('Added connection successfully',
                           className='h3', style={'font-family': 'Georgia', 'text-align': 'left',
                                                  'color': '#2ECC71'}), True
        else:
            raise PreventUpdate


# Callback for add user work button
@app.callback(
    Output(component_id='create_work_status_msg', component_property='children'),
    Output(component_id='add_work_button', component_property='disabled'),
    Input(component_id='add_work_button', component_property='n_clicks'),
    Input(component_id='add_work_button', component_property='children'),
    Input(component_id='user_id', component_property='data'),
    Input(component_id='work_id', component_property='value'),
    Input(component_id='work_title', component_property='value'),
    Input(component_id='work_cit_pub_id', component_property='value'),
    Input(component_id='work_reference_keywords', component_property='value'), prevent_initial_call=True)
def add_user_work(n_clicks, operation, userID, prePubID, workTitle, workCitationPubs, workReferenceKeywords):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        if workTitle is None:
            raise PreventUpdate
        elif ctx.triggered_id == 'add_work_button':
            # Must verify if the publications being cited and keywords being used are legit
            if operation == 'Create work':
                uWorkIDF = queryUserWorkTitle(workTitle, userID)
                if uWorkIDF.empty:
                    result = addToUserWorks(userID, workTitle, workCitationPubs, workReferenceKeywords)
                    msg = html.H3('Failed to add work', className='h3',
                                  style={'font-family': 'Georgia', 'color': '#E74C3C', 'margin-left': '5px'})
                    if result == 'SUCCESS':
                        msg = html.H3('Added to work successfully.', className='h3',
                                      style={'font-family': 'Georgia', 'color': '#2ECC71', 'margin-left': '5px'})
                    return msg, True
                else:
                    return html.H3('Ignoring: Duplicate work title "{workTitle}".'.format(workTitle=workTitle),
                                   className='h3', style={'font-family': 'Georgia', 'text-align': 'left',
                                                          'color': '#FF8800', 'margin-left': '5px'}), False
            else:  # Update request
                if not workTitle:
                    raise PreventUpdate
                else:
                    result = updateUserWorks(userID, prePubID, workTitle, workCitationPubs, workReferenceKeywords)
                    uMsg = html.H3('Failed to update the work', className='h3',
                                   style={'font-family': 'Georgia', 'color': '#E74C3C', 'margin-left': '5px'})
                    if result == 'SUCCESS':
                        uMsg = html.H3('Successfully updated the work item.', className='h3',
                                       style={'font-family': 'Georgia', 'color': '#2ECC71', 'margin-left': '5px'})

                    return uMsg, True
        else:
            raise PreventUpdate


# keyword search box cleanup action callback
@app.callback(
    Output(component_id='add_keyword_to_fav_msg', component_property='children', allow_duplicate=True),
    Output(component_id='publication_search_res', component_property='children', allow_duplicate=True),
    Output(component_id='add_keyword_fav_button', component_property='disabled', allow_duplicate=True),
    Input(component_id='keywordSearch', component_property='value'), prevent_initial_call=True)
def cleanup_keyword_search_msgs(searchTerm):
    if searchTerm is None:
        raise PreventUpdate
    else:
        return '', '', False


# Callback for yearly Top Keywords widget
@app.callback(
    Output('top_keywords_table', 'children'),
    Input('year-selection', 'value'),
    Input('keyword_count_slider', 'value')
)
def update_top_keywords_table(year, numOfKeywords):
    if not year or not numOfKeywords:
        return dash.no_update
    return getTopKeywords(year, numOfKeywords)


# Callback for University Research Trends widget
@app.callback(
    Output(component_id='graph-content', component_property='figure'),
    Input(component_id='university_selection', component_property='value'),
    Input(component_id='keyword_selection', component_property='value'))
def update_university_research_graph(selectedUnivs, selectedKeywords):
    if not selectedUnivs or not selectedKeywords:
        return dash.no_update
    else:
        return prepareUniversityTrendsGraph(selectedUnivs, selectedKeywords)


# Callback for Finding Faculty Connections
@app.callback(
    Output(component_id='faculty_relation_path', component_property='children'),
    State(component_id='faculty_selection_from', component_property='value'),
    State(component_id='faculty_selection_to', component_property='value'),
    State(component_id='university_selection_from', component_property='value'),
    State(component_id='university_selection_to', component_property='value'),
    State(component_id='keywords_selection_from', component_property='value'),
    Input(component_id='connection_search', component_property='n_clicks')
)
def update_connections_chart(fromFaculty, toFaculty, fromUniversity, toUniversity,
                             keywordOfInterest, n_clicks):
    if n_clicks == 0 or n_clicks is None:
        return dash.no_update
    if toFaculty is not None:
        result = getConnectionsToFaculty(fromFaculty, toFaculty)
    elif fromUniversity is not None:
        result = getConnectionsForKeywordByUni(fromUniversity, keywordOfInterest, toUniversity)
    else:
        result = getConnectionsForKeywordByFac(fromFaculty, keywordOfInterest, toUniversity)

    if result is None or not result:
        return html.Label('NO CONNECTION EXISTS', className='h3',
                          style={'font-family': 'Georgia', 'text-align': 'center',
                                 'color': 'gold', 'margin-top': '20px'})
    else:
        connectionGraph = cyto.Cytoscape(layout={'name': 'breadthfirst'}, elements=result,
                                         style={'width': '90%', 'height': '400px', 'background-color': 'rgba(0,0,0,0)'},
                                         stylesheet=[{'selector': 'label', 'style': {'content': 'data(label)',
                                                                                     'color': 'rgba(174,214,241,0)',
                                                                                     'font-family': 'Georgia',
                                                                                     'text-justification': 'center',
                                                                                     'background-color': 'rgba(244,208,63,0)'}}])
        return connectionGraph


if __name__ == '__main__':
    app.run_server(debug=True)
