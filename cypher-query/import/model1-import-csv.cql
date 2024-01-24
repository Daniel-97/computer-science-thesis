// CONSTRAINT
CREATE CONSTRAINT IF NOT EXISTS FOR (t:Transaction) REQUIRE t.hash IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (block: Block) REQUIRE block.hash IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (contract: SmartContract) REQUIRE contract.address IS UNIQUE;


// QUERY 1, EOA TRANSACTIONS
LOAD CSV WITH HEADERS FROM "file:///output/model1-data/eoa-transactions/eoa-transactions-1.csv" AS row
WITH row as transaction
// Create the transaction
CREATE (t:Transaction {hash: transaction.hash})
SET t = properties(transaction)

// Create the node
MERGE (fromNode: Account {address: transaction.fromAddress})
MERGE (toNode: Account {address: transaction.toAddress})
MERGE (block: Block {hash: transaction.blockHash})

// Create the relation
CREATE (t)-[:contained_in]->(block)
CREATE (t)<-[:sent]-(fromNode)
CREATE (t)-[:transfered]->(toNode)


// QUERY 2, SMART CONTRACT CREATION TRANSACTIONS
LOAD CSV WITH HEADERS FROM "file:///output/model1-data/contract-creation/contract-creation-1.csv" AS row
WITH row AS transaction WHERE NOT transaction.contractAddress IS NULL AND NOT transaction.fromAddress IS NULL
MERGE (t: Transaction {hash: transaction.hash})
SET t = properties(transaction)

MERGE (fromNode: Account {address: transaction.fromAddress})
MERGE (toContract: SmartContract {address: transaction.contractAddress})
MERGE (block: Block {hash: transaction.blockHash})

MERGE (fromNode)-[:sent]->(t)
MERGE (toContract)<-[:created]-(t)
MERGE (t)-[:contained_in]->(block)


// QUERY 3, CONTRACT INVOCATION TRANSACTIONS
LOAD CSV WITH HEADERS FROM "file:///output/model1-data/contract-transactions/contract-transactions-1.csv" AS row
WITH row AS transaction
MERGE (t: Transaction {hash: transaction.hash})
SET t = properties(transaction)

MERGE (fromNode: Account {address: transaction.fromAddress})
MERGE (toContract: SmartContract {address: transaction.toAddress})
MERGE (block: Block {hash: transaction.blockHash})

MERGE (fromNode)-[:sent]->(t)
MERGE (toContract)<-[:invoked]-(t)
MERGE (t)-[:contained_in]->(block)

//QUERY 4, CONTRACT LOGS
LOAD CSV WITH HEADERS FROM "file:///output/model1-data/contract-logs/contract-logs-1.csv" AS row
WITH row AS log
CREATE (event: Event)
SET event = properties(log)

WITH event, log.transactionHash as transactionHash
MATCH (transaction: Transaction {hash: transactionHash})
CREATE (transaction)-[:emitted]->(event)

// QUERY 5, BLOCKS
LOAD CSV WITH HEADERS FROM "file:///output/model1-data/blocks/blocks-1.csv" AS row
WITH row AS block
MERGE (b: Block {hash: block.hash})
set b = properties(block)
