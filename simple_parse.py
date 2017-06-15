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
  transl_tbl = {'<':'lt', '+':'add', '*':'mul', 'inc':'succ', '=':'set', '==':'eq'}
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
  def group_parens(words, sep = ' '):
    groups = []
    pdepth = 0
    for word in words:
      if pdepth > 0:
        groups[-1] = groups[-1] + sep + word
        if word == ')':
          pdepth = pdepth - 1
      else:
        groups.append(word)
        if word == '(':
          pdepth = 1
    return groups
  def clean_ws(word):
    return ' '.join([x for x in word.split() if len(x.strip())])
  def sep_parens(word):
    return clean_ws(' '.join(word.replace('(', ' ( ').replace(')', ' ) ').split()))
  def translate(word):
    return transl_tbl.get(word, word)
  nlines = []
  root = { 'depth':-1, 'content':None, 'kids':[], 'mother':None }
  node = root
  for line in [x for x in lines if len(x.strip())]:
    node = parse_line(node, line, indent)
    words = [translate(x) for x in sep_parens(clean_ws(node['content'])).split(' ')]
    node['content'] = ' '.join(words)
    if words[0] == '(':
      postpend(node['mother'], ' '.join(words[1:-1]), line, nlines)
    else:
      words = group_parens(words)
      if len(words) > 1:
        if words[0] == 'while':
          nlines.append(indent*node['depth']+words[0])
          postpend(node, ' '.join(words[1:]), line, nlines)
        else:
          if len(words) == 3 and words[1] in g_SIMPLE:
              words[0], words[1] = words[1], words[0]
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
#  auto_seq_tbl = {'while':(1,2)}
  def recurse(node):
    #if node['content'] in auto_seq_tbl and len(node['kids']) > auto_seq_tbl[node['contents']][1]:
    #  nnode = { 'content':'seq', 'kids':node['kids'][auto_seq_tbl[node['contents']][0]:] }
    #  node['kids'] = node['kids'][:auto_seq_tbl[node['contents']][0]] + [nnode]
    if node['content'] in g_SIMPLE:
      sub_strs = [recurse(child) for child in node['kids']]
      return "tbl['{}']({})".format(node['content'], ', '.join(sub_strs))
    else:
      if node['mother']['content'] in ['var', 'set']:
        return "'{}'".format(node['content'])
      else:
        return node['content']
  return [recurse(program) for program in root['kids']]
def run_program(program, indent):
  tbl, redu_expr = (ss_redu_tbl(), ss_redu_expr)
  preparse = preparse_lines(program.split('\n'), indent)
  #print '\n'.join(preparse).replace(' ', '.')
  root = parse_lines(preparse, indent)
  for expr_str in parsed_tree_to_expr(root):
    built_expr = eval(expr_str)
    e,env = redu_expr({}, built_expr)
    if '(' not in str(e):
      print 'result: {}'.format(e)
    if 'ret' in env:
      print 'returned: {}'.format(env['ret'])
    else:
      if len(env):
        print 'env: {}'.format(' '.join(['{}:{}'.format(x, env[x]) for x in sorted(env.keys())]))
def parse_interactive():
  lines = []
  val_str = '\n'
  while len(val_str):
    if len(val_str.strip()):
      lines.append(val_str)
    depth = len(val_str)-len(val_str.strip())
    depth = 0
    val_str = raw_input(' > {}'.format('.'*depth))
  root = parse_lines(preparse_lines(lines))
  tbl, redu_expr = (ss_redu_tbl(), ss_redu_expr)
  for expr_str in parsed_tree_to_expr(root):
    print expr_str
    built_expr = eval(expr_str)
    print redu_expr({}, built_expr)
