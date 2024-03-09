import proplot as plt, cmasher as cmr, pandas as pd, numpy as np, os, sys, networkx as nx, warnings

def multilayer_layout(
    G: nx.Graph,
    subset_key="layer",
    layout=nx.spring_layout,
    separation: float = 2.0,
) -> dict:
    # set positions
    layers = {}
    for node, layer in nx.get_node_attributes(G, subset_key).items():
        layers[layer] = layers.get(layer, []) + [node]

    # set layout within each layer
    pos = {}
    for layer, nodes in layers.items():
        subgraph = G.subgraph(nodes)
        layer_pos = {
            node: node_pos + separation * np.array([0, int(layer)])
            for node, node_pos in layout(subgraph).items()
        }
        pos.update(layer_pos)
    return pos


def draw_multilayer_layout(
    G,
    subset_key="layer",
    ax=None,
    layout=nx.spring_layout,
    separation=2.0,
    node_kwargs=dict(node_size=12),
    within_edge_kwargs=dict(style="solid", alpha=0.05),
    between_edge_kwargs=dict(style="dashed", alpha=0.65),
    cmap="Pastel2",
):
    # get the layout
    pos = multilayer_layout(
        G,
        subset_key=subset_key,
        layout=layout,
        separation=separation,
    )

    # find connections between and plot them differently
    connectors = set()
    others = set()
    for node in G.nodes():
        for neighbor in G.neighbors(node):
            if G.nodes[node][subset_key] != G.nodes[neighbor][subset_key]:
                connectors.add((node, neighbor))
            else:
                others.add((node, neighbor))
    # draw the graph
    if ax is None:
        fig, ax = plt.subplots()

    attr = set(nx.get_node_attributes(G, subset_key).values())
    color_space = np.linspace(0, 1, len(attr), 0)
    cmap = cmr.pride(color_space)

    node_colors = [cmap[G.nodes[node]["layer"]] for node in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, **node_kwargs)
    nx.draw_networkx_edges(G, pos, edgelist=others, **within_edge_kwargs)
    nx.draw_networkx_edges(G, pos, edgelist=connectors, **between_edge_kwargs)
    return ax


def disjoint_union_all(Gs: list[nx.Graph]) -> nx.Graph:
    G = Gs[0]
    for Gi in Gs[1:]:
        G = nx.disjoint_union(G, Gi)
    return G


if __name__ == "__main__":
    graphs = []
    for layer in range(3):
        g = nx.erdos_renyi_graph(10, 0.2)
        nx.set_node_attributes(g, layer, "layer")
        graphs.append(g)

    g = disjoint_union_all(graphs)
    from random import sample

    for ni in range(10):
        edge = sample(list(g.nodes()), 2)
        if not g.has_edge(*edge):
            g.add_edge(*edge)

    fig, ax = plt.subplots()
    draw_multilayer_layout(g, ax=ax)
    ax.axis("equal")
    ax.grid(False)

    plt.show(block=1)