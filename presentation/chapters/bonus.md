# Bonus

___

# Vector Storage

___

## Problem

### You need to store vectors and execute operations on them, e.g. nearest search and calculations

Note:
- for example for AI

___

![](img/weaviate_salesman.png) <!-- .element: style="height: 600px;" -->

Note:
- but stop, you don't need to use the big tools directly

___

# STOP

You should consider

___

# Postgres

## With a Vector extension

___

### How does it work?

install a postgres vector extension, e.g. vectorchord

create and query tables with vectors stored in columns

Note:
- I have no affiliation with vectorchord, there are also other vector extensions

___

## Vector data demo with vectorchord

___

- vectorchord introduces vector column types, indexes and operators
    - column types `vector`, `halfvec`, `sparsevec`, `bit`
    - operators for ordering
        - `<->`: squared Euclidean distance
        - `<#>`: negative dot product
        - `<=>`: cosine distance
    - operators for selection are different to push the filter down to the vector index
    - index `vchordrq` divides vectors into lists and searches only a subset of lists closest to the query vecto
- indexes configurable depending on vector size and used operators
- usually vector search is done with `ORDER BY` and `LIMIT`, for `WHERE` different operators must be used

___

### You should use _Postgres with a vector extension_, if you

- are just starting out with vectors
- need to keep vectors beside your relational data
- don't need extensive vector functionality 
- have vectors in the millions rather than in the billions

Note:
- there are benchmarks on the vectorchord website

___

# Hidden Bonus

- Postgres full-text search
- PostGIS extension for geospatial data
- Citus extension for distributed Postgres sharding and replication

and many more...
