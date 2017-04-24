# -*- coding: utf-8 -*-
import re


def lexer(tl_file, tok_file):
    flag_illegal_int = 0
    flag_scanner_error = 0
    tl_dict = {'(': 'LP',
               ')': 'RP',
               ':=': 'ASGN',
               ';': 'SC',
               '*': 'MULTIPLICATIVE(*)',
               'div': 'MULTIPLICATIVE(div)',
               'mod': 'MULTIPLICATIVE(mod)',
               '+': 'ADDITIVE(+)',
               '-': 'ADDITIVE(-)',
               '=': 'COMPARE(=)',
               '!=': 'COMPARE(!=)',
               '<': 'COMPARE(<)',
               '>': 'COMPARE(>)',
               '<=': 'COMPARE(<=)',
               '>=': 'COMPARE(>=)',
               'if': 'IF',
               'then': 'THEN',
               'else': 'ELSE',
               'begin': 'BEGIN',
               'end': 'END',
               'while': 'WHILE',
               'do': 'DO',
               'program': 'PROGRAM',
               'var': 'VAR',
               'as': 'AS',
               'int': 'INT',
               'bool': 'BOOL',
               'writeInt': 'WRITEINT',
               'readInt': 'READINT',
               }

    re_num = re.compile(r'^([1-9][0-9]*|0)$')
    re_boollit = re.compile(r'^(false|true)$')
    re_ident = re.compile(r'^([a-z_A-Z][a-zA-Z0-9]*)$')
    re_opr2 = re.compile(r'(:=|!=|<=|>=)')
    re_opr1 = re.compile(r'(\(|\)|;|\*|\+|-|=|<|>)')

    def match_token(key, f):
        global flag_illegal_int
        token = tl_dict.get(key)
        if token:
            pass
        elif re_num.match(key):
            try:
                if int(key) > 2147483647:
                    flag_illegal_int = 1
                    return False
            except ValueError:
                flag_illegal_int = 1
                return False
            token = 'num(' + key + ')'
        elif re_boollit.match(key):
            token = 'boollit(' + key + ')'
        elif re_ident.match(key):
            token = 'ident(' + key + ')'
        else:
            return False
        if f.tell():
            token = '\n' + token
        f.write(token)
        return True

    with open(tl_file, 'r') as f_tl, open(tok_file, 'w') as f_tok:
        for temp_key1 in f_tl.read().split():
            if not match_token(temp_key1, f_tok):
                for temp_key2 in re.sub(re_opr2, r' \1 ', temp_key1).split():
                    if not match_token(temp_key2, f_tok):
                        for temp_key3 in re.sub(re_opr1, r' \1 ', temp_key2).split():
                            if not match_token(temp_key3, f_tok):
                                if flag_illegal_int:
                                    print('SCANNER ERROR due to illegal integer \"'+temp_key3+'\"')
                                    flag_scanner_error = 1
                                    flag_illegal_int = 0
                                else:
                                    flag_scanner_error = 1
                                    print('SCANNER ERROR due to \"'+temp_key3+'\"')
    return flag_scanner_error == 0
