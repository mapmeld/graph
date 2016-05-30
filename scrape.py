from lxml import html
import requests
from py2neo import Graph, Node, Relationship

g = Graph(user="neo4j", password="Swift")

tx = g.begin()

page = requests.get('http://moma.org/collection/works/2')
tree = html.fromstring(page.content)

tree.cssselect('div')


tx.commit()
