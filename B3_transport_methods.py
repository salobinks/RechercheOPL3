from B3_data import *
from copy import deepcopy
import copy
from collections import deque
from colorama import Back, Fore, Style


# Fonction pour appliquer la méthode de Nord-Ouest
def nord_ouest_method(graph_data):
    """
    Applique la méthode de Nord-Ouest pour résoudre le problème de transport.
    :param graph_data: Dictionnaire contenant les données du problème de transport
    :return: Matrice des propositions de transport
    """
    # Récupérer les dimensions du tableau
    n = len(graph_data['provisions'])
    m = len(graph_data['commandes'])

    # Créer des copies des listes de provisions et de commandes
    provisions_copie = graph_data['provisions'][:]
    commandes_copie = graph_data['commandes'][:]

    # Initialiser la matrice des propositions avec des zéros
    propositions = [[0 for _ in range(m)] for _ in range(n)]

    # Indices pour parcourir les lignes et les colonnes
    i = 0
    j = 0

    # Tant qu'il reste des fournisseurs et des clients à servir
    while i < n and j < m:
        # Allouer autant que possible en partant du coin nord-ouest
        quantity = min(provisions_copie[i], commandes_copie[j])
        propositions[i][j] = quantity

        # Mettre à jour les provisions et les commandes restantes dans les copies
        provisions_copie[i] -= quantity
        commandes_copie[j] -= quantity

        # Passer au fournisseur suivant s'il n'a plus de provision
        if provisions_copie[i] == 0:
            i += 1

        # Passer au client suivant s'il n'a plus de commande
        if commandes_copie[j] == 0:
            j += 1

    return propositions


# Fonction pour appliquer la méthode de Balas-Hammer
def balas_hammer_method(graph_data, go=None):
    """
    Applique la méthode de Balas-Hammer pour résoudre le problème de transport.
    :param graph_data: Dictionnaire contenant les données du problème de transport
    :return: Matrice des propositions de transport
    """
    # Initialisation
    provisions = graph_data['provisions'].copy()  # Copie des provisions
    commandes = graph_data['commandes'].copy()  # Copie des commandes
    costs = deepcopy(graph_data['couts'])  # Copie des coûts
    taille = graph_data['taille']  # Dimensions du tableau
    fournisseurs, clients = taille  # Nombre de fournisseurs et de clients

    # Initialisation de la matrice des propositions avec des zéros
    propositions = [[0 for _ in range(clients)] for _ in range(fournisseurs)]

    while sum(provisions) > 0 and sum(commandes) > 0:
        delta_rows = []
        for row in costs:
            valid_costs = [cost for cost in row if cost != float('inf')]
            if len(valid_costs) > 1:
                sorted_costs = sorted(valid_costs)
                delta_rows.append(sorted_costs[1] - sorted_costs[0])
            else:
                delta_rows.append(-float('inf'))

        delta_cols = []
        for j in range(clients):
            valid_costs = [costs[i][j] for i in range(fournisseurs) if costs[i][j] != float('inf')]
            if len(valid_costs) > 1:
                sorted_costs = sorted(valid_costs)
                delta_cols.append(sorted_costs[1] - sorted_costs[0])
            else:
                delta_cols.append(-float('inf'))

        max_delta_row = max(delta_rows)
        max_delta_col = max(delta_cols)

        # Determiner l'origine de la pénalité maximale et chercher l'arête correspondante
        if max_delta_row >= max_delta_col:
            chosen_indexes = [i for i, val in enumerate(delta_rows) if val == max_delta_row]
        else:
            chosen_indexes = [j for j, val in enumerate(delta_cols) if val == max_delta_col]

        min_cost = float('inf')
        for index in chosen_indexes:
            if max_delta_row >= max_delta_col:
                for j in range(clients):
                    if costs[index][j] != float('inf') and costs[index][j] < min_cost:
                        min_cost = costs[index][j]
                        chosen_i, chosen_j = index, j
            else:
                for i in range(fournisseurs):
                    if costs[i][index] != float('inf') and costs[i][index] < min_cost:
                        min_cost = costs[i][index]
                        chosen_i, chosen_j = i, index

        if go:
            # Affichage de l'arête choisie avec toutes les informations nécessaires
            print(
                f"\n\nArête choisie pour remplissage : {Fore.LIGHTBLUE_EX}P{chosen_i + 1}{Style.RESET_ALL} - {Fore.LIGHTMAGENTA_EX}C{chosen_j + 1}{Style.RESET_ALL}")
            print(f"Coût minimal trouvé : {Fore.LIGHTWHITE_EX}{min_cost}{Style.RESET_ALL}")
            print(f"Quantité remplie : {Back.WHITE}{Fore.BLACK}{min(provisions[chosen_i], commandes[chosen_j])}{Style.RESET_ALL}")

        # Maximisation de la cellule choisie
        quantity = min(provisions[chosen_i], commandes[chosen_j])
        propositions[chosen_i][chosen_j] += quantity
        provisions[chosen_i] -= quantity
        commandes[chosen_j] -= quantity
        costs[chosen_i][chosen_j] = float('inf')  # Marquage de la cellule comme utilisée

        if provisions[chosen_i] == 0:
            for k in range(clients):
                costs[chosen_i][k] = float('inf')

        if commandes[chosen_j] == 0:
            for k in range(fournisseurs):
                costs[k][chosen_j] = float('inf')

        if go:
            print("----------------------------------------------")
            print("\nPénalités pour les lignes :")
            for i, delta in enumerate(delta_rows):
                if delta == -float('inf'):
                    print(f"P{i + 1} : /")
                else:
                    print(f"P{i + 1} : {delta}")

            print("\nPénalités pour les colonnes :")
            for j, delta in enumerate(delta_cols):
                if delta == -float('inf'):
                    print(f"C{j + 1} : /")
                else:
                    print(f"C{j + 1} : {delta}")

    return propositions


# Fonction pour vérifier la connexité du graphe en utilisant un parcours en largeur (Breadth-First Search)
def bfs_connexity(graph_data):
    """
    Vérifie si le graphe est connexe en utilisant un parcours en largeur (BFS).
    :param graph_data: Données du graphe
    :return: True si le graphe est connexe, False sinon
    """
    # Initialisation : extraire les dimensions du graphe
    num_fournisseurs, num_clients = graph_data['taille']

    # Total de sommets (fournisseurs + clients)
    total_vertices = num_fournisseurs + num_clients
    visited = [False] * total_vertices  # Initialiser tous les sommets comme non visités
    queue = deque([0])  # Commencer par le premier fournisseur

    # Parcours en largeur (BFS) pour trouver les connexions
    while queue:
        vertex = queue.popleft()  # Extraire le sommet de la file
        if not visited[vertex]:  # Si le sommet n'a pas été visité
            visited[vertex] = True  # Marquer le sommet comme visité

            # Ajouter les sommets adjacents à la file :
            if vertex < num_fournisseurs:  # Ce sommet est un fournisseur

                # Parcourir les propositions pour trouver les clients connectés
                for j in range(num_clients):
                    # Si proposition de la cellule > 0 et le client n'a pas été visité
                    if graph_data['propositions'][vertex][j] > 0 and not visited[num_fournisseurs + j]:
                        queue.append(num_fournisseurs + j)  # Ajouter le client à la file

            else:  # Ce sommet est un client
                client_index = vertex - num_fournisseurs  # Indice du client dans les propositions
                for i in range(num_fournisseurs):
                    # Si proposition de la cellule > 0 et le fournisseur n'a pas été visité
                    if graph_data['propositions'][i][client_index] > 0 and not visited[i]:
                        queue.append(i)  # Ajouter le fournisseur à la file

    return all(visited)  # Le graphe est connexe si tous les sommets ont été visités


# Fonction pour convertir l'index d'un sommet en son label
def vertex_to_label(index, num_providers):
    """
    Convertir l'index d'un sommet en son label correspondant.
    :param index: Index du sommet
    :param num_providers: Nombre de fournisseurs
    :return: Label du sommet
    """
    if index < num_providers:
        return f'P{index + 1}'
    else:
        return f'C{index - num_providers + 1}'


# Fonction pour vérifier si un chemin existe entre deux sommets dans le graphe
def path_exists(graph_data, start, end, visited, added_edges):
    """
    Vérifie s'il existe un chemin entre deux sommets dans le graphe et retourne ce chemin s'il existe.
    :param graph_data: Dictionnaire contenant les données du graphe
    :param start: Sommet de départ
    :param end: Sommet d'arrivée
    :param visited: Liste des sommets visités
    :param added_edges: Liste des arêtes ajoutées [(fournisseur, client)]
    :return: Tuple (bool, list) - (True si un chemin existe, False sinon, chemin suivi si existant)
    """
    queue = deque([start])
    predecessors = {start: None}
    visited[start] = True

    while queue:
        vertex = queue.popleft()
        if vertex == end:
            # Reconstruire le chemin à partir de la fin en utilisant les prédécesseurs
            path = []
            step = vertex
            while step is not None:
                path.append(vertex_to_label(step, graph_data['taille'][0]))
                step = predecessors[step]
            path.reverse()
            return True, path

        # Explorer les voisins normaux (fournisseurs -> clients et clients -> fournisseurs)
        if vertex < graph_data['taille'][0]:  # Fournisseurs
            for j in range(graph_data['taille'][1]):
                neighbor = graph_data['taille'][0] + j
                if graph_data['propositions'][vertex][j] > 0 and not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)
                    predecessors[neighbor] = vertex
        else:  # Clients
            client_index = vertex - graph_data['taille'][0]
            for i in range(graph_data['taille'][0]):
                if graph_data['propositions'][i][client_index] > 0 and not visited[i]:
                    visited[i] = True
                    queue.append(i)
                    predecessors[i] = vertex

        # Explorer les arêtes ajoutées
        for supplier_idx, client_idx in added_edges:
            supplier_vertex = supplier_idx
            client_vertex = graph_data['taille'][0] + client_idx
            if vertex == supplier_vertex and not visited[client_vertex]:
                visited[client_vertex] = True
                queue.append(client_vertex)
                predecessors[client_vertex] = vertex
            elif vertex == client_vertex and not visited[supplier_vertex]:
                visited[supplier_vertex] = True
                queue.append(supplier_vertex)
                predecessors[supplier_vertex] = vertex

    return False, []


# Fonction pour trouver les composants connexes du graphe
def find_connected_components(graph_data):
    """
    Trouve les composants connexes du graphe en utilisant un parcours en largeur (BFS).
    :param graph_data: Dictionnaire contenant les données du graphe
    :return: Liste des composants connexes
    """
    num_fournisseurs, num_clients = graph_data['taille']
    total_vertices = num_fournisseurs + num_clients
    visited = [False] * total_vertices
    components = []

    def bfs(start_vertex):
        """
        Parcours en largeur (BFS) pour trouver les composants connexes.
        :param start_vertex: Sommet de départ
        :return: Liste des sommets du composant connexe
        """
        queue = deque([start_vertex])
        component = []
        visited[start_vertex] = True
        while queue:
            vertex = queue.popleft()
            component.append(vertex)
            # Déterminer les connexions en fonction de si c'est un fournisseur ou un client
            if vertex < num_fournisseurs:
                for j in range(num_clients):
                    if graph_data['propositions'][vertex][j] > 0 and not visited[num_fournisseurs + j]:
                        visited[num_fournisseurs + j] = True
                        queue.append(num_fournisseurs + j)
            else:  # C'est un client
                client_index = vertex - num_fournisseurs
                for i in range(num_fournisseurs):
                    if graph_data['propositions'][i][client_index] > 0 and not visited[i]:
                        visited[i] = True
                        queue.append(i)
        return component

    for v in range(total_vertices):
        if not visited[v]:
            components.append(bfs(v))

    return components


def calcul_potentiels(graph_data, added_edges):
    """
    Calcule les potentiels en utilisant les arcs actifs et les arcs ajoutés pour assurer la connexité.
    Affiche les détails des calculs étape par étape.
    :param graph_data: Dictionnaire contenant les données du graphe
    :param added_edges: Liste des arêtes ajoutées [(fournisseur, client)]
    :return: Dictionnaire des potentiels
    """
    # Initialiser les potentiels : commencer par un fournisseur de référence
    potentiels = {'P1': 0}
    changes = True

    while changes:
        changes = False

        # Parcourir 2 fois pour s'assurer qu'on oublie aucun potentiel
        for p in range(0, 2):
            # Parcourir tous les arcs actifs (propositions > 0)
            for i, row in enumerate(graph_data['couts']):
                for j, cout in enumerate(row):
                    Pi = f"P{i + 1}"
                    Cj = f"C{j + 1}"
                    proposition = graph_data['propositions'][i][j]

                    if proposition > 0:  # Arc actif uniquement

                        if Pi in potentiels and Cj not in potentiels:
                            potentiels[Cj] = potentiels[Pi] - cout
                            print(f"E({Pi}) - E({Cj}) = {cout}")
                            changes = True
                        elif Cj in potentiels and Pi not in potentiels:
                            potentiels[Pi] = cout + potentiels[Cj]
                            print(f"E({Pi}) - E({Cj}) = {cout}")
                            changes = True
            p += 1

        # Parcourir les arcs ajoutés pour assurer la connexité
        for supplier_idx, client_idx in added_edges:
            Pi = f"P{supplier_idx + 1}"
            Cj = f"C{client_idx + 1}"
            cout = graph_data['couts'][supplier_idx][client_idx]

            # Si un arc ajouté est effectivement connecté et valide
            if Pi in potentiels and Cj not in potentiels:
                potentiels[Cj] = potentiels[Pi] - cout
                print(f"E({Pi}) - E({Cj}) = {cout}")
                changes = True
            elif Cj in potentiels and Pi not in potentiels:
                potentiels[Pi] = cout + potentiels[Cj]
                print(f"E({Pi}) - E({Cj}) = {cout}")
                changes = True

    print('\nRésultats des potentiels :')
    for key, value in potentiels.items():
        print(f"E({key}) = {value}")

    return potentiels


# Fonction pour trouver la combinaison minimale qui n'introduit pas de cycle dans le graphe
def trouver_combinaison_minimale(graph_data, ignore_set):
    """
    Trouver la combinaison minimale qui n'introduit pas de cycle dans le graphe.
    :param graph_data: Dictionnaire contenant les données du graphe
    :param ignore_set: Ensemble des arêtes à ignorer
    :return: Tuple (i, j) de la combinaison minimale
    """
    couts_temp = [row[:] for row in graph_data['couts']]
    n, m = graph_data['taille']
    for i in range(n):
        for j in range(m):
            if (i, j) in ignore_set or graph_data['propositions'][i][j] != 0:
                couts_temp[i][j] = float('inf')  # Ignorer cette arête

    # Trouver la valeur minimale dans les coûts ajustés
    min_value = float('inf')
    min_pos = None
    for i in range(n):
        for j in range(m):
            if couts_temp[i][j] < min_value:
                min_value = couts_temp[i][j]
                min_pos = (i, j)
    return min_pos


# Fonction pour vérifier la connexité du graphe
def rendre_graphe_connexe(graph_data):
    """
    Rendre le graphe connexe en ajoutant des arêtes.
    :param graph_data: Dictionnaire contenant les données du graphe
    :return: None
    """
    ignored_edges = set()

    # Vérifier si le graphe est déjà connexe
    if graph_data['propositions'] is None:
        graph_data['propositions'] = [[0] * graph_data['taille'][1] for _ in range(graph_data['taille'][0])]

    # Tant que le graphe n'est pas connexe, ajouter des arêtes
    while not bfs_connexity(graph_data):
        # Trouver une arête minimale à ajouter qui n'introduit pas de cycle
        combinaison_minimale = trouver_combinaison_minimale(graph_data, ignored_edges)
        i, j = combinaison_minimale
        # Ajouter cette arête au graphe
        print(f"Ajout de l'arête P{i + 1}C{j + 1} pour améliorer la connexité.")

    print("Le graphe est maintenant connexe.")


# Fonction pour détecter un cycle dans le graphe
def detect_cycle_with_edge(graph_data, edge, added_edges=None):
    """
    Vérifie si l'ajout d'une arête créerait un cycle dans le graphe.
    :param graph_data: Dictionnaire contenant les données du graphe
    :param edge: Sommets de l'arête à vérifier
    :return: True si un cycle est créé, False sinon
    """
    # Initialisation
    total_vertices = sum(graph_data['taille'])
    visited = [False] * total_vertices

    # Convertir l'arête dans les index de la liste visited
    edge_indices = (edge[0], edge[1] + graph_data['taille'][0])

    # Vérifier si un chemin existe déjà entre les deux sommets de l'arête améliorante
    valid, path = path_exists(graph_data, edge_indices[0], edge_indices[1], visited, added_edges)
    if valid:
        # Si un chemin existe, l'ajout de cette arête créerait un cycle
        return True, path
    return False, path


# Fonction pour calculer les coûts potentiels
def calcul_couts_potentiels(graph_data, dict_items):
    """
    Calculer les coûts potentiels pour chaque cellule du tableau.
    :param graph_data: Dictionnaire contenant les données du problème de transport
    :param dict_items: Dictionnaire contenant les valeurs des potentiels
    :return: Tableau des coûts potentiels
    """
    taille = graph_data['taille']
    tableau = [[0] * taille[1] for _ in range(taille[0])]

    for i in range(taille[0]):
        for j in range(taille[1]):
            p_key = 'P' + str(i + 1)
            c_key = 'C' + str(j + 1)
            p_value = dict_items.get(p_key, 0)
            c_value = dict_items.get(c_key, 0)
            tableau[i][j] = p_value - c_value

    return tableau


# Fonction pour calculer les coûts marginaux
def calcul_couts_marginaux(graph_data, couts_potentiels):
    """
    Calculer les coûts marginaux pour chaque cellule du tableau.
    :param graph_data: Dictionnaire contenant les données du problème de transport
    :param couts_potentiels: Tableau des coûts potentiels
    :return: Tableau des coûts marginaux
    """
    taille = graph_data['taille']
    tableau = [[0] * taille[1] for _ in range(taille[0])]

    for i in range(taille[0]):
        for j in range(taille[1]):
            tableau[i][j] = graph_data['couts'][i][j] - couts_potentiels[i][j]

    #print tableau
    return tableau


# Fonction pour calculer les coûts totaux
def cout_totaux(graph_data):
    """
    Calculer le coût total du transport en multipliant les coûts par les propositions.
    :param graph_data: Dictionnaire contenant les données du problème de transport
    :return: None
    """
    total_cost = 0
    # Obtenir le nombre de fournisseurs (rows) et de clients (columns)
    num_fournisseurs, num_clients = graph_data['taille']

    print()
    # Itérer sur chaque cellule de propositions
    for i in range(num_fournisseurs):
        for j in range(num_clients):
            if graph_data['propositions'][i][j] > 0:  # Vérifier si la proposition n'est pas nulle
                cost = graph_data['couts'][i][j]
                proposition = graph_data['propositions'][i][j]
                total_cost += cost * proposition  # Multiplier le coût par la proposition et ajouter au coût total
                print(f"Coût de transport de {Fore.LIGHTBLUE_EX}P{i + 1}{Style.RESET_ALL} à {Fore.LIGHTMAGENTA_EX}C{j + 1}{Style.RESET_ALL} : "
                      f"{Fore.LIGHTWHITE_EX}{cost}{Style.RESET_ALL} x {Fore.LIGHTWHITE_EX}{proposition}{Style.RESET_ALL} = "
                      f"{Fore.LIGHTWHITE_EX}{cost * proposition}{Style.RESET_ALL}")

    print()
    print( "Coûts totaux : " + Back.LIGHTBLUE_EX + Fore.BLACK + f' {total_cost} ' + Style.RESET_ALL)

    return total_cost


# Fonction pour vérifier si un coût marginal négatif existe
def is_marginal_negative(couts_marginaux):
    """
    Vérifie si au moins un coût marginal est négatif.
    :param couts_marginaux: Tableau des coûts marginaux
    :return: Le (i, j) du coût marginal le plus négatif
    """
    min_value = float('inf')
    min_pos = None
    for i, row in enumerate(couts_marginaux):
        for j, cost in enumerate(row):
            if cost < min_value:
                min_value = cost
                min_pos = (i, j)
    print(f"Coût marginal le plus négatif : {min_value} pour la cellule {Fore.LIGHTBLUE_EX}P{min_pos[0] + 1}{Style.RESET_ALL} - {Fore.LIGHTMAGENTA_EX}C{min_pos[1] + 1}{Style.RESET_ALL}")
    return min_pos if min_value < 0 else (None, None)


# Fonction pour appliquer la méthode de marche pied
def stepping_stone_method(graph_data, i, j, added_edges):
    """
    Applique la méthode de marche pied pour résoudre le problème de transport.
    :param graph_data: Dictionnaire contenant les données du problème de transport
    :param i: (int) Indice de la ligne de la cellule à ajuster
    :param j: (int) Indice de la colonne de la cellule à ajuster
    :return: Matrice des propositions de transport
    """
    propositions = copy.deepcopy(graph_data['propositions'])

    cycle_exists, cycle_path = detect_cycle_with_edge(graph_data, (i, j), added_edges)

    if not cycle_exists:
        print("Aucun cycle trouvé pour l'arête donnée.")
        return graph_data['propositions']
    else:
        cycle_path.append(cycle_path[0])
        cycle_path = cycle_path[::-1]
        print("Cycle trouvé pour l'arête donnée : ", end="")
        print(" -> ".join(cycle_path))

    # Créer un tableau pour stocker les arêtes du cycle, exemple : cycle_path = ['P1', 'C1', 'P2', 'C2'], donc cycle = P1 -> C1 -> P2 -> C2, donc array_cycle doit avoir [(P1, C1), (P2, C1), (P2, C2), (P1, C2)] mais avec des indices
    array_cycle = []
    for k in range(len(cycle_path) - 1):
        fournisseur = int(cycle_path[k][1:]) - 1
        client = int(cycle_path[k + 1][1:]) - 1
        array_cycle.append((fournisseur, client))

    # dans array_cycle, changer 1 fois sur 2 les indices de i et j en commençant par l'indice 1 (0-indexed)
    # par exemple [(1, 2), (3, 4), (5, 6), (7, 8)] devient [(1, 2), (4, 3), (5, 6), (8, 7)]
    for k in range(1, len(array_cycle), 2):
        array_cycle[k] = array_cycle[k][::-1]

    # Mettre à 0 les propositions des arêtes du cycle array_cycle
    for array in array_cycle:
        i, j = array
        propositions[i][j] = 0

    # Maximiser la proposition de la cellule (i, j)
    for array in array_cycle:
        # Récupérer les indices de la cellule à remplir
        i, j = array


        # Trouver le maximum que je peux remplir par rapport à ce qu'il y a déjà dans la ligne/colonne de la cellule que je veux remplir
        column = [propositions[k][j] for k in range(len(propositions))]
        row = [propositions[i][k] for k in range(len(propositions[0]))]

        """
        prendre toutes les valeurs de la ligne et de la colonne de la cellule à remplir et les additionner = addition_ligne et addition_colonne, les mettre dans une liste à ranger par ordre croissant
        ajouter les provisions et les commandes dans une liste puis ranger par ordre décroissant
        soustraire à ce maximum le premier de la liste_addition rangée par ordre croissant
        vérifier si le (résultat + somme des colonnes) est bien <= à la valeur provisions et (résultat + somme des lignes) <= à la valeur commandes de la cellule à remplir
        si oui, on peut remplir la cellule avec cette valeur
        sinon, on passe au second de la liste_addition et on refait le test
        """
        addition_ligne = sum(row)
        addition_colonne = sum(column)
        liste_addition = [addition_ligne, addition_colonne]
        liste_addition.sort()
        liste_provisions_commandes = [graph_data['provisions'][i], graph_data['commandes'][j]]
        liste_provisions_commandes.sort(reverse=True)
        quit = False
        for value in liste_addition:
            for val_liste in liste_provisions_commandes:
                result = val_liste - value
                if (result + addition_ligne) <= graph_data['provisions'][i] and (result + addition_colonne) <= graph_data['commandes'][j]:
                    quit = True
                    break
            if quit:
                break
        propositions[i][j] = result
        graph_data['propositions'][i][j] = result

    return propositions


