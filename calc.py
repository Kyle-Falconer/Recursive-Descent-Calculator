#!/usr/bin/python
# -*- coding: latin-1 -*-
# Kyle Falconer
# CSC 333 -- Homework 3 Recursive-descent calculator
# Time-stamp: <2012-10-03 02:48:01 CDT>
#
#    Copyright 2012 Kyle Falconer
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from __future__ import division, print_function

import logging
import optparse
LOGGING_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
    }



# --- lexer (lexical analyzer, or scanner) ---
import re
class Lexer:
    ignore = re.compile(r'[ \t]+')

    rules = [
        (re.compile(r'[0-9]+'),     lambda s: int(s)),
        (re.compile(r'[a-zA-Z]+'),  lambda s: s),
        (re.compile(r'(==)|(<=)|(>=)|(!=)'),  lambda s: s),
        (re.compile(r'[=?:|&!<>+\-*/%@^()]|'), lambda s: s),
        (re.compile(r'.'),          lambda s: '#' + str(ord(s))),
        ]


    def __init__(self, input_string):
        self.s = input_string
        self.pos = 0


    def next(self):
        # skip over ignorable characters
        m = self.ignore.match(self.s, self.pos)
        if m: self.pos = m.end()

        if self.pos >= len(self.s):
            return '$'      # denotes end of input

        for rule in self.rules:
            r, f = rule
            m = r.match(self.s, self.pos)
            if m:
                self.pos = m.end()
                return f(m.group())


# --- parse error exception ---

class ParseError(Exception):
    def __init__(self, message):
        self.message = message


# --- parser (syntax analyzer): returns an AST ---

class Parser:
    def __init__(self, input_string):
        self.lexer = Lexer(input_string)
        self.next()


    def error(self, message):
        logging.critical(message + ' [next token: ' + str(self.tok) + ']')


    def next(self):
        self.tok = self.lexer.next()


    def parse(self):
        """ input : expr '$' """

        e = self.parse_var()
        if self.tok == '$':
            return e
        else:
            self.error('extraneous input')


    def parse_var(self):            # Prec: 1, Assoc: RL
        """ var_expr ::= ternary_expr | var = var_expr """
        logging.debug("calc.parse_var()\t\t self.tok: "+str(self.tok))

        e = self.parse_ternary()
        if self.tok == '=':
            self.next()
            e = ('=',e,self.parse_var())
            logging.info("\t\tvar_expr:\t token : "+str(self.tok)+"\t e:"+str(e))
        
        return e


    def parse_ternary(self):        # Prec: 2, Assoc: RL
        """ ternary_expr ::= or_expr [ ? ternary_expr : ternary_expr ] """

        logging.debug("calc.parse_ternary()\t\t self.tok: "+str(self.tok))

        e = self.parse_or()
        if self.tok == '?':
            self.next()
            test_expression = e
            expression_1 = self.parse_ternary()
            self.next()
            expression_2 = self.parse_ternary()
            e = ('?', test_expression, expression_1, expression_2)

            logging.info("\t\tcalc.ternary_expr\t e:"+str(e))
        return e


    def parse_or(self):             # Prec: 3, Assoc: RL
        """ or_expr ::= and_expr { | and_expr} """

        logging.debug("calc.parse_or()\t\t self.tok: "+str(self.tok))

        e = self.parse_and()
        while self.tok is '|':
            t = self.tok      # remember operator
            self.next()
            e = (t,e,self.parse_and())
            logging.info("\t\tcalc.parse_or\t e:"+str(e))
        return e


    def parse_and(self):            # Prec: 4, Assoc: RL
        """ and_expr ::= not_expr { & not_expr} """
        logging.debug("calc.parse_and()\t\t self.tok: "+str(self.tok))

        e = self.parse_not()
        while self.tok is '&':
            t = self.tok    # remember operator
            self.next()
            e = (t,e,self.parse_not())
            logging.info("\t\tcalc.parse_and\t e:"+str(e))
        return e


    def parse_not(self):            # Prec: 5, Assoc: RL
        """ not_expr ::= {!} not_expr | comparison_expr"""
        logging.debug("calc.parse_not()\t\t self.tok: "+str(self.tok))

        if self.tok == '!':
            self.next()
            logging.info("\t\tnot_expr")
            return ('!', self.parse_not())
        else:
            return self.parse_comparison()


    def parse_comparison(self):     # Prec: 6, Assoc: LR
        """ comparison_expr ::= addsub_expr {(>,<,!=,==,>=,<=) addsub_expr} """
        logging.debug("calc.parse_comparison()\t self.tok: "+str(self.tok))

        e = self.parse_addsub()
        while self.tok in ('>','<','!=','==','>=','<='):
            t = self.tok      # remember operator
            self.next()

            e = (t,e,self.parse_addsub())
            logging.info("\t\tcomparison_expr\t e:"+str(e))
        return e


    def parse_addsub(self):         # Prec: 7, Assoc: LR
        """ addsub_expr ::= mul_expr {(+|-) mul_expr} """
        logging.debug("calc.parse_addsub()\t\t self.tok: "+str(self.tok))

        e = self.parse_mul()
        while self.tok in ('+', '-'):
            t = self.tok      # remember operator
            self.next()
            e = (t, e, self.parse_mul())
            logging.info("\t\taddsub_expr\t e:"+str(e))
        return e


    def parse_mul(self):            # Prec: 8, Assoc: LR
        """ mul_expr ::= neg_expr {(*|/|%) neg_expr} """
        logging.debug("calc.parse_mul()\t\t self.tok: "+str(self.tok))

        e = self.parse_neg()
        while self.tok in ('*', '/', '%'):
            t = self.tok      # remember operator
            self.next()
            logging.info("\t\tmul_expr\t e:"+str(e))
            e = (t, e, self.parse_neg())
        return e


    def parse_neg(self):            # Prec: 9, Assoc: RL
        """ neg_expr ::= - neg_expr | @ neg_expr | pow_expr  """
        logging.debug("calc.parse_neg()\t\t self.tok: "+str(self.tok))
        
        if self.tok in ('-','@'):
            t = 'abs' if self.tok == '@' else 'neg'
            logging.info("neg_expr:\t token : "+str(t))
            self.next()
            return (t, self.parse_neg())
        else:
            return self.parse_pow()


    def parse_pow(self):            # Prec: 10, Assoc: RL
        """ pow_expr ::= factor [^ pow_expr] """
        logging.debug("calc.parse_pow()\t\t self.tok: "+str(self.tok))

        e = self.parse_factor()
        if self.tok == '^':
            self.next()
            logging.info("pow_expr\t e:"+str(e))
            e = ('^', e, self.parse_pow())
        return e


    def parse_factor(self):
        """ factor ::= int | id | '(' expr ')' """
        logging.debug("calc.parse_factor()\t\t self.tok: "+str(self.tok))

        if isinstance(self.tok, int):
            n = self.tok
            self.next()
            return n
        elif self.tok.isalpha():
            var = self.tok
            self.next()
            logging.info("\t\treturning var "+str(var))
            return var
        elif self.tok == '(':
            self.next()
            e = self.parse_var()
            if self.tok != ')':
                self.error('missing )')
            else:
                self.next()
            return e
        else:
            self.error("got: "+str(self.tok)+" expected int or '('")


# --- postorder AST walker ---

VARS = {}   # dictionary of variables

def assign(v, value):
    # assignment is a statement in Python that 'returns' None;
    # this can be used as an expression, returning the value assigned
    VARS[v] = value
    return value

eval_op = {
    '='  : lambda x,y: assign(x,eval(y)),
    '?'  : lambda x,y,z: eval(y) if eval(x) !=0 else eval(z),
    '|'  : lambda x,y: eval(x) or eval(y),
    '&'  : lambda x,y: eval(x) and eval(y),
    '!'  : lambda x: int(not eval(x)),
    '<'  : lambda x,y: int(eval(x) <  eval(y)),
    '<=' : lambda x,y: int(eval(x) <= eval(y)),
    '>'  : lambda x,y: int(eval(x) >  eval(y)), 
    '>=' : lambda x,y: int(eval(x) >= eval(y)),
    '==' : lambda x,y: int(eval(x) == eval(y)),
    '!=' : lambda x,y: int(eval(x) != eval(y)),
    '+'  : lambda x,y: eval(x) + eval(y),
    '-'  : lambda x,y: eval(x) - eval(y),
    '*'  : lambda x,y: eval(x) * eval(y),
    '/'  : lambda x,y: eval(x) // eval(y),
    '%'  : lambda x,y: eval(x) % eval(y),
    '^'  : lambda x,y: eval(x) ** eval(y),
    'neg': lambda x: -eval(x),
    'abs'  : lambda x: abs(eval(x)),
    }

def eval(e):
    if isinstance(e, int):
        logging.info("calc.eval("+str(e)+"): "+str(e)+" is instance of int")

        return e
    elif isinstance(e, str):
        logging.info("calc.eval("+str(e)+"): "+str(e)+" is instance of str")
        return VARS.get(e, 0)
    else:
        logging.info("calc.eval("+str(e)+"): type(e):"+str(type(e)))
        return eval_op[e[0]](*e[1:])


# --- main calculator function ---

def calc(line):
    return eval(Parser(line).parse())


# --- scaffolding for interactive testing ---

def main():
    parser = optparse.OptionParser()
    parser.add_option('-l', '--logging-level', help='Logging level')
    parser.add_option('-f', '--logging-file', help='Logging file name')
    (options, args) = parser.parse_args()
    logging_level = LOGGING_LEVELS.get(options.logging_level, logging.CRITICAL)
    logging.basicConfig(level=logging_level, filename=options.logging_file,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    while True:
        try:
            line = raw_input('calc> ')
        except EOFError:
            break

        if line == '' or line.isspace(): break

        try:
            e = Parser(line).parse()
            print('\tAST:', str(e))
            print(eval(e))
        except ParseError as err:
            logging.critical('parse error: '+str(err.message))

if __name__ == '__main__':
    main()
