
# meta
def ul_meta_build_N(n):
  def recurse(i):
    return 'p({})'.format(recurse(i-1)) if i>0 else 'x'
  str = 'lambda p: (lambda x: {})'.format(recurse(int(n)))
  return (eval(str), str)

def ul_decode_N(lbda_n):
   return lbda_n(lambda x: x+1)(0)

def ul_decode_B(lbda_b):
  return lbda_b(True)(False)

'''
# This can never work, trying is akin to misunderstanding the expressivity of lambda-calculus
def ul_inspect_depth(lbda):
  def try_apply(lbda):
    for args in [[], [0], [lambda x:x], ['']]:
      try:
          return lbda(*args)
      except TypeError:
        pass
    raise TypeError()
  depth = 0
  while type(lbda) == type(lambda x:x):
    lbda = try_apply(lbda)
    depth = depth + 1
  return depth
'''

# lambdas
ul_true = (lambda t: (lambda f: t))
ul_false = (lambda t: (lambda f: f))

# convenience lambdas
ul_N = lambda N: ul_meta_build_N(N)[0]
ul_B = lambda B: ul_true if B else ul_false
ul_if = lambda b: b
ul_is0 = lambda n: n(lambda x: ul_false)(ul_true)

def test1():
  print '5', ul_decode_N(ul_N(5))
  print 'False', ul_decode_B(ul_B(False))
  print '0 is 0', ul_decode_B(ul_is0(ul_N(0)))
  print '5 is 0', ul_decode_B(ul_is0(ul_N(3)))