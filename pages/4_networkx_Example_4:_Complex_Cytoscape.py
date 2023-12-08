import networkx as nx
import pandas as pd
import numpy as np
import streamlit as st
from helper_functions import add_logo
import gc
# from st_cytoscape import cytoscape
from st_cytoscape_extra import cytoscape
import dash_cytoscape as cyto

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

# t1 = [(list(i)) for i in c]


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

    return G, c

# Create the graph object
G, c = create_graph(nodes,edges)
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
    """)


tab1, tab2, tab3 = st.tabs(["Edge Weight and Total Interaction Filtering", 
                            "Filter to Node Neighbourhood",
                    # "Minimum Spanning Trees Pruning", 
                    "Network Metrics"])

layout_options_list = ["cise", "fcose", "circle", "random", "grid", "concentric",
                           "breadthfirst", "cose", "klay", 
                           "avsdf", "elk","dagre", "cola", 
                            "spread"
                        # , "euler"
                           ]
with tab1:
    st.markdown("""
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
                    options=layout_options_list,
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
                "background-color": "data(CommunityColor)",
                # "transparency": f'mapData(Weight, 0, {max(bb)}, 0.4, 1)'
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
        }
    ]


    # Deal with the output on the page

    st.subheader("Interactions between characters in Game of Thrones - Series 1")

    if layout == "cise": 
        t1 = [(list(i)) for i in c]
        #[leaf for branch in tree for leaf in branch]
        clusters = [[node for node in t1[i] if node in list(G4.nodes)] for i in range(len(t1))]
        layout_dict = {"name": layout, 
                       "clusters": clusters}
    else:
        layout_dict = {"name": layout}

    selected = cytoscape(elements, 
                        stylesheet, 
                        key="graph", 
                        layout=layout_dict, 
                        height="900px")
   
    st.markdown(f"""
        Links representing fewer than {min_threshold_weight} interactions have been removed from this graph. 
        
        Characters with fewer than than {min_total_interactions} interactions have been removed from this graph. 

        {len(G4.nodes)} of {len(nodes)} nodes in original dataset displayed after filtering.

        **Interpret with caution.**

        """)

# Add ability to filter down to just the network for an individual
with tab2: 
    st.subheader("Show full network for particular characters")

    layout2 = st.radio(label="Select layout of filtered graph",
                    options=layout_options_list,
                    horizontal=True)

    character_filter = st.selectbox("Select characters to include (ordered in descending order starting with characters with the most total interactions)",
                options=nodes.sort_values("TotalInteractions", ascending=False)['ID'].drop_duplicates().tolist(),
                format_func=lambda x: x.title().replace("_", " "))


    def filter_node_neighbour(n1):

        return (character_filter in nx.all_neighbors(G, n1)) or (n1 == character_filter)


    G5 = nx.subgraph_view(G, 
                        filter_node=filter_node_neighbour)


    bb = nx.betweenness_centrality(G5).values()

    stylesheet = [
        {
            "selector": "node", 
            "style": {
                "label": "data(Label)", 
                "width": f"mapData(Size, {min(bb)}, {max(bb)}, 3, 15)", 
                "height": f"mapData(Size, {min(bb)}, {max(bb)}, 3, 15)",
                "font-size": "8px",
                "background-color": "data(CommunityColor)",
                # "transparency": f'mapData(Weight, 0, {max(bb)}, 0.4, 1)'
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
        }
     ]
    



    if layout2 == "cise": 
        t1 = [(list(i)) for i in c]
        #[leaf for branch in tree for leaf in branch]
        clusters = [[node for node in t1[i] if node in list(G5.nodes)] for i in range(len(t1))]

        layout_dict = {"name": layout2, "clusters": clusters}
    else:
        layout_dict = {"name": layout2}

    st.markdown(f"{character_filter} interacts with {len(G5.nodes)} characters ({round((len(G5.nodes)/len(G.nodes))*100, 2)}%) of a total of {len(G.nodes)} who appear in this season.")

    st.markdown(f"They had {nodes[nodes['ID'] == character_filter]['TotalInteractions'].values[0]} interactions in total.")

    selected = cytoscape(nx.cytoscape_data(G5)['elements'], 
                        stylesheet, 
                        key="graph_neighbour", 
                        layout=layout_dict, 
                        height="900px")

# with tab3:
#     st.subheader("Pruning with Minimum Spanning Trees Algorithm")

#     layout3 = st.radio(label="Select layout for minimum spanning tree graph",
#                     options=layout_options_list,
#                     horizontal=True)

#     T = nx.minimum_spanning_tree(G)

#     Ti = T.copy()
#     Ti.remove_nodes_from(list(nx.isolates(Ti)))

#     st.markdown(f"{len(Ti.nodes)} nodes remaining of {len(G.nodes)} after MST algorithm applied.")

#     stylesheet = [
#         {
#             "selector": "node", 
#             "style": {
#                 "label": "data(Label)", 
#                 "width": f"mapData(Size, {min(bb)}, {max(bb)}, 3, 15)", 
#                 "height": f"mapData(Size, {min(bb)}, {max(bb)}, 3, 15)",
#                 "font-size": "8px",
#                 "background-color": "data(CommunityColor)",
#                 # "transparency": f'mapData(Weight, 0, {max(bb)}, 0.4, 1)'
#                 }
#             },

#         {
#             "selector": "edge",
#             "style": {
#                 "width": f'mapData(Weight, 1, {edges["Weight"].max()}, 0.1, 5)',
#                 "curve-style": "bezier",
#                 "opacity": f'mapData(Weight, 0, {edges["Weight"].max()}, 0.4, 1)'
#                 #"target-arrow-shape": "triangle",
#                 #"arrow-scale": f'mapData(Weight, 1, {edges["Weight"].max()}, 0.1, 1)'
#             },
#         }
#      ]
    
#     if layout3 == "cise": 
#         t1 = [(list(i)) for i in c]
#         #[leaf for branch in tree for leaf in branch]
#         clusters = [[node for node in t1[i] if node in list(Ti.nodes)] for i in range(len(t1))]
#         layout_dict = {"name": layout3, 
#                        "clusters": clusters}
#     else:
#         layout_dict = {"name": layout3}


#     selected = cytoscape(nx.cytoscape_data(T)['elements'], 
#                         stylesheet, 
#                         key="graph_mst", 
#                         layout=layout_dict, 
#                         height="900px")

with tab3:
    st.subheader("Graphs of network metrics")

