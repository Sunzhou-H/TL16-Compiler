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

            def program():
                global current_tok
                if current_tok == 'PROGRAM':
                    return token('PROGRAM') and declaration() and token('BEGIN') and statementSequence() and token('END')
                else:
                    return False

            def declaration():
                pass

            def statementSequence():
                pass


            program()
        except StopIteration:
            print('Tokens end!')
