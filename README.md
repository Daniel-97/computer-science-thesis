# computer-science-thesis
This tool parse json file full of ethereum transaction and split them in different file based on
the destination address of the transaction.

## neo4j-admin import

### model1 
bin/neo4j-admin database import full
--delimiter=","
--array-delimiter=";"
--skip-duplicate-nodes
--nodes=Block=nodes/dump0-blocks-0.csv
--nodes=Transaction=nodes/dump0-txs-0.csv
--nodes=
--relationships=import/roles.csv 
neo4j

### model2

