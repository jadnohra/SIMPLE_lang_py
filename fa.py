import sys, random, time

# globals
g_free_char = '!'

# building
def dfa_build(rules):
  dfa = {}
  for src,char,tgt in rules:
    key = (src, char)
    if key in dfa:
      print ' Error duplicate ruless: [{}:{}>{}] [{}:{}>{}]'.format(src, char, tgt, src, char, rules[key][0])
    else:
      dfa[key] = [tgt]
  return dfa
def nfa_build(rules):
  nfa = {}
  for src,char,tgt in rules:
    key = (src, char)
    if key not in nfa:
      nfa[key] = []
    nfa[key].append(tgt)
  return nfa
# running
def dfa_run(fa, state, chars):
  for char in chars:
    state = fa[(state, char)][0]
  return state
def nfa_enrich_with_free_moves(fa, states):
  nstates = set()
  for state in states:
    for tgt in fa.get((state, g_free_char), []):
      nstates.add(tgt)
  return set(list(states) + list(nstates))
def nfa_run(fa, state, chars):
  states = nfa_enrich_with_free_moves(fa, set([state]))
  for char in chars:
    nstates = set()
    for state in states:
      for tgt in fa.get((state, char), []):
        nstates.add(tgt)
    states = nfa_enrich_with_free_moves(fa, nstates)
  return list(states)
def nfa_run_rnd(fa, state, chars, rnd):
  for char in chars:
    nstate = None
    states = nfa_enrich_with_free_moves(fa, set([state]))
    if len(states):
      state = states[rnd.randint(0, len(states)-1)]
      tgts = fa.get((state, char), [])
      if len(tgts):
        nstate = tgts[rnd.randint(0, len(tgts)-1)]
    state = nstate
    if nstate is None:
      break
  return state

# parsing
def parse_rule_line(line):
  lr_split = [x.strip() for x in line.strip().split(':')]
  rules = []
  if len(lr_split) == 2:
    l,r = [x.strip() for x in line.strip().split(':')]
    char_tgt_split = [x.strip() for x in r.strip().split('>')]
    if len(char_tgt_split) == 2:
      sources,chars,tgts = l, char_tgt_split[0], char_tgt_split[1]
      sources = sources.split(',')
      chars = chars.split(',')
      tgts = tgts.split(',')
      for src in sources:
        for char in chars:
          for tgt in tgts:
            rules.append((src, char, tgt))
  return rules
def parse_rule_lines(lines):
  rules = []
  for line in [x.strip() for x in lines if len(x.strip())]:
    lrules = parse_rule_line(line)
    if len(line) != 0 and len(lrules) == 0:
      print ' Error in line: [{}]'.format(line)
    rules.extend(lrules)
  return rules

def test1():
  # DFA at p.65
  test_str = '''
1: b > 1
1,2 : a > 2
2,3 : b > 3
3 : a > 3
'''
  fa = dfa_build(parse_rule_lines(test_str.split('\n')))
  print fa
  first_state = '1'; chars = 'aabb';
  print '{} : {} > {}'.format(first_state, chars, dfa_run(fa, '1', chars))
if '-test1' in sys.argv:
  test1()

def test2():
  # NFA at p. 71
  test_str = '''
1: a,b > 1
1: b > 2
2 : a,b > 3
3 : a,b > 4
'''
  fa = nfa_build(parse_rule_lines(test_str.split('\n')))
  print fa
  first_state = '1'; chars = 'bbabb';
  print '{} : {} > {}'.format(first_state, chars, sorted(nfa_run(fa, '1', chars)))
if '-test2' in sys.argv:
  test2()

def test3():
  # NFA at p. 77
  test_str = '''
1: ! > 2,4
2: a > 3
3: a > 2
4 : a > 5
5 : a > 6
6 : a > 4
'''
  fa = nfa_build(parse_rule_lines(test_str.split('\n')))
  print fa
  for chars in ['a'*3, 'a'*4, 'a'*5]:
    first_state = '1'
    print '{} : {} > {}'.format(first_state, chars, sorted(nfa_run(fa, '1', chars)))
if '-test3' in sys.argv:
  test3()