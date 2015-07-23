import networkx as nx 
from operator import itemgetter


G = nx.Graph()

docs  = ['a','b','c','d','e','f']
users = ['Sam','Muanis','Mike','Avery','Dan']

G.add_nodes_from(docs,node_type='doc')
G.add_nodes_from(users,node_type='user')
G.add_edges_from([('a','Sam'),('b','Muanis'),('c','Mike'),('Avery','d'),('Dan','e'),('Dan','f'),
				  ('Muanis','a'),('Muanis','d'),('d','Mike'),('Avery','b'),('Sam','e')])

def distribute(G, v, node_type=None):
    if G.node[v]['resource'] == 0.0:
        return G
    N = [u for u in G.neighbors(v) if node_type==None or G.node[u]['node_type']==node_type]
    for n in N:
        G.node[n]['resource'] += G.node[v]['resource']/len(N)
    G.node[v]['resource'] = 0.0
    return G 

def diffusion(G,v):
	H = G
	for u in H.nodes():
		H.node[u]['resource'] = 0.0
	H.node[v]['resource'] = 1.0
	H = distribute(H,v,node_type='doc')
	for u in G.neighbors(v):
		H = distribute(H,u,node_type='user')
	for u in G.neighbors(v):
		for w in G.neighbors(u):
			H = distribute(H,w,node_type='doc')
	return H

def get_recs(G,v,topn=15):
	G = diffusion(G,v)
	scores = {(u,G.node[u]['resource']) for u in G.nodes() if G.node[u]['node_type']=='doc'}
	recs, _   = zip(*sorted(scores, reverse=True, key=itemgetter(1)))
	return filter(lambda s: s not in set(G.neighbors(v)), recs)[:topn]


import matplotlib.pyplot as plt
import random

pos = {}
for d in docs:
	pos[d] = (random.random(),1.0)
for u in users:
	pos[u] = (random.random(),0.0)


nx.draw(G,pos,nodelist=(docs), node_color='r',node_shape='s')
nx.draw(G,pos,nodelist=(users),node_color='b',node_shape='o')
plt.show()


