import networkx as nx
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from helper_functions import add_logo
import gc
from st_cytoscape_extra import cytoscape

st.set_page_config(
    page_title="Static 2D Example",
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

# Create some simple graph data
nodes = {'ID':['1','2','3','4','5'],
         'Label':['Aspirin','Paracetamol','Ibuprofen','Codeine','Naproxen'],
         'Size': [50,60,75,40,100],
         'Color': ['#2c96c7','#32a852','#bd132f','#e6c315','#e315e6']}
edges = {'Source':['1','1','2','2','3','3','4','4','5','5'],
         'Target':['2','3','3','4','4','5','5','1','1','2'],
         'Weight':[3,6,4,7,8,2,4,3,2,5]}

nodes = pd.DataFrame(nodes)
edges = pd.DataFrame(edges)

nodeData = nodes
edgeData = edges

#Create graph function - networkX
def create_graph(nodeData, edgeData):
    ## Initiate the graph object
    G = nx.DiGraph()
    
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

    sizeDicts = {}
    sizeDicts.update(zip(nodeData['ID'], nodeData['Size']))

    colorDicts = {}
    colorDicts.update(zip(nodeData['ID'], nodeData['Color']))

    nx.set_node_attributes(G, sizeDicts, "Size")
    nx.set_node_attributes(G, colorDicts, "Color")

    return G

# Create the graph object
G = create_graph(nodes,edges)
# Define the node positions
# pos = nx.circular_layout(G)
# Define the attribute inputs



# e_size = nx.get_edge_attributes(G,'Weight')
e_col = np.array(['#2c96c7','#32a852',
                  '#bd132f','#e6c315',
                  '#e315e6','#2c96c7',
                  '#32a852','#bd132f',
                  '#e6c315','#e315e6'])
shape = 'D'
alpha = 0.8
# Draw the graph and add edge labels
# nx.draw_networkx_edge_labels(G,pos,edge_labels=e_size)

# Has to be written in this way to be threadsafe for streamlit
# if you just try to use the original code of 
# plot = nx.draw(G, pos, node_size=n_size, node_color=n_col, node_shape=shape, alpha=alpha, edge_color=e_col,arrows=True)
# st.pyplot(plot)
# You will receive a warning as this is a deprecated approach 

# fig, ax = plt.subplots()

# ax = nx.draw(G, pos, node_size=n_size, node_color=n_col, node_shape=shape, alpha=alpha, edge_color=e_col,arrows=True)

# st.pyplot(fig)

G_cs = nx.cytoscape_data(G)

elements = G_cs['elements']


stylesheet = [
    {
        "selector": "node", 
        "style": {
            "label": "data(Label)", 
            "width": "data(Size)", 
            "height": "data(Size)",
            "background-color": "data(Color)"
            
            }
        },

    {
        "selector": "edge",
        "style": {
            "width": 'data(Weight)',
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
        },
    },

    # {
    #     "layout": {
    #         # 'EdgeLength': length,
    #         'maxSimulationTime': 8000,
    #         'convergenceThreshold': 0.001,
    #         'nodeOverlap': 20,
    #         'refresh': 20,
    #         'fit': True,
    #         'padding': 30,
    #         'randomize': True,
    #         'componentSpacing': 100,
    #         'nodeRepulsion': 400000,
    #         'edgeElasticity': 100000,
    #         'nestingFactor': 5,
    #         'gravity': 80,
    #         'numIter': 1000,
    #         'initialTemp': 200,
    #         'coolingFactor': 0.95,
    #         'minTemp': 1.0
    #     }
    # }
]

layout = st.radio(label="Select layout",
                  options=["fcose", "random", "grid", "circle", "concentric",
                           "breadthfirst", "cose", "klay"], horizontal=True)

selected = cytoscape(elements, 
                     stylesheet, 
                     key="graph", 
                     layout={"name": layout}, 
                     height="500px")
