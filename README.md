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

## Query Cypher


<table>
<tr> <th>#</th> <th>Descrizione</th> <th>Model A</th> <th>Model B</th> </tr>

<tr>
<td>1</td>
<td>
Conta le transazioni di qualsiasi tipo
</td>
<td> <pre>
MATCH 
    (n: Transaction) 
RETURN 
    COUNT(*)
</pre> </td>
<td> <pre>
MATCH
    (s:Account)-[r]->(d) 
RETURN 
    COUNT(*)
</pre> </td>
</tr>

<tr>
<td>2</td>
<td>
Conta tutte le transazioni che hanno trasferito 0 ether
</td>
<td> <pre>
MATCH 
    (n: Transaction)
WHERE 
    n.value = 0 
RETURN 
    COUNT(*)
</pre> </td>
<td> <pre>
MATCH
    (s:Account)-[r]->(d)
WHERE 
    r.value = 0 
RETURN 
    COUNT(*)
</pre> </td>
</tr>

<tr>
<td>3</td>
<td>
Selezionare tutte le transazioni dell'account con indirizzo 0x54daeb3e8a6bbc797e4ad2b0339f134b186e4637
</td>
<td> <pre>
MATCH
    (a:Account)-[:SENT]->(t:Transaction)
WHERE 
    a.address = "0x54daeb3e8a6bbc797e4ad2b0339f134b186e4637"
RETURN t
</pre> </td>
<td> <pre>
MATCH
    (a:Account {address: "0x54daeb3e8a6bbc797e4ad2b0339f134b186e4637"})-[r]->()
RETURN r
</pre> </td>
</tr>

<tr>
<td>4</td>
<td>
Conta gli account che hanno effettuato trasferimenti verso se stessi (loop nel grafo)
</td>
<td> <pre>
MATCH
    (a:Account)-[r:SENT]->(t: Transaction)-[r2]->(b: Account {address: a.address})
RETURN 
    COUNT(r)
</pre> </td>
<td> <pre>
MATCH
    (a:Account)-[r]->(b: Account {address: a.address})
RETURN
    COUNT(r)
</pre> </td>
</tr>

<tr>
<td>5</td>
<td>
Trova tutti gli account che non hanno fatto nessuna transazione, ma che sono solo destinatari di trasferimenti
</td>
<td> <pre>
MATCH 
    (account: Account)
WHERE 
    NOT (account)-[:SENT]-(:Transaction) 
RETURN 
    account
</pre> </td>
<td> <pre>
MATCH 
    (account:Account) 
WHERE NOT 
    (account)-[]->(:Account) 
RETURN
    account
</pre> </td>
</tr>

<tr>
<td>6</td>
<td>
Numero medio di transazioni effettuate da ogni account
</td>
<td> <pre>
MATCH 
    (account:Account)-[:SENT]->(t:Transaction)-[:TRANSFERRED]->()
WITH 
    account,
    COUNT(t) as numTransazioni
RETURN 
    AVG(numTransazioni) AS mediaTransazioni
</pre> </td>
<td> <pre>
MATCH
    (a:Account)-[:TRANSFERRED]->(:Account)
WITH 
    a,
    COUNT(*) as numTransazioni
RETURN 
    AVG(numTransazioni) AS mediaTransazioni;
</pre> </td>
</tr>

<tr>
<td>7</td>
<td>
Numero medio di transazioni effettuate da ogni account
</td>
<td> <pre>
MATCH 
    (account:Account)-[:SENT]->(t:Transaction)-[:TRANSFERRED]->()
WITH 
    account,
    COUNT(t) as numTransazioni
RETURN 
    AVG(numTransazioni) AS mediaTransazioni
</pre> </td>
<td> <pre>
MATCH
    (a:Account)-[:TRANSFERRED]->(:Account)
WITH 
    a,
    COUNT(*) as numTransazioni
RETURN 
    AVG(numTransazioni) AS mediaTransazioni;
</pre> </td>
</tr>

<tr>
<td>8</td>
<td>
Conta il numero di transazioni che hanno emesso l'evento con firma 0xf63780e752c6a54a94fc52715dbc5518a3b4c3c2833d301a204226548a2a8545
</td>
<td> <pre>
MATCH 
    (e:Event)
WHERE
    ANY(topic in e.topics where topic = '0xf63780e752c6a54a94fc52715dbc5518a3b4c3c2833d301a204226548a2a8545')
RETURN COUNT(*);
</pre> </td>
<td> <pre>
MATCH 
    (n)-[r]->(c)
WHERE 
    ANY(topic in r.logs_topic WHERE topic =~ '.*0xf63780e752c6a54a94fc52715dbc5518a3b4c3c2833d301a204226548a2a8545.*') 
RETURN 
    COUNT(*)
</pre> </td>
</tr>

<tr>
<td>9</td>
<td>
Ritorna tutte le transazioni del blocco con hash 0x890158751fc766ad90d9abebde93830f66e8d503a99f5d25c8dbf8bffeeba388
</td>
<td> <pre>
MATCH 
    (t:Transaction)-[:CONTAINED]->(b:Block {hash: '0x890158751fc766ad90d9abebde93830f66e8d503a99f5d25c8dbf8bffeeba388'})
RETURN 
    t;
</pre> </td>
<td> <pre>
MATCH 
    (a:Account)-[r]->(b) 
WHERE
    r.block_hash = '0x890158751fc766ad90d9abebde93830f66e8d503a99f5d25c8dbf8bffeeba388' 
RETURN 
    r;
</pre> </td>
</tr>

<tr>
<td>10</td>
<td>
Numero medio di transazioni per blocco
</td>
<td> <pre>
MATCH 
    (b:Block)<-[:CONTAINED]-(t:Transaction)
WITH 
    b,
    COUNT(t) AS numTransazioni
RETURN 
    AVG(numTransazioni)
</pre> </td>
<td> <pre>
MATCH 
    (a)-[t]->(b)
WITH 
    t.blockHash as block,
    COUNT(t) as numT
RETURN
    AVG(numT)
</pre> </td>
</tr>

<tr>
<td>11</td>
<td>
Trova le transazioni dirette vero l'indirizzo nullo
</td>
<td> <pre>
MATCH 
    (t:Transaction)-[r]->(n {address: '0x0000000000000000000000000000000000000000'})
RETURN 
    t;
</pre> </td>
<td> <pre>
MATCH 
    (a: Account)-[t]->(b: Account) 
WHERE 
    b.address = '0x0000000000000000000000000000000000000000'
RETURN 
    t;
</pre> </td>
</tr>

<tr>
<td>11</td>
<td>
Ritorna per ogni blocco, il numero di transazioni al suo interno
</td>
<td> <pre>
MATCH 
    (block:Block)<-[:CONTAINED]-(transaction:Transaction)
WITH 
    block,
    COUNT(transaction) AS numTransactions
ORDER BY numTransactions DESC
RETURN 
    block,
    numTransactions
</pre> </td>
<td> <pre>
MATCH 
    ()-[t]->()
WITH 
    t.block_hash AS blockHash,
    COUNT(t) AS numTransactions
RETURN 
    blockHash,
    numTransactions
ORDER by numTransactions DESC
</pre> </td>
</tr>

</table>


