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

#TODO while in big-step is borken again... probably needs a different version that small-step!
