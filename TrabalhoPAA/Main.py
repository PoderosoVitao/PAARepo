'''
Trabalho PAA - Caixeiro Viajante
Integrantes:

Vinicius Dutra Goddard
Victor Hugo Braz

'''

import itertools
import networkx as nx
import os
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Sequence, Tuple
from matplotlib import pyplot as plt
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import time
import json

class MetroSolver:
    def __init__(self, graph):
        self.graph = graph
        self.adjacency = {node: list(graph.neighbors(node)) for node in graph.nodes()}
        self.node_count = graph.number_of_nodes()
        
    def execute_menu(self):
        print("\n Trabalho PAA: Vinicius Goddard e Victor Hugo \n")
        problem_choice = self._get_problem_selection()
        print(f"Problema {problem_choice} selecionado.\n")
        
        algorithm_map = {
            '1': self._run_brute_force,
            '2': self._run_branch_bound,
            '3': self._run_approximation,
            '0': lambda x: print("Encerrando.")
        }
        
        while True:
            self._display_algorithm_menu()
            choice = input("Digite sua escolha: ")
            
            if choice == '0':
                algorithm_map[choice](problem_choice)
                break
            elif choice in algorithm_map:
                algorithm_map[choice](problem_choice)
            else:
                print("Opção inválida. Tente novamente.")
    
    def _get_problem_selection(self):
        selection = None
        while selection not in ['1', '2']:
            print("Metrô de Paris\n")
            selection = input("Deseja Resolver Problema 1) ou Problema 2)? (1/2)\n").strip()
            if selection not in ['1', '2']:
                print("Escolha invalida.\n")
        return selection
    
    def _display_algorithm_menu(self):
        options = ["1) Força Bruta", "2) Branch and Bound", "3) Aproximação", "0) Sair"]
        print("Algoritmo:\n")
        for option in options:
            print(f"{option}\n")
    
    def _run_brute_force(self, problem_type):
        if problem_type == '1':
            self.bruteForce_solve_longest_path()
        else:
            self.bruteForce_solve_dominating_set()
    
    def _run_branch_bound(self, problem_type):
        if problem_type == '1':
            self.branchBound_solve_longest_path()
        else:
            self.branchBound_solve_dominating_set()
    
    def _run_approximation(self, problem_type):
        if problem_type == '1':
            self.greedy_solve_longest_path()
        else:
            self.greedy_solve_dominating_set()
    
    # algorithmo de força bruta com backtracking
    # Adicionei logs detalhados para verificar se os nós estão sendo explorados e se o algoritmo está entrando nos loops esperados.
    def bruteForce_solve_longest_path(self, output_file="maior_caminhoBrute.txt"):
        sorted_nodes = sorted(self.graph.nodes(), key=self.graph.degree, reverse=True)
        optimal_path = []
        search_count = 0
        with open(output_file, "w"):
            pass

        N_start = len(sorted_nodes)
        start_count = 0
        threshold = 5

        def explore_path(current_node, visited_set, current_path):
            nonlocal optimal_path, search_count
            visited_set.add(current_node)
            current_path.append(current_node)
            #pruning
            remaining_nodes = self.node_count - len(visited_set)
            if len(current_path) + remaining_nodes <= len(optimal_path):
                visited_set.remove(current_node)
                current_path.pop()
                return

            for neighbor in self.adjacency[current_node]:
                if neighbor not in visited_set:
                    explore_path(neighbor, visited_set, current_path)
            if len(current_path) > len(optimal_path):
                optimal_path = current_path.copy()
                if len(optimal_path) == self.node_count:
                    raise StopIteration

            search_count += 1
            visited_set.remove(current_node)
            current_path.pop()

        try:
            for start_node in sorted_nodes:
                explore_path(start_node, set(), [])
                start_count += 1
                percent = (start_count / N_start) * 100
                if percent >= threshold:
                    print(f"{threshold}% completo")
                    self.update_progress(threshold)
                    threshold += 5
        except StopIteration:
            pass

        self._write_path_result(optimal_path, output_file)
        print(f"Nos iniciais testados: {start_count}/{N_start} ({round((start_count/N_start)*100)}%)")
        print(f"Total de chamadas recursivas: {search_count}")
        return optimal_path, search_count

    def bruteForce_solve_dominating_set(self, min_size=17, max_size=21, output_file="dominantBrute.txt"):
        node_list = sorted(self.graph.nodes, key=self.graph.degree, reverse=True)
        neighborhood_closure = {node: set(self.graph.neighbors(node)) | {node} for node in node_list}
        with open(output_file, "w"):
            pass
        total_combinations = 0
        max_k = min(max_size, self.node_count)
        for size in range(min_size, max_k + 1):
            total_combinations += math.comb(self.node_count, size)

        tested_count = 0
        threshold = 5
        for size in range(min_size, max_k + 1):
            print(f"\nVerificando subconjuntos de tamanho {size}")
            for candidate_set in itertools.combinations(node_list, size):
                tested_count += 1

                percent = (tested_count / total_combinations) * 100
                if percent >= threshold:
                    print(f"{threshold:.0f}%")
                    threshold += 5

                covered_nodes = set()
                for idx, vertex in enumerate(candidate_set):
                    covered_nodes |= neighborhood_closure[vertex]
                    if len(covered_nodes) == self.node_count:
                        self._write_dominating_result(candidate_set, size, output_file)
                        print(f"Set dominante encontrado {size} apos testar {tested_count} combinacoes.")
                        return list(candidate_set)

                    remaining_vertices = candidate_set[idx + 1 :]
                    if remaining_vertices:
                        max_coverage = max(len(neighborhood_closure[w]) for w in remaining_vertices)
                        if len(covered_nodes) + (size - idx - 1) * max_coverage < self.node_count:
                            break

        print("Nenhum conjunto dominante identificado nos tamanhos testados.")
        return None

    def _write_dominating_result(self, dominating_set, size, filename):
        with open(filename, "a", encoding="utf-8") as file:
            file.write(f"Conjunto dominante com {size} vértices:\n{list(dominating_set)}\n")
    
    def branchBound_solve_longest_path(self, output_file="maior_caminhoBranch.txt"):
        best_len = 0
        best_path = []
        N = self.node_count
        adjacency = self.adjacency

        with open(output_file, "w", encoding="utf-8"):
            pass

        visited = set()
        path_stack = []
        search_count = 0
        start_count = 0

        def dfs_branch(node):
            nonlocal best_len, best_path, search_count
            search_count += 1
            visited.add(node)
            path_stack.append(node)

            vizinhos_livres = [nbr for nbr in adjacency[node] if nbr not in visited]
            if not vizinhos_livres:
                if len(path_stack) > best_len:
                    best_len = len(path_stack)
                    best_path = list(path_stack)
            else:
                remaining = N - len(visited)
                if len(path_stack) + remaining > best_len:
                    for nbr in vizinhos_livres:
                        dfs_branch(nbr)

            visited.remove(node)
            path_stack.pop()

        nodes_sorted = sorted(self.graph.nodes(), key=self.graph.degree, reverse=True)
        N_start = len(nodes_sorted)
        next_threshold = 5

        for start in nodes_sorted:
            if best_len == N:
                break
            start_count += 1
            percent = (start_count / N_start) * 100
            while percent >= next_threshold:
                print(f"{next_threshold}% completo")
                self.update_progress(next_threshold)  # Update progress using next_threshold
                next_threshold += 5
            dfs_branch(start)

        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"Comprimento do trajeto mais longo: {best_len}\n")
            f.write(f"Trajeto: {best_path}\n")

        print(f"Nos de inicio testados: {start_count}/{N_start} ({round((start_count/N_start)*100)}%)")
        print(f"Total chamadas recursivas: {search_count}")
        return best_path, best_len

    def branchBound_solve_dominating_set(self, output_file="dominantBranch.txt"):
        adjacency = self.adjacency
        nodes_sorted = sorted(self.graph.nodes())
        index_map = {v: i for i, v in enumerate(nodes_sorted)}
        N = self.node_count
        max_cover = max(self.graph.degree(v) for v in nodes_sorted) + 1
        best_size = N
        best_set = set(nodes_sorted)
        search_count = 0
        start_count = 0

        with open(output_file, "w", encoding="utf-8"):
            pass

        def dfs_dom(next_idx, current_set, dominated_set, start_i):
            nonlocal best_size, best_set, search_count
            search_count += 1
            if len(dominated_set) == N:
                if len(current_set) < best_size:
                    best_size = len(current_set)
                    best_set = set(current_set)
                return
            remaining_undom = N - len(dominated_set)
            bound = (remaining_undom + max_cover - 1) // max_cover
            if len(current_set) + bound >= best_size:
                return
            target = None
            for j in range(next_idx, N):
                v = nodes_sorted[j]
                if v not in dominated_set:
                    target = v
                    break
            if target is None:
                return
            candidates = [target] + [u for u in adjacency[target] if index_map[u] > start_i]
            for u in candidates:
                if u not in current_set:
                    new_set = current_set | {u}
                    new_dom = dominated_set | {u} | set(adjacency[u])
                    dfs_dom(index_map[u] + 1, new_set, new_dom, start_i)

        N_start = N
        next_threshold = 5
        for i, v in enumerate(nodes_sorted):
            if best_size == 1:
                break
            start_count += 1
            percent = (start_count / N_start) * 100
            while percent >= next_threshold:
                print(f"{next_threshold}%")
                next_threshold += 5
            current_set = {v}
            dominated_set = {v} | set(adjacency[v])
            dfs_dom(i + 1, current_set, dominated_set, i)

        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"Tamanho mínimo do conjunto dominante: {best_size}\n")
            f.write(f"Conjunto dominante: {sorted(best_set)}\n")

        print(f"Nós de inicio testados: {start_count}/{N_start} ({round((start_count/N_start)*100)}%)")
        print(f"Chamadas recursivas: {search_count}")
        return best_set, best_size

    def greedy_solve_longest_path(self, output_file="maior_caminhoGreedy.txt"):
        best_len = 0
        best_path = []
        N = self.node_count
        adjacency = self.adjacency

        with open(output_file, "w", encoding="utf-8"):
            pass

        search_count = 0
        start_count = 0

        nodes_sorted = sorted(self.graph.nodes(), key=self.graph.degree, reverse=True)
        N_start = len(nodes_sorted)
        next_threshold = 5

        for v in nodes_sorted:
            start_count += 1
            percent = (start_count / N_start) * 100
            while percent >= next_threshold:
                print(f"{next_threshold}%")
                next_threshold += 5

            visited_local = {v}
            path_local = [v]
            current = v

            while True:
                candidates = [nbr for nbr in adjacency[current] if nbr not in visited_local]
                if not candidates:
                    break

                best_candidate = None
                best_cover = -1
                for u in candidates:
                    cover = sum(1 for w in adjacency[u] if w not in visited_local)
                    if cover > best_cover:
                        best_cover = cover
                        best_candidate = u

                visited_local.add(best_candidate)
                path_local.append(best_candidate)
                current = best_candidate
                search_count += 1

            if len(path_local) > best_len:
                best_len = len(path_local)
                best_path = list(path_local)

        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"Caminho mais longo {best_len}\n")
            f.write(f"Caminho: {best_path}\n")

        print(f"Nos iniciais testados: {start_count}/{N_start} ({round((start_count/N_start)*100)}%)")
        print(f"Chamadas recursivas: {search_count}")
        return best_path, best_len

    def greedy_solve_dominating_set(self, output_file="dominantGreedy.txt"):
        adjacency = self.adjacency
        nodes_sorted = sorted(self.graph.nodes())
        N = self.node_count

        with open(output_file, "w", encoding="utf-8"):
            pass

        best_size = N
        best_set = set(nodes_sorted)
        search_count = 0
        start_count = 0

        N_start = len(nodes_sorted)
        next_threshold = 5

        for v in nodes_sorted:
            start_count += 1
            percent = (start_count / N_start) * 100
            while percent >= next_threshold:
                print(f"{next_threshold}%")
                next_threshold += 5

            current_set = {v}
            dominated = {v} | set(adjacency[v])
            while len(dominated) < N:
                # pick vertex that covers most undominated
                best_candidate = None
                best_cover = -1
                for u in nodes_sorted:
                    if u not in dominated:
                        cover = 0
                        for w in adjacency[u]:
                            if w not in dominated:
                                cover += 1
                        if cover > best_cover:
                            best_cover = cover
                            best_candidate = u
                current_set.add(best_candidate)
                dominated |= {best_candidate} | set(adjacency[best_candidate])
                search_count += 1

            if len(current_set) < best_size:
                best_size = len(current_set)
                best_set = set(current_set)

        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"Tamanho aproximado do set dominante: {best_size}\n")
            f.write(f"set dominante: {sorted(best_set)}\n")

        print(f"Nos de inicio testados: {start_count}/{N_start} ({round((start_count/N_start)*100)}%)")
        print(f"Chamadas recursivas gulosas: {search_count}")
        return best_set, best_size

    def apply_greedy_approximation(self):
        def find_farthest_path(start_vertex, blocked_vertices=set()):
            explored = set()
            parent_map = {}
            distance_map = {}
            
            def depth_search(vertex, depth):
                explored.add(vertex)
                distance_map[vertex] = depth
                for adjacent in self.graph.neighbors(vertex):
                    if adjacent not in explored and adjacent not in blocked_vertices:
                        parent_map[adjacent] = vertex
                        depth_search(adjacent, depth + 1)
            
            depth_search(start_vertex, 0)
            if not distance_map:
                return [], None
            
            farthest_vertex = max(distance_map, key=distance_map.get)
            path_reconstruction = []
            current = farthest_vertex
            
            while current != start_vertex:
                path_reconstruction.append(current)
                current = parent_map[current]
            path_reconstruction.append(start_vertex)
            path_reconstruction.reverse()
            
            return path_reconstruction, farthest_vertex
        
        initial_vertex = next((v for v in self.graph.nodes() if self.graph.degree(v) == 1), 
                             list(self.graph.nodes())[0])
        
        first_path, endpoint = find_farthest_path(initial_vertex)
        used_vertices = set(first_path)
        used_vertices.discard(endpoint)
        
        second_path, _ = find_farthest_path(endpoint, used_vertices)
        
        if len(second_path) > 1 and self.graph.has_edge(first_path[-1], second_path[1]):
            complete_path = first_path + second_path[1:]
        else:
            complete_path = first_path
        
        with open("resultados/maior_caminho.txt", "a") as output:
            output.write(f"Caminho simples aproximado com {len(complete_path)} vértices:\n")
            output.write(f"{complete_path}\n")

    def _write_path_result(self, path, filename):
        if path:
            with open(filename, "a", encoding="utf-8") as file:
                file.write(f"Trajeto mais longo com {len(path)} vértices:\n")
                file.write(f"{path}\n")
        else:
            print("Trajeto válido não encontrado.")

    def _serialize_result(self, result):
        if isinstance(result, set):
            return list(result)
        elif isinstance(result, dict):
            return {key: self._serialize_result(value) for key, value in result.items()}
        elif isinstance(result, (list, tuple)):
            return [self._serialize_result(item) for item in result]
        return result

    def update_progress(self, new_progress):
        global progress_data
        progress_data["progress"] = new_progress
        print(f"Progress updated: {progress_data}")

class GraphBuilder:
    @staticmethod
    def load_station_data(file_path):
        station_dict = {}
        
        with open(file_path, encoding="utf-8") as file_handle:
            for raw_line in file_handle:
                cleaned_line = raw_line.strip()
                if not cleaned_line:
                    continue
                
                station_name, x_coordinate, y_coordinate = cleaned_line.rsplit(" ", 2)
                coordinates = float(x_coordinate), float(y_coordinate)
                station_dict[station_name] = coordinates
        
        return station_dict
    
    @staticmethod
    def load_line_data(file_path):
        line_collection = []
        current_name = current_color = None
        connection_list = []
        
        with open(file_path, encoding="utf-8") as file_handle:
            for processed_line in file_handle:
                processed_line = processed_line.strip()
                if not processed_line:
                    continue
                
                if processed_line.lower().startswith("linha"):
                    if current_name is not None:
                        line_collection.append((current_name, current_color, connection_list))
                        connection_list = []
                    
                    parts = processed_line.split(",")
                    current_name = parts[0].strip()
                    current_color = parts[1].strip() if len(parts) > 1 else "black"
                    continue
                
                if ";" in processed_line:
                    station_a, station_b = (token.strip() for token in processed_line.split(";", 1))
                    connection_list.append((station_a, station_b))
        
        if current_name is not None:
            line_collection.append((current_name, current_color, connection_list))
        
        return line_collection
    
    @staticmethod
    def construct_network(station_data, line_data):
        network = nx.Graph()
        network.add_nodes_from((name, {"pos": position}) for name, position in station_data.items())
        
        for line_identifier, line_color, edge_connections in line_data:
            for node_u, node_v in edge_connections:
                if node_u in station_data and node_v in station_data:
                    network.add_edge(node_u, node_v, cor=line_color, linha=line_identifier)
        
        return network

class GraphVisualizer:
    @staticmethod
    def _normalize_color(color_name):
        color_mapping = {
            'yellow': 'gold',
            'blue': 'blue',
            'purple': 'purple',
            'lightgreen': 'lightgreen',
            'pink': 'pink',
            'olive': 'olive',
            'sienna': 'sienna',
            'brown': 'brown',
            'darkgreen': 'darkgreen',
            'indigo': 'indigo'
        }
        return color_mapping.get(color_name.lower(), 'gray')
    
    @staticmethod
    def render_network(network, output_path="grafo_metro.png", resolution=300):
        position_data = nx.get_node_attributes(network, "pos")
        color_grouped_edges = defaultdict(list)
        
        for node_u, node_v, edge_data in network.edges(data=True):
            normalized_color = GraphVisualizer._normalize_color(edge_data["cor"])
            color_grouped_edges[normalized_color].append((node_u, node_v))
        
        plt.figure(figsize=(14, 10))
        nx.draw_networkx_nodes(network, position_data, node_size=300, node_color="lightgray")
        nx.draw_networkx_labels(network, position_data, font_size=8)
        
        for edge_color, edge_list in color_grouped_edges.items():
            nx.draw_networkx_edges(network, position_data, edgelist=edge_list, width=2, edge_color=edge_color)
        
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path, dpi=resolution)
        plt.close()
        print(f"Grafo salvo em {output_path}.")

def read_stations(path):
    return GraphBuilder.load_station_data(path)

def read_lines(path):
    return GraphBuilder.load_line_data(path)

def build_graph(stations, metro_lines):
    return GraphBuilder.construct_network(stations, metro_lines)

def draw_graph(g, out_file="grafo_metro.png", dpi=300):
    GraphVisualizer.render_network(g, out_file, dpi)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Inicializa o solver globalmente
graph = None  # Substitua pelo carregamento do grafo real
solver = None

@app.route('/initialize', methods=['POST'])
def initialize():
    global graph, solver
    print("/initialize endpoint hit")
    station_data = read_stations("./estacoes.txt")#request.json.get('stations')
    line_data = read_lines("./linhas.txt")#request.json.get('lines')

    if not station_data or not line_data:
        print("Erro: Dados de estações ou linhas estão vazios.")
        return jsonify({"error": "Dados de estações ou linhas estão vazios."}), 400

    graph = GraphBuilder.construct_network(station_data, line_data)
    if graph.number_of_nodes() == 0 or graph.number_of_edges() == 0:
        print("Erro: Grafo construído está vazio.")
        return jsonify({"error": "Grafo construído está vazio."}), 400

    solver = MetroSolver(graph)
    print(f"Grafo inicializado com {graph.number_of_nodes()} nós e {graph.number_of_edges()} arestas.")
    return jsonify({"message": "Grafo inicializado com sucesso."})

# Adicionei logs detalhados para identificar o ponto exato do erro durante a execução dos algoritmos.

@app.route('/run', methods=['POST'])
def run_algorithm():
    global solver
    if not solver or not solver.graph or solver.graph.number_of_nodes() == 0:
        print("Erro: Solver não inicializado ou grafo vazio.")
        return jsonify({"error": "Solver não inicializado ou grafo vazio."}), 400

    data = request.json
    problem = data.get('problem')
    algorithm = data.get('algorithm')

    print(f"Recebido problema: {problem}, algoritmo: {algorithm}")

    start_time = time.time()
    result = None

    try:
        if algorithm == 'forca_bruta':
            print("Executando força bruta...")
            if problem == 'A':
                result = solver.bruteForce_solve_longest_path()
            elif problem == 'B':
                result = solver.bruteForce_solve_dominating_set()
        elif algorithm == 'branch_and_bound':
            print("Executando branch and bound...")
            if problem == 'A':
                result = solver.branchBound_solve_longest_path()
            elif problem == 'B':
                result = solver.branchBound_solve_dominating_set()
        elif algorithm == 'heuristica':
            print("Executando heurística...")
            if problem == 'A':
                result = solver.greedy_solve_longest_path()
            elif problem == 'B':
                result = solver.greedy_solve_dominating_set()
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        return jsonify({"error": str(e)}), 500

    elapsed_time = time.time() - start_time

    print(f"Resultado: {result}, Tempo de execução: {elapsed_time}s")

    serialized_result = solver._serialize_result(result)

    return jsonify({
        "result": serialized_result,
        "elapsed_time": elapsed_time
    })

progress_data = {"progress": 0}

@app.route('/progress-updates', methods=['GET'])
def progress_updates():
    def generate():
        while True:
            yield f"data: {json.dumps(progress_data)}\n\n"
            print(f"Streaming progress data: {progress_data}")
            time.sleep(1)

    return Response(generate(), content_type='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True)
