import openai
import os
from tqdm import tqdm
import networkx as nx
import numpy as np
import argparse
import time
import random
from datetime import datetime, timedelta, timezone
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff


import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from utils.graph_motif_find import find_length_two_paths, find_cycles, find_length_three_paths, find_length_four_paths
from utils.predict import predict


model_list = ["gpt-3.5-turbo","gpt-4o-mini"]
parser = argparse.ArgumentParser(description="treedepth")
parser.add_argument('--model', type=str, default="gpt-4o-mini", help='name of LM (default: gpt-4o-mini)')
parser.add_argument('--mode', type=str, default="easy", help='mode (default: easy)')
parser.add_argument('--prompt', type=str, default="none", help='prompting techniques (default: none)')
parser.add_argument('--T', type=int, default=0, help='temprature (default: 0)')
parser.add_argument('--token', type=int, default=400, help='max token (default: 400)')
parser.add_argument('--SC', type=int, default=0, help='self-consistency (default: 0)')
parser.add_argument('--SC_num', type=int, default=5, help='number of cases for self-consistency (default: 5)')
parser.add_argument('--basic', type=int, default=1, help='use basic prompt or not')
args = parser.parse_args()

def translate(edge, n, args):
    Q = ''
    if args.prompt in ["CoT", "Shortpath"] and args.basic == 1:
        with open("Graph/treedepth/prompt/" + args.prompt + "-prompt.txt", "r") as f:
            exemplar = f.read()
        Q = Q + exemplar + "\n\n\n"
    Q += "In a tree rooted at node 0, (i, j) means that node i and node j are connected with an undirected edge.\n"
    Q += "The nodes are numbered from 0 to " + str(n - 1) + ", and the edges are:"
    #character = [chr(65+i) for i in range(26)] + [chr(65+i)+chr(65+i) for i in range(26)]
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
    Q += "The depth of a tree is defined as the maximum length of a path from the root node to any leaf node, where the depth of the root node 0 is considered 0.\n"
    # Q += "Q: What is the depth of this tree?\nA:"
    # Q += "Q: What is the depth of this tree? Provide your reasoning and state the result clearly as “the depth of this tree is “X” at the end.\nA:"
    # Q += "Q: What is the depth of this tree? Finally, output the result as “the depth of this tree is “X”. Please do not use programming to solve this.\nA: Let's think step by step:"
    return Q

def log(Q, res, answer, args):
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    time = bj_dt.now().strftime("%Y%m%d---%H-%M-%S")
    newpath = 'log/treedepth/'+args.model+'-'+args.mode+'-'+time+ '-' + args.prompt
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


def find_tree_depth(graph):
    def dfs(node, parent):
        max_depth = 0
        for neighbor in graph.neighbors(node):  # Use graph.neighbors to get adjacent nodes
            if neighbor != parent:  # Avoid revisiting the parent
                max_depth = max(max_depth, dfs(neighbor, node))
        return max_depth + 1

    return dfs(0, -1)


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
        for j in range(i*batch_num, min(g_num, (i+1)*batch_num)):
            with open("Graph/treedepth/graph/"+args.mode+"/standard/graph"+str(j)+".txt","r") as f:
                n, m = [int(x) for x in next(f).split()]
                edge = []
                for line in f:
                    edge.append([int(x) for x in line.split()])
                G = nx.Graph()
                G.add_nodes_from(range(n))
                for k in range(m):
                    G.add_edge(edge[k][0], edge[k][1])
                Q = translate(edge, n, args)
                Q_list.append(Q)
                G_list.append(G)
        sc = 1
        if args.SC == 1:
            sc = args.SC_num
        sc_list = []
        for k in range(sc):
            answer_list = predict(Q_list, args)
            sc_list.append(answer_list)
        for j in range(len(Q_list)):
            vote = 0
            for k in range(sc):
                ans, G = sc_list[k][j].lower(), G_list[j]
                answer.append(Q_list[j] + ans)
                pos = ans.rfind("depth")
                if pos != -1:
                    depth = find_tree_depth(G)
                    i = pos
                    while i < len(ans) and not (ans[i] >= '0' and ans[i] <= '9'):
                        i += 1
                    num = 0
                    while i < len(ans) and ans[i] >= '0' and ans[i] <= '9':
                        num = num * 10 + int(ans[i])
                        i += 1
                    if num + 1 == depth:
                        vote += 1
                    print(num, depth)
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