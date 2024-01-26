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
    SET r.logs_index = SPLIT(transaction.logs_index,',')
    SET r.logs_data = SPLIT(transaction.logs_data,',')
    SET r.logs_block_number = SPLIT(transaction.logs_block_number,',')
    SET r.logs_transaction_index = SPLIT(transaction.logs_transaction_index,',')
    SET r.logs_index = SPLIT(transaction.logs_index,',')
    SET r.logs_type = SPLIT(transaction.logs_type,',')
    SET r.logs_type = SPLIT(transaction.logs_index,',')
    SET r.logs_transaction_hash = SPLIT(transaction.logs_transaction_hash,',')

    // split by , resplit by ; and save the result as collection of collections. Not supported by neo4j
    // WITH transaction, SPLIT(transaction.logs_topic,',') AS topics
    //     UNWIND topics as topic
    //     WITH transaction, SPLIT(topic, ';') as subtopics
    //         WITH transaction, COLLECT(subtopics) as subtopic
    //             MERGE (fromNode)-[r:invoked]->(contract)
    //             SET r.logs_topic = COALESCE(r.logs_topic, []) + subtopic
    SET r.logs_topic = SPLIT(transaction.logs_topic,',')

} IN TRANSACTIONS OF 10000 ROWS;


// QUERY 3, CONTRACT CREATION TRANSACTIONS
:auto LOAD CSV WITH HEADERS FROM "file:///output/model2-data/contract-creation/contract-creation-1.csv" AS transaction
call {
    WITH transaction
    MERGE (fromNome: Account {address: transaction.fromAddress})
    MERGE (contract: SmartContract {address: transaction.contractAddress})

    CREATE (fromNode)-[r:created]->(contract)
    SET r = properties(transaction)
    SET r.logs_topic = SPLIT(transaction.logs_topic,',')
    SET r.logs_index = SPLIT(transaction.logs_index,',')
    SET r.logs_data = SPLIT(transaction.logs_data,',')
    SET r.logs_block_number = SPLIT(transaction.logs_block_number,',')
    SET r.logs_transaction_index = SPLIT(transaction.logs_transaction_index,',')
    SET r.logs_index = SPLIT(transaction.logs_index,',')
    SET r.logs_type = SPLIT(transaction.logs_type,',')
    SET r.logs_type = SPLIT(transaction.logs_index,',')
    SET r.logs_transaction_hash = SPLIT(transaction.logs_transaction_hash,',')
} IN TRANSACTIONS OF 10000 ROWS;




