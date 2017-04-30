# -*- coding: utf-8 -*-
import AST


class CodeVisitor(AST.DummyVisitor):
    def __init__(self, symbol_table, f_cfg):
        self.symbol_table = symbol_table
        self.f_cfg = f_cfg
        self.stream = []

    def visit_Program(self, node):
        if node.decl_list.decls:
            self.visit(node.decl_list)
        if node.stmt_list.stmts:
            self.visit(node.stmt_list)

    def visit_DeclList(self, node):
        for de in node.decls:
            self.visit(de)

    def visit_Decl(self, node):
        r1 = Register.next()
        self.symbol_table[node.ident].reg = r1
        self.emit(Instruction('li', r1, 0))

    def visit_StmtList(self, node):
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_Assignment(self, node):
        self.visit(node.ident)
        if node.ident.reg == '':
            r1 = Register.next()
            node.ident.reg = r1
        else:
            r1 = node.ident.reg
        self.visit(node.modify)
        r2 = node.modify.reg
        self.emit(Instruction('move', r1, r2))

    def visit_Readint(self, node):
        r1 = Register.next()
        # todo MIPS doesn't have readInt operator
        self.emit(Instruction('readInt', r1))
        node.reg = r1

    def visit_If(self, node):
        self.visit(node.cond)
        r1 = node.cond.reg
        else_label = Label.next()
        end_label = Label.next()
        self.emit(Instruction('beqz', r1, else_label))
        self.visit(node.stmt_list)
        self.emit(Instruction('j', end_label))
        self.emit(else_label)
        if node.ec.stmts:
            self.visit(node.ec)
        self.emit(end_label)

    def visit_While(self, node):
        start_label = Label.next()
        self.emit(start_label)
        self.visit(node.cond)
        r1 = node.cond.reg
        end_label = Label.next()
        self.emit(Instruction('beqz', r1, end_label))
        if node.stmt_list.stmts:
            self.visit(node.stmt_list)
        self.emit(Instruction('j', start_label))
        self.emit(end_label)

    def visit_Writeint(self, node):
        self.visit(node.expr)
        r1 = node.expr.reg
        # todo MIPS doesn't have writeInt operator
        self.emit(Instruction('writeInt', r1))

    def visit_Comp(self, node):
        self.visit(node.left)
        r1 = node.left.reg
        self.visit(node.right)
        r2 = node.right.reg
        r3 = Register.next()
        if node.op == '=':
            self.emit(Instruction('seq', r3, r1, r2))
        elif node.op == '!=':
            self.emit(Instruction('sne', r3, r1, r2))
        elif node.op == '<':
            self.emit(Instruction('slt', r3, r1, r2))
        elif node.op == '>':
            self.emit(Instruction('sgt', r3, r1, r2))
        elif node.op == '<=':
            self.emit(Instruction('sle', r3, r1, r2))
        elif node.op == '>=':
            self.emit(Instruction('sge', r3, r1, r2))
        else:
            raise CodeError
        node.reg = r3

    def visit_Add(self, node):
        self.visit(node.left)
        r1 = node.left.reg
        self.visit(node.right)
        r2 = node.right.reg
        r3 = Register.next()
        if node.op == '+':
            self.emit(Instruction('addu', r3, r1, r2))
        elif node.op == '-':
            self.emit(Instruction('subu', r3, r1, r2))
        else:
            raise CodeError
        node.reg = r3

    def visit_Multi(self, node):
        self.visit(node.left)
        r1 = node.left.reg
        self.visit(node.right)
        r2 = node.right.reg
        r3 = Register.next()
        if node.op == '*':
            self.emit(Instruction('mul', r3, r1, r2))
        elif node.op == 'div':
            self.emit(Instruction('div', r3, r1, r2))
        elif node.op == 'mod"':
            # todo MIPS doesn't have mod operator
            self.emit(Instruction('mod', r3, r1, r2))
        else:
            raise CodeError
        node.reg = r3

    def visit_Ident(self, node):
        r1 = self.symbol_table[node.name].reg
        if r1 != '':
            node.reg = r1
        else:
            print("Code Error due to variable '"+node.name+"' isn't initialized.")
            raise InitError

    def visit_Num(self, node):
        r1 = Register.next()
        self.emit(Instruction('li', r1, int(node.name)))

    def visit_Boollit(self, node):
        r1 = Register.next()
        if node.name == 'false':
            self.emit(Instruction('li', r1, 0))
        elif node.name == 'true':
            self.emit(Instruction('li', r1, 1))
        else:
            raise CodeError

    def emit(self, line):
        self.stream.append(line)


class Register(object):
    register = 0

    def __init__(self, name):
        self.name = name

    @classmethod
    def next(cls):
        current = Register('r'+str(cls.register))
        cls.register += 1
        return current


class Label(object):
    label = 0

    def __init__(self, name):
        self.name = name

    @classmethod
    def next(cls):
        cls.label += 1
        return Label('L'+str(cls.label)+':')


class Instruction(object):
    def __init__(self, name, *args):
        self.name = name
        self.args = args


class CodeError(Exception):
    pass


class InitError(CodeError):
    pass


def code_generator(ast_tree, symbol_table, cfg_file):
    with open(cfg_file, 'w') as f_cfg:
        c_visitor = CodeVisitor(symbol_table, f_cfg)
        try:
            c_visitor.visit(ast_tree)
            print(1)
        except InitError:
            return False
        except CodeError:
            print('Code Generation Error!')
            return False
        else:
            print('Code Generation done!')
            return True
