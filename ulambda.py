import sys

# i-o kludge
def ul_out(x, msg):
  sys.stdout.write(msg); return x;


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
ul_left = (lambda l: (lambda r: l))
ul_right = (lambda l: (lambda r: r))
ul_tuple = (lambda l: (lambda r: (lambda p: p(l)(r))))
ul_ltup = (lambda tup: tup(ul_left))
ul_rtup = (lambda tup: tup(ul_right))
ul_succ = (lambda n: (lambda p: (lambda m: p(n(p)(m)) )))
ul_pred = (lambda n: (lambda p: (lambda m: ul_rtup(n(lambda pm_m: ul_tuple(p(ul_ltup(pm_m)))(ul_ltup(pm_m)) )(ul_tuple(m)(m)))) ))
ul_add = (lambda n1: (lambda n2: n2(lambda m: ul_inc(m))(n1) ))
ul_sub = (lambda n1: (lambda n2: n2(lambda m: ul_pred(m))(n1) ))
ul_mul = (lambda n1: (lambda n2: n2(ul_add(n1))(lambda p: lambda m: m) ))
ul_pow = (lambda n1: (lambda n2: n2(ul_mul(n1))(lambda p: lambda m: p(m)) ))

# alternative lambdas that do not use 'constants' such as 0,1 and
# are hence more general, not relying on the structure of the encoding of naturals
_ul_mul_v1 = (lambda n1: (lambda n2: (ul_pred(n2))(ul_add(n1))(n1) ))
_ul_mul_v2 = (lambda n1: (lambda n2: n2(ul_add(n1))( ul_sub(n1)(n1) ) ))
_ul_pow_v1 = (lambda n1: (lambda n2: (ul_pred(n2))(ul_mul(n1))(n1) ))

# convenience lambdas
ul_true = ul_left
ul_false = ul_right
ul_inc = ul_succ
ul_dec = ul_pred
ul_N = lambda N: ul_meta_build_N(N)[0]
ul_B = lambda B: ul_true if B else ul_false
ul_if = lambda b: b
ul_is0 = lambda n: n(lambda m: ul_false)(ul_true)

# more complex lambdas
ul_leq = (lambda n1: (lambda n2: ul_is0( ul_sub(n1)(n2) ) ))
ul_less = (lambda n1: (lambda n2: ul_is0( ul_sub(ul_inc(n1))(n2) ) ))
_ul_mod_v1 = (lambda n1: (lambda n2: ((ul_less(n1)(n2))(n2)(n1))(lambda m: (ul_less(m)(n2))(m)(ul_sub(m)(n2)) )(n1) )) #one trick to not have to recurse: iterate over the larger number
#bad_ul_mod_naive = (lambda n1: (lambda n2: ( ul_leq(n1)(n2) )( n1 )( ul_mod_bad(ul_sub(n1)(n2))(n2)  ) )) #this turns into an infinite recursion
#bad_ul_mod_v2_rec = (lambda rec: (lambda n1: (lambda n2: ( ul_leq(n1)(n2) )( n1 )( _ul_mod_v2_rec(rec)(ul_sub(n1)(n2))(n2)  ) )) )
#bad_ul_mod_v2 = _ul_mod_v2_rec(_ul_mod_v2_rec) #this does not help either
ul_comile_rec = lambda cond: lambda l: lambda r: cond(l)(r)
_ul_mod_v2 = (lambda n1: (lambda n2: ul_comile_rec(ul_less(n1)(n2))(lambda: n1)(lambda: _ul_mod_v2(ul_sub(n1)(n2))(n2) )() ) ) # I think this is a Z combinator
ul_mod = _ul_mod_v2

def test1():
  print '5:', ul_decode_N(ul_N(5))
  print 'False:', ul_decode_B(ul_B(False))
  print '0 is 0:', ul_decode_B(ul_is0(ul_N(0)))
  print '5 is 0:', ul_decode_B(ul_is0(ul_N(3)))
  print 'right of (3,6):', ul_decode_N(ul_rtup(ul_tuple(ul_N(3))(ul_N(6))))
  print 'inc 5:', ul_decode_N(ul_succ(ul_N(5)))
  print 'dec 5:', ul_decode_N(ul_dec(ul_N(5)))
  print 'dec 0:', ul_decode_N(ul_dec(ul_N(0)))
  print '5 + 3:', ul_decode_N(ul_add(ul_N(5))(ul_N(3)) )
  print '5 - 3:', ul_decode_N(ul_sub(ul_N(5))(ul_N(3)) )
  print '5 * 3:', ul_decode_N(ul_mul(ul_N(5))(ul_N(3)) )
  print '2 ^ 3:', ul_decode_N(ul_pow(ul_N(2))(ul_N(3)) )
  print '5 <= 3:', ul_decode_B(ul_leq(ul_N(5))(ul_N(3)) )
  print '3 <= 5:', ul_decode_B(ul_leq(ul_N(3))(ul_N(5)) )
  print '3 <= 3:', ul_decode_B(ul_leq(ul_N(3))(ul_N(3)) )
  print '3 < 3:', ul_decode_B(ul_less(ul_N(3))(ul_N(3)) )
  print '3 < 5:', ul_decode_B(ul_less(ul_N(3))(ul_N(5)) )
  print '3 % 5:', ul_decode_N(ul_mod(ul_N(3))(ul_N(5)) )
  print '10 % 3:', ul_decode_N(ul_mod(ul_N(10))(ul_N(3)) )
  print '3 % 3:', ul_decode_N(ul_mod(ul_N(3))(ul_N(3)) )


def test_fizzbuzz(mx = 30):
  ul_mod_print = lambda s: lambda a: lambda n: ul_is0(ul_mod(n)(a))(lambda: ul_out(n, s))(lambda: ul_out(n, ''))()
  prog_ul_fizzbuzz = lambda mx: ( ul_N(mx)(lambda m: ul_inc( ul_mod_print('FizzBuzz ')(ul_N(15))(ul_mod_print('Buzz ')(ul_N(5))( ul_mod_print('Fizz ')(ul_N(3))(m)) ) )) ( ul_N(0) ) )
  prog_ul_fizzbuzz(mx)
  print ''