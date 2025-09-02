# Document Storage

___

## Problem

### You need to store schemaless or data with a varying schema

___


![](img/document_storage_salesman.png) <!-- .element: style="height: 600px;" -->

Note:
- but stop, you don't need to use the big tools directly

___

# STOP

You should consider

___

# Postgres

## JSONB

___

### How does it work?

`JSONB` columns allow storing objects with varying fields

`JSONB` columns' keys and values can be indexed and used for selection and projection

Note:
- selection: where-clause
- projection: select-clause

___

## JSONB Demo

___

- Postgres provides two types of columns for JSON
    - **`JSON`**: stored as raw text ➡️ Postgres validates it is valid JSON on insert but does not parse or index the structure
    - **`JSONB`**: stored in a binary, decomposed form ➡️ ignores key order and removes duplicate keys
    - ➡️ for most use-cases **you want `JSONB`**
- `JSONB` operators allow retrieval and checking of nested keys/values
- `JSONB` columns' keys/values can be indexed
    - GIN indices allow fast containment queries ➡️ does a rows' `JSONB` contain a specific key?
    - Btree indices allow fast value retrieval ➡️ does a rows' `JSONB` key contain a specific value?
    - Partial indices are also possible, if many documents don't have a key

___

- `CHECK` constraints can be defined on `JSONB` columns to enforce certain rules and/or format
- large `JSONB` values will be TOASTed and compressed, but max size for one field is 1GB
- any update creates a new row version ➡️ even changing one nested key rewrites the whole JSONB value and row ➡️ impact on bloat and VACUUM
- regular column values can be generated on insert from `JSONB` key/values

___

### You should use _JSONB_, if you

- want to combine the advantages of a relational database with document storage
    - use regular columns for always present data 
    - use `JSONB` columns for varying data
- have data with a lot of varying fields
- don't need to update the JSONB fields very frequently


Note:
- by default the maximum size of a postgres JSONB column is even bigger than the one of a MongoDB document
