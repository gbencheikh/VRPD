class VRPDInstance: 
    def __init__(self, num_vehicles, vehicle_capacities, num_drones, drone_capacities, depot, clients, from_file=False, file_path=None):
        self.num_vehicles = num_vehicles
        self.vehicle_capacities = vehicle_capacities
        self.num_drones = num_drones
        self.drone_capacities = drone_capacities
        self.depot = depot
        self.clients = clients
        self.from_file = from_file
        self.file_path = file_path

    @classmethod
    def from_file(cls, file_path):
        filePath = file_path
        fromFile = True
        with open(file_path, 'r') as file:
            lines = file.readlines()
            
            num_vehicles = int(lines[0].strip())
            vehicle_capacities = [int(capacity) for capacity in lines[1].strip().split()]
            num_drones = int(lines[2].strip())
            drone_capacities = [int(capacity) for capacity in lines[3].strip().split()]
            depot = tuple(map(int, lines[4].strip().split()))
            
            clients = []
            for line in lines[5:]:
                parts = line.strip().split()
                demand = int(parts[0])
                location = tuple(map(int, parts[1:]))
                clients.append({'demand': demand, 'location': location})

        return cls(num_vehicles, vehicle_capacities, num_drones, drone_capacities, depot, clients,from_file=True, file_path=file_path)
    
    def __repr__(self):
        chaine = "------------------------------------------------------------------------ \n"
        if self.from_file == True:
            chaine += f"Instance file = {self.file_path} \n"
        else:
            chaine += "randomly generated \n"
        chaine += "------------------------------------------------------------------------ \n"
        chaine += f"number of vehicules (and drones)={self.num_vehicles} \n"
        chaine += f"vehicle_capacities={self.vehicle_capacities} \n"
        chaine += f"drone_capacities={self.drone_capacities},\n" 
        chaine += f"depot={self.depot}, \n"
        chaine += "Clients:\n"
        
        for idx, client in enumerate(self.clients):
            chaine += f"  Client {idx + 1}: Demand = {client['demand']}, Location = {client['location']}\n"
        chaine += "------------------------------------------------------------------------\n"

        return (chaine)

def printSolution(solution):
    """
    Affiche une solution du problème de VRP avec drone.

    :param solution: Liste de tuples (id_client, id_vehicule, 'T' / 'D')
    """
    for id_client, id_vehicule, type_livraison in solution:
        if type_livraison == 'T':
            moyen = "Camion"
        elif type_livraison == 'D':
            moyen = "Drone"
        else:
            moyen = "Inconnu"
        print(f"Client {id_client} est servi par le véhicule {id_vehicule} avec un {moyen}.")

def drawGraph(instance, solution, saveSolution, showGraph):   
    import networkx as nx
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    """
    Affiche un graphe de la solution du problème de VRP avec drone.

    :param solution: Liste de tuples (id_client, id_vehicule, 'T' / 'D')
    :param depot_id: Identifiant du dépôt (par défaut 0)
    """
    # Création du graphe

    fig, grp = plt.subplots(figsize=(10, 5))  
    plt.title("VPRD",fontsize=25 )

    G = nx.DiGraph()
    # Définir une palette de couleurs
    colors = list(mcolors.TABLEAU_COLORS.keys())

    vehicule_colors = {}
    color_index = 0

    depot_id = 0
    NV = instance.num_vehicles
    vehicule = [[0,0] for i in range(NV)]

    # Ajout du noeud dépot
    G.add_node(depot_id, pos=instance.depot, label='0', color='red', shape='s')
    
    for id_client, id_vehicule, type_livraison in solution:
        # Ajouter un nœud pour chaque client
        G.add_node(id_client, pos=instance.clients[id_client-1]['location'], label=f'{id_client}', color='lightgreen', shape='o')
        
        # Associer une couleur au véhicule s'il n'en a pas encore
        if id_vehicule not in vehicule_colors:
            vehicule_colors[id_vehicule] = colors[color_index % len(colors)]
            color_index += 1

        # Ajouter une arête entre le dépôt et le client
        if type_livraison == 'T':
            G.add_edge(vehicule[id_vehicule-1][0], id_client, label='Camion', color=vehicule_colors[id_vehicule], style='solid')

            if(vehicule[id_vehicule-1][0] != vehicule[id_vehicule-1][1]):
                G.add_edge(vehicule[id_vehicule-1][1], id_client, label='Drone', color='red', style='dashed')

            vehicule[id_vehicule-1][0] = id_client
            vehicule[id_vehicule-1][1] = id_client
            
        elif type_livraison == 'D':
            G.add_edge(vehicule[id_vehicule-1][1], id_client, label='Drone', color='red', style='dashed')
            vehicule[id_vehicule-1][1] = id_client
    
    # Retour des véhicules au dépot 
    for id, v in enumerate(vehicule): 
        if v[0] != 0:
            G.add_edge(v[0], depot_id, label='Camion',color=vehicule_colors[id+1], style='solid')

    # Obtenir les positions des nœuds pour l'affichage
    pos = nx.get_node_attributes(G, 'pos')
    
    # Dessiner les nœuds
    for node in G.nodes(data=True):
        nx.draw_networkx_nodes(G, pos, nodelist=[node[0]], node_size=300,
                               node_color=node[1]['color'], node_shape=node[1]['shape'])
        
    # Dessiner les étiquettes des nœuds
    labels = nx.get_node_attributes(G, 'label')
    nx.draw_networkx_labels(G, pos, labels)
    
    # Dessiner les arêtes avec les couleurs spécifiées
    edges = G.edges(data=True)
    edge_colors = [edge[2]['color'] for edge in edges]
    edge_styles = [edge[2]['style'] for edge in edges]

    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=edge_colors, style=edge_styles, arrows=True)
    
    if saveSolution:
        fileName = "VRPDSolution"
        fig.savefig(fileName, bbox_inches='tight')
        print(f"Image has been saved succesfully -- Image fileName: {fileName}.png")

    if showGraph==0: plt.close(fig)