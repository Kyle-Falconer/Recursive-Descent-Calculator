#!/usr/bin/python
# -*- coding: latin-1 -*-
# Kyle Falconer
# CSC 333 - Fall 2012 - Homework 3
# Time-stamp: <2012-09-23 4:11 CDT>
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


import calc, sys, traceback

import logging
import optparse

LOGGING_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
    }



def main():
    parser = optparse.OptionParser()
    parser.add_option('-l', '--logging-level', help='Logging level')
    parser.add_option('-f', '--logging-file', help='Logging file name')
    (options, args) = parser.parse_args()
    logging_level = LOGGING_LEVELS.get(options.logging_level, logging.CRITICAL)
    logging.basicConfig(level=logging_level, filename=options.logging_file,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    tests = {
        # "3+5":"8",
        # "9*7":"63",
        # "1|2":"1",
        # "0|2":"2",
        # "0&2":"0",
        # "2&0":"0",
        # "1&2":"2",
        # "2<-4":"0",
        # "2>-5":"1",
        # "4>=5":"0",
        # "4<=5":"1",
        # "5%3":"2",
        # "5%4":"1",
        # "5%5":"0",
        # "@-4":"4",
        # "@3":"3",
        # "@(@-3)*4":"12",
        # "3?5?9?4:3:2:1":"4",
        # "3?4:5":"4",
        # "0?4:5":"5",
        # "!!!!!4":"0",
        # "3|4|5|6":"3",
        # "y=1":"1",
        # "x=-3":"-3",
        # "x=y=z=4":"4",
        # "x=-3 | y=4":"4",
        # "x=4 -1 < -4":"0",
        # "x=4 -1 > -5":"1",
        # "x=4 -1 >= 5":"0",
        # "x=4 -1 <= 5":"1",
        # "(1+3)-2":"2",
        # "@(x=-3)":"3",
        # "(alpha = beta = 3 - 6/2 ? 10 : 5) & alpha*beta":"25",
        # "(bar = 4) + bar":"8",
        # "((d = d + 1) | (d = d + 456)) + d":"2",
        # "((e = 1 - (f = f + 1)) & f) | f":"1",
        }
    for test in tests:
        
        logging.info("\n============================================\n"+
            "\ttestcalc.main\ttest is : "+str(test)+
            "\n============================================")

        try:
            e = calc.Parser(test).parse()

            logging.info('\tAST:'+ str(e))

            result = calc.eval(e)
            if str(tests[test]) == str(result):
                logging.info("\nSUCCESS!\n\tresult : "+str(result)+"\n")
            else:
                logging.warning("FAILURE:\n\tresult : "+str(result)+" != expected result : "+str(tests[test])+"\n")

        except:
            logging.critical(
                "\n\n+------------------------------------------\n"+
                "+------------------------------------------\n"+
                "\n"+
                ""+str(sys.exc_info()[0])+"\n"+
                "\n"+
                ""+str(sys.exc_info()[1])+"\n"+
                "\n"+traceback.format_exc()+"\n"+
                "\n"+
                "+------------------------------------------\n"+
                "+------------------------------------------\n\n")


if __name__ == '__main__':
    main()