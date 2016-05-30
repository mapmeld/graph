import requests, re
from lxml import html
from py2neo import Graph, Node, Relationship

# find a numeric ID in a URL (without any other digits)
findid = re.compile(r"\d+")

# change the Neo4j password to yours
g = Graph(user="neo4j", password="Swift")

# reset the graph
g.run('MATCH () -[r:`ARTIST OF`] -> () DELETE r;')
g.run('MATCH (n:Artist) DELETE n;')
g.run('MATCH (m:Artwork) DELETE m;')

tx = g.begin()

def ScrapeCollection(workID):
    page = requests.get('http://moma.org/collection/works/' + str(workID))
    tree = html.fromstring(page.content)

    # the title is a complex, potentially italicized field
    titles = tree.cssselect('.short-caption h1.object-tile--gothic')
    for title in titles:
        full_title = title.text.strip()
        break

    # the date is a string field which can be a year, range of years, or approximation
    dates = tree.cssselect('.short-caption h3')
    for date in dates:
        first_date = date.text.strip()
        break

    # store relevant data about this artwork
    artwork = Node("Artwork", title=full_title, date=first_date, moma_id=workID)
    tx.create(artwork)

    # link artists to the artwork
    artists = tree.cssselect('.short-caption h2 a')
    index = 0
    for artist in artists:
        name = artist.text.strip()
        artist_link = artist.get('href')
        artistID = findid.search(artist_link).group(0)

        bio = Node("Artist", name=name, moma_id=artistID)
        tx.create(bio)

        c = Relationship(bio, "ARTIST OF", artwork, order=index)
        index = index + 1
        tx.create(c)

ScrapeCollection(2)
tx.commit()
