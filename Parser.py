# -*- coding: utf-8 -*-
current_tok = ''


class ASTNode(object):
    def __init__(self, node_type):
        self.node_type = node_type
        # Python is dynamic language, so we can use the single class ASTNode and add necessary information to class
        # node_type:
        # program(decl_list, stmt_list)
        # decl_list(decls)
        # decl(ident, type)
        # stmt_list(stmts)
        # assignment(ident, modify)
        # readint
        # if(cond, stmts, ec)
        # while(cond, stmts)
        # writeint(expr)
        # comp(left, op, right)
        # add(left, op, right)
        # multi(left, op, right)
        # ident(ident)
        # num(num)
        # boollit(boollit)


class ParserError(Exception):
    pass


def parser(tok_file, ast_file):
    global current_tok
    with open(tok_file, 'r') as f_tok, open(ast_file, 'w') as f_ast:
        try:
            source_toks = iter(f_tok.read().split())
            # todo empty file check
            current_tok = next(source_toks)

            def token(tok):
                global current_tok
                if tok in current_tok:
                    print(current_tok)
                    current_tok = next(source_toks)
                    return True
                else:
                    raise ParserError

            def program():
                if current_tok == 'PROGRAM':
                    token('PROGRAM')
                    p = ASTNode('program')
                    p.decl_list = decl_list()
                    token('BEGIN')
                    p.stmt_list = stmt_list()
                    token('END')
                    return p
                else:
                    raise ParserError

            def decl_list():
                if current_tok == 'VAR':
                    d = ASTNode('decl_list')
                    d.decls = []
                    d.decls.append(decl())
                    token('SC')
                    d.decls += decl_list().decls
                    return d
                elif current_tok == 'BEGIN':
                    d = ASTNode('decl_list')
                    d.decls = []
                    return d
                else:
                    raise ParserError

            def decl():
                token('VAR')
                if 'ident(' in current_tok:
                    d = ASTNode('decl')
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
                    s = ASTNode('stmt_list')
                    s.stmts = []
                    s.stmts.append(statement())
                    token('SC')
                    s.stmts += stmt_list().stmts
                    return s
                elif current_tok in ('END', 'ELSE'):
                    s = ASTNode('stmt_list')
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
                    a = ASTNode('assignment')
                    i = ASTNode('ident')
                    i.ident = current_tok.split('(')[1].split(')')[0]
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
                    r = ASTNode('readint')
                    token('READINT')
                    return r
                else:
                    raise ParserError

            def if_statement():
                if current_tok == 'IF':
                    token('IF')
                    i = ASTNode('if')
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
                    w = ASTNode('while')
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
                    w = ASTNode('writeint')
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
                    c = ASTNode('comp')
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
                    a = ASTNode('add')
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
                    i = ASTNode('ident')
                    i.ident = current_tok.split('(')[1].split(')')[0]
                    token('ident(')
                    return i
                elif 'num(' in current_tok:
                    n = ASTNode('num')
                    n.num = current_tok.split('(')[1].split(')')[0]
                    token('num(')
                    return n
                elif 'boollit(' in current_tok:
                    b = ASTNode('boollit')
                    b.boollit = current_tok.split('(')[1].split(')')[0]
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
                    m = ASTNode('multi')
                    m.op = current_tok.split('(')[1].split(')')[0]
                    token('MULTIPLICATIVE(')
                    m.right = term()
                    return m
                elif any(tok in current_tok for tok in ('ADDITIVE(', 'COMPARE(', 'SC', 'THEN', 'DO', 'RP')):
                    return None
                else:
                    raise ParserError

            program()
        except StopIteration:
            print('Tokens end!')
        except ParserError:
            print('PARSER ERROR due to'+current_tok)
