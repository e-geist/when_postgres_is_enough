# Publish/Subscribe

___

## Problem

### You need to notify one application from another

e.g. about added/changed database rows

___


![](img/kafka_salesman.png) <!-- .element: style="height: 600px;" -->

Note:
- but stop, you don't need to use the big tools directly

___

# STOP

You should consider

___

# Postgres 

# NOTIFY/LISTEN

___

### How does it work?

database session _1_ runs `LISTEN channel`

database session _2_ executes `NOTIFY channel, id123`

➡️ session _1_ receives the payload _id123_ from session _2_

___

# Listen/Notify Demo

___

- **every currently-listening session** is informed on **every `NOTIFY`**
- notifications cannot be re-read or re-delivered, they are **ephemeral**
- notifications are sent when the notifier commits
- listeners only receive notifications between transactions
- instead of `NOTIFY ...`, `pg_notify(channel, payload)` can also be used
- payload must be string
- payload in default configuration must be shorter than 8000 bytes
- notifications with same payload to one channel in one transaction are only delivered **once**
- sessions can unsubscribe from a channel by
    - running `UNLISTEN`
    - ending the session
- internal queue holds all notifications that were not processed by listeners yet
    - default-size: 8GB
    - if queue becomes full, transactions calling `NOTIFY` will **fail at commit**

___

### You should use _LISTEN/NOTIFY_, if you

- have events with _small_ payload e.g. IDs
- have small to mid data volume
- don't need to re-process missed events
- don't need redundancy ➡️ LISTEN/NOTIFY only possible on primary postgres servers
- don't need control over who is allowed to LISTEN and NOTIFY ➡️ no access rights available

Note:
- if you have any of the listed requirements, maybe a proper message queue / event streaming platform is the right case for you

