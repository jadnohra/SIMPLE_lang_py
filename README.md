# SIMPLE_lang_py
Small-Step, big-step, and denotational semantics of the 'SIMPLE' language
as per the book *[ [Understanding Computation: From Simple Machines to Impossible Programs. (Tom Stuart)] ](http://shop.oreilly.com/product/0636920025481.do)*,
but implemented in Python instead of Ruby, along with slight modifications for even simpler expressions
of the reduction functions.

Example

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
