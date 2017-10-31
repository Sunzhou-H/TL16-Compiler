# TL16-Compiler
This is a TL language compiler. TL language is a "Toy Language" derived from a simplified subset of Pascal. This compiler is specifically written for TL16.0 and the whole project was tested by Python 3.6. 

This compiler program could translate target TL16 program into several files including “.tok” file from scanner part, “.ast.dot” file from parser part and “cfg.dot and .s” files from code generation part. During these phases, Lexical error, syntax error and sematic error will be captured, and warnings will be presented to the user. During code generation phase, the compiler will perform the optimization by applying register allocation and liveness analysis.
