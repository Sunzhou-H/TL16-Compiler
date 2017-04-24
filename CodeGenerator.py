# -*- coding: utf-8 -*-
import AST


class CodeVisitor(AST.DummyVisitor):
    def __init__(self, symbol_table, f_cfg):
        self.symbol_table = symbol_table
        self.f_cfg = f_cfg
        self.Register = Register()
        self.Label = Label()

    def visit_Program(self, node):
        if node.decl_list.decls:
            self.visit(node.decl_list)
        if node.stmt_list.stmts:
            self.visit(node.stmt_list)

    def visit_DeclList(self, node):
        for de in node.decls:
            self.visit(de)

    def visit_Decl(self, node):
        self.symbol_table[node.ident].reg = 'r_'+'node.ident'


class Register(object):
    def __init__(self):
        self.register = 0

    def next(self):
        self.register += 1
        return 'r'+str(self.register)


class Label(object):
    def __init__(self):
        self.label = 0

    def next(self):
        self.label += 1
        return 'B'+str(self.label)


def code_generator(ast_tree, symbol_table, cfg_file):
    with open(cfg_file, 'w') as f_cfg:
        c_visitor = CodeVisitor(symbol_table, f_cfg)
        c_visitor.visit(ast_tree)
