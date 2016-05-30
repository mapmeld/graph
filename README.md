# Graph Databases tutorial

Organize a Neo4j graph database for the Museum of Modern Art collection

Scrape web pages into graph data

Make cool queries of graph data

# Prerequisites

You need Java, Neo4j Community Edition 3.x, Python, and the pip installer for Python modules.

Start the Neo4j database:

```bash
neo4j start
```

After a minute, open the browser view at ```http://localhost:7474``` and log in with the default
login (neo4j / neo4j).  Set a new password (in the source code, it's Swift).

## Install dependencies

Install the latest py2neo and other modules:

```bash
pip install -r requirements.txt
```

## Run the sample graph

```bash
python sample-graph.py
```

When you update the browser view, click the top-left icon (with the database can icon).

Select "Person" to see a visualization of all people-nodes. You should see circles for Alice and Bob, and a KNOWS relationship between them.

# Create the dataset

## Build up a model

- Artworks (unique id: MoMA collection page)
- People (including Artists) (unique id: MoMA bio page)
- Link people to artworks (with order intact)

You can either plan around scraping people or scraping artworks. Not all people in the database
are artists (as it includes publishers and other roles) so we'll start with the artworks.

## Scrape data from a collection item

The first item in the MoMA collection is an architectural drawing of a bridge at http://moma.org/collection/works/2

By changing the number at the end of the URL, we can view thousands more works. Not every number
has a work - it may be a 404 page.

Using the ```requests``` module which you've installed, it's simple to scrape the source of a webpage:

```python
import requests
...
page = requests.get('http://moma.org/collection/works/' + str(id))
print(page.content)
```

We don't just want the text, though - we want to be able to pick out a particular link, read the artist name, and read their bio page's ID from the link. Using the ```lxml``` module:

```python
from lxml import html
...
tree = html.fromstring(page.content)
artists = tree.cssselect('.short-caption h2 a')
```

Artists returns an array, because there could be multiple artists. Let's extract text from each lxml Element object and print it, to make sure we got the artists' names:

```python
for artist in artists:
  print(artist.text)

> Otto Wagner
```

Include the link, the 'href' attribute, as well:

```python
for artist in artists:
  print(artist.get('href'))

> /collection/artists/6210?locale=en
```

Note two things: that the URL is a relative URL and does not contain moma.org, and that the artist ID is the only number in the link.

We can extract the ID using Python's built-in regex library, ```re```. Search for multiple digits using the ```\d+``` operator.

```python
import re
matchID = re.compile(r"\d+")
...
for artist in artists:
  artistLink = artist.get('href')
  print(matchID.search(artistLink).group(0))
```

## Store the scraped data in the database

```python
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
```

### Browsing and querying the database

You can view the data after running this script at http://localhost:7474

Click on 'Artist' and then click on the circle to see the attributes and relationship.

This is a good time to introduce Cypher, Neo4j's preferred query language. When you work with
graphs, you can't use SQL. There isn't one standard comparable to SQL in the graph world. The Neo4j team has been working to make Cypher an open language. Neo4j also supports Gremlin, a more common but perhaps more difficult query language. Other databases support SPARQL.

When you clicked 'Artist' in the admin panel, you were initiating your first Cypher query:

```bash
MATCH (n:Artist) RETURN n LIMIT 25
```

Here we establish a query for a list of all Artist nodes, stored as n, return it, and use the SQL-like
LIMIT to keep us from returning too many nodes.

You can return Artworks in a similar syntax, but you could also make a more graph-like query using an ASCII-art arrow:

```bash
MATCH () -[`ARTIST OF`] -> (m:Artwork) RETURN m LIMIT 25
```

Here the empty parentheses represent 'any node', inside the arrow we specify the relationship name (which only needs these quotes if it includes a space) and the arrow points to the artwork which
we like to return.


## Remove old data when re-running the script

As we develop the script, we risk storing multiple copies of artworks and artists each time we rewrite and re-run our script.

Neo4j requires you to delete relationships before deleting individual nodes. Delete these connections first, making sure not to use the LIMIT clause and partially-deleting things:

```bash
MATCH () -[r:`ARTIST OF`] -> () DELETE r;
```

Then the artists and artworks:

```bash
MATCH (n:Artist) DELETE n;
MATCH (m:Artwork) DELETE m;
```

Here's how we can run the deletion at the beginning of our Python script (no transaction needed)

```python
g.run('MATCH () -[r:`ARTIST OF`] -> () DELETE r;')
g.run('MATCH (n:Artist) DELETE n;')
g.run('MATCH (m:Artwork) DELETE m;')
```

## Storing ten artworks

- loop
- make sure artist -ID- is looked up before creating a new artist

# License

MIT license for code, Creative Commons Zero license for educational content
