# -*- coding: utf-8 -*-
import sys
import Lexer
import Parser
import CodeGenerator

tl_file = sys.argv[1]
file_name = tl_file.split('.')[0]
tok_file = file_name + '.tok'
ast_file = file_name + '.ast.dot'
cfg_file = file_name + '.3A.cfg.dot'

if Lexer.lexer(tl_file, tok_file):
    print('Lexer done!')
    temp = Parser.parser(tok_file, ast_file)
    if temp:
        ast_tree = temp[0]
        symbol_table = temp[1]
        CodeGenerator.code_generator(ast_tree, symbol_table, cfg_file)
