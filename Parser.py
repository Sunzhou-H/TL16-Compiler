# -*- coding: utf-8 -*-
current_tok = ''


def parser(tok_file, ast_file):
    global current_tok

    class ASTNode(object):
        def __init__(self):
            pass

    # program(decl_list, stmt_list)
    class Program(ASTNode):
        def __init__(self):
            super(ASTNode, self).__init__()

    # decl_list(decls)
    class DeclList(ASTNode):
        def __init__(self):
            super(ASTNode, self).__init__()
            self.decls = []

    # decl(ident, type)
    class Decl(ASTNode):
        def __init__(self):
            super(ASTNode, self).__init__()

    # stmt_list(stmts)
    class StmtList(ASTNode):
        def __init__(self):
            super(ASTNode, self).__init__()
            self.stmts = []

    # stmt
    class Stmt(ASTNode):
        def __init__(self):
            super(ASTNode, self).__init__()

    # assignment(ident, modify)
    class Assignment(Stmt):
        def __init__(self):
            super(Stmt, self).__init__()

    # readint
    class Readint(ASTNode):
        def __init__(self):
            super(ASTNode, self).__init__()

    # if(cond, stmts, ec)
    class If(Stmt):
        def __init__(self):
            super(Stmt, self).__init__()

    # while(cond, stmts)
    class While(Stmt):
        def __init__(self):
            super(Stmt, self).__init__()

    # writeint(expr)
    class Writeint(Stmt):
        def __init__(self):
            super(Stmt, self).__init__()

    # expr
    class Expr(ASTNode):
        def __init__(self):
            super(ASTNode, self).__init__()
            self.left = ASTNode()
            self.op = ''
            self.right = ASTNode()

    # comp(left, op, right)
    class Comp(Expr):
        def __init__(self):
            super(Expr, self).__init__()

    # add(left, op, right)
    class Add(Expr):
        def __init__(self):
            super(Expr, self).__init__()

    # multi(left, op, right)
    class Multi(Expr):
        def __init__(self):
            super(Expr, self).__init__()

    # factor(name)
    class Factor(ASTNode):
        def __init__(self):
            super(ASTNode, self).__init__()
            self.name = ''

    # ident(name)
    class Ident(Factor):
        def __init__(self):
            super(Factor, self).__init__()

    # num(name)
    class Num(Factor):
        def __init__(self):
            super(Factor, self).__init__()

    # boollit(name)
    class Boollit(Factor):
        def __init__(self):
            super(Factor, self).__init__()

    # Visitor
    class Visitor(object):
        def visit(self, node, *args, **kwargs):
            meth = None
            for cls in node.__class__.__mro__:
                meth_name = 'visit_' + cls.__name__
                meth = getattr(self, meth_name, None)
                if meth:
                    break
            if not meth:
                meth = self.generic_visit
            return meth(node, *args, **kwargs)

        def generic_visit(self, node, *args, **kwargs):
            print('generic_visit ' + node.__class__.__name__)

        def visit_Program(self, node, *args, **kwargs):
            print('visit_Program ' + node.__class__.__name__)

    # Error
    class ParserError(Exception):
        pass

    with open(tok_file, 'r') as f_tok:
        try:
            source_toks = iter(f_tok.read().split())
            current_tok = next(source_toks)
        except StopIteration:
            print('Empty Program!')
            return False

    def token(tok):
        global current_tok
        if tok in current_tok:
            print(current_tok)
            try:
                current_tok = next(source_toks)
            except StopIteration:
                print('Tokens end!')
            return True
        else:
            raise ParserError

    def program():
        if current_tok == 'PROGRAM':
            token('PROGRAM')
            p = Program()
            p.decl_list = decl_list()
            token('BEGIN')
            p.stmt_list = stmt_list()
            token('END')
            return p
        else:
            raise ParserError

    def decl_list():
        if current_tok == 'VAR':
            d = DeclList()
            d.decls = []
            d.decls.append(decl())
            token('SC')
            d.decls += decl_list().decls
            return d
        elif current_tok == 'BEGIN':
            d = DeclList()
            d.decls = []
            return d
        else:
            raise ParserError

    def decl():
        token('VAR')
        if 'ident(' in current_tok:
            d = Decl()
            d.ident = current_tok.split('(')[1].split(')')[0]
        else:
            raise ParserError
        token('ident(')
        token('AS')
        d.type = type_tl()
        return d

    def type_tl():
        if current_tok == 'INT':
            token('INT')
            return 'INT'
        elif current_tok == 'BOOL':
            token('BOOL')
            return 'BOOL'
        else:
            raise ParserError

    def stmt_list():
        if ('ident('in current_tok) or (current_tok in ('IF', 'WHILE', 'WRITEINT')):
            s = StmtList()
            s.stmts = []
            s.stmts.append(statement())
            token('SC')
            s.stmts += stmt_list().stmts
            return s
        elif current_tok in ('END', 'ELSE'):
            s = StmtList()
            s.stmts = []
            return s
        else:
            raise ParserError

    def statement():
        if 'ident('in current_tok:
            return assignment()
        elif current_tok == 'IF':
            return if_statement()
        elif current_tok == 'WHILE':
            return while_statement()
        elif current_tok == 'WRITEINT':
            return writeint()
        else:
            raise ParserError

    def assignment():
        if 'ident('in current_tok:
            a = Assignment()
            i = Ident()
            i.name = current_tok.split('(')[1].split(')')[0]
            a.ident = i
            token('ident(')
            token('ASGN')
            a.modify = assignment_modified()
            return a
        else:
            raise ParserError

    def assignment_modified():
        if any(tok in current_tok for tok in ('ident(', 'num(', 'boollit(', 'LP')):
            return expression()
        elif current_tok == 'READINT':
            r = Readint()
            token('READINT')
            return r
        else:
            raise ParserError

    def if_statement():
        if current_tok == 'IF':
            token('IF')
            i = If()
            i.cond = expression()
            token('THEN')
            i.stmts = stmt_list()
            i.ec = else_clause()
            token('END')
            return i
        else:
            raise ParserError

    def while_statement():
        if current_tok == 'WHILE':
            token('WHILE')
            w = While()
            w.cond = expression()
            token('DO')
            w.stmts = stmt_list()
            token('END')
            return w
        else:
            raise ParserError

    def writeint():
        if current_tok == 'WRITEINT':
            token('WRITEINT')
            w = Writeint()
            w.expr = expression()
            return w
        else:
            raise ParserError

    def expression():
        if any(tok in current_tok for tok in ('ident(', 'num(', 'boollit(', 'LP')):
            se = simple_expression()
            e = comp()
            if e:
                e.left = se
                return e
            else:
                return se
        else:
            raise ParserError

    def else_clause():
        if current_tok == 'ELSE':
            token('ELSE')
            return stmt_list()
        elif current_tok == 'END':
            return stmt_list()
        else:
            raise ParserError

    def simple_expression():
        if any(tok in current_tok for tok in ('ident(', 'num(', 'boollit(', 'LP')):
            t = term()
            a = add()
            if a:
                a.left = t
                return a
            else:
                return t
        else:
            raise ParserError

    def comp():
        if 'COMPARE(' in current_tok:
            c = Comp()
            c.op = current_tok.split('(')[1].split(')')[0]
            token('COMPARE(')
            c.right = expression()
            return c
        elif current_tok in ('SC', 'THEN', 'DO'):
            return None
        else:
            raise ParserError

    def term():
        if any(tok in current_tok for tok in ('ident(', 'num(', 'boollit(', 'LP')):
            f = factor()
            m = multi()
            if m:
                m.left = f
                return m
            else:
                return f
        else:
            raise ParserError

    def add():
        if 'ADDITIVE(' in current_tok:
            a = Add()
            a.op = current_tok.split('(')[1].split(')')[0]
            token('ADDITIVE(')
            a.right = simple_expression()
            return a
        elif (current_tok in ('SC', 'THEN', 'DO', 'RP')) or ('COMPARE(' in current_tok):
            return None
        else:
            raise ParserError

    def factor():
        if 'ident(' in current_tok:
            i = Ident()
            i.name = current_tok.split('(')[1].split(')')[0]
            token('ident(')
            return i
        elif 'num(' in current_tok:
            n = Num()
            n.name = current_tok.split('(')[1].split(')')[0]
            token('num(')
            return n
        elif 'boollit(' in current_tok:
            b = Boollit()
            b.name = current_tok.split('(')[1].split(')')[0]
            token('boollit(')
            return b
        elif current_tok == 'LP':
            token('LP')
            se = simple_expression()
            token('RP')
            return se
        else:
            raise ParserError

    def multi():
        if 'MULTIPLICATIVE(' in current_tok:
            m = Multi()
            m.op = current_tok.split('(')[1].split(')')[0]
            token('MULTIPLICATIVE(')
            m.right = term()
            return m
        elif any(tok in current_tok for tok in ('ADDITIVE(', 'COMPARE(', 'SC', 'THEN', 'DO', 'RP')):
            return None
        else:
            raise ParserError

    try:
        ast_tree = program()
        print(ast_tree)
    except ParserError:
        print('PARSER ERROR due to'+current_tok)
        return False
    with open(ast_file, 'w') as f_ast:
        pass
