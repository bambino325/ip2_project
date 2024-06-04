# This Python file uses the following encoding: utf-8
import sys, os
import matplotlib.pyplot as plt
import itertools as it
import networkx as nx
from matplotlib.lines import Line2D
from collections import Counter
from PySide2.QtWidgets import QApplication, QWidget, QMessageBox, QFileDialog
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader


# povezivanje odgovarajucih cvorova
# prilikom dodavanja veza treba obratiti
# paznju da je skup povezan samo sa nadskupovima
def add_edges(layer1, layer2):
    result = []
    for l2 in layer2:
        for l1 in layer1:
            if (all(x in l2 for x in l1)):
                result += zip([l1], [l2])
    return result

# kreiranje grafa na osnovu date velicine
def multilayered_graph(*subset_sizes):
    extents = nx.utils.pairwise(it.accumulate((0,) + subset_sizes))
    layers = [range(start, end) for start, end in extents]
    G = nx.MultiGraph()

    for i, layer in enumerate(layers):
        G.add_nodes_from(layer, layer=i)
    return G

# povezivanje nivoa
def draw_edges(G, layers):
    for layer1, layer2 in nx.utils.pairwise(layers):
        G.add_edges_from(add_edges(layer1, layer2))
    return G


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.load_ui()
        self.window.setWindowTitle("Maximum closed transation sets")
        self.connect_ui()

    def init_data(self):
        self.flat_superset = []
        self.transactions = {}
        self.itemset = {}
        self.superset = [['']]
        self.subset_sizes = []
        self.support = {}
        self.frequent = []
        self.max_frequent = []
        self.closed_itemset = []
        self.min_support = 2

    def connect_ui(self):
        self.window.loadTButton.clicked.connect(self.load_transaction_button_clicked)
        self.window.drawGButton.clicked.connect(self.draw_grid_button_clicked)

    # ucitavanje skupa transakcija iz fajla
    def read_transactions(self):
        fname, _ = QFileDialog().getOpenFileName(None , 'Source Text', '', 'Text files (*.txt)')
        i = 0
        try:
            with open(fname, "r") as file:
                for line in file:

                    self.transactions[i] = line
                    i += 1
        except Exception as e:
            QMessageBox.critical(None, 'Error', f'Error reading file: {str(e)}')
            return
        self.window.listWidget3.clear()
        for key, transaction in self.transactions.items():
            item_text = f"{key+1}: {transaction}"
            self.window.listWidget3.addItem(item_text)

    # u itemsetu se cuvaju pojedinacne stavke
    def update_data(self):
        for transaction in self.transactions.values():
            for item in transaction:
                if not item.isalpha():
                    continue
                if item not in self.itemset:
                    self.itemset[item] = 1
                else:
                    self.itemset[item] += 1

        self.itemset = dict(sorted(self.itemset.items()))

        # generisanje svih kombinacija stavki razlicitih duzina
        i = 1
        while (i <= len(self.itemset)):
            self.superset.append(list(map(''.join, sorted(list(it.combinations(self.itemset, i))))))
            i += 1

        # izdvajanje podataka u potrebne kolekcije
        # subset_sizes cuva velicinu svakog nivoa resetka,
        # (potrebno za crtanje)
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
        self.window.listWidget2.clear()
        self.window.listWidget4.clear()
        self.read_transactions()
        self.update_data()

    #izdvajanje cestih skupova stavki
    def calculate_support(self):
        pairs = {frozenset(x) for x in self.flat_superset}
        frequnce = Counter(pair for pair in pairs for t in self.transactions.values() if pair.issubset(t))
        for k, v in sorted(frequnce.items()):
            s = ''.join(list(sorted(k)))
            self.support[s] = v
            if v >= self.min_support:
                self.frequent.append(s)

    def closed_sets(self):
        depth = 1
        while (depth < (len(self.superset)-1)):
            width = 0

            #   za svaki element superset[depth][width]
            #   treba proveriti da li neki njegov neposredni nadskup (depth+1)
            #   ima istu podrsku, ako ima onda nije zatvoren

            while (width < len(self.superset[depth])):
                el = self.superset[depth][width]
                k = 0
                closed = True

                #   ova petlja prolazi kroz nadskupove
                while k < len(self.superset[depth+1]):
                    if all(x in self.superset[depth+1][k] for x in el):
                        if (self.support[el] == self.support[self.superset[depth+1][k]]):
                            closed = False
                    k += 1

                #   ukoliko ne postoji nadskup sa istom podrskom --> zatvoren
                if closed is True and el in self.frequent:
                    self.closed_itemset.append(self.superset[depth][width])

                width += 1
            depth += 1

    def max_sets(self):
        # petlja ide od kraja, pa ce prvo ubaciti najduze skupove stavki
        # koji su cesti, i za ostale proveravati da li su podskupovi
        # nekog od max cestih, ako jeste podskup onda nije max cest
        for el in reversed(self.flat_superset):
            ind = False

            for freq in self.max_frequent:
                if all(x in freq for x in el):
                    ind = True
            if ind:
                continue

            if self.support[el] >= self.min_support:
                self.max_frequent.append(el)

    # funkcija za iscrtavanja resetke
    def draw_grid(self):
        color_map = []
        G = multilayered_graph(*self.subset_sizes)

        mapping = dict(zip(G, self.flat_superset))
        G = nx.relabel_nodes(G, mapping, copy=False)

        G = draw_edges(G, self.superset)

        for el in self.flat_superset:
            if el in self.max_frequent and el in self.closed_itemset:
                color_map.append('magenta')
            elif el in self.max_frequent:
                color_map.append('red')
            elif el in self.closed_itemset:
                color_map.append('lightgreen')
            elif el in self.frequent:
                color_map.append('orange')
            else:
                color_map.append('lightblue')

        pos = nx.multipartite_layout(G, subset_key="layer", align='horizontal')
        flipped_pos = {node: (-x, -y) for (node, (x, y)) in pos.items()}
        plt.figure(figsize=(16, 8))
        nx.draw(G, flipped_pos, with_labels=True,node_color=color_map, node_size=500)
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='basic node',markerfacecolor='lightblue', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='frequent',markerfacecolor='orange', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='max_frequent',markerfacecolor='red', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='closed',markerfacecolor='lightgreen', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='closed and max_frequent',markerfacecolor='magenta', markersize=15)
        ]
        plt.legend(handles=legend_elements)
        plt.show()

    # ispis skupova u odgovarajuce prozore
    def update_list_widgets(self):
        self.window.listWidget1.clear()
        self.window.listWidget2.clear()
        self.window.listWidget4.clear()
        self.max_frequent = sorted(self.max_frequent)
        self.closed_itemset = sorted(self.closed_itemset)
        max_closed = sorted(list(set(self.max_frequent) & set(self.closed_itemset)))

        for el in self.max_frequent:
            self.window.listWidget1.addItem(el + " ---> " + str(self.support[el]))
        for el in self.closed_itemset:
            self.window.listWidget4.addItem(el + " ---> " + str(self.support[el]))
        for el in max_closed:
            self.window.listWidget2.addItem(el + " ---> " + str(self.support[el]))

    def draw_grid_button_clicked(self):
        support_line = self.window.support.text()
        if support_line == "" or not support_line.isnumeric():
            self.min_support = 2
        else:
            self.min_support = int(self.window.support.text())

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
