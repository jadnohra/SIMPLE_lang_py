import sys
from simple_lang import *
from simple_parse import *

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

def test3():
  test_str1 = '''
seq
  lt
    var
      i
    5
  lt
    i
    5
  eq
    B
      T
    F
  lt 4 5
'''
  test_str2 = '''
while lt i 5
  seq
    set
      i
      succ i
    set
      j
      mul i 10
'''
  test_str3 = '''
while i < 5
  seq
    i = (inc i)
    j = (i * 10)
'''
  for test_str in [test_str1, test_str2, test_str3]:
    print '\n'.join(preparse_lines(test_str.split('\n'), '  '))
if '-test3' in sys.argv:
  test3()

if '-i' in sys.argv:
  parse_interactive()