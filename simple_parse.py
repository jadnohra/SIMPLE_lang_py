from simple_lang import *

g_def_indent = ' '
def parse_line(mother, line, indent = g_def_indent):
  depth = 0; content = line;
  while content.startswith(indent):
    content = content[len(indent):]; depth = depth+1;
  depth = depth if depth <= mother['depth'] + 1 else mother['depth'] + 1
  while depth != mother['depth'] + 1:
    mother = mother['mother']
  node = { 'depth':depth, 'content':content, 'kids':[], 'mother':mother }
  mother['kids'].append(node)
  return node
def parse_lines(lines, indent = g_def_indent):
  root = { 'depth':-1, 'content':None, 'kids':[], 'mother':None }
  node = root
  for line in [x for x in lines if len(x.strip())]:
    node = parse_line(node, line, indent)
  return root
def preparse_lines_once(lines, indent = g_def_indent):
  def prepend(node, ncontent, line, nlines):
    nnode = { 'depth':node['depth'], 'content':ncontent, 'kids':[node], 'mother':node['mother'] }
    node['mother']['kids'][node['mother']['kids'].index(node)] = nnode
    node['mother'] = nnode
    nlines.append(indent*nnode['depth'] + nnode['content'])
    nlines.append(indent + line)
  def postpend(node, ncontent, line, nlines):
    nnode = { 'depth':node['depth']+1, 'content':ncontent, 'kids':[], 'mother':node }
    node['mother']['kids'].append(nnode)
    nlines.append(indent*nnode['depth'] + nnode['content'])
  nlines = []
  root = { 'depth':-1, 'content':None, 'kids':[], 'mother':None }
  node = root
  for line in [x for x in lines if len(x.strip())]:
    node = parse_line(node, line, indent)
    words = node['content'].split(' ')
    if len(words) > 1:
      if words[0] == 'while':
        nlines.append(indent*node['depth']+words[0])
        postpend(node, ' '.join(words[1:]), line, nlines)
      else:
        nlines.append(indent*node['depth']+words[0])
        node['contents'] = words[0]
        for nword in words[1:]:
          postpend(node, nword, line, nlines)
    elif node['content'].isdigit() and node['mother'] is not None and node['mother']['content'] != 'I':
      prepend(node, 'I', line, nlines)
    elif node['content'] not in g_SIMPLE and node['content'].lower()[0] in ['t','f'] and node['mother'] is not None and node['mother']['content'] != 'B':
      prepend(node, 'B', line, nlines)
    elif node['content'] not in g_SIMPLE and node['mother'] is not None and node['mother']['content'] not in ['B', 'I', 'var', 'set']:
      prepend(node, 'var', line, nlines)
    else:
      nlines.append(line)
  return nlines
def preparse_lines(lines, indent = g_def_indent):
  n = 0
  while True:
    nlines = preparse_lines_once(lines, indent)
    if nlines != lines:
      lines = nlines; n = n + 1;
    else:
      break
  return nlines
def parsed_tree_to_expr(root):
  def recurse(node):
    if node['content'] in g_SIMPLE:
      sub_strs = [recurse(child) for child in node['kids']]
      return "tbl['{}']({})".format(node['content'], ', '.join(sub_strs))
    else:
      if node['mother']['content'] in ['var', 'set']:
        return "'{}'".format(node['content'])
      else:
        return node['content']
  return recurse(root['kids'][0])
def parse_interactive():
  lines = []
  val_str = '\n'
  while len(val_str):
    if len(val_str.strip()):
      lines.append(val_str.replace(' ', '.'))
    depth = len(val_str)-len(val_str.strip())
    depth = 0
    val_str = raw_input(' > {}'.format('.'*depth))
  root = parse_lines(lines, '.')
  expr_str = parsed_tree_to_expr(root)
  print expr_str
  tbl, redu_expr = (ss_redu_tbl(), ss_redu_expr)
  built_expr = eval(expr_str)
  print redu_expr({}, built_expr)
