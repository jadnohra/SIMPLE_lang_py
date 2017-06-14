import sys, random, copy

'''
Small-Step, big-step, and denotational semantics of the 'SIMPLE' language
as per the book:
  [Stuart, Tom. Understanding Computation: From Simple Machines to Impossible Programs. " O'Reilly Media, Inc.", 2013],
but implemented in Python instead of Ruby, along with slight modifications for even simpler expressions
of the reduction functions.
'''

# i-o kludge
def env_get(env, name):
  if name not in env:
    if '-randin' in sys.argv:
      val = random.randint(0, 100)
    else:
      val_str = raw_input(' > {}? '.format(name))
      val = int(val_str) if val_str.isdigit() else (val_str[0].lower() == 't')
    env[name] = val
  return env[name]
def env_set(env, name, val):
  env[name] = val
  return val

# commonalities between semantics
def expr(redu, *sub_exps):
  return { 'redu':redu, 'sub_exps':list(sub_exps) }
def is_expr(e):
  return type(e) == type({})
def expr_dup(e):
  return copy.deepcopy(e)
def redu_expr(env, e, redu_func):
  while is_expr(e):
    e = redu_func(env, e)
  return (e, env)

# operational semantics
#  big-step semantics
def bs_redu_expr_once(env, e):
  return e['redu'](env, [bs_redu_expr_once(env, sub_exp) for sub_exp in e['sub_exps']])
bs_redu_expr = lambda env, e: redu_expr(env, e, bs_redu_expr_once)
#  small-step semantics
def ss_redu_expr_once(env, e):
  if 'sub_vals' not in e:
    e['sub_vals'] = []
  n_sub_vals = len(e['sub_vals'])
  if n_sub_vals == len(e['sub_exps']):
    return e['redu'](env, e['sub_vals'])
  redu_res = ss_redu_expr_once(env, e['sub_exps'][n_sub_vals])
  if is_expr(redu_res):
    e['sub_exps'][n_sub_vals] = redu_res
  else:
    e['sub_vals'].append(redu_res)
  return e
ss_redu_expr = lambda env, e: redu_expr(env, e, ss_redu_expr_once)
#  reduction functions
os_b = lambda val: (lambda env, exp_children: bool(val))
os_i = lambda val: (lambda env, exp_children: int(val))
os_not = lambda env, exp_children: (not exp_children[0])
os_and = lambda env, exp_children: (exp_children[0] and exp_children[1])
os_or = lambda env, exp_children: (exp_children[0] or exp_children[1])
os_eq = lambda env, exp_children: (exp_children[0] == exp_children[1])
os_neq = lambda env, exp_children: (exp_children[0] != exp_children[1])
os_lt = lambda env, exp_children: (exp_children[0] < exp_children[1])
os_add = lambda env, exp_children: (exp_children[0] + exp_children[1])
os_mul = lambda env, exp_children: (exp_children[0] * exp_children[1])
os_var = lambda name: ( lambda env, exp_children: env_get(env, name) )
os_set = lambda name: ( lambda env, exp_children: env_set(env, name, exp_children[0]) )
os_if = lambda l, r: ( lambda env, exp_children: l if exp_children[0] else r )
os_seq = lambda env, exp_children: ('done seq')
os_while = lambda c, b: (lambda env, exp_children: expr( os_if( expr(os_while(c, b), expr_dup(b) ) , expr(os_seq)), expr_dup(c) ) )
# additional functions
os_le = lambda env, exp_children: (exp_children[0] <= exp_children[1])
os_ge = lambda env, exp_children: (exp_children[0] >= exp_children[1])
os_gt = lambda env, exp_children: (exp_children[0] > exp_children[1])
os_inc = lambda env, exp_children: (exp_children[0] + 1)
os_dec = lambda env, exp_children: (exp_children[0] - 1)
os_sub = lambda env, exp_children: (exp_children[0] - exp_children[1])
os_eq0 = lambda env, exp_children: (exp_children[0] == 0)

# tests
def test1():
  for redu_expr in [ss_redu_expr, bs_redu_expr]:
    print expr(os_b(True))
    print redu_expr({}, expr(os_b(True)) )
    print redu_expr({}, expr( os_not, expr(os_b(True))) )
    expr_1 = expr(os_lt, expr(os_i(4)), expr(os_i(5)))
    expr_2 = expr(os_gt, expr(os_i(4)), expr(os_i(5)))
    expr_3 = expr(os_or, expr_1, expr_2)
    print redu_expr({}, expr_3 )
    print redu_expr({}, expr( os_not, expr(os_var('x_b'))) )
    print redu_expr({}, expr( os_set('y'), expr(os_inc, expr(os_var('x')))) )
    expr_1 = expr( os_set('y'), expr(os_inc, expr(os_var('x'))))
    expr_2 = expr( os_set('z'), expr(os_inc, expr(os_var('y'))))
    print redu_expr({}, expr( os_seq, expr_1, expr_2) )
    expr_c = expr(os_lt, expr(os_i(4)), expr(os_i(5)))
    print redu_expr({}, expr( os_if(expr(os_i(6)), expr(os_i(-6))), expr_c) )
    expr_c = expr(os_lt, expr(os_var('i')), expr(os_i(5)))
    expr_b = expr( os_set('i'), expr(os_inc, expr(os_var('i'))) )
    print redu_expr({'i':0}, expr( os_while(expr_c, expr_b) ) )
    print ''
if '-test' in sys.argv:
  test1()
