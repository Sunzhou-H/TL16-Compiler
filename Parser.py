# -*- coding: utf-8 -*-
current_tok = ''


class ASTNode(object):
    def __init__(self, node_type):
        self.node_type = node_type  # program decl_list decl

# class Program(ASTNode):
#     __slots__ = ('decls', 'stmt_list')
#
#
# class DeclList(ASTNode):
#     __slots__ = 'decl'
#
#
# class Decl(ASTNode):
#     __slots__ = ('ident', 'type_tl')


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

            def epsilon():
                return True

            def program():
                if current_tok == 'PROGRAM':
                    token('PROGRAM')
                    p = ASTNode('program')
                    p.decl_list = decl_list()
                    token('BEGIN')
                    p.stmt_list = statement_sequence()
                    token('END')
                    return p
                else:
                    raise ParserError

            def decl_list():
                if current_tok == 'VAR':
                    d = ASTNode('decl_list')
                    d.decls = []
                    d.decls.append(decl())
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
                token('SC')
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

            def statement_sequence():
                if ('ident('in current_tok) or (current_tok in ('IF', 'WHILE', 'WRITEINT')):
                    return statement() and token('SC') and statement_sequence()
                elif current_tok in ('END', 'ELSE'):
                    return epsilon()
                else:
                    return False

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
                    return False

            def assignment():
                if 'ident('in current_tok:
                    return token('ident(') and token('ASGN') and assignment_modified()
                else:
                    return False

            def if_statement():
                if current_tok == 'IF':
                    return token('IF') and expression() and token('THEN') and statement_sequence() and else_clause() \
                           and token('END')
                else:
                    return False

            def while_statement():
                if current_tok == 'WHILE':
                    return token('WHILE') and expression() and token('DO') and statement_sequence() and token('END')
                else:
                    return False

            def writeint():
                if current_tok == 'WRITEINT':
                    return token('WRITEINT') and expression()
                else:
                    return False

            def assignment_modified():
                if any(tok in current_tok for tok in ('ident(', 'num(', 'boollit(', 'LP')):
                    return expression()
                elif current_tok == 'READINT':
                    return token('READINT')
                else:
                    return False

            def expression():
                if any(tok in current_tok for tok in ('ident(', 'num(', 'boollit(', 'LP')):
                    return simple_expression() and comp()
                else:
                    return False

            def else_clause():
                if current_tok == 'ELSE':
                    return token('ELSE') and statement_sequence()
                elif current_tok == 'END':
                    return epsilon()
                else:
                    return False

            def simple_expression():
                if any(tok in current_tok for tok in ('ident(', 'num(', 'boollit(', 'LP')):
                    return term() and add()
                else:
                    return False

            def comp():
                if 'COMPARE(' in current_tok:
                    return token('COMPARE(') and expression()
                elif current_tok in ('SC', 'THEN', 'DO'):
                    return epsilon()
                else:
                    return False

            def term():
                if any(tok in current_tok for tok in ('ident(', 'num(', 'boollit(', 'LP')):
                    return factor() and multi()
                else:
                    return False

            def add():
                if 'ADDITIVE(' in current_tok:
                    return token('ADDITIVE(') and simple_expression()
                elif (current_tok in ('SC', 'THEN', 'DO', 'RP')) or ('COMPARE(' in current_tok):
                    return epsilon()
                else:
                    return False

            def factor():
                if 'ident(' in current_tok:
                    return token('ident(')
                elif 'num(' in current_tok:
                    return token('num(')
                elif 'boollit(' in current_tok:
                    return token('boollit(')
                elif current_tok == 'LP':
                    return token('LP') and simple_expression() and token('RP')
                else:
                    return False

            def multi():
                if 'MULTIPLICATIVE(' in current_tok:
                    return token('MULTIPLICATIVE(') and term()
                elif any(tok in current_tok for tok in ('ADDITIVE(', 'COMPARE(', 'SC', 'THEN', 'DO', 'RP')):
                    return epsilon()
                else:
                    return False

            program()
        except StopIteration:
            print('Tokens end!')
        except ParserError:
            print('PARSER ERROR due to'+current_tok)
