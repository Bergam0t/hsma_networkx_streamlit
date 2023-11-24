import networkx as nx
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from helper_functions import add_logo
import gc

st.set_page_config(
    page_title="Semi-Interactive 2D Example",
    # page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

st.title("Semi-Interactive 2D Example: networkx and plotly")

gc.collect()

st.markdown(
    """
    This is just the networkx plotly example from the plotly documentation. 
    
    https://plotly.com/python/network-graphs/
    """
)

# # Create some simple graph data
# nodes = {'ID':['1','2','3','4','5'],
#          'Label':['1','2','3','4','5']}
# edges = {'Source':['1','1','2','2','3','3','4','4','5','5'],
#          'Target':['2','3','3','4','4','5','5','1','1','2'],
#          'Weight':[3,6,4,7,8,2,4,3,2,5]}

# nodes = pd.DataFrame(nodes)
# edges = pd.DataFrame(edges)

# #Create graph function - networkX
# def create_graph(nodeData, edgeData):
#     ## Initiate the graph object
#     G = nx.DiGraph()
    
#     ## Tranform the data into the correct format for use with NetworkX
#     # Node tuples (ID, dict of attributes)
#     idList = nodeData['ID'].tolist()
#     labels =  pd.DataFrame(nodeData['Label'])
#     labelDicts = labels.to_dict(orient='records')
#     nodeTuples = [tuple(r) for r in zip(idList,labelDicts)]
    
#     # Edge tuples (Source, Target, dict of attributes)
#     sourceList = edgeData['Source'].tolist()
#     targetList = edgeData['Target'].tolist()
#     weights = pd.DataFrame(edgeData['Weight'])
#     weightDicts = weights.to_dict(orient='records')
#     edgeTuples = [tuple(r) for r in zip(sourceList,targetList,weightDicts)]
    
#     ## Add the nodes and edges to the graph
#     G.add_nodes_from(nodeTuples)
#     G.add_edges_from(edgeTuples)
    
#     return G

# # Create the graph object
# G = create_graph(nodes,edges)
# # Define the node positions
# pos = nx.circular_layout(G)


G = nx.random_geometric_graph(200, 0.125)

edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = G.nodes[edge[0]]['pos']
    x1, y1 = G.nodes[edge[1]]['pos']
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

node_x = []
node_y = []
for node in G.nodes():
    x, y = G.nodes[node]['pos']
    node_x.append(x)
    node_y.append(y)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        # colorscale options
        #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
        colorscale='YlGnBu',
        reversescale=True,
        color=[],
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        ),
        line_width=2))


node_adjacencies = []
node_text = []
for node, adjacencies in enumerate(G.adjacency()):
    node_adjacencies.append(len(adjacencies[1]))
    node_text.append('# of connections: '+str(len(adjacencies[1])))

node_trace.marker.color = node_adjacencies
node_trace.text = node_text

fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='<br>Network graph made with Python',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

st.plotly_chart(fig,
                use_container_width=True)