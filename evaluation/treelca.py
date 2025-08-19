import os
import openai
import argparse
import numpy as np
from tqdm import tqdm
import networkx as nx
from datetime import datetime, timedelta, timezone
from tenacity import retry, stop_after_attempt, wait_random_exponential
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from utils.predict import predict
from utils.graph_motif_find import find_length_two_paths, find_cycles, find_length_three_paths, find_length_four_paths

parser = argparse.ArgumentParser(description="LCA Task")
parser.add_argument('--model', type=str, default="gpt-4o-mini", help='name of LM (default: gpt-4o-mini)')
parser.add_argument('--mode', type=str, default="easy", help='mode (default: easy)')
parser.add_argument('--prompt', type=str, default="none", help='prompting techniques (default: none)')
parser.add_argument('--T', type=int, default=0, help='temperature (default: 0)')
parser.add_argument('--token', type=int, default=400, help='max token (default: 400)')
parser.add_argument('--SC', type=int, default=0, help='self-consistency (default: 0)')
parser.add_argument('--SC_num', type=int, default=5, help='number of cases for self-consistency (default: 5)')
args = parser.parse_args()

def preprocess_tree_edges(edges):
    G = nx.Graph()
    G.add_edges_from(edges)
    return G

def find_lca(tree, u, v):
    root = 0  # Assume root is 0
    paths = nx.single_source_shortest_path(tree, root)
    path_u, path_v = paths[u], paths[v]

    # Find the last common node in both paths
    lca = -1
    for i in range(min(len(path_u), len(path_v))):
        if path_u[i] == path_v[i]:
            lca = path_u[i]
        else:
            break
    return lca


def translate(edge, n, q, args):
    Q = ''
    if args.prompt in ["CoT","Shortpath"]:
        with open("Graph/treelca/prompt/" + args.prompt + "-prompt.txt", "r") as f:
            exemplar = f.read()
        Q = Q + exemplar + "\n\n\n"
    Q += "In a tree rooted at node 0, (i, j) means that node i and node j are connected with an undirected edge.\n"
    Q += "The nodes are numbered from 0 to " + str(n - 1) + ", and the edges are:"
    for i in range(len(edge)):
        Q = Q + ' ('+str(edge[i][0])+','+str(edge[i][1])+')'
    if args.prompt == "Shortpath":
        length_two_paths = find_length_two_paths(edge)
        max_paths = 5
        prompt = "Here are some paths in the graph constructed by the above edges to help you understand the entire graph:\n"
        prompt += "A path in a graph is a sequence of vertices where each adjacent pair is connected by an edge.\n"
        count = 0
        for path in length_two_paths:
            if count < max_paths:
                prompt += f"{path}\n"
                count += 1
            else:
                break
        Q += prompt

    Q += f"Q: What is the lowest common ancestor of node {q[0]} and node {q[1]}?\nA:"
    # Q += f"Q: What is the lowest common ancestor of node {q[0]} and node {q[1]}? Provide your reasoning and state the result clearly as “the lowest common ancestor of node {q[0]} and node {q[1]} is” at the end.\nA:"
    # Q = Q + " Let's think step by step:"
    return Q


def log(Q, res, answer, args):
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    time = bj_dt.now().strftime("%Y%m%d---%H-%M-%S")
    newpath = 'log/treelca/'+args.model+'-'+args.mode+'-'+time+ '-' + args.prompt
    if args.SC == 1:
        newpath = newpath + "+SC"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    newpath = newpath + "/"
    np.save(newpath+"res.npy", res)
    np.save(newpath+"answer.npy", answer)
    with open(newpath+"prompt.txt","w") as f:
        f.write(Q)
        f.write("\n")
        f.write("Acc: " + str(res.sum())+'/'+str(len(res)) + '\n')
        print(args, file=f)

def main():
    # if 'OPENAI_API_KEY' in os.environ:
    #     openai.api_key = os.environ['OPENAI_API_KEY']
    # else:
    #     raise Exception("Missing openai key!")
    # if 'OPENAI_ORGANIZATION' in os.environ:
    #     openai.organization = os.environ['OPENAI_ORGANIZATION']
    res, answer = [], []
    if args.mode == "easy":
        g_num = 100
    elif args.mode == "medium":
        g_num = 100
    elif args.mode == "hard":
        g_num = 100


    batch_num = 20
    for i in tqdm(range((g_num + batch_num - 1) // batch_num)):
        G_list, Q_list = [], []
        for j in range(i * batch_num, min(g_num, (i + 1) * batch_num)):
            with open(f"Graph/treelca/graph/{args.mode}/standard/graph{j}.txt", "r") as f:
                n, m = [int(x) for x in next(f).split()]
                array = []
                for line in f:  # read rest of lines
                    array.append([int(x) for x in line.split()])
                edge, q = array[:-1], array[-1]
                G = preprocess_tree_edges(edge)
                Q = translate(edge, n, q, args)
                Q_list.append(Q)
                G_list.append((G, q))

        sc = 1
        if args.SC == 1:
            sc = args.SC_num
        sc_list = []
        for k in range(sc):
            answer_list = predict(Q_list, args)
            sc_list.append(answer_list)

        for j in range(len(Q_list)):
            vote = 0
            G, queries = G_list[j]
            u, v = queries
            lca = find_lca(G, u, v)
            mode_str = f"the lowest common ancestor of node {u} and node {v} is"
            for k in range(sc):
                ans = sc_list[k][j].strip().lower()
                answer.append(Q_list[j] + ans)
                pos = ans.rfind(mode_str)
                if pos != -1:
                    pos = pos + len(mode_str) + 1
                    i = pos
                    while i < len(ans) and not (ans[i] >= '0' and ans[i] <= '9'):
                        i += 1
                    num = 0
                    while i < len(ans) and ans[i] >= '0' and ans[i] <= '9':
                        num = num * 10 + int(ans[i])
                        i += 1
                    print(num, lca)
                    if num == lca:
                        vote += 1
            if vote * 2 >= sc:
                res.append(1)
            else:
                res.append(0)

    res = np.array(res)
    answer = np.array(answer)
    log(Q, res, answer, args)
    print(res.sum())

if __name__ == "__main__":
    main()