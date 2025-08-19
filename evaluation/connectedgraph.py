import openai
import os
from tqdm import tqdm
import networkx as nx
import numpy as np
import argparse
from datetime import datetime, timedelta, timezone

import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from utils.graph_motif_find import find_cycles, find_length_two_paths
from utils.predict import predict

model_list = ["gpt-3.5-turbo","gpt-4o-mini"]
parser = argparse.ArgumentParser(description="connectedgraph")
parser.add_argument('--model', type=str, default="gpt-4o-mini", help='name of LM (default: gpt-4o-mini)')
parser.add_argument('--mode', type=str, default="easy", help='mode (default: easy)')
parser.add_argument('--prompt', type=str, default="none", help='prompting techniques (default: none)')
parser.add_argument('--T', type=int, default=0, help='temprature (default: 0)')
parser.add_argument('--token', type=int, default=400, help='max token (default: 400)')
parser.add_argument('--SC', type=int, default=0, help='self-consistency (default: 0)')
parser.add_argument('--SC_num', type=int, default=5, help='number of cases for self-consistency (default: 5)')
parser.add_argument('--basic', type=int, default=1, help='use basic prompt or not')
parser.add_argument('--both', type=int, default=0, help='use shortpath and motif prompt')
args = parser.parse_args()
def translate(edge, n, args):
    Q = ''
    if args.prompt in ["CoT","Shortpath","Motif"] and args.basic == 1:
        with open("Graph/connectedgraph/prompt/" + args.prompt + "-prompt.txt", "r") as f:
            exemplar = f.read()
        Q = Q + exemplar + "\n\n\n"
    Q = Q + "In an undirected graph, (i,j) means that node i and node j are connected with an undirected edge.\nThe nodes are numbered from 0 to " + str(n-1)+", and the edges are:"
    for i in range(len(edge)):
        Q = Q + ' ('+str(edge[i][0])+','+str(edge[i][1])+')'

    Q = Q + "\n"

    if args.prompt == "Shortpath" or args.both == 1:
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
    if args.prompt == "Motif" or args.both == 1:
        # Find cycles (motifs) in the graph
        k = 3
        motifs = find_cycles(edge, k)
        max_motifs = 5
        prompt = "Here are some cycles in the graph constructed by the above edges to help you understand the structure:\n"
        prompt += "A cycle in a graph is a sequence of vertices starting and ending at the same vertex, with no repeated edges.\n"
        count = 0
        for motif in motifs:
            if count < max_motifs:
                prompt += f"{motif}\n"
                count += 1
            else:
                break
        Q += prompt

    Q = Q + "Q: Is this graph connected?\nA:"
    # Q = Q + "Q: Is this graph connected?\n Provide your reasoning and state the result clearly as 'yes' or 'no' at the end.\nA:"
    # Q = Q + "Q: Is this graph connected?\n Just give the answer.A:"
    # Q = Q + "Q: Is this graph connected? Finally, output the result as “yes” or “no.”\nA: Let's think step by step:"
    return Q

def log(Q, res, answer, args):
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    time = bj_dt.now().strftime("%Y%m%d---%H-%M-%S")
    newpath = 'log/connectedgraph/'+args.model+'-'+args.mode+'-'+time+ '-' + args.prompt
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
        for j in range(i*batch_num, min(g_num, (i+1)*batch_num)):
            with open("Graph/connectedgraph/graph/"+args.mode+"/standard/graph"+str(j)+".txt","r") as f:
                n, m = [int(x) for x in next(f).split()]
                edge = []
                for line in f: # read rest of lines
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
                ans = ans.replace("**", "")
                answer.append(Q_list[j] + ans)
                p1 = ans.rfind("yes")
                p2 = ans.rfind("no")
                idx = i * batch_num + j
                if (idx * 2 < g_num and p1 > p2) or (idx * 2 >= g_num and p2 > p1):
                    vote += 1
                print(i * batch_num + j, p1, p2, vote)
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