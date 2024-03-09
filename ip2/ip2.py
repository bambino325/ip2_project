import string
import matplotlib.pyplot as plt
import itertools as it
import networkx as nx
from collections import Counter

def add_edges(layer1, layer2):
    result = []
    for l2 in layer2:
        for l1 in layer1:
            if (all(x in l2 for x in l1)):
                result += zip([l1], [l2])
    return result


def multilayered_graph(*subset_sizes):
    extents = nx.utils.pairwise(it.accumulate((0,) + subset_sizes))
    layers = [range(start, end) for start, end in extents]
    G = nx.MultiGraph()

    for i, layer in enumerate(layers):
        G.add_nodes_from(layer, layer=i)

    return G

def draw_edges(G, layers):

    for layer1, layer2 in nx.utils.pairwise(layers):
        G.add_edges_from(add_edges(layer1, layer2))

    return G

flat_superset = []
transactions = {}
itemset = {}
superset = [['']]
subset_sizes = []
support = {}
frequent = []
closed_itemset = []

#min_support = int(input("Enter minimum support:\n"))
min_support = 2

i = 0
print("Enter transaction or q for end:")
while True:
    data = str(input())
    i += 1
    if(data == "q"):
        break
    else:
        transactions[i] = data


for transaction in transactions.values():
    for item in transaction:
        if not item.isalpha():
            continue
        if item not in itemset:
            itemset[item] = 1
        else:
            itemset[item] += 1

itemset = dict(sorted(itemset.items()))


i = 1
while (i <= len(itemset)):
    superset.append(list(map(''.join,list(it.combinations(itemset, i)))))
    i += 1

for row in superset:
    size = 0
    for el in row:
        flat_superset.append(el)
        support[el] = 0
        size += 1
    subset_sizes.append(size)


## TODO : dovde sam stigo


#       support
    
pairs = {frozenset(x) for x in flat_superset}
frequnce = Counter(pair for pair in pairs for t in transactions.values() if pair.issubset(t))
for k, v in sorted(frequnce.items()):
    s = ''.join(list(sorted(k)))
    support[s] = v

# for k,v in support.items():
#     print(k, v)


##      zatvoreni skupovi

depth = 1
while(depth < (len(superset)-1)):
    width = 0
    while(width < len(superset[depth])):
# za svaki element superset[depth][width] treba proveriti roditelje koji ga sadrze
# ako nadskup ima podrsku 0 nisam zatvoren
        k = 0
        closed = True
        while k < len(superset[depth+1]):
            if all(x in superset[depth+1][k] for x in superset[depth][width]):
                if (support[superset[depth][width]] == support[superset[depth+1][k]]):
                    closed = False
            k += 1
        
# proveriti i  sve sinove da li imaju manju podrsku
        # p = 0
        # subset_closed = True
        # while p < len(superset[depth-1]):
        #     if all(x in superset[depth][width] for x in superset[depth-1][p]):
        #         if (support[superset[depth][width]] >= support[superset[depth-1][p]]):
        #             subset_closed = False    
        #     p += 1

        if closed == True:  #and subset_closed == True:
            closed_itemset.append(superset[depth][width])

        width += 1
    depth += 1


##      maksimalni skupovi
    
for el in reversed(flat_superset):

    ind = False
    for freq in frequent:
        if all(x in freq for x in el):
            ind = True
            
    if ind:
        continue

    if support[el] >= min_support:
        frequent.append(el)
        #print(el)

# for k,v in support.items():
#     print(k, v)

color_map = []
G = multilayered_graph(*subset_sizes)

mapping = dict(zip(G, flat_superset))
G = nx.relabel_nodes(G, mapping, copy=False)

G = draw_edges(G, superset)

for el in flat_superset:
    if el in frequent and el in closed_itemset:
        color_map.append('blue')
    elif el in frequent:
        color_map.append('red')
    elif el in closed_itemset:
        color_map.append('green')
    else:
        color_map.append('lightblue')

pos = nx.multipartite_layout(G, subset_key="layer", align='horizontal')
flipped_pos = {node: (-x, -y) for (node, (x, y)) in pos.items()}
plt.figure(figsize=(14, 6))
nx.draw(G, flipped_pos, with_labels=True,node_color=color_map, node_size=800)

plt.show()

#plt.legend(['Cesti'])

#for i in itemset:
 #   print(i + " : " + str(itemset[i]))

