// CONSTRAINT
CREATE CONSTRAINT IF NOT EXISTS FOR (a: Account) REQUIRE a.address IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (contract: SmartContract) REQUIRE contract.address IS UNIQUE;

// QUERY 1, EOA TRANSACTIONS
LOAD CSV WITH HEADERS FROM "file:///output/model2-data/eoa-transactions/eoa-transactions-1.csv" AS row
WITH row AS transaction
MERGE (fromNode: Account {address: transaction.fromAddress})
MERGE (toNode: Account {address: transaction.toAddress})

CREATE (fromNode)-[r:sent]->(toNode)
ON CREATE SET r = properties(transaction)


// QUERY 2, CONTRACT INVOCATION TRANSACTIONS
LOAD CSV WITH HEADERS FROM "file:///output/model2-data/contract-transactions/contract-transactions-1.csv" AS row
WITH row AS transaction
MERGE (fromNome: Account {address: transaction.fromAddress})
MERGE (contract: SmartContract {address: transaction.toAddress})

CREATE (fromNode)-[r:invoked]->(contract)
SET r = properties(transaction)


// QUERY 3, CONTRACT CREATION TRANSACTIONS
LOAD CSV WITH HEADERS FROM "file:///output/model2-data/contract-creation/contract-creation-1.csv" AS row
WITH row AS transaction
MERGE (fromNome: Account {address: transaction.fromAddress})
MERGE (contract: SmartContract {address: transaction.contractAddress})

CREATE (fromNode)-[r:created]->(contract)
SET r = properties(transaction)




