// Projected graph test
MATCH (from: Account)-[:sent]-(t:Transaction)-[:transfered]->(to: Account)
return from,to, apoc.create.vRelationship(from, 'transfered',{amount: t.value}, to) limit 100

// Projected graph transfer
MATCH (from: Account)-[:sent]-(t:Transaction)-[:transfered]->(to: Account)
with gds.graph.project('projected_transfer',from, to) as g
return  g.graphName AS graph, g.nodeCount AS nodes, g.relationshipCount AS rels

// Projected graph invocation
MATCH (from: Account)-[:sent]-(t:Transaction)-[:invoked]->(to: Account)
with gds.graph.project('invoked',from, to) as g
return  g.graphName AS graph, g.nodeCount AS nodes, g.relationshipCount AS rels

// Projected graph contract creation
MATCH (from: Account)-[:sent]-(t:Transaction)-[:created]->(to: Account)
with gds.graph.project('sc_creation',from, to) as g
return  g.graphName AS graph, g.nodeCount AS nodes, g.relationshipCount AS rels

// Projected graph for all account interaction
MATCH (from: Account)-[:sent]-(t:Transaction)-[]->(to: Account)
with gds.graph.project('all_interaction',from, to) as g
return  g.graphName AS graph, g.nodeCount AS nodes, g.relationshipCount AS rels


// Page rank
call gds.pageRank.stream('projected_transfer') yield nodeId, score
return gds.util.asNode(nodeId).address as address, score
order by score DESC

// Node centrality
call gds.degree.stream('projected_transfer') yield nodeId, score
return gds.util.asNode(nodeId).address as address, score
order by score DESC