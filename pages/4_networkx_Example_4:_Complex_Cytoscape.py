import networkx as nx
import pandas as pd
import numpy as np
import streamlit as st
from helper_functions import add_logo
import gc
from st_cytoscape import cytoscape

st.set_page_config(
    page_title="Interactive 2D Example - Complex",
    # page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

st.title("Static 2D Example: networkx and matplotlib")

gc.collect()


st.markdown(
    """
    This is an example of an interactive 2d plot where individual nodes can be selected.
    
    The underlying graph code is from 
    
    https://github.com/hsma-programme/4d_advanced_network_analysis_pt2/blob/main/code_along/networkx_vis_example.py
    
    The visualisation implementation is done with st-cytoscape
    
    https://github.com/vivien000/st-cytoscape
    """
)

edges = pd.read_csv("data/got-s1-edges.csv")
nodes = pd.read_csv("data/got-s1-nodes.csv").rename(columns={"Id": "ID"})

total_interactions_node = pd.concat([edges[['Source', 'Weight']].groupby('Source').sum().reset_index(drop=False),
                                     edges[['Target', 'Weight']].groupby('Target').sum().reset_index(drop=False).rename(columns={'Target':'Source'})]
                                     ).groupby('Source').sum().rename(columns={'Weight':'TotalInteractions'})

nodes = nodes.merge(total_interactions_node, how="left", left_on="ID", right_on="Source")
# Create some simple graph data
# nodes = {'ID':['1','2','3','4','5'],
#          'Label':['Aspirin','Paracetamol','Ibuprofen','Codeine','Naproxen'],
#          'Size': [50,60,75,40,100],
#          'Color': ['#2c96c7','#32a852','#bd132f','#e6c315','#e315e6']}
# edges = {'Source':['1','1','2','2','3','3','4','4','5','5'],
#          'Target':['2','3','3','4','4','5','5','1','1','2'],
#          'Weight':[3,6,4,7,8,2,4,3,2,5]}

# nodes = pd.DataFrame(nodes)
# edges = pd.DataFrame(edges)

nodeData = nodes
edgeData = edges

#Create graph function - networkX
def create_graph(nodeData, edgeData):
    ## Initiate the graph object
    G = nx.Graph()
    # G = nx.DiGraph()
    
    ## Tranform the data into the correct format for use with NetworkX
    
    # Node tuples (ID, dict of attributes)
    idList = nodeData['ID'].tolist()
    
    labels =  pd.DataFrame(nodeData['Label'])
    labelDicts = labels.to_dict(orient='records')

    nodeTuples = [tuple(r) for r in zip(idList,labelDicts)]
    
    
    # Edge tuples (Source, Target, dict of attributes)
    sourceList = edgeData['Source'].tolist()
    targetList = edgeData['Target'].tolist()
    
    weights = pd.DataFrame(edgeData['Weight'])
    weightDicts = weights.to_dict(orient='records')
    
    edgeTuples = [tuple(r) for r in zip(sourceList,targetList,weightDicts)]
    
    ## Add the nodes and edges to the graph
    G.add_nodes_from(nodeTuples)
    G.add_edges_from(edgeTuples)

    totalInteractionsDicts = {}
    totalInteractionsDicts.update(zip(nodeData['ID'], nodeData['TotalInteractions']))
    nx.set_node_attributes(G, totalInteractionsDicts, "TotalInteractions")

    # colorDicts = {}
    # colorDicts.update(zip(nodeData['ID'], nodeData['Color']))
    bb = nx.betweenness_centrality(G)
    nx.set_node_attributes(G, bb, "Size")

    c = nx.community.greedy_modularity_communities(G)

    community_dict = pd.DataFrame(c).reset_index(drop=False).melt(id_vars="index")[['value','index']]
    community_dict = community_dict[community_dict['value'].notnull()]
    communityDicts = {}
    communityDicts.update(zip(community_dict['value'], community_dict['index']))

    nx.set_node_attributes(G, communityDicts, "Community")

    color_df = pd.DataFrame(
        [{'index': 0, 'color': "#fbf59a"},
        {'index': 1, 'color': "#674ea7"},
        {'index': 2, 'color': "#72a45d"},
        {'index': 3, 'color': "#f2600b"},
        {'index': 4, 'color': "#2986cc"}]
    )

    community_dict = community_dict.merge(color_df, how="left", on="index")

    communityColorDicts = {}
    communityColorDicts.update(zip(community_dict['value'], community_dict['color']))

    nx.set_node_attributes(G, communityColorDicts, "CommunityColor")
    # nx.set_node_attributes(G, colorDicts, "Color")

    return G

# Create the graph object
G = create_graph(nodes,edges)
# Define the node positions
# pos = nx.circular_layout(G)
# Define the attribute inputs

st.markdown(
    """
    Node size reflects betweenness centrality.
   
    Betweenness centrality is 'a widely used measure that captures a person's role in allowing information to pass from one part of the network to the other.'
    
    [Source](https://www.sciencedirect.com/topics/computer-science/betweenness-centrality)
    
    Colour reflects group membership. 

    Communities were detected using Clauset-Newman-Moore modularity maximisation. 
    
    [Source](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.modularity_max.greedy_modularity_communities.html) 
    
    Filtering is done on the weight of the edges (in this case, number of interactions between characters)

    If there are no remaining links after filtering, the node is removed from the dataset.


    **Filtering should be used with caution.** 
    
    In a directional graph, filtering of weights is done per direction and could lead to some very misleading outputs - for example, if A --> B has a weight of 99, but B --> A has a weight of 101 and your threshold is 100, you'd lose the A --> B connection while it would look like B --> A mattered.
    
    In an undirected graph, it may give the impression that two characters have never interacted with each other.

    
    
    Game of thrones data from [this repo](https://github.com/hsma-programme/4d_advanced_network_analysis_pt2/tree/main/data)
    """
)



# add streamlit inputs
layout = st.radio(label="Select layout",
                  options=["fcose", "circle", "random", "grid", "concentric",
                           "breadthfirst", "cose", "klay"],
                  horizontal=True)

min_threshold_weight = st.slider(
    "Filter out edges that don't meet this threshold weight", 
    int(1),
    int(edges["Weight"].max())
    )

# Define the edge filter 
def filter_edge(n1, n2):

    return G[n1][n2]['Weight'] >= min_threshold_weight

G2 = nx.subgraph_view(G, 
                     filter_edge=filter_edge)

# Remove any nodes that now don't meet the weight threshold
# Have to take a copy of the graph first because the output of the 
# filter step is read only
G3 = G2.copy()
G3.remove_nodes_from(list(nx.isolates(G3)))



min_total_interactions = st.slider(
    "Filter out characters with fewer than a threshold number of interactions", 
    int(1),
    int(nodes["TotalInteractions"].max())
    )

# Define the edge filter 
def filter_node(n1):

    return G.nodes[n1]['TotalInteractions'] >= min_total_interactions

G4 = nx.subgraph_view(G3, 
                     filter_node=filter_node)


G_cs = nx.cytoscape_data(G4)

bb = nx.betweenness_centrality(G4).values()

elements = G_cs['elements']

# This is a nice example of how to adjust the stylesheet
# https://github.com/cytoscape/cytoscape.js/blob/master/documentation/demos/colajs-graph/cy-style.json
stylesheet = [
    {
        "selector": "node", 
        "style": {
            "label": "data(Label)", 
            "width": f"mapData(Size, {min(bb)}, {max(bb)}, 3, 15)", 
            "height": f"mapData(Size, {min(bb)}, {max(bb)}, 3, 15)",
            "font-size": "8px",
            "background-color": "data(CommunityColor)"
            
            }
        },

    {
        "selector": "edge",
        "style": {
            "width": f'mapData(Weight, 1, {edges["Weight"].max()}, 0.1, 5)',
            "curve-style": "bezier",
            "opacity": f'mapData(Weight, 0, {edges["Weight"].max()}, 0.4, 1)'
            #"target-arrow-shape": "triangle",
            #"arrow-scale": f'mapData(Weight, 1, {edges["Weight"].max()}, 0.1, 1)'
        },
    },

    # {
    #     "layout": {
    #         # 'EdgeLength': length,
    #         # 'maxSimulationTime': 8000,
    #         # 'convergenceThreshold': 0.001,
    #         # 'nodeOverlap': 20,
    #         # 'refresh': 20,
    #         # 'fit': True,
    #         # 'padding': 30,
    #         # 'randomize': True,
    #         # 'componentSpacing': 100,
    #         'nodeRepulsion': 400,
    #         # 'edgeElasticity': 100000,
    #         # 'nestingFactor': 5,
    #         # 'gravity': 80,
    #         # 'numIter': 1000,
    #         # 'initialTemp': 200,
    #         # 'coolingFactor': 0.95,
    #         # 'minTemp': 1.0
    #     }
    # }
]


# Deal with the output on the page

st.subheader("Interactions between characters in Game of Thrones - Series 1")

layout2 = st.radio(label="Select layout of filtered graph",
                  options=["fcose", "circle", "random", "grid", "concentric",
                           "breadthfirst", "cose", "klay"],
                  horizontal=True)



selected = cytoscape(elements, 
                     stylesheet, 
                     key="graph", 
                     layout={"name": layout}, 
                     height="900px")

st.markdown(f"""
    Links representing fewer than {min_threshold_weight} interactions have been removed from this graph. 
    
    Characters with fewer than than {min_total_interactions} interactions have been removed from this graph. 

    {len(G4.nodes)} of {len(nodes)} nodes in original dataset displayed after filtering.

    **Interpret with caution.**

    """)




# Add ability to filter down to just the network for an individual

st.subheader("Show full network for particular characers")

character_filter = st.selectbox("Select characters to include",
             options=nodes['ID'].drop_duplicates().tolist(),
             format_func=lambda x: x.title().replace("_", " "))


def filter_node_neighbour(n1):

    return (character_filter in nx.all_neighbors(G, n1)) or (n1 == character_filter)


G5 = nx.subgraph_view(G, 
                     filter_node=filter_node_neighbour)


bb = nx.betweenness_centrality(G5).values()

selected = cytoscape(nx.cytoscape_data(G5)['elements'], 
                     stylesheet, 
                     key="graph_neighbour", 
                     layout={"name": layout2}, 
                     height="900px")
