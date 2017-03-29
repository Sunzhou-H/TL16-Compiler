# -*- coding: utf-8 -*-
def parser(tok_file, ast_file):
    global current_tok
    with open(tok_file, 'r') as f_tok, open(ast_file, 'w') as f_ast:
        try:
            source_toks = iter(f_tok.read().split())
            # todo empty file check
            current_tok = next(source_toks)

            def token(tok):
                global current_tok
                if tok == current_tok:
                    print(current_tok)
                    current_tok = next(source_toks)
                    return True
                else:
                    return False

            def epsilon():
                return True
            # match ident() to ident

            def program():
                global current_tok
                if current_tok == 'PROGRAM':
                    return token('PROGRAM') and declaration() and token('BEGIN') and statementSequence() and token('END')
                else:
                    return False

            def declaration():
                global current_tok
                if current_tok == 'VAR':
                    return token('VAR') and token('ident') and token('AS') and type() and token('SC') and declaration()
                elif current_tok == 'BEGIN':
                    return epsilon()
                else:
                    return False

            def statementSequence():
                global current_tok
                if current_tok == 'ident':
                    return statement() and token('SC') and statementSequence()
                elif current_tok == 'IF':
                    return statement() and token('SC') and statementSequence()
                elif current_tok == 'WHILE':
                    return statement() and token('SC') and statementSequence()
                elif current_tok == 'WRITEINT':
                    return statement() and token('SC') and statementSequence()
                elif current_tok == 'END':
                    return epsilon()
                elif current_tok == 'ELSE':
                    return epsilon()
                else:
                    return False

            def  statement():
                global current_tok
                if current_tok == 'ident':
                    return assignment()
                elif current_tok == 'IF':
                    return ifStatement()
                elif current_tok == 'WHILE':
                    return whileStatement()
                elif current_tok == 'WRITEINT':
                    return writeInt()
                else:
                    return False
                #  handle SC

            def type():
                global current_tok
                if current_tok == 'INT':
                    return token('INT')
                elif current_tok == 'BOOL':
                    return token('BOOL')
                else:
                    return False

            def assignment():
                global current_tok
                if current_tok == 'ident':
                    return token('ident') and token('ASGN') and assignmentModified()
                else:
                    return False

            def ifStatement():
                global current_tok
                if current_tok == 'IF':
                    return token('IF') and expression() and token('THEN') and statementSequence() and elseClause() and token('END')
                else:
                    return False

            def whileStatement():
                global current_tok
                if current_tok == 'WHILE':
                    return token('WHILE') and expression() and token('DO') and statementSequence() and token('END')
                else:
                    return False

            def writeInt():
                global current_tok
                if current_tok == 'WRITEINT':
                    return token('WRITEINT') and expression()
                else:
                    return False

            def assignmentModified():
                global current_tok
                if current_tok == 'ident':
                    return expression()
                elif current_tok == 'READINT':
                    return token('READINT')
                elif current_tok == 'num':
                    return expression()
                elif current_tok == 'boollit':
                    return expression()
                elif current_tok == 'LP':
                    return expression()
                else:
                    return False

            def expression():
                global current_tok
                if current_tok == 'ident':
                    return simpleExpression() and comp()
                elif current_tok == 'num':
                    return simpleExpression() and comp()
                elif current_tok == 'boollit':
                    return simpleExpression() and comp()
                elif current_tok == 'LP':
                    return simpleExpression() and comp()
                else:
                    return False

            def elseClause():
                global current_tok
                if current_tok == 'ELSE':
                    return token('ELSE') and statementSequence()
                elif current_tok == 'END':
                    return epsilon()
                else:
                    return False

            def simpleExpression():
                global current_tok
                if current_tok == 'ident':
                    return term() and add()
                elif current_tok == 'num':
                    return term() and add()
                elif current_tok == 'boollit':
                    return term() and add()
                elif current_tok == 'LP':
                    return term() and add()
                else:
                    return False

            def comp():
                global current_tok
                if current_tok == 'COMPARE':
                    return token('COMPARE') and expression()
                elif current_tok == 'SC':
                    return epsilon()
                elif current_tok == 'THEN':
                    return epsilon()
                elif current_tok == 'DO':
                    return epsilon()
                else:
                    return False

            def term():
                global current_tok
                if current_tok == 'ident':
                    return factor() and multi()
                elif current_tok == 'num':
                    return factor() and multi()
                elif current_tok == 'boollit':
                    return factor() and multi()
                elif current_tok == 'LP':
                    return factor() and multi()
                else:
                    return False

            def add():
                global current_tok
                if current_tok == 'ADDITIVE':
                    return token('ADDITIVE') and simpleExpression()
                elif current_tok == 'SC':
                    return epsilon()
                elif current_tok == 'THEN':
                    return epsilon()
                elif current_tok == 'DO':
                    return epsilon()
                elif current_tok == 'COMPARE':
                    return epsilon()
                elif current_tok == 'RP':
                    return epsilon()
                else:
                    return False

            def factor():
                global current_tok
                if current_tok == 'ident':
                    return token('ident')
                elif current_tok == 'num':
                    return token('num')
                elif current_tok == 'boollit':
                    return token('boollit')
                elif current_tok == 'LP':
                    return token('LP') and simpleExpression() and token('RP')
                else:
                    return False

            def multi():
                global current_tok
                if current_tok == 'MULTIPLICATIVE':
                    return token('MULTIPLICATIVE') and term()
                elif current_tok == 'ADDITIVE':
                    return epsilon()
                elif current_tok == 'COMPARE':
                    return epsilon()
                elif current_tok == 'SC':
                    return epsilon()
                elif current_tok == 'THEN':
                    return epsilon()
                elif current_tok == 'DO':
                    return epsilon()
                elif current_tok == 'RP':
                    return epsilon()
                else:
                    return False

            program()
        except StopIteration:
            print('Tokens end!')
