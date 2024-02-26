# computer-science-thesis
This tool parse json file full of ethereum transaction and split them in different file based on
the destination address of the transaction.

## neo4j-admin import

### model1 
bin/neo4j-admin database import full \
--verbose \
--delimiter="," \
--array-delimiter=";" \
--skip-duplicate-nodes \
--overwrite-destination=true \
--report-file=report.txt \
--nodes=Block=import/output/model1-data/nodes/dump0-blocks0.csv \
--nodes=Account=import/output/model1-data/nodes/dump0-account0.csv \
--nodes=Transaction=import/output/model1-data/nodes/dump0-txs0.csv \
--nodes=Log=import/output/model1-data/nodes/dump0-log0.csv \
--relationships=SENT=import/output/model1-data/rel/dump0-sent0.csv \
--relationships=CREATED=import/output/model1-data/rel/dump0-creation0.csv \
--relationships=EMITTED=import/output/model1-data/rel/dump0-emitted0.csv \
--relationships=INVOKED=import/output/model1-data/rel/dump0-invocation0.csv \
--relationships=TRANSFERRED=import/output/model1-data/rel/dump0-transfer0.csv \
--relationships=TO=import/output/model1-data/rel/dump0-unk0.csv \
model1

### model2

