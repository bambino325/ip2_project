# This Python file uses the following encoding: utf-8
import sys, os, string
import matplotlib.pyplot as plt
import itertools as it
import networkx as nx
from collections import Counter
from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtCore import QFile, QObject
from PySide2.QtUiTools import QUiLoader
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QDialog, QPushButton
from PyQt5.QtWidgets import QFileDialog

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


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.load_ui()
        self.window.setWindowTitle("Minimal closed transation sets")
        self.connect_ui()


    def init_data(self):
        self.flat_superset = []
        self.transactions = {}
        self.itemset = {}
        self.superset = [['']]
        self.subset_sizes = []
        self.support = {}
        self.frequent = []
        self.closed_itemset = []
        self.min_support = 2



    def connect_ui(self):
        self.window.loadTButton.clicked.connect(self.load_transaction_button_clicked)
        self.window.drawGButton.clicked.connect(self.draw_grid_button_clicked)

    def read_transactions(self):
        fname, _ = QFileDialog().getOpenFileName(None , 'Source Text', '', 'Text files (*.txt)')
        print(fname)
        i = 0
        file = open(fname, "r")
        for line in file:
            # obrada ulaza
            self.transactions[i] = line
            i += 1
        self.window.listWidget3.clear()
        self.window.listWidget3.addItems(self.transactions.values())
        file.close()

    def update_data(self):
        for transaction in self.transactions.values():
            for item in transaction:
                if not item.isalpha():
                    continue
                if item not in self.itemset:
                    self.itemset[item] = 1
                else:
                    self.itemset[item] += 1

        itemset = dict(sorted(self.itemset.items()))

        i = 1
        while (i <= len(itemset)):
            self.superset.append(list(map(''.join,list(it.combinations(self.itemset, i)))))
            i += 1

        for row in self.superset:
            size = 0
            for el in row:
                self.flat_superset.append(el)
                self.support[el] = 0
                size += 1
            self.subset_sizes.append(size)



    def load_transaction_button_clicked(self):
        self.init_data()
        self.window.listWidget1.clear()
        self.window.listWidget4.clear()
        self.read_transactions()
        self.update_data()

    def calculate_support(self):
        pairs = {frozenset(x) for x in self.flat_superset}
        frequnce = Counter(pair for pair in pairs for t in self.transactions.values() if pair.issubset(t))
        for k, v in sorted(frequnce.items()):
            s = ''.join(list(sorted(k)))
            self.support[s] = v

    def closed_sets(self):
        depth = 1
        n = len(self.superset) - 1
        while(depth < n):
            width = 0
            m = len(self.superset[depth])
            while(width < m):
                k = 0
        # za svaki element superset[depth][width] treba proveriti roditelje koji ga sadrze
                closed = True
                l = len(self.superset[depth+1])
                while k < l:
                    if all(x in self.superset[depth+1][k] for x in self.superset[depth][width]):
                        if (self.support[self.superset[depth][width]] == self.support[self.superset[depth+1][k]]):
                            closed = False
                    k += 1

                if closed == True:
                    self.closed_itemset.append(self.superset[depth][width])

                width += 1
            depth += 1

    def max_sets(self):
        for el in reversed(self.flat_superset):
            ind = False
            for freq in self.frequent:
                if all(x in freq for x in el):
                    ind = True
            if ind:
                continue

            if self.support[el] >= self.min_support:
                self.frequent.append(el)

    def draw_grid(self):
        color_map = []
        G = multilayered_graph(*self.subset_sizes)

        mapping = dict(zip(G, self.flat_superset))
        G = nx.relabel_nodes(G, mapping, copy=False)

        G = draw_edges(G, self.superset)

        for el in self.flat_superset:
            if el in self.frequent and el in self.closed_itemset:
                color_map.append('blue')
            elif el in self.frequent:
                color_map.append('red')
            elif el in self.closed_itemset:
                color_map.append('green')
            else:
                color_map.append('lightblue')

        pos = nx.multipartite_layout(G, subset_key="layer", align='horizontal')
        flipped_pos = {node: (-x, -y) for (node, (x, y)) in pos.items()}
        plt.figure(figsize=(14, 6))
        nx.draw(G, flipped_pos, with_labels=True,node_color=color_map, node_size=800)

        plt.show()

    def update_list_widgets(self):
        self.window.listWidget1.clear()
        self.window.listWidget4.clear()
        self.window.listWidget1.addItems(self.frequent)
        self.window.listWidget4.addItems(self.closed_itemset)

    def draw_grid_button_clicked(self):
        self.min_support = int(self.window.support.text())
       # print("draw grid clicked, support is " + self.min_support)
        self.calculate_support()
        self.closed_sets()
        self.max_sets()
        self.draw_grid()
        self.update_list_widgets()


    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "gui/mainwindow.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadWrite)
        self.window = loader.load(ui_file)
        ui_file.close()



    def show(self):
        self.window.show()


if __name__ == "__main__":
    app = QApplication([])
    window = Widget()
    window.show()

    sys.exit(app.exec_())


