# -*- coding: utf-8 -*-
import sys
import Lexer
import Parser

tl_file = sys.argv[1]
file_name = tl_file.split('.')[0]
tok_file = file_name + '.tok'
ast_file = file_name + '.ast.dot'

if Lexer.lexer(tl_file, tok_file):
    Parser.parser(tok_file, ast_file)
