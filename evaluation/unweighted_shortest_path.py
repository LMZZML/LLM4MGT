import openai
import os
from tqdm import tqdm
import networkx as nx
import numpy as np
import argparse
import random
import time
from datetime import datetime, timedelta, timezone
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

import sys
# 获取项目根目录路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from utils.graph_motif_find import find_length_two_paths, find_cycles
from utils.predict import predict

model_list = ["gpt-3.5-turbo","gpt-4o-mini"]
parser = argparse.ArgumentParser(description="shortest path")
parser.add_argument('--model', type=str, default="gpt-4o-mini", help='name of LM (default: gpt-4o-mini)')
parser.add_argument('--mode', type=str, default="easy", help='mode (default: easy)')
parser.add_argument('--prompt', type=str, default="none", help='prompting techniques (default: none)')
parser.add_argument('--T', type=int, default=0, help='temprature (default: 0)')
parser.add_argument('--token', type=int, default=400, help='max token (default: 400)')
parser.add_argument('--SC', type=int, default=0, help='self-consistency (default: 0)')
parser.add_argument('--city', type=int, default=0, help='whether to use city (default: 0)')
parser.add_argument('--SC_num', type=int, default=5, help='number of cases for self-consistency (default: 5)')
args = parser.parse_args()


def translate(G, q, args):
    edge = list(G.edges())
    n, m = G.number_of_nodes(), G.number_of_edges()
    Q = ''
    prompt_folder = "prompt"
    if args.city == 1:
        prompt_folder = "city-prompt"
    if args.prompt in ["CoT",'Shortpath','Motif']:
        with open("Graph/unweighted_shortest_path/"+prompt_folder+"/" + args.prompt + "-prompt.txt", "r") as f:
            exemplar = f.read()
        Q = Q + exemplar + "\n\n\n"
    Q = Q + "In an undirected graph, (i,j) means that node i and node j are connected with an undirected edge of weight 1.\n"
    Q = Q + "The nodes are numbered from 0 to " + str(n - 1) + ", and the edges are:"

    for i in range(len(edge)):
        Q = Q + ' (' + str(edge[i][0]) + ',' + str(edge[i][1]) +')'

    Q = Q + '\n'
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
    if args.prompt == "Motif":
        # Find cycles (motifs) in the graph
        k = 3
        motifs = find_cycles(edge, k)
        max_motifs = 5
        prompt = "Here are some cycles in the graph constructed by the above edges to help you understand the structure:\n"
        prompt += "A cycle in a graph is a sequence of vertices starting and ending at the same vertex, with no repeated edges.\n"
        count = 0
        for motif in motifs:
            if count < max_motifs:
                prompt += f"{list(motif)}\n"
                count += 1
            else:
                break
        Q += prompt

    Q = Q + "Q: Give the shortest path from node " + str(q[0])+" to node " + str(q[1]) + ".\nA:"
    # Q = Q + "Q: Give the shortest path from node " + str(q[0])+" to node " + str(q[1]) + ".? Provide your reasoning and state the result in the format: 'The shortest path from node X to node Y is [path] with a total weight of Z.' at the end\nA:"
    # Q = Q + "Q: Give the shortest path from node " + str(q[0])+" to node " + str(q[1]) + ". Just give the answer.\nA:"
    # Q = Q + "Q: Give the shortest path from node " + str(q[0])+" to node " + str(q[1]) + ".\nA: Let's think step by step."

    return Q

def log(Q, res1, res2, answer, args):
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    time = bj_dt.now().strftime("%Y%m%d---%H-%M-%S")
    newpath = 'log/unweighted_shortest_path/'+args.model+'-'+args.mode+ '-'+time+ '-' + args.prompt
    if args.city == 1:
        newpath = newpath + "+city"
    if args.SC == 1:
        newpath = newpath + "+SC"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    newpath = newpath + "/"
    np.save(newpath+"res1.npy", res1)
    np.save(newpath+"res2.npy", res2)
    np.save(newpath+"answer.npy", answer)
    with open(newpath+"prompt.txt","w") as f:
        f.write(Q)
        f.write("\n")
        f.write("Acc: " + str(res1.sum())+'/'+str(len(res1)) + '\n')
        f.write("Acc2: " + str(res2.sum())+'/'+str(len(res2)) + '\n')
        f.write("\n")
        print(args, file=f)

def evaluate(ans, G, q):
    entity = "node"
    if args.city == 1:
        entity = "city"
    mode_str = "the shortest path from "+entity+' '+str(q[0])+" to "+ entity + ' ' + str(q[1]) + ' is'
    pos = ans.find(mode_str)
    if pos == -1:
        return 0, 0
    pos = pos + len(mode_str) + 1
    num, flag = 0, 0
    solution = []
    for i in range(pos, len(ans)):
        if ans[i] >= '0' and ans[i] <='9':
            num = num*10 + int(ans[i])
            flag = 1
        else:
            if flag == 1:
                solution.append(num)
                if num == q[1]:
                    break
                flag = 0
            num = 0
    length = 0
    flag1, flag2 = 1, 1
    for i in range(len(solution)-1):
        if not G.has_edge(solution[i], solution[i+1]):
            flag1 = 0
            break
        length += G[solution[i]][solution[i+1]]["weight"]
    shortest = nx.shortest_path_length(G, source=q[0], target=q[1], weight="weight")
    if length != shortest:
        flag1 = 0
    pos = ans.rfind("total weight")
    if pos == -1:
        return flag1, 0
    i = pos
    while i < len(ans) and not (ans[i] >= '0' and ans[i] <='9'):
        i+=1
    num = 0
    while i < len(ans) and ans[i] >= '0' and ans[i] <='9':
        num = num*10 + int(ans[i])
        i+=1
    if num != shortest:
        flag2 = 0
    print(num, shortest)
    return flag1, flag2

def main():
    # if 'OPENAI_API_KEY' in os.environ:
    #     openai.api_key = os.environ['OPENAI_API_KEY']
    # else:
    #     raise Exception("Missing openai key!")
    # if 'OPENAI_ORGANIZATION' in os.environ:
    #     openai.organization = os.environ['OPENAI_ORGANIZATION']

    res1,  res2, answer = [], [], []
    if args.mode == "easy":
        g_num = 100
    elif args.mode == "medium":
        g_num = 100
    elif args.mode == "hard":
        g_num = 100

    batch_num = 20
    for i in tqdm(range((g_num + batch_num - 1) // batch_num)):
        G_list, Q_list, q_list = [], [], []
        for j in range(i*batch_num, min(g_num, (i+1)*batch_num)):
            with open("Graph/unweighted_shortest_path/graph/"+args.mode+"/standard/graph"+str(j)+".txt","r") as f:
                n, m = [int(x) for x in next(f).split()]
                array = []
                for line in f: # read rest of lines
                    array.append([int(x) for x in line.split()])
                edge, q = array[:-1], array[-1]
                G = nx.Graph()
                G.add_nodes_from(range(n))
                for k in range(m):
                    G.add_edge(edge[k][0], edge[k][1], weight = edge[k][2])
                Q = translate(G, q, args)
                Q_list.append(Q)
                G_list.append(G)
                q_list.append(q)
        sc = 1
        if args.SC == 1:
            sc = args.SC_num
        sc_list = []
        for k in range(sc):
            answer_list = predict(Q_list, args)
            sc_list.append(answer_list)
        for j in range(len(Q_list)):
            vote1, vote2 = 0, 0
            for k in range(sc):
                ans, G = sc_list[k][j].lower(), G_list[j]
                answer.append(Q_list[j] + ans)
                try:
                    r1, r2 = evaluate(ans.lower(), G, q_list[j]) # r1 for path_length check and r2 for total weight check
                    vote1 += r1
                    vote2 += r2
                except:
                    print(ans.lower())
            r1 = 1 if vote1*2 > sc else 0
            r2 = 1 if vote2*2 > sc else 0 
            res1.append(r1)
            res2.append(r2)

    res1 = np.array(res1)
    res2 = np.array(res2)
    answer = np.array(answer)
    log(Q, res1, res2, answer, args)
    print(res2.sum())

if __name__ == "__main__":
    main()