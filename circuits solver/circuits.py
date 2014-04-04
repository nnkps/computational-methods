__author__ = 'ania'
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random as rand

def draw_circuit_and_get_currents(name_of_file, s, t, E):

    try:
        G = nx.read_weighted_edgelist(name_of_file)  # parsing edge list with weights to create graph
    except IOError:
        print('there is no such file')
        return []

    G = nx.convert_node_labels_to_integers(G)

    G.edge[s][t]['SEM'] = E  # setting SEM value

    number_of_nodes = G.number_of_nodes()
    number_of_edges = G.number_of_edges()

    cycles = nx.cycle_basis(G)  # list of cycles in graph - minimal collection
                                # of cycles that any cycle can be a sum of cycles in basis

    number_of_cycles = cycles.__len__()

    result_matrix = np.zeros((number_of_nodes + number_of_cycles, number_of_edges))  # set of equations

    nodes = list(G.node)  # list of nodes

    edges = G.edges()  # list of edges

    # 1st Kirchoff's Law
    DG = nx.DiGraph()  # creating directed graph which includes direction of flow of electric charge
    i = 0
    for edge in edges:  # for every edge in graph setting random direction of flow
        if (rand.randint(0, 1) == 0):
            DG.add_edge(edge[0], edge[1])
        else:
            DG.add_edge(edge[1], edge[0])

    for node in nodes:
        for neighbor in G.neighbors(node):  # checking neighbours of node
                                            # setting the coefficients for equation
            if (node, neighbor) in edges:
                tuple = (node, neighbor)
            else:
                tuple = (neighbor, node)

            if (node, neighbor) in DG.edges():
                result_matrix[node][edges.index(tuple)] = 1  # setting the value on 1 if current on edge (node, neighbor)
                                                             # flows according to the direction of flow of electric charge
            else:
                result_matrix[node][edges.index(tuple)] = -1 # otherwise setting the value on -1

    # 2nd Kirchoff's Law
    Y = np.zeros((number_of_nodes + number_of_cycles, 1))  # creating the vector of right side of the equations

    iter = 0
    for cycle in cycles:  # for every cycle setting the coefficients for equations
        for i in xrange(cycle.__len__()):  # checking every edge in cycle
            if (cycle[i-1], cycle[i]) in edges:
                tuple = (cycle[i-1], cycle[i])
            else:
                tuple = (cycle[i], cycle[i-1])

            # in matrix coefficients in equations are resistances on edges, resistance is under key 'weight' in dict
            result_matrix[number_of_nodes + iter][edges.index(tuple)] = G.edge[tuple[0]][tuple[1]]['weight']

            try:
                Y[number_of_nodes + iter] = G.edge[tuple[0]][tuple[1]]['SEM'] # if sem is set for edge
            except KeyError:                                                  # adding value of SEM in vector of
                pass                                                          # right side of equations

            if (cycle[i-1], cycle[i]) in DG.edges():
                result_matrix[number_of_nodes + iter][edges.index(tuple)] *= (-1)  # setting values according to flow
                if Y[number_of_nodes + iter] != 0:
                    Y[number_of_nodes + iter] *= (-1)
            else:
                pass
        iter += 1


    A = np.squeeze(np.asarray(result_matrix))
    B = np.squeeze(np.asarray(Y))

    currents = np.linalg.lstsq(A, B)  # solving the equation Ax = B, function returns
                                      # the least-squares solution to a linear matrix equation

    list_of_currents = currents[0]

    edge_labels = {}
    for i in xrange(edges.__len__()):
        if list_of_currents[i] < 0: # checking every current on edge if value is negative
            try:
                DG.remove_edge(edges[i][0], edges[i][1])  # reversing direction of edge in directed graph
                DG.add_edge(edges[i][1], edges[i][0])
            except nx.exception.NetworkXError:
                DG.remove_edge(edges[i][1], edges[i][0])
                DG.add_edge(edges[i][0], edges[i][1])

            list_of_currents[i] *= (-1)  # setting current on edge on non-negative value

        # adding the labels for every edge - R, I and SEM if exists
        # rounding the value of current
        edge_labels[(edges[i][0], edges[i][1])] = "\nR: " + str(G.edge[edges[i][0]][edges[i][1]]['weight']) + "\nI: " + str(round(list_of_currents[i], 3))
        try:
            edge_labels[(edges[i][0], edges[i][1])] += "\nSEM: " + str(G.edge[edges[i][0]][edges[i][1]]['SEM'])
        except KeyError:
            pass

    # drawing directed graph with labels
    pos = nx.spring_layout(DG)
    nx.draw_networkx_edges(DG, pos)
    nx.draw_networkx_edge_labels(DG, pos, edge_labels=edge_labels)
    nx.draw_networkx_nodes(DG, pos, with_labels=True)
    plt.show()

    return list_of_currents

if __name__ == '__main__':
    currents = draw_circuit_and_get_currents("test.txt", 0, 1, 100)
    print(currents)
