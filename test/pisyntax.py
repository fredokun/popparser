
'''{

The syntax of pi-calculus processes.

Process P ::=
  0                                # termination
| nu(x) P                          # restriction
| [G] act.P1 + ... + [G] act.PN    # guarded choice
| P1 || ... || PN                  # parallel  (Pi's not parallel themselves)
| D(v1, ..., vN)                   # call

Action act ::=
   tau    # internal action
 | a!b    # output
 | a?(x)  # input

Guard G ::=
   a = b          # match
 | a <> b         # mismatch
 | G1 ^ ... ^ GN  # conjunction
Definition D(x1, ..., xN) = P

}'''


class Process:
    def __init__(self, tag):
        self.tag = tag

    def is_term(self):
        return self.tag == 'term'

    def is_restrict(self):
        return self.tag == 'restrict'

    def is_choice(self):
        return self.tag == 'choice'

    def is_parallel(self):
        return self.tag == 'parallel'

    def is_call(self):
        return self.tag == 'call'

    def is_gc(self):
        return self.tag == 'gc'

    def subst(self, env):
        raise Exception("subst method not implemented")

def subst_name(name, env):
    if name in env:
        return env[name]
    else:
        return name

class Term(Process):
    def __init__(self):
        super().__init__('term')

    def subst(self, vars, vals):
        return Term()

    def __eq__(self, other):
        if not isinstance(other, Term):
            return False

        return True

    def __hash__(self):
        return hash("term")

    def __str__(self):
        return "0"

    def __repr__(self):
        return "Term()"


class Restriction(Process):
    def __init__(self, name, cont):
        super().__init__('restrict')
        self.name = name
        self.cont = cont

    def subst(self, env):
        nenv = { nparam:env[nparam] for nparam in env if nparam != self.name }
        for param in nenv:
            if nenv[param] == self.name:
                del nenv[param]
        return Restriction(self.name, self.cont.subst(nenv))

    def __eq__(self, other):
        if not isinstance(other, Restriction):
            return False

        return (self.name == other.name) and (self.cont == other.cont)

    def __hash__(self):
        return hash(self.name) + hash(self.cont) * 16384

    def __str__(self):
        return "new({}){{{}}}".format(self.name, str(self.cont))

    def __repr__(self):
        return "Restriction({}, {})".format(self.name, repr(self.cont))

class GC(Process):
    def __init__(self, cont):
        super().__init__('gc')
        self.cont = cont

    def subst(self, env):
        return GC(self.cont.subst(env))

    def __eq__(self, other):
        if not isinstance(other, GC):
            return False

        return self.cont == other.cont

    def __hash__(self):
        return hash("gc") + hash(self.cont) * 16384

    def __str__(self):
        return "<GC>=>{}".format(str(self.cont))

    def __repr__(self):
        return "GC({})".format(repr(self.cont))


class Call(Process):
    def __init__(self, def_name, args):
        super().__init__('call')
        self.def_name = def_name
        self.args = tuple(args)

    def subst(self, env):
        nargs = [ subst_name(arg, env) for arg in self.args ]
        return Call(self.def_name, nargs)

    def __eq__(self, other):
        if not isinstance(other, Call):
            return False

        return (self.def_name == other.def_name) and (self.args == other.args)

    def __hash__(self):
        return hash(self.def_name) + hash(self.args) * 16384

    def __str__(self):
        return "{}({})".format(self.def_name, ", ".join((str(arg) for arg in self.args)))

    def __repr__(self):
        return "Call({})".format(", ".join((str(arg) for arg in self.args)))

class Action:
    def __init__(self, tag):
        self.tag = tag

    def is_tau(self):
        return self.tag == 'tau'

    def is_output(self):
        return self.tag == 'output'

    def is_input(self):
        return self.tag == 'input'

    def subst(self, env):
        raise Exception("'subst' method not implemented")

class Tau(Action):
    def __init__(self):
        super().__init__('tau')

    def subst(self, env):
        return Tau()

    def __eq__(self, other):
        if not isinstance(other, Tau):
            return False

        return True

    def __hash__(self):
        return hash("tau")

    def __str__(self):
        return "tau"

    def __repr__(self):
        return "Tau()"

class Output(Action):
    def __init__(self, chan, data):
        super().__init__('output')
        self.chan = chan
        self.data = data

    def subst(self, env):
        return Output(subst_name(self.chan, env), subst_name(self.data, env))

    def __eq__(self, other):
        if not isinstance(other, Output):
            return False

        return (self.chan == other.chan) and (self.data == other.data)

    def __hash__(self):
        return hash(self.chan) + hash(self.data) * 16384

    def __str__(self):
        return "{}!{}".format(self.chan, self.data)

    def __repr__(self):
        return "Output({}, {})".format(self.chan, self.data)

class Input(Action):
    def __init__(self, chan, var):
        super().__init__('input')
        self.chan = chan
        self.var = var

    def subst(self, env):
        return Input(subst_name(self.chan, env), self.var)

    def __eq__(self, other):
        if not isinstance(other, Input):
            return False

        return (self.chan == other.chan) and (self.var == other.var)

    def __hash__(self):
        return hash(self.chan) + hash(self.var) * 16384

    def __str__(self):
        return "{}?({})".format(self.chan, self.var)

    def __repr__(self):
        return "Input({}, {})".format(self.chan, self.var)

def str_one_branch(guard, act, cont):
    return "{}{}.{}".format(str(guard), str(act), str(cont))


class Guard:
    def __init__(self, *conds):
        self.conds = conds

    def subst(self, env):
        nconds = []
        for cond in self.conds:
            nconds.append(cond.subst(env))

        return Guard(*nconds)

    def __eq__(self, other):
        if not isinstance(other, Guard):
            return False

        return self.conds == other.conds

    def __hash__(self):
        return hash(self.conds)

    def __str__(self):
        if not self.conds:
            return ""

        ret = "["
        sep = ""

        for cond in self.conds:
            ret += sep
            if not sep:
                sep = "^"
            ret += str(cond)

        ret += "] "

        return ret

    def __repr__(self):
        ret = "Guard("
        ret += ", ".join((str(cond) for cond in self.conds))
        ret += ")"
        return ret

class Cond:
    def __init__(self, tag, lname, rname):
        self.tag = tag
        self.lname = lname
        self.rname = rname

    def is_match(self):
        return self.tag == 'match'

    def is_mismatch(self):
        return self.tag == 'mismatch'

    def subst(self, env):
        raise Exception("'subst' method not implemented")

class Match(Cond):
    def __init__(self, lname, rname):
        super().__init__('match', lname, rname)

    def subst(self, env):
        return Match(subst_name(self.lname, env),
                     subst_name(self.rname, env))

    def __eq__(self, other):
        if not isinstance(other, Match):
            return False

        return (self.lname == other.lname) and (self.rname == other.rname)

    def __hash__(self):
        return hash(self.lname) + hash(self.rname) * 16384

    def __str__(self):
        return "{}={}".format(str(self.lname), str(self.rname))

    def __repr__(self):
        return "Match({}, {})".format(repr(self.lname), repr(self.rname))

class Mismatch(Cond):
    def __init__(self, lname, rname):
        super().__init__('mismatch', lname, rname)

    def subst(self, env):
        return Mismatch(subst_name(self.lname, env),
                        subst_name(self.rname, env))

    def __eq__(self, other):
        if not isinstance(other, Mismatch):
            return False

        return (self.lname == other.lname) and (self.rname == other.rname)

    def __hash__(self):
        return hash(self.lname) + hash(self.rname) * 16384

    def __str__(self):
        return "{}<>{}".format(str(self.lname), str(self.rname))

    def __repr__(self):
        return "Mismatch({}, {})".format(repr(self.lname), repr(self.rname))

class Choice(Process):
    def __init__(self, *branches):
        super().__init__('choice')
        self.branches = tuple(branches)

    def subst(self, env):
        nbranches = []

        for (guard, act, cont) in self.branches:
            nenv = {param:env[param] for param in env}
            nguard = guard.subst(nenv)
            nact = act.subst(nenv)
            if nact.is_input():
                if nact.var in nenv:
                    del nenv[nact.var]
                for param in nenv:
                    if nenv[param] == nact.var:
                        del nenv[param]
            ncont = cont.subst(nenv)
            nbranches.append((nguard, nact, ncont))

        return Choice(*nbranches)

    def __eq__(self, other):
        if not isinstance(other, Choice):
            return False

        return self.branches == other.branches

    def __hash__(self):
        return hash(self.branches)

    def __str__(self):
        if not(self.branches):
            return "<EMPTY CHOICE>"

        if len(self.branches) == 1:
            guard, act, cont = self.branches[0]
            return str_one_branch(guard, act, cont)

        ret = "("
        sep = ""
        for branch in self.branches:
            ret += sep
            if not sep:
                sep = " + "

            guard, act, cont = branch
            ret += str_one_branch(guard, act, cont)

        ret += ")"

        return ret

    def __repr__(self):
        ret = "Choice("
        sep = ""
        for branch in self.branches:
            ret += sep
            if not sep:
                sep = ", "
            guard, act, cont = branch
            ret += "({}, {}, {})".format(repr(guard), repr(act), repr(cont))

        ret += ")"

        return ret

def prefix(act, cont):
    return Choice((Guard(), act, cont))

def guarded(guard, act, cont):
    return Choice((guard, act, cont))

def cond_process(match, act, cont):
    return guarded(Guard(match), act, cont)

class Parallel(Process):
    def __init__(self, *children):
        super().__init__('parallel')
        assert len(children) >= 2
        for child in children:
            assert isinstance(child, Process)
            assert not child.is_parallel()

        self.children = tuple(children)

    def subst(self, env):
        nchildren = []
        for child in self.children:
            nchild = child.subst(env)
            nchildren.append(nchild)

        return Parallel(*nchildren)

    def __eq__(self, other):
        if not isinstance(other, Parallel):
            return False

        return self.children == other.children

    def __hash__(self):
        return hash(self.children)

    def __str__(self):
        if not(self.children):
            return "<EMPTY PARALLEL>"

        if len(self.children) == 1:
            return str(self.children[0])

        ret = "("
        sep = ""
        for child in self.children:
            ret += sep
            if not sep:
                sep = " || "

            ret += str(child)

        ret += ")"

        return ret

    def __repr__(self):
        ret = "Parallel("
        sep = ""
        for child in self.children:
            ret += sep
            if not sep:
                sep = ", "
            ret += repr(child)

        ret += ")"

        return ret

class Definition:
    def __init__(self, name, params, proc):
        self.name = name
        self.params = params
        self.proc = proc

    def __str__(self):
        return "{}({})={}".format(self.name, ", ".join((str(param) for param in self.params)),
                                  str(self.proc))

    def __repr__(self):
        return "Definition({}, ({}), {})".format(self.name, ",".join((str(param) for param in self.params)),
                                                 repr(self.proc))

def def_unfold_call(defs, call):
    assert isinstance(call, Call)

    defn = defs.get(call.def_name, None)

    if defn is None:
        raise Exception("Call to undefined '{}'".format(call.def_name))

        if len(defn.params) != len(call.args):
            raise Exception("Call arity error: {} parameters, vs. {} arguments".format(len(defn.params), len(call.args)))

    subst_env = { param:arg for (param, arg) in zip(defn.params, call.args) }
    sproc = defn.proc.subst(subst_env)

    return sproc

def fetch_static_vars(proc, def_map=None, env_map=None):
    if env_map is None:
        env_map = dict()  # dict[str,set[name]]  the static vars of calls
    if def_map is None:
        def_map = dict()

    if proc.is_term():
        return set()
    elif proc.is_restrict():
        return fetch_static_vars(proc.cont, def_map, env_map) - {proc.name}
    elif proc.is_gc():
        return fetch_static_vars(proc.cont, def_map, env_map)
    elif proc.is_call():
        dvars = env_map.get(str(proc), None)
        if dvars is not None:
            return dvars
        sproc = def_unfold_call(def_map, proc)
        ivars = set()
        env_map[str(proc)] = ivars
        while True:
            dvars = fetch_static_vars(sproc, def_map, env_map)
            if dvars != ivars:
                ivars |= dvars
            else:
                break # no change, exit the loop

        return ivars
    elif proc.is_choice():
        static_vars = set()
        for (guard, act, cont) in proc.branches:
            for cond in guard.conds:
                if cond.is_match() or cond.is_mismatch():
                    static_vars |= {cond.lname, cond.rname}

            static_vars |= fetch_static_vars(cont, def_map, env_map)

            if act.is_output():
                static_vars |= {act.chan, act.data}
            elif act.is_input():
                static_vars |= {act.chan}
                static_vars -= {act.var}

        return static_vars

    elif proc.is_parallel():
        static_vars = set()
        for child in proc.children:
            static_vars |= fetch_static_vars(child, def_map, env_map)

        return static_vars
    else:
        raise Exception("Unknown process kind: {}".format(proc))

def fetch_private_vars(proc, def_map=None, env_map=None):
    if env_map is None:
        env_map = dict()  # dict[str,set[name]]  the private vars of calls
    if def_map is None:
        def_map = dict()

    if proc.is_term():
        return set()
    elif proc.is_restrict():
        return fetch_private_vars(proc.cont, def_map, env_map) | {proc.name}
    elif proc.is_gc():
        return fetch_private_vars(proc.cont, def_map, env_map)
    elif proc.is_call():
        dvars = env_map.get(str(proc), None)
        if dvars is not None:
            return dvars
        sproc = def_unfold_call(def_map, proc)
        ivars = set()
        env_map[str(proc)] = ivars
        while True:
            dvars = fetch_private_vars(sproc, def_map, env_map)
            if dvars != ivars:
                ivars |= dvars
            else:
                break # no change, exit the loop

        return ivars
    elif proc.is_choice():
        private_vars = set()
        for (guard, act, cont) in proc.branches:
            private_vars |= fetch_private_vars(cont, def_map, env_map)

        return private_vars

    elif proc.is_parallel():
        private_vars = set()
        for child in proc.children:
            child_private_vars = fetch_private_vars(child, def_map, env_map)
            for v in child_private_vars:
                if v in private_vars:
                    raise Exception("Duplicate private variable: {}".format(v))
            private_vars |= child_private_vars

        return private_vars
    else:
        raise Exception("Unknown process kind: {}".format(proc))

def fetch_input_vars(proc, def_map=None, env_map=None):
    if env_map is None:
        env_map = dict()  # dict[str,set[name]]  the private vars of calls
    if def_map is None:
        def_map = dict()

    if proc.is_term():
        return set()
    elif proc.is_restrict():
        return fetch_input_vars(proc.cont, def_map, env_map)
    elif proc.is_gc():
        return fetch_input_vars(proc.cont, def_map, env_map)
    elif proc.is_call():
        dvars = env_map.get(str(proc), None)
        if dvars is not None:
            return dvars
        sproc = def_unfold_call(def_map, proc)
        ivars = set()
        env_map[str(proc)] = ivars
        while True:
            dvars = fetch_input_vars(sproc, def_map, env_map)
            if dvars != ivars:
                ivars |= dvars
            else:
                break # no change, exit the loop

        return ivars
    elif proc.is_choice():
        input_vars = set()
        for (guard, act, cont) in proc.branches:
            branch_input_vars = fetch_input_vars(cont, def_map, env_map)

            if act.is_input():
                if act.var in branch_input_vars:
                    raise Exception("Duplicate input variable: {}".format(act.var))
                input_vars |= {act.var}
            input_vars |= branch_input_vars

        return input_vars

    elif proc.is_parallel():
        input_vars = set()
        for child in proc.children:
            child_input_vars = fetch_input_vars(child, def_map, env_map)
            for v in child_input_vars:
                if v in input_vars:
                    raise Exception("Duplicate input variable: {}".format(v))
            input_vars |= child_input_vars

        return input_vars
    else:
        raise Exception("Unknown process kind: {}".format(proc))

def example_term():
    return Term()

def example_tau():
    return prefix(Tau(), Term())

def example_2_taus():
    return Parallel(prefix(Tau(), Term()),
                    prefix(Tau(), Term()))

def example_sync():
    return Parallel(prefix(Output('c', 'b'), Term()),
                    prefix(Input('c', 'x'),
                                   prefix(Output('a', 'x'), Term())))

def example_priv_sync():
    return Restriction('c',
                       Parallel(prefix(Output('c', 'b'), Term()),
                                prefix(Input('c', 'x'),
                                               prefix(Output('a', 'x'), Term()))))

def example_bound_output():
    return Restriction('a',
                       prefix(Output('c', 'a'), prefix(Output('a', 'b'), Term())))



def example_recursive_def():
    def_map = dict()
    def_map['D'] = Definition('D', ('x', 'y'),
                              prefix(Output('c','x'),
                                             prefix(Output('c','y'),
                                                        Call('D', ('y', 'x')))))
    return (def_map, prefix(Output('d', 'c'), Call('D', ('a', 'b'))))


def example_infinite_generator():
    def_map = dict()
    def_map['Gen'] = Definition('Gen', (), Restriction('a',
                                                       prefix(Output('c', 'a'),
                                                                      Call('Gen', ()))))

    return (def_map, Call('Gen', ()))

def example_finite_generator():
    def_map = dict()
    def_map['FGen'] = Definition('FGen', (), Restriction('a',
                                                         GC(prefix(Output('c', 'a'),
                                                                           Call('FGen', ())))))

    return (def_map, Call('FGen', ()))

def counter_example_HAL():
    return prefix(Input('c', 'x'),
                  prefix(Input('c', 'y'),
                         guarded(Guard(Match('x', 'y')), Input('c', 'z'),
                                 prefix(Output('z', 'x'),
                                        prefix(Output('z', 'y'), Term())))))

def print_vars(proc, def_map = None):
    print("Static vars = {}".format(fetch_static_vars(proc, def_map)))
    print("Private vars = {}".format(fetch_private_vars(proc, def_map)))
    print("Input vars = {}".format(fetch_input_vars(proc, def_map)))

if __name__ == "__main__":

    example_term = example_term()

    print("Terminated = {}  (tag '{}')".format(example_term, example_term.tag))

    print("----")

    example_tau = example_tau()

    print("Example with tau:")
    print(example_tau)

    print("----")

    example_sync = example_sync()

    print("Example with synchronization:")
    print(example_sync)

    print_vars(example_sync)

    print("----")

    example_priv_sync = example_priv_sync()

    print("Example with (private) synchronization:")
    print(example_priv_sync)

    print_vars(example_priv_sync)

    print("----")

    example_bound_output = example_bound_output()

    print("Example with bound output:")
    print(example_bound_output)

    print_vars(example_bound_output)

    print("----")

    example_HAL = counter_example_HAL()

    print("Example HAL-counter-example:")
    print(example_HAL)

    print_vars(example_HAL)

    print("----")

    example_rec_defs, example_rec = example_recursive_def()

    print("Example with recursive definition:")
    print(example_rec_defs['D'])
    print(example_rec)

    print_vars(example_rec, def_map = example_rec_defs)

    print("----")

    example_inf_defs, example_inf = example_infinite_generator()

    print("Example: infinite generator")
    print(example_inf_defs['Gen'])
    print(example_inf)

    print_vars(example_inf, def_map = example_inf_defs)

    print("----")

    example_fin_defs, example_fin = example_finite_generator()

    print("Example: finite generator")
    print(example_fin_defs['FGen'])
    print(example_fin)

    print_vars(example_fin, def_map = example_fin_defs)


