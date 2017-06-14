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
SIMPLE = ['b', 'i',
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
  for x in SIMPLE:
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
os_b = lambda val: expr(lambda env, kids: bool(val))
os_i = lambda val: expr(lambda env, kids: int(val))
os_not = lambda child: expr(lambda env, kids: (not kids[0]), child)
os_and = lambda l,r: expr(lambda env, kids: (kids[0] and kids[1]), l, r)
os_or = lambda l,r: expr(lambda env, kids: (kids[0] or kids[1]), l, r)
os_eq = lambda l,r: expr(lambda env, kids: (kids[0] == kids[1]), l, r)
os_lt = lambda l,r: expr(lambda env, kids: (kids[0] < kids[1]), l, r)
os_succ = lambda child: expr(lambda env, kids: (kids[0] + 1), child)
os_add = lambda l,r: expr(lambda env, kids: (kids[0] + kids[1]), l, r)
os_mul = lambda l,r: expr(lambda env, kids: (kids[0] * kids[1]), l, r)
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
dspy_b = lambda val: ( lambda env, kids: '{}'.format(bool(val)) )
dspy_i = lambda val: ( lambda env, kids: '{}'.format(int(val)) )
dspy_not = lambda env, kids: '(not ({}))'.format(kids[0])
dspy_and = lambda env, kids: '(({}) and ({}))'.format(kids[0], kids[1])
dspy_or = lambda env, kids: '(({}) or ({}))'.format(kids[0], kids[1])
dspy_eq = lambda env, kids: '(({}) == ({}))'.format(kids[0], kids[1])
dspy_lt = lambda env, kids: '(({}) < ({}))'.format(kids[0], kids[1])
dspy_succ = lambda env, kids: '(({})+1)'.format(kids[0])
dspy_var = lambda name: ( lambda env, kids: '{}'.format(name) )
dspy_set = lambda name: ( lambda env, kids: '{} = ({})'.format(name, kids[0]) )
'''
dspy_concat(strings):
  return '[&]'.join(strings)
dspy_if = lambda l, r: ( lambda env, kids: expr(kids[0], l, r) )
'''

# tests
def test1():
  for tbl, redu_expr in [(ss_redu_tbl(), ss_redu_expr), (bs_redu_tbl(), bs_redu_expr), (dspy_redu_tbl(), dspy_redu_expr)][0:2]:
    print tbl['b'](True)
    print redu_expr({}, tbl['b'](True) )
    print redu_expr({}, tbl['not'](tbl['b'](True)) )
    expr_1 = tbl['lt'](tbl['i'](4), tbl['i'](5))
    expr_2 = tbl['lt'](tbl['i'](5), tbl['i'](4))
    expr_3 = tbl['or'](expr_1, expr_2)
    print redu_expr({}, expr_3 )
    print redu_expr({}, tbl['not'](tbl['var']('x', 'test boolean')))
    print redu_expr({}, os_set('y', tbl['succ'](tbl['var']('x'))))
    expr_1 = os_set('y', tbl['succ'](tbl['var']('x')))
    expr_2 = os_set('z', tbl['succ'](tbl['var']('y')))
    print redu_expr({}, tbl['seq'](expr_1, expr_2))
    expr_c = tbl['lt'](tbl['i'](4), tbl['i'](5))
    print redu_expr({}, tbl['if'](expr_c, tbl['i'](6), tbl['i'](-6)) )
    expr_c = tbl['lt'](tbl['var']('i'), tbl['i'](5))
    expr_bdy = os_set('i', tbl['succ'](tbl['var']('i')))
    print redu_expr({'i':0}, os_while(expr_c, expr_bdy))
    print ''
if '-test' in sys.argv:
  test1()
