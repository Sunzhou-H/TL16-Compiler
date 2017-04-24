# -*- coding: utf-8 -*-
import AST
current_tok = ''
source_toks = iter([])


# Error
class ParserError(Exception):
    pass


# Build AST
def token(tok):
    global current_tok
    if tok in current_tok:
        # print(current_tok)
        try:
            current_tok = next(source_toks)
        except StopIteration:
            pass
        return True
    else:
        raise ParserError


def program():
    if current_tok == 'PROGRAM':
        token('PROGRAM')
        p = AST.Program()
        p.decl_list = decl_list()
        token('BEGIN')
        p.stmt_list = stmt_list()
        token('END')
        print('Parser done!')
        return p
    else:
        raise ParserError


def decl_list():
    if current_tok == 'VAR':
        d = AST.DeclList()
        d.decls = []
        d.decls.append(decl())
        token('SC')
        d.decls += decl_list().decls
        return d
    elif current_tok == 'BEGIN':
        d = AST.DeclList()
        d.decls = []
        return d
    else:
        raise ParserError


def decl():
    token('VAR')
    if 'ident(' in current_tok:
        d = AST.Decl()
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
        return 'int'
    elif current_tok == 'BOOL':
        token('BOOL')
        return 'bool'
    else:
        raise ParserError


def stmt_list():
    if ('ident(' in current_tok) or (current_tok in ('IF', 'WHILE', 'WRITEINT')):
        s = AST.StmtList()
        s.stmts = []
        s.stmts.append(statement())
        token('SC')
        s.stmts += stmt_list().stmts
        return s
    elif current_tok in ('END', 'ELSE'):
        s = AST.StmtList()
        s.stmts = []
        return s
    else:
        raise ParserError


def statement():
    if 'ident(' in current_tok:
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
    if 'ident(' in current_tok:
        a = AST.Assignment()
        i = AST.Ident()
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
        r = AST.Readint()
        token('READINT')
        return r
    else:
        raise ParserError


def if_statement():
    if current_tok == 'IF':
        token('IF')
        i = AST.If()
        i.cond = expression()
        token('THEN')
        i.stmt_list = stmt_list()
        i.ec = else_clause()
        token('END')
        return i
    else:
        raise ParserError


def while_statement():
    if current_tok == 'WHILE':
        token('WHILE')
        w = AST.While()
        w.cond = expression()
        token('DO')
        w.stmt_list = stmt_list()
        token('END')
        return w
    else:
        raise ParserError


def writeint():
    if current_tok == 'WRITEINT':
        token('WRITEINT')
        w = AST.Writeint()
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
        c = AST.Comp()
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
        a = AST.Add()
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
        i = AST.Ident()
        i.name = current_tok.split('(')[1].split(')')[0]
        token('ident(')
        return i
    elif 'num(' in current_tok:
        n = AST.Num()
        n.name = current_tok.split('(')[1].split(')')[0]
        token('num(')
        return n
    elif 'boollit(' in current_tok:
        b = AST.Boollit()
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
        m = AST.Multi()
        m.op = current_tok.split('(')[1].split(')')[0]
        token('MULTIPLICATIVE(')
        m.right = term()
        return m
    elif any(tok in current_tok for tok in ('ADDITIVE(', 'COMPARE(', 'SC', 'THEN', 'DO', 'RP')):
        return None
    else:
        raise ParserError


class SymbolVisitor(AST.DummyVisitor):
    def __init__(self):
        self.symbol_table = {}
        self.type_error = False

    def is_type_error(self):
        return self.type_error

    def get_table(self):
        return self.symbol_table

    def visit_Decl(self, node):
        if node.ident in self.symbol_table:
            node.type_error = True
            self.type_error = True
            print("TYPE ERROR due to identifier '" + node.ident + "' has been defined more than once")
        else:
            self.symbol_table[node.ident] = AST.Symbol(node.ident, node.type)


# Type Check Visitor
class TypeCheckVisitor(AST.DummyVisitor):
    def __init__(self, symbol_table, f_ast):
        self.symbol_table = symbol_table
        self.f_ast = f_ast
        self.node_num = 1
        self.type_error = False

    def is_type_error(self):
        return self.type_error

    def visit_Program(self, node):
        self.f_ast.write('digraph TL16Ast {'+'\n')
        self.f_ast.write('  ordering=out;'+'\n')
        self.f_ast.write('  node [shape = box, style = filled, fillcolor="white"];'+'\n')
        current_num = self.node_num
        self.f_ast.write('  n'+str(current_num)+' [label="program",shape=box]'+'\n')
        if node.decl_list.decls:
            self.node_num += 1
            self.f_ast.write('  n' + str(current_num) + ' -> '+'n'+str(self.node_num)+'\n')
            self.visit(node.decl_list)
        if node.stmt_list.stmts:
            self.node_num += 1
            self.f_ast.write('  n' + str(current_num) + ' -> ' + 'n' + str(self.node_num) + '\n')
            self.visit(node.stmt_list)
        self.f_ast.write('}')

    def visit_DeclList(self, node):
        current_num = self.node_num
        self.f_ast.write('  n'+str(current_num)+' [label="decl list",shape=box]'+'\n')
        for de in node.decls:
            self.node_num += 1
            self.f_ast.write('  n' + str(current_num) + ' -> ' + 'n' + str(self.node_num) + '\n')
            self.visit(de)

    def visit_Decl(self, node):
        current_num = self.node_num
        self.f_ast.write('  n' + str(current_num) + ' [label="decl:\''+node.ident+'\':'+node.type+'",shape=box')
        if node.type_error:
            self.f_ast.write(',fillcolor="/pastel13/1"')
        self.f_ast.write(']' + '\n')

    def visit_StmtList(self, node):
        current_num = self.node_num
        self.f_ast.write('  n' + str(current_num) + ' [label="stmt list",shape=box]' + '\n')
        for stmt in node.stmts:
            self.node_num += 1
            self.f_ast.write('  n' + str(current_num) + ' -> ' + 'n' + str(self.node_num) + '\n')
            self.visit(stmt)

    def visit_Assignment(self, node):
        current_num = self.node_num
        self.node_num += 1
        self.f_ast.write('  n' + str(current_num) + ' -> ' + 'n' + str(self.node_num) + '\n')
        l = self.visit(node.ident)
        self.node_num += 1
        self.f_ast.write('  n' + str(current_num) + ' -> ' + 'n' + str(self.node_num) + '\n')
        r = self.visit(node.modify)
        if not (l and r):
            self.f_ast.write('  n' + str(current_num) + ' [label=":=",shape=box]'+'\n')
            return False
        elif l != r:
            node.type_error = True
            self.type_error = True
            print("TYPE ERROR due to '", l, ':=', r, "'")
        self.f_ast.write('  n' + str(current_num) + ' [label=":=",shape=box')
        if node.type_error:
            self.f_ast.write(',fillcolor="/pastel13/1"')
        self.f_ast.write(']' + '\n')

    def visit_Readint(self, node):
        self.f_ast.write('  n' + str(self.node_num) + ' [label="readInt:int",shape=box]' + '\n')
        node.type = 'int'
        return node.type

    def visit_If(self, node):
        current_num = self.node_num
        self.f_ast.write('  n' + str(current_num) + ' [label="if",shape=box]' + '\n')
        self.node_num += 1
        self.f_ast.write('  n' + str(current_num) + ' -> ' + 'n' + str(self.node_num) + '\n')
        self.visit(node.cond)
        self.node_num += 1
        self.f_ast.write('  n' + str(current_num) + ' -> ' + 'n' + str(self.node_num) + '\n')
        self.visit(node.stmt_list)
        if node.ec.stmts:
            self.node_num += 1
            self.f_ast.write('  n' + str(current_num) + ' -> ' + 'n' + str(self.node_num) + '\n')
            self.visit(node.ec)

    def visit_While(self, node):
        current_num = self.node_num
        self.f_ast.write('  n' + str(current_num) + ' [label="while",shape=box]' + '\n')
        self.node_num += 1
        self.f_ast.write('  n' + str(current_num) + ' -> ' + 'n' + str(self.node_num) + '\n')
        self.visit(node.cond)
        if node.stmt_list.stmts:
            self.node_num += 1
            self.f_ast.write('  n' + str(current_num) + ' -> ' + 'n' + str(self.node_num) + '\n')
            self.visit(node.stmt_list)

    def visit_Writeint(self, node):
        current_num = self.node_num
        self.node_num += 1
        self.f_ast.write('  n' + str(current_num) + ' -> ' + 'n' + str(self.node_num) + '\n')
        out = self.visit(node.expr)
        if not out:
            pass
        elif out != 'int':
            node.type_error = True
            self.type_error = True
        self.f_ast.write('  n' + str(current_num) + ' [label="writeInt",shape=box')
        if node.type_error:
            self.f_ast.write(',fillcolor="/pastel13/1"')
        self.f_ast.write(']' + '\n')

    def visit_Expr(self, node):
        current_num = self.node_num
        self.node_num += 1
        self.f_ast.write('  n' + str(current_num) + ' -> ' + 'n' + str(self.node_num) + '\n')
        l = self.visit(node.left)
        self.node_num += 1
        self.f_ast.write('  n' + str(current_num) + ' -> ' + 'n' + str(self.node_num) + '\n')
        r = self.visit(node.right)
        self.f_ast.write('  n' + str(current_num) + ' [label="'+node.op)
        if not (l and r):
            self.f_ast.write('",shape=box]' + '\n')
            return False
        elif 'bool' in (r, l):
            node.type_error = True
            self.type_error = True
            print("TYPE ERROR due to '"+node.op+"'")
            self.f_ast.write('",shape=box,fillcolor="/pastel13/1"]' + '\n')
            return False
        elif node.__class__.__name__ == 'Comp':
            node.type = 'bool'
            self.f_ast.write(':bool",shape=box]' + '\n')
            return node.type
        else:
            node.type = 'int'
            self.f_ast.write(':int",shape=box]' + '\n')
            return node.type

    def visit_Ident(self, node):
        self.f_ast.write('  n' + str(self.node_num) + ' [label="' + node.name)
        s = self.symbol_table.get(node.name)
        if s:
            node.type = s.type
            self.f_ast.write(':' + node.type + '",shape=box]')
            return s.type
        else:
            node.type_error = True
            self.type_error = True
            print('TYPE ERROR due to undefined identifier (' + node.name + ')')
            self.f_ast.write('",shape=box,fillcolor="/pastel13/1"]'+'\n')
            return False

    def visit_Num(self, node):
        node.type = 'int'
        self.f_ast.write('  n' + str(self.node_num) + ' [label="' + node.name+':'+node.type+'",shape=box]')
        return node.type

    def visit_Boollit(self, node):
        node.type = 'bool'
        self.f_ast.write('  n' + str(self.node_num) + ' [label="' + node.name + ':' + node.type + '",shape=box]')
        return node.type


def parser(tok_file, ast_file):
    with open(tok_file, 'r') as f_tok:
        global source_toks
        global current_tok
        try:
            source_toks = iter(f_tok.read().split())
            current_tok = next(source_toks)
        except StopIteration:
            print('Empty Program!')
            return False

    try:
        ast_tree = program()
    except ParserError:
        print('PARSER ERROR due to '+current_tok)
        return False

    with open(ast_file, 'w') as f_ast:
        # Symbol table
        s_visitor = SymbolVisitor()
        s_visitor.visit(ast_tree)
        symbol_table = s_visitor.get_table()
        # Type check
        t_visitor = TypeCheckVisitor(symbol_table, f_ast)
        t_visitor.visit(ast_tree)
        if t_visitor.is_type_error() or s_visitor.is_type_error():
            return False
        else:
            return ast_tree
