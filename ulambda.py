
# meta
def ul_meta_build_N(n):
  def recurse(i):
    return 'p({})'.format(recurse(i-1)) if i>0 else 'x'
  str = 'lambda p: (lambda x: {})'.format(recurse(int(n)))
  return (eval(str), str)

def test1():
  print ul_meta_build_N(5)[0](lambda x: x+2)(0)
