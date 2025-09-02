# Agenda

- **Why Postgres?**
- **Publish/Subscribe**
- **Distributed Queues**
- **Document Storage**
- **Bonus: Vectors**

___

## About me

![](img/me.jpg) <!-- .element: style="height: 230px;" -->

- Software und Data Engineering Freelancer
- Contact
  - [eugengeist.com](https://eugengeist.com)
  - [mail@eugengeist.com](mailto:mail@eugengeist.com)
  - [https://linkedin.com/in/eugen-geist/](https://linkedin.com/in/eugen-geist/)

---

# Why this talk?

___

# We love new shiny things

As soon as a new problem occurs, we tend to search the perfect solution for it

___

# We love complexity

Complexity is interesting, you can lose yourself in it

Note:
- we need queuing ➡️ Redis
- we need pub/sub or events ➡️ Kafka
- we need vectors ➡️ graph database

___

![](img/installing.png) <!-- .element: style="height: 600px;" -->

Note:
- at the beginning we introduce the technologies and configure them

___

![](img/maintaining.png) <!-- .element: style="height: 600px;" -->

Note:
- in the end it sometimes feels as if we are trapped in them

___

![](img/enslaved.png) <!-- .element: style="height: 600px;" -->

___

# Instead of solving real problems, we get lost in technology

___

Instead of introducing the _right tool_ for the new job, we can get pretty far with the _existing tool_

___

Every tool has it's purpose, but it also has to be introduced and maintained ➡️ costs money and manpower

___

Most teams don't need the featureset of Kafka or MongoDB.

Especially not small teams.

___

Keep it simple and make pragmatic choices, instead of interesting ones.

___

[Boring Technology Club](https://boringtechnology.club/)

[You are not Google](https://blog.bradfieldcs.com/you-are-not-google-84912cf44afb)

Note:
- Two of my favorite talks about pragmatism
- Kafka was built by LinkedIn for their data volume
- Service-Oriented-Architecture was introduced by Amazon when they had 7800 employees
- Hadoop was built by Google for their data volume and size

___

... and if it turns out, that you need the _right tool_ you can still introduce it, as soon as needed!
