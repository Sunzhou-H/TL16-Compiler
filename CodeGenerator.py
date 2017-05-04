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
        elif node.op == 'mod':
            self.emit(Instruction('remu', r3, r1, r2))
        else:
            print(node.op)
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
            if not isinstance(ins, Label):
                self.f_s.write('\t')
            self.f_s.write(ins.output()+'\n')

    def output_cfg(self):
        self.f_cfg.write('digraph graphviz {\n\tnode [shape = none];\n\tedge [tailport = s];\n')
        self.f_cfg.write('\tentry\n')
        self.f_cfg.write('\tsubgraph cluster {\n')
        self.f_cfg.write('\tcolor="/x11/white"\n')
        for b_index in range(1, self.stream[-1].block+1):
            self.f_cfg.write('\tn' + str(b_index) + ' [label=<<table border="0">')
            self.f_cfg.write('<tr><td border="1" colspan="4">B'+str(b_index)+'</td></tr>')
            for ins in self.stream:
                if ins.block == b_index:
                    for tr in ins.output().split('\n\t'):
                        self.f_cfg.write('<tr>')
                        td4 = tr.split()
                        if len(td4) < 4:
                            for i in range(4-len(td4)):
                                td4.append('')
                        for td in td4:
                            self.f_cfg.write('<td align="left">')
                            self.f_cfg.write(td)
                            self.f_cfg.write('</td>')
                        self.f_cfg.write('</tr>')
            self.f_cfg.write('</table>>,fillcolor="/x11/white",shape=box]\n')
        for edge in self.cfg_edges:
            self.f_cfg.write('\tn'+str(edge[0])+' -> n'+str(edge[1])+'\n')
        self.f_cfg.write('\t}\n')
        self.f_cfg.write('\tentry -> n'+str(self.stream[0].block)+'\n')
        self.f_cfg.write('\tn' + str(self.stream[-1].block) + ' -> exit\n')
        self.f_cfg.write('}')

    def create_cfg_graphviz(self):
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

    def create_cfg_live(self):
        for idx, ins in enumerate(self.stream):
            if ins.name == 'j' and ins.args[0]:
                ins.pred.add(idx-1)
                ins.succ.add(self.stream.index(ins.args[0]))
                self.stream[self.stream.index(ins.args[0])].pred.add(idx)
            elif ins.name == 'beqz' and ins.args[1]:
                ins.pred.add(idx - 1)
                ins.succ.add(idx + 1)
                ins.succ.add(self.stream.index(ins.args[1]))
                self.stream[self.stream.index(ins.args[1])].pred.add(idx)
            else:
                if self.stream[idx-1].name != 'j':
                    ins.pred.add(idx-1)
                ins.succ.add(idx+1)
        self.stream[0].pred.discard(-1)
        self.stream[-1].succ.discard(len(self.stream))

    def liveness(self):
        self.create_cfg_live()
        while True:
            equal_flag = True
            for ins in reversed(self.stream):
                ins.live_in_save = ins.live_in
                ins.live_out_save = ins.live_out
                for i in ins.succ:
                    ins.live_out = ins.live_out | self.stream[i].live_in
                ins.live_in = ins.use | (ins.live_out - ins.define)
                if (ins.live_in_save == ins.live_in) and (ins.live_out_save == ins.live_out):
                    equal_flag = equal_flag and True
                else:
                    equal_flag = equal_flag and False
            if equal_flag:
                break

    def coloring(self, reg_num):
        self.liveness()
        for ins in self.stream:
            if ins.live_in:
                for i in ins.live_in:
                    i.adj = i.adj | (ins.live_in - {i})
        graph = {}
        for reg in Register.reg_list:
            graph[reg] = set(reg.adj)
        stack = []
        while len(graph):
            if all(len(graph.get(node)) >= reg_num for node in graph):
                node = graph.popitem()[0]
                stack.append(node)
                for n in graph:
                    graph.get(n).discard(node)
            for node in graph:
                if len(graph.get(node)) <= (reg_num-1):
                    stack.append(node)
                    graph.pop(node)
                    for n in graph:
                        graph.get(n).discard(node)
                    break
        while len(stack):
            node = stack.pop()
            colors_list = []
            for reg in range(reg_num):
                colors_list.append('$t'+str(reg))
            for register in node.adj:
                if register.reg in colors_list:
                    colors_list.remove(register.reg)
            if len(colors_list) == 0:
                node.reg = str(-4*int(node.name[1:]))+'($fp)'
            else:
                node.reg = colors_list.pop(0)

    def optimization(self):
        self.emit(Instruction('exit'))
        self.coloring(7)
        self.create_cfg_graphviz()


class Register(object):
    register = 0
    reg_list = []

    def __init__(self, name):
        self.name = name
        self.reg = 'NULL'
        self.adj = set()

    @classmethod
    def next(cls):
        cls.register += 1
        reg = Register('r'+str(cls.register))
        cls.reg_list.append(reg)
        return reg


class Instruction(object):
    def __init__(self, name, *args):
        self.name = name
        self.args = args
        self.block = -1
        self.live_in = set()
        self.live_out = set()
        self.use = set()
        self.define = set()
        self.pred = set()
        self.succ = set()
        if len(args) == 3:
            self.define.add(args[0])
            self.use.add(args[1])
            self.use.add(args[2])
        elif name == 'li':
            self.define.add(args[0])
        elif name == 'move':
            self.define.add(args[0])
            self.use.add(args[1])
        elif name == 'readInt':
            self.define.add(args[0])
        elif name == 'beqz':
            self.use.add(args[0])
        elif name == 'writeInt':
            self.use.add(args[0])
        else:
            return

    def output(self):
        temp_reg = ['$t7', '$t8', '$t9']
        if self.name == 'readInt':
            ins = 'li $v0, 5' + '\n\tsyscall\n' + '\tmove '
            if self.args:
                if self.args[0].reg.startswith('-'):
                    ins = ins + temp_reg[0] + ', $v0\n\t'+'sw '+temp_reg[0]+', '+self.args[0].reg
                else:
                    ins = ins + self.args[0].reg + ', $v0'
            else:
                raise CodeError
            return ins
        elif self.name == 'writeInt':
            if self.args:
                if self.args[0].reg.startswith('-'):
                    ins = 'li $v0, 1\n\tlw '+temp_reg[0]+', '+self.args[0].reg+'\n\tmove $a0, '+temp_reg[0]+'\n\t' \
                                                                                                            'syscall'
                else:
                    ins = 'li $v0, 1\n\tmove $a0, '+self.args[0].reg + '\n\tsyscall'
            else:
                raise CodeError
            return ins
        elif self.name == 'exit':
            ins = 'li $v0, 10\n\tsyscall'
            return ins
        elif self.name == 'li' and self.args[0].reg.startswith('-'):
            ins = 'li '+temp_reg[0]+', '+str(self.args[1])+'\n\tsw '+temp_reg[0]+', '+self.args[0].reg
            return ins
        elif self.name == 'move' and (self.args[0].reg.startswith('-') or self.args[1].reg.startswith('-')):
            r1 = self.args[0].reg
            r2 = self.args[1].reg
            ins_p = ''
            ins_f = ''
            if r1.startswith('-'):
                ins_f += '\n\tsw '+temp_reg[0]+', '+r1
                r1 = temp_reg[0]
            if r2.startswith('-'):
                ins_p += 'lw '+temp_reg[1]+', '+r2+'\n\t'
                r2 = temp_reg[1]
            ins = 'move '+r1+', '+r2
            return ins_p+ins+ins_f
        elif self.name == 'beqz' and self.args[0].reg.startswith('-'):
            ins = 'lw '+temp_reg[0]+', '+self.args[0].reg+'\n\t'
            ins = ins + 'beqz '+temp_reg[0]+', '+self.args[1].name
            return ins
        elif len(self.args) == 3 and (self.args[0].reg.startswith('-')
                                      or self.args[1].reg.startswith('-')
                                      or self.args[2].reg.startswith('-')):
            r3 = self.args[0].reg
            r1 = self.args[1].reg
            r2 = self.args[2].reg
            ins_p = ''
            ins_f = ''
            if r3.startswith('-'):
                ins_f += '\n\tsw ' + temp_reg[2] + ', ' + r3
                r3 = temp_reg[2]
            if r1.startswith('-'):
                ins_p += 'lw ' + temp_reg[0] + ', ' + r1 + '\n\t'
                r1 = temp_reg[0]
            if r2.startswith('-'):
                ins_p += 'lw '+temp_reg[1]+', '+r2+'\n\t'
                r2 = temp_reg[1]
            ins = self.name + ' '+r3+', '+r1+', '+r2
            return ins_p + ins + ins_f
        else:
            ins = self.name
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
