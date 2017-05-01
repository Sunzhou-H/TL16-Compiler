# -*- coding: utf-8 -*-
import AST


class CodeVisitor(AST.DummyVisitor):
    def __init__(self, symbol_table, f_cfg, f_s):
        self.symbol_table = symbol_table
        self.stream = []
        self.cfg_edges = []
        self.f_cfg = f_cfg
        self.f_s = f_s

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
            self.emit(Instruction('remu', r3, r1, r2))
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
        node.reg = r1

    def visit_Boollit(self, node):
        r1 = Register.next()
        if node.name == 'false':
            self.emit(Instruction('li', r1, 0))
        elif node.name == 'true':
            self.emit(Instruction('li', r1, 1))
        else:
            raise CodeError
        node.reg = r1

    def emit(self, line):
        self.stream.append(line)

    def output_mips(self):
        self.f_s.write('\t.data\nnewline:\t.asciiz "\\n"\n\t.text\n\t.globl main\nmain:\n')
        self.f_s.write('\tli $fp, 0x7ffffffc\n')
        for ins in self.stream:
            self.f_s.write(ins.output()+'\n')

    def output_cfg(self):
        for ins in self.stream:
            print(ins.name, ins.block)
        for edge in self.cfg_edges:
            print(edge)

    def create_cfg(self):
        if isinstance(self.stream[0], Label):
            block_index = 0
        else:
            block_index = 1
        for ins in self.stream:
            if isinstance(ins, Label):
                block_index += 1
                ins.block = block_index
            elif ins.name == 'beqz':
                ins.block = block_index
                block_index += 1
            else:
                ins.block = block_index
        self.cfg_edges = []
        pre_ins = Instruction('temp')
        pre_ins.block = 1
        for ins in self.stream:
            if ins.name == 'j' and ins.args[0]:
                self.cfg_edges.append((ins.block, ins.args[0].block))
            elif ins.name == 'beqz' and ins.args[1]:
                self.cfg_edges.append((ins.block, ins.args[1].block))
            if pre_ins.block != ins.block:
                if pre_ins.name != 'j':
                    self.cfg_edges.append((pre_ins.block, ins.block))
            pre_ins = ins

    def optimization(self):
        self.emit(Instruction('exit'))
        self.create_cfg()


class Register(object):
    register = 0

    def __init__(self, name):
        self.name = name
        self.reg = name
        #   todo reg

    @classmethod
    def next(cls):
        current = Register('r'+str(cls.register))
        cls.register += 1
        return current


class Instruction(object):
    def __init__(self, name, *args):
        self.name = name
        self.args = args
        self.block = -1

    def output(self):
        if self.name == 'readInt':
            ins = '\tli $v0, 5' + '\n\tsyscall\n' + '\tmove '
            if self.args:
                ins = ins + self.args[0].reg + ', $v0'
            else:
                raise CodeError
            return ins
        elif self.name == 'writeInt':
            ins = '\tli $v0, 1'+'\n'+'\tmove $a0, '
            if self.args:
                ins = ins + self.args[0].reg + '\n\tsyscall'
            else:
                raise CodeError
            return ins
        elif self.name == 'exit':
            ins = '\tli $v0, 10\n\tsyscall'
            return ins
        else:
            ins = '\t' + self.name
            for arg in self.args:
                if isinstance(arg, Register):
                    ins = ins + ' ' + str(arg.reg) + ','
                elif isinstance(arg, Label):
                    ins = ins + ' ' + str(arg.name)
                else:
                    ins = ins + ' ' + str(arg)
            if ins.endswith(','):
                ins = ins[:-1]
            return ins


class Label(Instruction):
    label = 0

    def __init__(self, name, *args):
        super().__init__(name, args)

    @classmethod
    def next(cls):
        cls.label += 1
        return Label('L'+str(cls.label))

    def output(self):
        return self.name+':'


class CodeError(Exception):
    pass


class InitError(CodeError):
    pass


def code_generator(ast_tree, symbol_table, cfg_file, s_file):
    with open(cfg_file, 'w') as f_cfg, open(s_file, 'w') as f_s:
        c_visitor = CodeVisitor(symbol_table, f_cfg, f_s)
        try:
            c_visitor.visit(ast_tree)
            c_visitor.optimization()
            c_visitor.output_cfg()
            c_visitor.output_mips()
        except InitError:
            return False
        except CodeError:
            print('Code Generation Error!')
            return False
        else:
            print('Code Generation done!')
            return True
