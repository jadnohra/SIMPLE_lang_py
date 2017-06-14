import sys, random, copy

'''
Small-Step, big-step, and denotational semantics of the 'SIMPLE' language
as per the book:
  [Stuart, Tom. Understanding Computation: From Simple Machines to Impossible Programs. " O'Reilly Media, Inc.", 2013],
but implemented in Python instead of Ruby, along with slight modifications for even simpler expressions
of the reduction functions.
'''

# i-o kludge
def env_get(env, name, descr = ''):
  if name not in env:
    if '-randin' in sys.argv:
      val = random.randint(0, 100)
    else:
      val_str = raw_input(' > {}{} : '.format(name, ' ({})'.format(descr) if descr else ''))
      val = int(val_str) if val_str.isdigit() else (val_str[0].lower() == 't')
    env[name] = val
  return env[name]
def env_set(env, name, val):
  env[name] = val
  return val

# SIMPLE syntax elements
g_SIMPLE = ['B', 'I',
          'not', 'and', 'or', 'eq', 'lt', 'succ', 'add', 'mul',
          'var', 'set', 'if', 'seq', 'while']

# commonalities between semantics
def expr(redu, *kids):
  return { 'redu':redu, 'kids':list(kids) }
def is_expr(e):
  return type(e) == type({})
def expr_dup(e):
  return copy.deepcopy(e)
def redu_expr(env, e, redu_func):
  while is_expr(e):
    e = redu_func(env, e)
  return (e, env)
def redu_tbl(prefix):
  tbl = {}
  for x in g_SIMPLE:
    tbl[x] = globals().get('{}_{}'.format(prefix, x), None)
  return tbl

# operational semantics
#  big-step semantics
def bs_redu_expr_once(env, e):
  return e['redu'](env, [bs_redu_expr_once(env, sub_exp) for sub_exp in e['kids']])
bs_redu_expr = lambda env, e: redu_expr(env, e, bs_redu_expr_once)
bs_redu_tbl = lambda: redu_tbl('os')
#  small-step semantics
def ss_redu_expr_once(env, e):
  for i,child in enumerate(e['kids']):
    if is_expr(child):
      e['kids'][i] = ss_redu_expr_once(env, child)
      return e
  return e['redu'](env, e['kids'])
ss_redu_expr = lambda env, e: redu_expr(env, e, ss_redu_expr_once)
ss_redu_tbl = lambda: redu_tbl('os')
#  reduction functions
os_B = lambda val: expr(lambda env, kids: bool(val))
os_I = lambda val: expr(lambda env, kids: int(val))
os_not = lambda child: expr(lambda env, kids: (not kids[0]), child)
os_and = lambda l,r: expr(lambda env, kids: (kids[0] and kids[1]), l,r)
os_or = lambda l,r: expr(lambda env, kids: (kids[0] or kids[1]), l,r)
os_eq = lambda l,r: expr(lambda env, kids: (kids[0] == kids[1]), l,r)
os_lt = lambda l,r: expr(lambda env, kids: (kids[0] < kids[1]), l,r)
os_succ = lambda child: expr(lambda env, kids: (kids[0] + 1), child)
os_add = lambda l,r: expr(lambda env, kids: (kids[0] + kids[1]), l,r)
os_mul = lambda l,r: expr(lambda env, kids: (kids[0] * kids[1]), l,r)
os_var = lambda name,descr='': expr(lambda env, kids: env_get(env, name, descr))
os_set = lambda name,r: expr(lambda env, kids: env_set(env, name, kids[0]), r)
os_if = lambda c,l,r: expr(lambda env, kids: (l if kids[0] else r), c)
os_seq = lambda *exprs: expr(lambda env, kids: ('done seq'), *exprs)
os_while = lambda c,bdy: os_if(expr_dup(c), os_seq(expr_dup(bdy), expr(lambda env,kids: os_while(c,bdy))), os_seq())

#denotational semantics (to python)
def dspy_redu_expr_once(env, e):
  return e['redu'](env, [bs_redu_expr_once(env, sub_exp) for sub_exp in e['kids']])
dspy_redu_expr = lambda env, e: redu_expr(env, e, dspy_redu_expr_once)
dspy_redu_tbl = lambda: redu_tbl('dspy')
#  reduction functions
dspy_B = lambda val: expr(lambda env, kids: '{}'.format(bool(val)))
dspy_I = lambda val: expr(lambda env, kids: '{}'.format(int(val)))
dspy_not = lambda child: expr(lambda env, kids: '(not ({}))'.format(kids[0]), child)
dspy_and = lambda l,r: expr(lambda env, kids: '(({}) and ({}))'.format(kids[0], kids[1]), l,r)
dspy_or = lambda l,r: expr(lambda env, kids: '(({}) or ({}))'.format(kids[0], kids[1]), l,r)
dspy_eq = lambda l,r: expr(lambda env, kids: '(({}) == ({}))'.format(kids[0], kids[1]), l,r)
dspy_lt = lambda l,r: expr(lambda env, kids: '(({}) < ({}))'.format(kids[0], kids[1]), l,r)
dspy_succ = lambda child: expr(lambda env, kids: '(({})+1)'.format(kids[0]), child)
dspy_var = lambda name,descr='': expr(lambda env, kids: '{}'.format(name) )
dspy_set = lambda name,r: expr(lambda env, kids: '{} = ({})'.format(name, kids[0]), r)
dspy_if = lambda c,l,r: expr(lambda env, kids: 'if {}: {{ {} }} else: {{ {} }}'.format(kids[0], kids[1], kids[2]), c,l,r)
dspy_seq = lambda *exprs: expr(lambda env, kids: '\n{};\n'.format('; \n'.join(kids)), *exprs)
dspy_while = lambda c,bdy: expr(lambda env, kids: 'while {}: {{ {} }}'.format(kids[0], kids[1]), c,bdy)

# parsing
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

# tests
def test1():
  print ''
  for title, tbl, redu_expr in [('small-step', ss_redu_tbl(), ss_redu_expr), ('big-step', bs_redu_tbl(), bs_redu_expr), ('denotational (py)', dspy_redu_tbl(), dspy_redu_expr)]:
    print 'Testing {} semantics...\n'.format(title)
    #print tbl['B'](True)
    print redu_expr({}, tbl['B'](True) )
    print redu_expr({}, tbl['not'](tbl['B'](True)) )
    expr_1 = tbl['lt'](tbl['I'](4), tbl['I'](5))
    expr_2 = tbl['lt'](tbl['I'](5), tbl['I'](4))
    expr_3 = tbl['or'](expr_1, expr_2)
    print redu_expr({}, expr_3 )
    print redu_expr({}, tbl['not'](tbl['var']('x', 'test boolean')))
    print redu_expr({}, tbl['set']('y', tbl['succ'](tbl['var']('x'))))
    expr_1 = tbl['set']('y', tbl['succ'](tbl['var']('x')))
    expr_2 = tbl['set']('z', tbl['succ'](tbl['var']('y')))
    print redu_expr({}, tbl['seq'](expr_1, expr_2))
    expr_c = tbl['lt'](tbl['I'](4), tbl['I'](5))
    print redu_expr({}, tbl['if'](expr_c, tbl['I'](6), tbl['I'](-6)) )
    expr_c = tbl['lt'](tbl['var']('i'), tbl['I'](5))
    expr_bdy = tbl['set']('i', tbl['succ'](tbl['var']('i')))
    print redu_expr({'i':0}, tbl['while'](expr_c, expr_bdy))
    print ''
if '-test1' in sys.argv:
  test1()

def test2():
  test_str = '''
while
  lt
    var
      i
    I
      5
  seq
    set
      i
      succ
        var
          i
    set
      j
      mul
        var
          i
        I
          10
'''
  root = parse_lines(test_str.split('\n'), '  ')
  print root
  expr_str = parsed_tree_to_expr(root)
  print expr_str
  tbl, redu_expr = (ss_redu_tbl(), ss_redu_expr)
  built_expr = eval(expr_str)
  print built_expr
  print redu_expr({'i':0}, built_expr)

if '-test2' in sys.argv:
  test2()

if '-i' in sys.argv:
  parse_interactive()

#TODO while in big-step is borken again... probably needs a different version that small-step!
