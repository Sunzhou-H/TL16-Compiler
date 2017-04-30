# -*- coding: utf-8 -*-
class ASTNode(object):
    def __init__(self):
        self.type = ''
        self.type_error = False
        self.reg = ''


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
        self.type_error = False


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


# if(cond, stmt_list, ec)
class If(Stmt):
    def __init__(self):
        super(Stmt, self).__init__()


# while(cond, stmt_list)
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


# Visitor Pattern
class Visitor(object):
    def visit(self, node):
        meth = None
        for cls in node.__class__.__mro__:
            meth_name = 'visit_' + cls.__name__
            meth = getattr(self, meth_name, None)
            if meth:
                break
        if not meth:
            meth = self.generic_visit
        return meth(node)

    @staticmethod
    def generic_visit(node):
        print('generic_visit ' + node.__class__.__name__)


class DummyVisitor(Visitor):
    def visit_Program(self, node):
        if node.decl_list.decls:
            self.visit(node.decl_list)
        if node.stmt_list.stmts:
            self.visit(node.stmt_list)

    def visit_DeclList(self, node):
        for de in node.decls:
            self.visit(de)

    def visit_Decl(self, node):
        return

    def visit_StmtList(self, node):
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_Assignment(self, node):
        self.visit(node.ident)
        self.visit(node.modify)

    def visit_Readint(self, node):
        return

    def visit_If(self, node):
        self.visit(node.cond)
        self.visit(node.stmt_list)
        if node.ec.stmts:
            self.visit(node.ec)

    def visit_While(self, node):
        self.visit(node.cond)
        if node.stmt_list.stmts:
            self.visit(node.stmt_list)

    def visit_Writeint(self, node):
        self.visit(node.expr)

    def visit_Expr(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Ident(self, node):
        return

    def visit_Num(self, node):
        return

    def visit_Boollit(self, node):
        return


class Symbol(object):
    def __init__(self, name, s_type):
        self.name = name
        self.type = s_type
        self.reg = ''
