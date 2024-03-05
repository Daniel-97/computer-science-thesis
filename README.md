# computer-science-thesis
This tool parse json file full of ethereum transaction and split them in different file based on
the destination address of the transaction.

## Build and run

### Environment
Create a `.env` file in the `src` directory, using `.env.example` as a template or manually pass the env variable to the script.

### Run trie builder
Build the trie used by the parser for address classification

```bash
python trie_builder.py \
--input /data/backup/eth/blocks/output_0-999999.json.gz \
--output trie_dump/trie.trie \
--print-stat
```

### Run parser
Generate the csv for both model A and model B for neo4j import

```bash
python json_splitter.py \
-i /run/media/daniele/Dati/Università/Informatica/Tesi/eth_dumps/dump0_0-999999.json.gz \
-o ./output \
-s -1 \
--format csv \
--start-block 0 \
--end-block 2000000 \
--trie-path trie_dump/trie.trie
```

## neo4j-admin import
For full import change incremental argument 'incremental' with 'full' and remove --force --stage

### model1 import example
```bash
bin/neo4j-admin database import full \
--verbose \
--delimiter="," \
--array-delimiter=";" \
--skip-duplicate-nodes \
--skip-bad-relationships \
--report-file=report-model1.txt \
--nodes=Block=import/output/model1-data/headers/block_node_headers.csv,import/output/model1-data/nodes/blocks.\* \
--nodes=Account=import/output/model1-data/headers/account_node_headers.csv,import/output/model1-data/nodes/account.\* \
--nodes=Transaction=import/output/model1-data/headers/txs_node_headers.csv,import/output/model1-data/nodes/txs.\* \
--nodes=Log=import/output/model1-data/headers/log_node_headers.csv,import/output/model1-data/nodes/log.\* \
--relationships=SENT=import/output/model1-data/headers/sent_rel_headers.csv,import/output/model1-data/rel/sent.\* \
--relationships=CREATED=import/output/model1-data/headers/creation_rel_headers.csv,import/output/model1-data/rel/creation.\* \
--relationships=EMITTED=import/output/model1-data/headers/log_rel_headers.csv,import/output/model1-data/rel/emitted.\* \
--relationships=INVOKED=import/output/model1-data/headers/invocation_rel_headers.csv,import/output/model1-data/rel/invocation.\* \
--relationships=TRANSFERRED=import/output/model1-data/headers/transfer_rel_headers.csv,import/output/model1-data/rel/transfer.\* \
--relationships=TO=import/output/model1-data/headers/unk_rel_headers.csv,import/output/model1-data/rel/unk.\* \
--relationships=CONTAINED=import/output/model1-data/headers/contain_rel_headers.csv,import/output/model1-data/rel/contained.\* \
--relationships=CHILD_OF=import/output/model1-data/headers/block_child_rel_headers.csv,import/output/model1-data/rel/child-of.\* \
model1
```

### model2 import example
```bash
bin/neo4j-admin database import full \
--verbose \
--delimiter="," \
--array-delimiter=";" \
--skip-duplicate-nodes \
--overwrite-destination=true \
--report-file=report-model2.txt \
--nodes=Account=import/output/model2-data/headers/account_node_headers.csv,import/output/model2-data/nodes/account.\* \
--relationships=CREATED=import/output/model2-data/headers/creation_rel_headers.csv,import/output/model2-data/rel/creation.\* \
--relationships=INVOKED=import/output/model2-data/headers/invocation_rel_headers.csv,import/output/model2-data/rel/invocation.\* \
--relationships=TRANSFERRED=import/output/model2-data/headers/transfer_rel_headers.csv,import/output/model2-data/rel/transfer.\* \
--relationships=TO=import/output/model2-data/headers/unk_rel_headers.csv,import/output/model2-data/rel/unk.\* \
model2
```
