from lxml import html
import requests
from py2neo import Graph, Node, Relationship

g = Graph(user="neo4j", password="admin")
tx = g.begin()
a = Node("Person", name="Alice")
tx.create(a)
tx.commit()

page = requests.get('http://moma.org/collection/works/2')
tree = html.fromstring(page.content)

print(len(tree.cssselect('div')))
