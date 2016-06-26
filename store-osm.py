# OSM Points and Streets
# Build from nodes and ways

# For each node, add it to node-ids with lat and lng
# For each way, add them to Streets
## If Street has a node with a previous street, build a connectsto relation between the two

# 0) Opening the file
from py2neo import Graph, Node, Relationship
# from lxml import etree

g = Graph(user="neo4j", password="Swift")


osmfile = open('bangkok_thailand.osm', 'r')

inway = False
wayname = ""
waynodes = []
addedways = []
wayids = {}
knownnodes = {}
isHighway = False
osmwayid = ""

for line in osmfile:

  # 2) Add Streets
  if(line.find('<way') > -1):
    inway = True
    osmwayid = line[ line.find('id=') + 4 : len(line) ]
    osmwayid = osmwayid[ 0 : osmwayid.find('"') ]
    #print(osmwayid)

  elif(inway == True):
    if(line.find('<nd ref') > -1):
      # add this node id
      id = line[ line.find('ref="') + 5 : len(line) ]
      id = id[ 0 : id.find('"') ]
      waynodes.append( id )
    
    elif(line.find('k="highway"') > -1):
      isHighway = True
      
    elif(line.find('k="name"') > -1):
      # found the road name
      wayname = line[ line.find('v="') + 3 : len(line) ]
      wayname = wayname[ 0 : wayname.find('"') ]
      # use database's preferred parsing of street names
      wayname = wayname.lower().replace(' ','')

    elif(line.find('</way>') > -1):
      inway = False
      
      # only add a road (highway=*)
      if(wayname != "" and isHighway == True):
        # check if way needs to be added to the database
        street = g.find_one("Street", "nameslug", wayname)
        if(street == None):
          print('add ' + wayname)
          
          # create street in database
          street = Node("Street", nodeids=waynodes, nameslug=wayname)
          tx = g.begin()
          tx.create(street)
          tx.commit()
        
        else:
          # know this street, add the way id
          street['nodeids'] = street['nodeids'] + waynodes
          street.push()

        # now add relationships to nodes in the way
        for node in waynodes:
          if(node in knownnodes):
            streetnames = g.run("MATCH (n:Street) WHERE {nodeid} IN n.nodeids RETURN n.nameslug LIMIT 25", nodeid=node)
            for streetrecord in streetnames:
              streetname = streetrecord['n.nameslug']
              if streetname == wayname:
                continue
              print('matching ' + streetname + ' and ' + wayname)
              street2 = g.find_one("Street", "nameslug", streetname)
              if street2 is None:
                continue
              intersect = Relationship(street, "MEETS", street2)
              intersect2 = Relationship(street2, "MEETS", street)
              tx = g.begin()
              tx.create(intersect)
              tx.create(intersect2)
              tx.commit()
            
              print("connection made")
            
          knownnodes[node] = wayname

      # reset way defaults
      wayname = ""
      waynodes = []
      isHighway = False
