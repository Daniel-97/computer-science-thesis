// USE FOR DELETE
:auto match (n) call {with n detach delete n} in transactions of 10000 rows;

// CONSTRAINT
CREATE CONSTRAINT IF NOT EXISTS FOR (a: Account) REQUIRE a.address IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (contract: SmartContract) REQUIRE contract.address IS UNIQUE;

// QUERY 1, EOA TRANSACTIONS
:auto LOAD CSV WITH HEADERS FROM "file:///output/model2-data/eoa-transactions/eoa-transactions-1.csv" AS transaction
call {
    WITH transaction
    MERGE (fromNode: Account {address: transaction.fromAddress})
    MERGE (toNode: Account {address: transaction.toAddress})

    CREATE (fromNode)-[r:sent]->(toNode)
    SET r = properties(transaction)
} IN TRANSACTIONS OF 10000 ROWS;


// QUERY 2, CONTRACT INVOCATION TRANSACTIONS
:auto LOAD CSV WITH HEADERS FROM "file:///output/model2-data/contract-transactions/contract-transactions-1.csv" AS transaction
call {
    WITH transaction
    MERGE (fromNome: Account {address: transaction.fromAddress})
    MERGE (contract: SmartContract {address: transaction.toAddress})

    CREATE (fromNode)-[r:invoked]->(contract)
    SET r = properties(transaction)
} IN TRANSACTIONS OF 10000 ROWS;


// QUERY 3, CONTRACT CREATION TRANSACTIONS
:auto LOAD CSV WITH HEADERS FROM "file:///output/model2-data/contract-creation/contract-creation-1.csv" AS transaction
call {
    WITH transaction
    MERGE (fromNome: Account {address: transaction.fromAddress})
    MERGE (contract: SmartContract {address: transaction.contractAddress})

    CREATE (fromNode)-[r:created]->(contract)
    SET r = properties(transaction)
} IN TRANSACTIONS OF 10000 ROWS;




