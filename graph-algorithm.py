import networkx as nx 
from networkx.readwrite import json_graph
from operator import itemgetter
import matplotlib.pyplot as plt
import random,ujson
import papi

# for timing
# "from profilehooks import profile"
# decorate a function with "@profile"

# given:  a graph G and a node v,
# return: the graph G, but with the 
#         resources on v distributed 
#         equally across neighbors N(v)
def distribute(G, v, node_type=None):
    if G.node[v]['resource'] == 0.0:
        return G
    N = [u for u in G.neighbors(v) if node_type==None or G.node[u]['node_type']==node_type]
    for n in N:
        G.node[n]['resource'] += G.node[v]['resource']/len(N)
    G.node[v]['resource'] = 0.0
    return G 

# given:  a graph G and a user node v,
# return: the graph G, but with the 
#         resources passed between users 
#         and docs so as to score docs
def diffusion_ud(G,v):
	H = G
	for u in H.nodes():
		H.node[u]['resource'] = 0.0
	H.node[v]['resource'] = 1.0
	H = distribute(H,v,node_type='doc')
	for u in G.neighbors(v):
		H = distribute(H,u,node_type='user')
	for u in G.neighbors(v):
		for w in G.neighbors(u):
			if H.node[w]['node_type'] == 'user':
				H = distribute(H,w,node_type='doc')
	return H

# given:  a graph G and a user node v,
# return: the graph G, but with the 
#         resources passed between tags 
#         and docs so as to score docs
def diffusion_dt(G,v):
	H = G
	for u in H.nodes():
		H.node[u]['resource'] = 0.0
	H.node[v]['resource'] = 1.0
	H = distribute(H,v,node_type='doc') 
	for u in G.neighbors(v):
		H = distribute(H,u,node_type='tag') 
	for u in G.neighbors(v):
		for w in G.neighbors(u):
			if H.node[w]['node_type'] == 'tag':
				H = distribute(H,w,node_type='doc')
	return H

# given:  a graph G and a user node v,
# return: topn recommended docs as 
#         ranked by diffusion
def get_recs(G,v,topn=5,eta=0.0):
	H_dt = diffusion_dt(G,v)
	H_ud = diffusion_ud(G,v)
	scores = {(u,eta*H_ud.node[u]['resource']+(1.0-eta)*H_dt.node[u]['resource']) for u in G.nodes() if G.node[u]['node_type']=='doc'}
	recs, _   = zip(*sorted(scores, reverse=True, key=itemgetter(1))) or ([],[])
	return list(filter(lambda s: s not in set(G.neighbors(v)), recs)[:topn])

def get_similar_users(G,v,topn=5):
	H = G
	for u in H.nodes():
		H.node[u]['resource'] = 0.0
	H.node[v]['resource'] = 1.0
	H = distribute(H,v,node_type='doc')
	for u in G.neighbors(v):
		H = distribute(H,u,node_type='user')
	scores = {(u,H.node[u]['resource']) for u in H.nodes() if H.node[u]['node_type']=='user'}
	recs, _   = zip(*sorted(scores, reverse=True, key=itemgetter(1)))
	return list(filter(lambda s: s != v, recs)[:topn])



# __ Create Big Graph from Memcache, 
# __ write small subgraph from regi to json 
G = nx.Graph()
tagger = papi.Tagger()

regi = '68039315' #'16177164' 
# JAKE SOLOFF : 72218121
# MUANIS      : 67618194
# MIKE DEWAR  : 67198392
G.add_node(regi,node_type='user',group='#000000')

import memcache, time
mc = memcache.Client(['127.0.0.1:11211'], debug=0)
counter = 8000
counter2= 0

while True:
    
    key = 'chunk' + str(counter)
    result = mc.get(key)
    print(key, result)
    if result:
    	nodes = map(list, zip(*result))
    	G.add_nodes_from(nodes[0],node_type='doc')
    	G.add_nodes_from(nodes[1],node_type='user')
    	G.add_edges_from(result)

    	for url in nodes[0]:
    		tags = tagger.get_tags(url)
    		if tags:
	    		G.add_nodes_from([t['content'] for t in tags],node_type='tag',group='#FF0000')
    			G.add_edges_from([(url,t['content']) for t in tags])
    	

        counter += 1
        #if counter%1000 == 0:
        #	tagger.write_cache()
    else:
    	recs = get_recs(G,regi,5)

    	N = G.neighbors(regi)
    	NN = get_similar_users(G,regi,20) 
    	tags = []
    	for url in N + recs:
    		tags += [w for w in G.neighbors(url) if G.node[w]['node_type']=='tag']


    	H = G.subgraph(tags+NN+N+recs+[regi])
    	for r in N:
    		H.node[r]['group'] = '#0000FF'
    	for r in recs:
    		H.node[r]['group'] = '#FFCC00'
    	for r in NN:
    		H.node[r]['group'] = '#00FF00'
    	H.node[regi]['group'] = '#000000'

    	for node in tags+NN+N+recs+[regi]:
    		H.node[node]['name'] = node

    	data = json_graph.node_link_data(H)
    	with open('data_test.json', 'w') as outfile:
    		ujson.dump(data, outfile)

    	counter2+=1
    	if counter2==3:
    		break

    	time.sleep(3)

tagger.write_cache()