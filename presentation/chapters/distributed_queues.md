# Distributed Queues

___

## Problem

### You need to decouple workflows with a distributed queue

___


![](img/distributed_queues_salesman.png) <!-- .element: style="height: 600px;" -->

Note:
- but stop, you don't need to use the big tools directly

___

# STOP

You should consider

___

# Postgres

## SELECT ... FOR UPDATE SKIP LOCKED

___

### How does it work?

`SELECT … FOR UPDATE SKIP LOCKED` grabs row-level locks on the rows your query returns

but silently skips any rows that are already locked by another transaction

___

## SELECT ... FOR UPDATE SKIP LOCKED Demo

___

Different waiting mechanisms in Postgres when selecting with lock
- `SELECT FOR UPDATE` ➡️ waits for locked rows
- `SELECT FOR UPDATE ... NOWAIT` ➡️ errors if it hits a locked row
- `SELECT FOR UPDATE ... SKIP LOCKED` ➡️ ignores locked rows and keeps going

➡️ 

`SELECT FOR UPDATE ... SKIP LOCKED`  is perfect for _concurrent job pickers_ where many workers select the next row without stepping on each other

___

- use SKIP LOCKED when multiple workers are contending for the same _next items_
- always ORDER BY something deterministic, e.g. priority, then run_at, then id
- always `LIMIT` to avoid scanning huge sets
- don’t do long work while holding the row lock 
    - long transactions bloat and block vacuum
    - use a lease column
- idempotency matters ➡️ crashes can cause reprocessing
- make sure queries on queue tables are fast
    - use (partial) indices for queries
    - archive old entries, that are finished
- batching can reduce database round trips, but also lowers parallelism as one worker holds many rows
- reduce polling of table by using NOTIFY/LISTEN to be notified about new entries

Note:
- reprocessing happens e.g. if work is done, but application crashes before updating state in job table to done
- batching means grabbing muliple rows at once: LIMIT higher than 1

___

### You should use _FOR UPDATE SKIP LOCKED_, if you

- want to concurrently process entries from a table/queue without taking care of locking yourself
- need persistency of items to process
- don't need 
    - FIFO 
    - per-key fairness
    - sophisticated queue patterns
- run at moderate scale ➡️ thousands to tens of thousands jobs per minute

Note:
- if you don't need persistence, use redis or in-memory
- otherwise a proper message queue of course might make sense