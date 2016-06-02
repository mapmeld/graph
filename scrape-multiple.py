import requests, re
from lxml import html
from py2neo import Graph, Node, Relationship

# find a numeric ID in a URL (without any other digits)
findid = re.compile(r"\d+")

# change the Neo4j password to yours
g = Graph(user="neo4j", password="Swift")

# reset the graph
# take care to use an underscore in ARTIST_OF
# or in queries you will need to use tic quotes ``
g.run('MATCH () -[r:ARTIST_OF] -> () DELETE r;')
g.run('MATCH (n:Artist) DELETE n;')
g.run('MATCH (m:Artwork) DELETE m;')

def ScrapeCollection(workID):
    page = requests.get('http://moma.org/collection/works/' + str(workID))
    if (str(page.content).find('moma.org/404.html') > -1):
        print('404')
        return
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

        # see if artist exists yet
        bio = g.find_one("Artist", "moma_id", artistID)

        if bio is None:
            bio = Node("Artist", name=name, moma_id=artistID)
            tx.create(bio)

        c = Relationship(bio, "ARTIST_OF", artwork, order=index)
        index = index + 1
        tx.create(c)

id = 1
while id < 100:
    print('Scanning ' + str(id))
    tx = g.begin()
    ScrapeCollection(id)
    tx.commit()
    id = id + 1
