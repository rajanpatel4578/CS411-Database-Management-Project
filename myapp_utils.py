import json
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html, dash_table
from pandas import DataFrame
from collections import defaultdict

from mysql_utils import queryTop5Faculties, queryMyFavoriteKeywords, queryMyFavoritePublications, \
    queryMyFavoriteFaculties, queryUniversities, queryAffiliationsForUser, \
    queryConnectionsForUser, queryFaculties, queryWorksForUser, queryTrendingKeywordsByYear, \
    queryUniversityResearchTrends, \
    queryKeywords, queryFavKeywordsForUser
from mongodb_utils import queryRelevantPublications, getTopFacultiesByKeywords, \
    getTopUniversitiesByKeywords


# Utility function to prepare my dashboard widget
def prepareMyDashboardWidget(userID=0):
    return html.Div(
        children=[html.Hr(),
                  dcc.Tabs(id='my_dashboard_tabs', value='myFavouritesTab', children=[
                      dcc.Tab(label='My Favorites', value='myFavouritesTab',
                              style={'font-family': 'Georgia', 'padding': '3px',
                                     'text-align': 'center', 'color': '#E5E8E8'},
                              selected_style={
                                  'font-family': 'Georgia',
                                  'backgroundColor': '#21618C',
                                  'color': 'white',
                                  'fontWeight': 'bold',
                                  'padding': '6px'
                              }
                              ),
                      dcc.Tab(label='My Collaborations', value='myCollabsTab',
                              style={'font-family': 'Georgia', 'padding': '3px',
                                     'text-align': 'center', 'color': '#E5E8E8'},
                              selected_style={
                                  'font-family': 'Georgia',
                                  'backgroundColor': '#0E6655',
                                  'color': 'white',
                                  'fontWeight': 'bold',
                                  'padding': '6px'
                              }
                              )
                  ], colors={'border': 'none',
                             'background': '#212F3D'
                             }, style={'height': '40px', 'color': 'white'}),
                  html.Div(id='my_dashboard_content'),
                  html.Hr(),
                  html.Label('Search by keywords', className='h3',
                             style={'font-family': 'Georgia', 'color': '#99FF33',
                                    'fontWeight': 'bold', 'margin-left': '10px'}),
                  html.Div([
                      dcc.Input(
                          id='keywordSearch',
                          className='inputBox',
                          placeholder='Enter Keywords',
                          type='text',
                          style={'backgroundColor': '#34495E', 'color': 'white'}
                      ),
                      html.Button('Search', id='keyword_search', n_clicks=0, className='buttonStyle'),
                      html.Button('+', id='add_keyword_fav_button', disabled=False, className='buttonStyle',
                                  title='Click to add to favorite keywords', n_clicks=0,
                                  style={'border-radius': '100%',
                                         'background-image': 'linear-gradient(#0d47a1, #4285F4)'}),
                      html.Div(id='add_keyword_to_fav_msg')]),
                  dcc.Store(id='keyword_search_result'),
                  html.Div(id='publication_search_res', style={'margin-left': '10px'}),
                  dcc.Loading(id='loading_search_res',
                              parent_style={'position': 'absolute', 'align-self': 'left',
                                            'margin-top': '25px', 'margin-left': '150px'},
                              style={'align-self': 'left', 'margin-top': '50px', 'margin-left': '200px'},
                              type='default'),
                  html.Hr()
                  ], style={'width': '85%', 'display': 'block'})


# Utility function to prepare my dashboard widget
def prepareMyFavouritesWidget():
    return html.Div(
        children=[
            dcc.Tabs(id='my_favorites_tabs', value='myFavKeywords', children=[
                dcc.Tab(label='Keywords', value='myFavKeywords',
                        style={'borderBottom': '1px solid #d6d6d6', 'padding': '6px'},
                        selected_style={
                            'font-family': 'Georgia',
                            # 'borderTop': '1px solid #d6d6d6',
                            'borderBottom': '1px solid #d6d6d6',
                            'backgroundColor': '#2471A3',
                            'color': 'white',
                            'padding': '6px'
                        }),
                dcc.Tab(label='Publications', value='myFavPublications',
                        style={'borderBottom': '1px solid #d6d6d6', 'padding': '6px'},
                        selected_style={
                            'font-family': 'Georgia',
                            # 'borderTop': '1px solid #d6d6d6',
                            'borderBottom': '1px solid #d6d6d6',
                            'backgroundColor': '#2471A3',
                            'color': 'white',
                            'padding': '6px'
                        }),
                dcc.Tab(label='Faculties', value='myFavFaculties',
                        style={'borderBottom': '1px solid #d6d6d6', 'padding': '6px'},
                        selected_style={
                            'font-family': 'Georgia',
                            # 'borderTop': '1px solid #d6d6d6',
                            'borderBottom': '1px solid #d6d6d6',
                            'backgroundColor': '#2471A3',
                            'color': 'white',
                            'padding': '6px'
                        }),
            ], colors={
                'border': 'none',
                'background': '#2E2E2E'
            }),
            html.Div(id='my_favorite_content')])


# Utility function to prepare my collaborations pane under my dashboard widget
def prepareMyCollaborationsWidget():
    return html.Div(
        children=[
            dcc.Tabs(id='my_collab_tabs', value='myAffiliations', children=[
                dcc.Tab(label='Affiliations', value='myAffiliations',
                        style={'borderBottom': '1px solid #d6d6d6', 'padding': '6px'},
                        selected_style={
                            'font-family': 'Georgia',
                            # 'borderTop': '1px solid #d6d6d6',
                            'borderBottom': '1px solid #d6d6d6',
                            'backgroundColor': '#117A65',
                            'color': 'white',
                            'padding': '6px'
                        }),
                dcc.Tab(label='Works', value='myWorks',
                        style={'borderBottom': '1px solid #d6d6d6', 'padding': '6px'},
                        selected_style={
                            'font-family': 'Georgia',
                            # 'borderTop': '1px solid #d6d6d6',
                            'borderBottom': '1px solid #d6d6d6',
                            'backgroundColor': '#117A65',
                            'color': 'white',
                            'padding': '6px'
                        }),
                dcc.Tab(label='Connections', value='myConnections',
                        style={'borderBottom': '1px solid #d6d6d6', 'padding': '6px'},
                        selected_style={
                            'font-family': 'Georgia',
                            # 'borderTop': '1px solid #d6d6d6',
                            'borderBottom': '1px solid #d6d6d6',
                            'backgroundColor': '#117A65',
                            'color': 'white',
                            'padding': '6px'
                        }),
            ], colors={
                'border': 'none',
                'background': '#2E2E2E'
            }),
            dcc.Store(id='collab_query_result'),
            html.Div(id='my_collab_content')])


# Prepare publication row
def preparePubRow(pubData):
    return dbc.Row(children=
    [
        dbc.Stack(children=
        [
            html.Label(pubData['ID'],
                       style={'font-family': 'Georgia', 'text-align': 'left',
                              'color': '#FFFF99', 'font-weight': '50', 'margin-left': '10px'}),
            html.Label(pubData['Title'],
                       style={'font-family': 'Georgia', 'text-align': 'left',
                              'color': '#00FFFF', 'font-weight': '25', 'margin-left': '5px'})
        ], direction='horizontal', gap=2)
    ])


# Generate dynamic header for the top publications recommendations
def getDynamicHeaderForTopPubsRecos(user_id):
    header = ''
    if user_id > 0:
        keywordsDF = queryFavKeywordsForUser(user_id, 5)
        if keywordsDF.empty:
            header = 'Top publications by top keywords in past 5 years'
        else:
            header = 'Top publications by your favorite keywords'
    else:
        header = 'Most cited publications'
    return html.Label(header, className='h2',
                      style={'color': '#52BE80', 'animation': 'blinker_text 2s linear infinite',
                             'font-family': 'Georgia', 'margin-left': '10px'})


# Generate dynamic header for the top faculties recommendations
def getDynamicHeaderForTopFaculties(user_id=0):
    header = ''
    if user_id > 0:
        keywordsDF = queryFavKeywordsForUser(user_id, 5)
        if keywordsDF.empty:
            header = 'Top faculties by top keywords in past 5 years'
        else:
            header = 'Top faculties by your favorite keywords'
    else:
        header = 'Top faculties by most citations'
    return html.Label(header, className='h2',
                      style={'color': '#52BE80', 'font-family': 'Georgia', 'margin-left': '10px'})


# Generate dynamic header for the top universities recommendations
def getDynamicHeaderForTopUniversities(user_id=0):
    header = 'Top universities by most trending keywords in past 5 years'

    if user_id > 0:
        keywordsDF = queryFavKeywordsForUser(user_id, 5)
        if not keywordsDF.empty:
            header = 'Top universities by your favorite keywords'

    return html.Label(header, className='h2',
                      style={'color': '#52BE80', 'animation': 'blinker_text 2s linear infinite',
                             'font-family': 'Georgia', 'margin-left': '10px'})


# Get to recommendation of publications for user
def getTopPubsListForUser(user_id=0):
    topRecosPubsDF = queryRelevantPublications(user_id)
    return html.Div(children=
    [
        getDynamicHeaderForTopPubsRecos(user_id),
        dbc.Stack(children=
        [
            preparePubRow(row) for index, row in topRecosPubsDF.iterrows()
        ], gap=1)
    ])


# Utility function to prepare the HTML data for each faculty to be displayed.
def prepareFacultyDetails(facData):
    return dbc.Row(children=[html.Img(src=facData['Picture'], className='portrait'),
                             html.Label(facData['Name'], className='h3',
                                        style={'font-family': 'Fantasy', 'text-align': 'left',
                                               'color': '#F9E79F', 'margin-top': '5px'}),
                             html.Label(facData['University'], className='h4',
                                        style={'font-family': 'Georgia', 'text-align': 'left',
                                               'color': '#EAF2F8', 'margin-top': '2px'}),
                             html.Label(facData['Title'], className='h4',
                                        style={'font-family': 'Georgia', 'text-align': 'left',
                                               'color': '#EAECEE', 'font-weight': '50', 'margin-top': '2px'})])


# Utility function to prepare the HTML data for each University to be displayed.
def prepareUniversityDetails(univData):
    return dbc.Col(children=[html.Img(src=univData['URL'], className='uniLogo'),
                             dbc.Row(html.Label(univData['University'], className='h3',
                                                style={'font-family': 'Georgia', 'text-align': 'left',
                                                       'color': '#5DADE2', 'margin-top': '5px'})),
                             dbc.Row(html.Label("Faculty keyword relevance: {}".format(univData['KeywordCount']),
                                                className='h4',
                                                style={'font-family': 'Georgia', 'text-align': 'left',
                                                       'color': '#EAF2F8', 'margin-top': '2px'}))],
                   style={'font-family': 'Georgia', 'text-align': 'left', 'color': '#EAF2F8', 'margin-top': '2px'})


# Utility function to prepare the search by keyword result pane
def prepareSearchByKeywordResult(topPubsDF):
    return html.Div([
        dash_table.DataTable(
            id='keyword_search_res_table',
            data=topPubsDF.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in topPubsDF.columns],
            page_size=5,
            page_current=0,
            sort_action='native',
            row_selectable='single',
            selected_rows=[],
            style_as_list_view=True,
            style_table={'overflowY': 'scroll'},
            style_cell={'padding': '5px', 'textAlign': 'left', 'backgroundColor': '#34495E'},
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_data_conditional=[{
                'if': {'column_id': 'Publication ID'},
                'textDecoration': 'underline',
                'textDecorationStyle': 'double',
            }],
            style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white',
                          'fontWeight': 'bold'}),
        dcc.Store(id='selected_publication_details'),
        html.Div(id='publication_details_res')
    ])


#  Prepare the Publication details pane to display
def preparePublicationDetailsPane(selected_rows, searchRes):
    searchResDF = DataFrame.from_dict(searchRes)
    pubDetails = defaultdict(list)
    pubDetails = defaultdict(list)
    pubD = dict(searchResDF.loc[:, ['ID', 'Year', 'Venue', 'Citation count']].iloc[selected_rows[0]])
    details = html.Div(
        children=[html.Div(children=[
            html.Label(str(header + ': '), className='h3', style={'font-family': 'Georgia', 'color': '#0099FF'}),
            html.Data(value)]) for header, value in
            pubD.items()])
    pubDetails['pub_id'].append(pubD['ID'])
    # Prepare the Authors Dataframe for the selected row
    dfAJ = json.loads(DataFrame.to_json(searchResDF.loc[:, 'Authors'][selected_rows]))
    authorsDF = DataFrame.from_records(dfAJ["{idx}".format(idx=selected_rows[0])])
    authorsDF['affiliation'] = pd.json_normalize(authorsDF['affiliation'])
    authorsIDF = authorsDF.loc[:, ['id']]
    authorsDF = authorsDF.loc[:, ['name', 'affiliation']]
    authorsDF.rename(columns={'name': 'Author(s)', 'affiliation': 'University'}, inplace=True)
    for auth_id in authorsIDF.values:
        pubDetails['author_ids'].append(str(auth_id[0]))
    return html.Div(
        children=[html.Label('Details of the selected publication', className='h3',
                             style={'font-family': 'Georgia', 'color': '#99FF33'}),
                  html.Hr(),
                  details,
                  dash_table.DataTable(authorsDF.to_dict('records'), [{'name': i, 'id': i} for i in authorsDF.columns],
                                       style_as_list_view=True,
                                       style_table={'overflowY': 'scroll'},
                                       style_cell={'padding': '5px', 'textAlign': 'left', 'backgroundColor': '#34495E'},
                                       style_header={'backgroundColor': 'rgb(115, 147, 192)', 'color': 'Black',
                                                     'fontWeight': 'bold'}),
                  html.Br(),
                  html.Button('Add to favorite', id='add_to_favorite_button', n_clicks=0, disabled=False,
                              className='buttonStyle'),
                  html.Div(id='add_favorite_status_msg')]), pubDetails


# Utility function to get the top 5 faculties
def getTop5Faculties(user_id=0):
    if user_id == 0:
        top5FacsDF = queryTop5Faculties()
    else:
        top5FacsDF = getTopFacultiesByKeywords(user_id)
    return dbc.Col(
        children=[getDynamicHeaderForTopFaculties(user_id),
                  dbc.Stack(children=[prepareFacultyDetails(row) for index, row in top5FacsDF.iterrows()], gap=3)],
        className='g-0',
        width={'size': 12, 'order': 'last'})


# Utility function to get the top 5 faculties
def getTop5Universities(user_id=0):
    top5UnivsDF = getTopUniversitiesByKeywords(user_id, 5)
    return dbc.Col(
        children=[getDynamicHeaderForTopUniversities(user_id),
                  dbc.Stack(children=[prepareUniversityDetails(row) for index, row in top5UnivsDF.iterrows()], gap=3)],
        className='g-0',
        width={'size': 12, 'order': 'last'})


# Utility function to get my favourite keywords table
def getMyFavoriteKeywords(userName):
    favKDF = queryMyFavoriteKeywords(userName)
    return html.Div([
        dash_table.DataTable(favKDF.to_dict('records'), [{'name': i, 'id': i} for i in favKDF.columns],
                             id='fav_keyword_table',
                             style_as_list_view=True,
                             style_data={
                                 'whiteSpace': 'normal',
                                 'height': 'auto',
                             },
                             row_deletable=True,
                             style_table={'height': 300, 'overflowY': 'scroll'},
                             style_cell={'padding': '5px', 'textAlign': 'left', 'backgroundColor': '#34495E'},
                             style_header={'backgroundColor': '#2E86C1', 'color': 'white',
                                           'fontWeight': 'bold', 'height': '30px', 'textAlign': 'left'}),
        html.Div(id='fav_keyword_delete_msg')])


# Utility function to get my favourite publications table
def getMyFavoritePublications(userName):
    favPDF = queryMyFavoritePublications(userName)
    return html.Div([
        dash_table.DataTable(favPDF.to_dict('records'), [{'name': i, 'id': i} for i in favPDF.columns],
                             id='fav_pubs_table',
                             style_as_list_view=True,
                             style_data={
                                 'whiteSpace': 'normal',
                                 'height': 'auto',
                             },
                             row_deletable=True,
                             style_table={'height': 300, 'overflowY': 'scroll'},
                             style_cell={'padding': '5px', 'textAlign': 'left', 'backgroundColor': '#34495E'},
                             style_header={'backgroundColor': '#2E86C1', 'color': 'white',
                                           'fontWeight': 'bold', 'height': '30px', 'textAlign': 'left'}),
        html.Div(id='fav_pubs_delete_msg')])


# Utility function to get my favourite faculties table
def getMyFavoriteFaculties(userName):
    favFDF = queryMyFavoriteFaculties(userName)
    return html.Div([
        dash_table.DataTable(favFDF.to_dict('records'), [{'name': i, 'id': i} for i in favFDF.columns],
                             id='fav_faculty_table',
                             style_as_list_view=True,
                             style_table={'height': 300, 'overflowY': 'scroll'},
                             style_data={
                                 'whiteSpace': 'normal',
                                 'height': 'auto',
                             },
                             row_deletable=True,
                             style_cell={'padding': '5px', 'textAlign': 'left', 'backgroundColor': '#34495E'},
                             style_header={'backgroundColor': '#2E86C1', 'color': 'white',
                                           'fontWeight': 'bold', 'height': '30px', 'textAlign': 'left'}),
        html.Div(id='fav_faculty_delete_msg')])


# Utility function to get my affiliations
def getMyAffiliations(userID):
    affDF = queryAffiliationsForUser(userID)
    resList = list(affDF)
    affD = DataFrame(resList)
    return html.Div(
        [
            dash_table.DataTable(affDF.to_dict('records'), [{'name': i, 'id': i} for i in affDF.columns],
                                 id='user_affiliations_table',
                                 style_as_list_view=True,
                                 style_data={
                                     'whiteSpace': 'normal',
                                     'height': 'auto',
                                 },
                                 row_deletable=True,
                                 style_table={'height': 300, 'overflowY': 'scroll'},
                                 style_cell={'padding': '5px', 'textAlign': 'left', 'color': 'black',
                                             'backgroundColor': '#A2D9CE'},
                                 style_header={'backgroundColor': '#0B5345', 'color': 'white',
                                               'fontWeight': 'bold', 'height': '30px', 'textAlign': 'left'}),
            dcc.Dropdown(id='affiliation_univ_dropdown', options=queryUniversities(),
                         style={'width': '75%', 'border': '#AEB6BF'}),
            html.Br(),
            html.Button('Add affiliation', id='add_affiliation_button', disabled=False, className='buttonStyle',
                        title='Click to add to affiliations', n_clicks=0,
                        style={'background-image': 'linear-gradient(#82E0AA, #186A3B)', 'margin-left': '5px',
                               'height': '30px'}),
            html.Div(id='add_affiliation_status_msg'),
            html.Div(id='affiliation_delete_msg')
        ]
    ), affD.to_dict()


# Utility function to get my connections
def getMyConnections(userID):
    connDF = queryConnectionsForUser(userID)
    resList = list(connDF)
    connD = DataFrame(resList)
    return html.Div(
        [
            dash_table.DataTable(connDF.to_dict('records'), [{'name': i, 'id': i} for i in connDF.columns],
                                 id='user_connections_table',
                                 style_as_list_view=True,
                                 style_data={
                                     'whiteSpace': 'normal',
                                     'height': 'auto',
                                 },
                                 row_deletable=True,
                                 style_table={'height': 300, 'overflowY': 'scroll'},
                                 style_cell={'padding': '5px', 'textAlign': 'left', 'color': 'black',
                                             'backgroundColor': '#A2D9CE'},
                                 style_header={'backgroundColor': '#0B5345', 'color': 'white',
                                               'fontWeight': 'bold', 'height': '30px', 'textAlign': 'left'}),
            dcc.Dropdown(id='connection_names_dropdown', options=queryFaculties(),
                         style={'width': '75%', 'border': '#AEB6BF'}),
            html.Br(),
            html.Button('Add connection', id='add_connection_button', disabled=False, className='buttonStyle',
                        title='Click to add connection', n_clicks=0,
                        style={'background-image': 'linear-gradient(#82E0AA, #186A3B)', 'margin-left': '5px',
                               'height': '30px'}),
            html.Div(id='add_connection_status_msg'),
            html.Div(id='connection_delete_msg')
        ]
    ), connD.to_dict()


# Utility function to get users current works
def getMyWorks(userID):
    ucwDF, ucwD = queryWorksForUser(userID)
    return html.Div(
        [
            dash_table.DataTable(ucwDF.to_dict('records'), [{'name': i, 'id': i} for i in ucwDF.columns],
                                 id='user_current_works_table',
                                 style_as_list_view=True,
                                 style_data={
                                     'whiteSpace': 'normal',
                                     'height': 'auto',
                                 },
                                 row_selectable='single',
                                 selected_rows=[],
                                 row_deletable=True,
                                 style_table={'height': 300, 'overflowY': 'scroll'},
                                 style_cell={'padding': '5px', 'textAlign': 'left', 'color': 'black',
                                             'backgroundColor': '#A2D9CE'},
                                 style_header={'backgroundColor': '#0B5345', 'color': 'white',
                                               'fontWeight': 'bold', 'height': '30px', 'textAlign': 'left'}),
            html.Label('ID', hidden=True, id='work_id'),
            html.Label('Title: ', style={'display': 'inline-block', 'margin-right': 5}),
            dcc.Input(

                id='work_title',
                className='inputBox',
                placeholder='Enter Title',
                type='text',
                style={'backgroundColor': '#138D75', 'color': 'white', 'width': '503px'}
            ),
            html.Br(),
            html.Label('Citing publications: ', style={'display': 'inline-block', 'margin-right': 5}),
            dcc.Input(
                id='work_cit_pub_id',
                className='inputBox',
                placeholder='Enter comma separated publication IDs',
                type='text',
                style={'backgroundColor': '#138D75', 'color': 'white', 'width': '400px'}
            ),
            html.Br(),
            html.Label('Keywords: ', style={'display': 'inline-block', 'margin-right': 5}),
            dcc.Input(
                id='work_reference_keywords',
                className='inputBox',
                placeholder='Enter command separated keywords (if any)',
                type='text',
                style={'backgroundColor': '#138D75', 'color': 'white', 'width': '465px'}
            ),
            html.Br(),
            html.Br(),
            html.Button('Create work', id='add_work_button', disabled=False, className='buttonStyle',
                        title='Click to create new work', n_clicks=0,
                        style={'background-image': 'linear-gradient(#82E0AA, #186A3B)', 'margin-left': '5px',
                               'height': '30px'}),
            html.Div(id='create_work_status_msg'),
            html.Div(id='delete_work_msg')
        ]
    ), ucwD.to_dict()


# Utility function to get top Keywords for any given year
def getTopKeywords(year, limit):
    topKeywordsDF = queryTrendingKeywordsByYear(year, limit)
    return html.Div(children=[
        dash_table.DataTable(data=topKeywordsDF.to_dict('records'),
                             columns=[{'name': i, 'id': i} for i in topKeywordsDF.columns],
                             style_table={
                                 'overflowX': 'auto'
                             },
                             style_data={
                                 'border': 'none'
                             },
                             style_cell={
                                 'textAlign': 'left',
                                 'whiteSpace': 'normal',
                                 'overflow': 'hidden',
                                 'textOverflow': 'ellipsis',
                                 'maxWidth': '0',
                                 'padding': '10px',
                                 'border-bottom': '1px solid #ECECEC',
                                 'font-size': '14px',
                                 'backgroundColor': 'rgba(0, 0, 0, 0)',
                                 'height': 'auto'
                             },
                             style_header={
                                 'backgroundColor': 'rgba(0, 0, 0, 0)',
                                 'fontWeight': 'bold',
                                 'text-align': 'left',
                                 'font-size': '16px',
                                 'color': '#52BE80',
                                 'border': 'none'
                             }
                             )])


# Utility function to get research trend for Universities
def prepareUniversityTrendsGraph(selectedUnivs=None, selectedKeyword=None):
    result = queryUniversityResearchTrends(selectedUnivs, selectedKeyword)
    result = pd.DataFrame.from_records(result, columns=['University', 'Year', 'Publications Count'])
    result = result.sort_values('Year').reset_index(drop=True)
    fig = px.scatter(result, x='Year', y='Publications Count', size='Publications Count', color='University',
                     labels={"Keyword": selectedKeyword}, size_max=60)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False), font_color="#4D92F6", font_family='Georgia',
                      margin=dict(l=15, r=15, t=15, b=30), legend_font_color="#F8F9F9")
    return fig


def prepareConnectionFinderInputFrom(userID):
    if userID == 0 or None:
        return dbc.Col(children=[
            html.Label('Connection From', style={'font-family': 'Georgia', 'color': '#F4D03F', 'display': 'block',
                                                 'text-align': 'left', 'margin-top': '10px'}),
            dcc.Dropdown(queryUniversities(), placeholder="University of illinois at Urbana Champaign",
                         id="university_selection_from", style={'border': '#AEB6BF'}),
            html.Br(),
            dcc.Dropdown(queryKeywords(), placeholder="Select a Keyword", id="keywords_selection_from",
                         style={'border': '#AEB6BF'}),
            html.Br(),
            dcc.Dropdown(queryFaculties(), placeholder="Select a connection",
                         id="faculty_selection_from",
                         style={'border': '#AEB6BF'}),
            html.Br()])
    else:
        return dbc.Col(children=[
            html.Label('My Collaborations', style={'font-family': 'Georgia', 'color': '#F4D03F', 'display': 'block',
                                                   'text-align': 'left', 'margin-top': '10px'}),
            dcc.Dropdown(queryUniversities(userID), placeholder="University of illinois at Urbana Champaign",
                         id="university_selection_from", style={'border': '#AEB6BF'}),
            html.Br(),
            dcc.Dropdown(queryKeywords(userID), placeholder="Select a Keyword", id="keywords_selection_from",
                         style={'border': '#AEB6BF'}),
            html.Br(),
            dcc.Dropdown(queryConnectionsForUser(userID)['Name'], placeholder="Select a connection",
                         id="faculty_selection_from",
                         style={'border': '#AEB6BF'}),
            html.Br()])


def prepareConnectionFinderInputWidget(userID):
    return dbc.Row(children=[
        prepareConnectionFinderInputFrom(userID),
        dbc.Col([
            html.Label('Connection To', style={'font-family': 'Georgia', 'color': '#F4D03F',
                                               'display': 'block', 'text-align': 'left',
                                               'margin-top': '10px'}),
            dcc.Dropdown(queryUniversities(), placeholder="Select University", id="university_selection_to",
                         style={'border': '#AEB6BF'}),
            html.Label('OR', style={'font-family': 'Georgia', 'color': '#F4D03F', 'display': 'block',
                                    'text-align': 'left', 'margin-top': '10px'}),
            dcc.Dropdown(queryFaculties(), placeholder="Select Faculty", id="faculty_selection_to",
                         style={'border': '#AEB6BF'}),
            html.Br(),
            html.Button('Search', id='connection_search', n_clicks=0, className='buttonStyle'),
        ])
    ])
