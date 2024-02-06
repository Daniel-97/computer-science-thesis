// Projeted graph
match (from: Account)-[:sent]->(to: Account)
with gds.graph.project('projected_transfer', from, to) as g
return g.graphName as graph, g.nodeCount as nodes, g.relationshipCount as rels