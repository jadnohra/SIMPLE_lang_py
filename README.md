# SIMPLE_lang_py
Small-Step, big-step, and denotational semantics of the 'SIMPLE' language
as per the book *[ [Understanding Computation: From Simple Machines to Impossible Programs. (Tom Stuart)] ](http://shop.oreilly.com/product/0636920025481.do)*,
but implemented in Python instead of Ruby, along with slight modifications for even simpler expressions
of the reduction functions.

## Examples

  Running in interactive mode:

    > python simple_lang.py -i
    > > while i < 5
    > >  seq
    > >   i = (inc i)
    > >   j = (i * 10)
    > >
    >
    > while
    >   lt
    >     var
    >       i
    >     I
    >       5
    >   seq
    >     set
    >       i
    >       succ
    >         var
    >           i
    >     set
    >       j
    >       mul
    >         var
    >           i
    >         I
    >           10
    >
    > tbl['while'](tbl['lt'](tbl['var']('i'), tbl['I'](5)), tbl['seq'](tbl['set']('i', tbl['succ'](tbl['var']('i'))), tbl['set']('j', tbl['mul'](tbl['var']('i'), tbl['I'](10)))))
    >
    > ('done seq', {'i': 5, 'j': 50})

Running a program that calculates powers of 2:

    > python simple_lang.py -pow2
    > >  exp : 3
    > returned: 16

The listing of the -pow2 program is:

    > seq
    >  if (exp < 1)
    >    ret = 1
    >    seq
    >      ret = 2
    >      i = 0
    >      while i < exp
    >        seq
    >          ret = (ret * 2)
    >          i = (inc i)
