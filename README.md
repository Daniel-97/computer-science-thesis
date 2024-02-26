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
--nodes=Block=import/output/model1-data/headers/block_node_headers.csv,import/output/model1-data/nodes/dump0-blocks0.csv \
--nodes=Account=import/output/model1-data/headers/account_node_headers.csv,import/output/model1-data/nodes/dump0-account0.csv \
--nodes=Transaction=import/output/model1-data/headers/txs_node_headers.csv,import/output/model1-data/nodes/dump0-txs0.csv \
--nodes=Log=import/output/model1-data/headers/log_node_headers.csv,import/output/model1-data/nodes/dump0-log0.csv \
--relationships=SENT=import/output/model1-data/headers/sent_rel_headers.csv,import/output/model1-data/rel/dump0-sent0.csv \
--relationships=CREATED=import/output/model1-data/headers/creation_rel_headers.csv,import/output/model1-data/rel/dump0-creation0.csv \
--relationships=EMITTED=import/output/model1-data/headers/log_rel_headers.csv,import/output/model1-data/rel/dump0-emitted0.csv \
--relationships=INVOKED=import/output/model1-data/headers/invocation_rel_headers.csv,import/output/model1-data/rel/dump0-invocation0.csv \
--relationships=TRANSFERRED=import/output/model1-data/headers/transfer_rel_headers.csv,import/output/model1-data/rel/dump0-transfer0.csv \
--relationships=TO=import/output/model1-data/headers/unk_rel_headers.csv,import/output/model1-data/rel/dump0-unk0.csv \
model1

### model2
bin/neo4j-admin database import full \
--verbose \
--delimiter="," \
--array-delimiter=";" \
--skip-duplicate-nodes \
--overwrite-destination=true \
--report-file=report-model2-import.txt \
--nodes=Account=import/output/model2-data/headers/account_node_headers.csv,import/output/model2-data/nodes/dump0-account0.csv \
--relationships=CREATED=import/output/model2-data/headers/creation_rel_headers.csv,import/output/model2-data/rel/dump0-creation0.csv \
--relationships=INVOKED=import/output/model2-data/headers/invocation_rel_headers.csv,import/output/model2-data/rel/dump0-invocation0.csv \
--relationships=TRANSFERRED=import/output/model2-data/headers/transfer_rel_headers.csv,import/output/model2-data/rel/dump0-transfer0.csv \
--relationships=TO=import/output/model2-data/headers/unk_rel_headers.csv,import/output/model2-data/rel/dump0-unk0.csv \
model2
