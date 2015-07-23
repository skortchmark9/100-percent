import networkx as nx 
from networkx.readwrite import json_graph
from operator import itemgetter
import matplotlib.pyplot as plt
#from profilehooks import profile
import random,ujson

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

#@profile
def get_recs(G,v,topn=5):
	G = diffusion(G,v)
	scores = {(u,G.node[u]['resource']) for u in G.nodes() if G.node[u]['node_type']=='doc'}
	recs, _   = zip(*sorted(scores, reverse=True, key=itemgetter(1)))

	#print [G.node[u]['resource'] for u in G.nodes() if G.node[u]['node_type']=='doc' and G.node[u]['resource'] > 0.0]
	return filter(lambda s: s not in set(G.neighbors(v)), recs)[:topn]


"""
G = nx.Graph()

docs  = ['a','b','c','d','e','f']
users = ['Sam','Muanis','Mike','Avery','Dan']

G.add_nodes_from(docs,node_type='doc')
G.add_nodes_from(users,node_type='user')
G.add_edges_from([('a','Sam'),('b','Muanis'),('c','Mike'),('Avery','d'),('Dan','e'),('Dan','f'),
				  ('Muanis','a'),('Muanis','d'),('d','Mike'),('Avery','b'),('Sam','e')])

pos = {}
for d in docs:
	pos[d] = (random.random(),1.0)
for u in users:
	pos[u] = (random.random(),0.0)

nx.draw(G,pos,nodelist=(docs), node_color='r',node_shape='s')
nx.draw(G,pos,nodelist=(users),node_color='b',node_shape='o')
plt.show()
"""




G = nx.Graph()

regi = '67198392' #'16177164' 
# JAKE SOLOFF : 72218121
# MUANIS      : 67618194
# MIKE DEWAR  : 67198392
G.add_node(regi,node_type='user',group='#000000')

import memcache, time
mc = memcache.Client(['127.0.0.1:11211'], debug=0)
counter = 0

#docs  = set([]) #
#users = {regi}
#pos = {}
#pos[regi] = (0.0,0.0)
#docs |= set(nodes[0]) #
#users|= set(nodes[1])
#for d in docs:
#	pos[d] = (random.random(),1.0)
#for u in users:
#	pos[u] = (random.random(),0.0)


while True:
    
    key = 'chunk' + str(counter)
    result = mc.get(key)
    print(key, result)
    if result:
    	nodes = map(list, zip(*result))
    	G.add_nodes_from(nodes[0],node_type='doc',group='#0000FF')
    	G.add_nodes_from(nodes[1],node_type='user',group='#FF0000')
    	G.add_edges_from(result)

        counter += 1
    else:
    	recs = list(get_recs(G,regi,5))
    	#print G.neighbors(regi)
    	#print recs

    	u = regi
    	N = G.neighbors(regi)
    	NN = reduce(lambda a,b: a+b, map(lambda u: G.neighbors(u),N))
    	NNN = reduce(lambda a,b: a+b, map(lambda u: G.neighbors(u),NN))
    	H = G.subgraph([regi]+N+list(recs))#+NN)#+NNN)
    	H.node[regi]['group'] = '#000000'
    	for r in recs:
    		H.node[regi]['group'] = '#FFCC00'

    	H.node[regi]['name'] = regi
    	for u in N:
    		H.node[u]['name'] = u
    	for r in recs:
    		H.node[r]['name'] = r
    	
    	data = json_graph.node_link_data(H)
    	with open('data.json', 'w') as outfile:
    		ujson.dump(data, outfile)


    	#time.sleep(1)



