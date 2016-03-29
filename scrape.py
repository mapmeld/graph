from lxml import html
import requests

page = requests.get('http://moma.org/collection/works/2')
tree = html.fromstring(page.content)

print(len(tree.cssselect('div')))
