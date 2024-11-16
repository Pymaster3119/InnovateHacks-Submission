import requests
from bs4 import BeautifulSoup
import lxml.html
import lxml.etree
from collections import defaultdict


def drop_extra(el):
  if el is None:
    return
  print(el.tag, type(el))
  if isinstance(el, lxml.html.HtmlElement):
    if el.tag not in ['html', 'body', 'section', 'article', 'div', 'a', 'form', 'input', 'submit', 'p', 'li', 'ul', 'h1', 'h2', 'h3', 'h4', 'b']:
      el.getparent().remove(el)
  elif isinstance(el, lxml.html.HtmlComment):
    el.getparent().remove(el)

    return
  for c in el.getchildren():
    drop_extra(c)



with open('page.html', 'rt') as inpf:
  content = inpf.read()
  tree = lxml.html.fromstring(content)

drop_extra(tree)
content = lxml.html.tostring(tree, encoding='unicode', pretty_print=False, include_meta_content_type=False, method='xml')

with open('form.html', 'wt') as outf:
  tree = lxml.etree.fromstring(content)
  content = lxml.etree.tostring(tree, pretty_print=True, method='c14n2',with_comments=False,strip_text=True)
  outf.write(content.decode())
