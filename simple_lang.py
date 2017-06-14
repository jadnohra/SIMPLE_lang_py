import sys, random, copy

'''
Small-Step, big-step, and denotational semantics of the 'SIMPLE' language
as per the book:
  [Stuart, Tom. Understanding Computation: From Simple Machines to Impossible Programs. " O'Reilly Media, Inc.", 2013],
but implemented in Python instead of Ruby, along with slight modifications for even simpler expressions
of the reduction functions.
'''

# i-o kludge
g_rand_input = '-randin' in sys.argv
def env_get(env, name):
  if name not in env:
    if g_rand_input:
      val = random.randint(0, 100)
    else:
      val_str = raw_input(' > {}? '.format(name))
      val = int(val_str) if val_str.isdigit() else (val_str[0].lower() == 't')
    env[name] = val
  return env[name]
def env_set(env, name, val):
  env[name] = val
  return val

# small-step semantics
def ss_expr(redu, *sub_exps):
  return { 'redu':redu, 'sub_exps':list(sub_exps), 'sub_vals':[] }
def ss_is_expr(e):
  return type(e) == type({})
def ss_redu_expr(env, e):
  n_sub_vals = len(e['sub_vals'])
  if n_sub_vals == len(e['sub_exps']):
    return e['redu'](env, e['sub_vals'])
  redu_res = ss_redu_expr(env, e['sub_exps'][n_sub_vals])
  if ss_is_expr(redu_res):
    e['sub_exps'][n_sub_vals] = redu_res
  else:
    e['sub_vals'].append(redu_res)
  return e
def ss_redu_expr_iter(env, e):
  while ss_is_expr(e):
    e = ss_redu_expr(env, e)
  return (e, env)
def ss_expr_dup(e):
  return copy.deepcopy(e)

# small-step reduction functions
ss_b = lambda val: (lambda env, sub_vals: bool(val))
ss_i = lambda val: (lambda env, sub_vals: int(val))
ss_not = lambda env, sub_vals: (not sub_vals[0])
ss_and = lambda env, sub_vals: (sub_vals[0] and sub_vals[1])
ss_or = lambda env, sub_vals: (sub_vals[0] or sub_vals[1])
ss_eq = lambda env, sub_vals: (sub_vals[0] == sub_vals[1])
ss_neq = lambda env, sub_vals: (sub_vals[0] != sub_vals[1])
ss_lt = lambda env, sub_vals: (sub_vals[0] < sub_vals[1])
ss_add = lambda env, sub_vals: (sub_vals[0] + sub_vals[1])
ss_mul = lambda env, sub_vals: (sub_vals[0] * sub_vals[1])
ss_var = lambda name: ( lambda env, sub_vals: env_get(env, name) )
ss_set = lambda name: ( lambda env, sub_vals: env_set(env, name, sub_vals[0]) )
ss_if = lambda l, r: ( lambda env, sub_vals: l if sub_vals[0] else r )
ss_seq = lambda env, sub_vals: ('done seq')
ss_while = lambda c, b: (lambda env, sub_vals: ss_expr( ss_if( ss_expr(ss_seq, ss_expr_dup(b), ss_expr(ss_while(c, b)) ) , ss_expr(ss_seq)), ss_expr_dup(c) ) )
# additional functions
ss_le = lambda env, sub_vals: (sub_vals[0] <= sub_vals[1])
ss_ge = lambda env, sub_vals: (sub_vals[0] >= sub_vals[1])
ss_gt = lambda env, sub_vals: (sub_vals[0] > sub_vals[1])
ss_inc = lambda env, sub_vals: (sub_vals[0] + 1)
ss_dec = lambda env, sub_vals: (sub_vals[0] - 1)
ss_sub = lambda env, sub_vals: (sub_vals[0] - sub_vals[1])
ss_eq0 = lambda env, sub_vals: (sub_vals[0] == 0)

# to string
g_pretty_redu = { ss_not:'not', ss_inc:'inc' }
def string_expr_tree(e):
  def recurse(state, e, depth):
    if ss_is_expr(e):
      state.append(' {}{}'.format(''.join(['.']*depth), g_pretty_redu.get(e['redu'], '?')))
      for c in e['sub_exps']:
        recurse(state, c, depth+1)
    else:
      state.append( ' {}{}'.format(''.join(['.']*depth), e))
  state = []
  recurse(state, e, 0)
  return '\n'.join(state)

# tests
def test1():
  print ss_expr(ss_b(True))
  print ss_redu_expr({}, ss_expr(ss_b(True)) )
  print ss_redu_expr_iter({}, ss_expr( ss_not, ss_expr(ss_b(True))) )

  expr_1 = ss_expr(ss_lt, ss_expr(ss_i(4)), ss_expr(ss_i(5)))
  expr_2 = ss_expr(ss_gt, ss_expr(ss_i(4)), ss_expr(ss_i(5)))
  expr_3 = ss_expr(ss_or, expr_1, expr_2)
  print ss_redu_expr_iter({}, expr_3 )

  print ss_redu_expr_iter({}, ss_expr( ss_not, ss_expr(ss_var('x_b'))) )

  print ss_redu_expr_iter({}, ss_expr( ss_set('y'), ss_expr(ss_inc, ss_expr(ss_var('x')))) )

  expr_1 = ss_expr( ss_set('y'), ss_expr(ss_inc, ss_expr(ss_var('x'))))
  expr_2 = ss_expr( ss_set('z'), ss_expr(ss_inc, ss_expr(ss_var('y'))))
  print ss_redu_expr_iter({}, ss_expr( ss_seq, expr_1, expr_2) )

  expr_c = ss_expr(ss_lt, ss_expr(ss_i(4)), ss_expr(ss_i(5)))
  print ss_redu_expr_iter({}, ss_expr( ss_if(ss_expr(ss_i(6)), ss_expr(ss_i(-6))), expr_c) )

  expr_c = ss_expr(ss_lt, ss_expr(ss_var('i')), ss_expr(ss_i(5)))
  expr_b = ss_expr( ss_set('i'), ss_expr(ss_inc, ss_expr(ss_var('i'))) )
  #expr_b = ss_expr(ss_var('j'))
  print ss_redu_expr_iter({'i':0}, ss_expr( ss_while(expr_c, expr_b) ) )

if '-test' in sys.argv:
  test1()
