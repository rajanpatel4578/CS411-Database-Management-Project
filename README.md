# PawanTare_RajanPatel

## Title: My Academic World

**Purpose**: The 'My Academic World' application is designed for users interested in academia who wish to have a centralized dashboard giving them the option to create a profile and track their research and publication progress.
The academic world dashboard can be very useful for students, faculties, industry research personal and any user in general such as publication staff, technical writers etc.
Main objective of the Academic world application is to present its users with ongoing trends, useful search capabilities to fine tune their profile by saving the search results in an organized manner. Additionally, the dashboard help user organize their ongoing work items in an efficient manner.
The dashboard also finetunes its recommendation by smartly using the user's profile and presents the user with top recommendations based on their research work and interests.

**Demo**: Even though the dashboard application is designed to be simple and easy to user, a short demo about how one can make the best use of the 'My Academic World' application is available here:https://mediaspace.illinois.edu/media/t/1_hiq6shdx

**Installation**: Because the 'My Academic World' makes use of the academic world databases in three different database technologies, primarily RDBMS, DocumentDB and GraphDB, it needs the source databases provisioned as following.
| Database | Connection details | Comments |
| --- | --- | --- |
| RDBMS | MySQL database of the Academic world with user credentials root:password (username:password)  host:'localhost' port:'3306' | source the mysql.sql by downloading from the source repository to create tables, views and constraints. i.e. user specific tables, views and triggers created in the MySQL database  |
| MongoDB | Document database for academic world with default settings. host:'localhost' port:'27017' | MongoDB Index: Creating an index over publications helps expedite the queries and hence following instruction should be executed inside mongo shell (mongosh) : db.publications.createIndex({keywords:1}) |
| Neo4J | Graph database with standard credentials neo4j:password (username:password) host:'localhost' port:'7687' | |

In addition to the above, the 'My Academic World' application also needs styles.css file (available in source repository) which contains the required CSS style definitions and is vital for the layout of the application and hence shall be copied under the 'assets' directory under the Dash workspace.


**Usage**: Upon loading the 'My Academic World' application, it presents the user with standard recommendations based on the research trends, publications, and their citations along with the keywords, universities, and faculties associated with those.
The default layout of the 'My Academic World' application populates the widgets such as 'Most cited publications', 'Top faculties by most citations', 'Top universities by most trending keywords in past 5 years', 'University Research Trends By Keyword', 'Academic Connection Finder' and 'Trending Keywords'
The initial screen also populates 'My Dashboard' widget which provides with an input box for username, if the user profile does not exist yet, the application allows the user to create the new profile and enables the load button.
Upon loading the user profile, the 'Reload' and 'Delete' buttons are enabled for the user profile widget and following 3 widgets are presented to end user to work on enriching their profile.
'My Favorites' widget: This widget is meant to help user organize their interests by allowing user to create a list of their favorite keywords, publications, and faculties in the field of their interest.
'My Collaborations' widget: This widget helps user save their ongoing work in the field of their interest and also allows them to enrich their profile with their current and past collaborations with universities, faculties etc.
The most important feature of the 'My Collaborations' widget is it allows the user to save their work in progress and offers with a backend database with complete control over Create, Read, Update and Delete functionalities.
Once the user's profile is successfully loaded, all the widgets on the 'My Academic World' application will be fine-tuned based on the user's interest's data collected from their profile.


**Design**: The application makes use of the strengths from each of database technologies it uses in the backend. For example, to maintain user profiles and all associated CRUD functionalities it uses the MySQL database, to populate recommendation about the publications, universities associated with their work and interests it uses the strengths of MongoDB (document database).
To help user connect to another entity such as faculties, universities which may be important association for their research work, it offers a connection finder widget which makes best use of strengths of the GraphDB such as Neo4j.

**Implementation**: The 'My Academic World' application uses the strengths and simplicity of Dash Plotly framework for the user interface design, for querying MySQL database it uses the 'SQLAlchemy' interface package which offers reliable connection and querying of the MySQL database in the backend.
For connecting to MongoDB it uses 'pymongo' package offered by Python and similarly for connecting to Neo4j it uses the 'neo4j' package from python library.
Additionally, to populate the connections it uses the 'dash_cytoscape' package, to populate the graphs it uses 'plotly.express' package from Dash Plotly framework.

**Database Techniques**: We used Indexing, Views, Constraints, Triggers, Prepared statements to query, create, update, delete operation of the database in the most efficient manner.

**Extra-Credit Capabilities**: The project has following extra credit capabilities:

| Sr. No | Description |
| --- | --- |
| 1 | The user profile creation, update, deletion widget which offers the user with complete control over personalizing their profile and make best use of academic world database. In addition, users can use the profile to keep track of their interests and ongoing work. |
| 2 | Most of the recommendation widgets in the 'My Academic World' application use the strengths of each database type and hence combines the queries by chaining them to generate the recommendations in the most efficient manner. |
| 3 | Using the RDBMS backend database capabilities, the dashboard provides functionality for reloading and deleting user profiles in a manner that is efficient. Deleted user profiles also have an audit log feature that records the timestamp as well as the user who deleted them. |
| 4 | Application widgets and data/recommendations are tailored to match a user's profile and interests in order to provide a better end-user experience. |
| 5 | It offers creative widgets such as 'Search by keyword' which not only presents the user with matching publications but also allows the user to add the selective search results to their favorites. |

Overall, the 'My Academic World' application offers variety of creative widgets which help them to be productive and at the same time uses their profile data to create recommendations which can be very useful to them based on the ongoing update to the academic world database.


**Contributions**:The project was done by Pawan and Rajan using a divide and concur approach to accomplish the completion of more than 9 widgets to build the application which helped both to learn and apply the knowledge acquired from the content of the course 'CS 411: Database Systems
'.

Following are the key areas handled by each of the team member in this project.

| Team Member | UIUC ID | Widgets | Hours Spent |
| --- | --- | --- | --- |
| Pawan Tare | ptare2 | My Dashboard, My Favourites, My Collaboartions, Search by keywords, Top Faculties, Top Universities, Top Publications | 50 hours |
| Rajan Patel | rajansp2 | Academic Connection Finder, University Research Trends, Trending Keywords | 28-30 hours total |

Detailed efforts are listed below

Pawan: Overall layout and design of the application along with its styling using CSS, designed and developed the user’s database in MySQL, efficiently using strengths of each database to populate the recommendations using the data from the user's profile, implemented the user dashboard profile creation, loading, reloading, and delete functionality. Implemented the widgets for 'My Dashboard', 'My Favorites', 'My Collaborations', 'Search by keywords', 'Top faculties', 'Top Universities', 'Top publications'.

Rajan: Collaborating with Pawan on the layout of the dashboard, researching different CSS styles to make widgets look appealing as well as comprehensible, Research on Graph database and its presentation on the dashboard using dash_Cytoscape library to display widget 'Academic Connections Finder', display scatter plot widgets for 'University Research Trends', setup 'Trending Keywords' widget usign RDBMS views and additionally incorporating changes to 'Academic Connections Finder' widget based on user's profile. Rajan ended up spending roughly 10 hours on coding the functionalities and 18-20 hours on researching, debugging, styling the dashboard and preparing the documentation. 
