from py2neo import Graph, Node, Relationship

# Run: neo4j start
# go to http://localhost:7474 to change the default password from neo4j / neo4j
# change the password in this code:
g = Graph(user="neo4j", password="Swift")
tx = g.begin()

a = Node("Person", name="Alice")
tx.create(a)

b = Node("Person", name="Bob")
tx.create(b)

c = Relationship(a, "KNOWS", b, order=1)
tx.create(c)

tx.commit()

print('Sample graph successfully created! Check out http://localhost:7474')
