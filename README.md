# SIMPLE_lang_py
Small-Step, big-step, and denotational semantics of the 'SIMPLE' language
as per the book:
  [Stuart, Tom. Understanding Computation: From Simple Machines to Impossible Programs. " O'Reilly Media, Inc.", 2013],
but implemented in Python instead of Ruby, along with slight modifications for even simpler expressions
of the reduction functions.

Example

    > python simple_lang.py -i
    > > while
    > >  lt
    > >   var
    > >    i
    > >   I
    > >    5
    > >  seq
    > >    set
    > >      i
    > >      succ
    > >        var
    > >          i
    > >    set
    > >      j
    > >      mul
    > >        var
    > >          i
    > >        I
    > >          10
    > >
    > 
    > tbl['while'](tbl['lt'](tbl['var']('i'), tbl['I'](5)), tbl['seq'](tbl['set']('i', tbl['succ'](tbl['var']('i'))), tbl['set']('j', tbl['mul'](tbl['var']('i'), tbl['I'](10)))))
    >
    > ('done seq', {'i': 5, 'j': 50})
