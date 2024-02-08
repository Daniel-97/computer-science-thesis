// Conta il numero di nodi senza relazioni
MATCH (n) WHERE size(labels(n)) = 0 RETURN count(n)

// Ritrorna la lista di account che ha effettuato piu transazioni (ordine decrescente)
MATCH (n: Account)-[r]->(b) 
WITH n, count(r) AS numTransactions 
ORDER BY numTransactions DESC
return n, numTransactions

// Ritorna i vicini dei nodi verso i quali i primi 1000 nodi hanno fatto transazioni
// Trova i nodi account che hanno eseguito il maggior numero di transazioni
PROFILE MATCH (n:Account)-[r:transfered]->(b:Account)
where n <> b
WITH n, COUNT(r) AS numTransactions
ORDER BY numTransactions DESC
LIMIT 100 // Limita ai nodi account con il maggior numero di transazioni
MATCH (n)-[*3]->(neighbor) // Espandi fino ai vicini dei vicini
WHERE neighbor <> n AND (neighbor:Account) // Assicurati che i vicini non siano i nodi stessi e siano nodi account
RETURN count(distinct neighbor);