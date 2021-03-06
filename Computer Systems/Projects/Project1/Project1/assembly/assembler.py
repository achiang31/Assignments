#!/usr/bin/env python3

from __future__ import print_function
import argparse
import os
import importlib
import operator
import re

"""assembler.py: General, modular 2-pass assembler accepting ISA definitions to assemble code."""
__author__ = "Christopher Tam"


VERBOSE = False
FILE_NAME = ''
ISA = None
RE_PARAMS = re.compile('^(?P<key>.+)=(?P<value>.+)$')

def verbose(s):
    if VERBOSE:
        print(s)
        
def error(line_number, message):
    print("Error {}:{}: {}.\n".format(FILE_NAME, line_number, message))

def pass1(file):
    verbose("\nBeginning Pass 1...\n")
    # use a program counter to keep track of addresses in the file
    pc = 0
    line_count = 0
    no_errors = True

    # Seek to beginning of file
    #f.seek(0)

    for line in file:
        line_count += 1

        # Skip blank lines and comments
        if ISA.is_blank(line):
            verbose(line)
            continue
        
        # Trim any leading and trailing whitespace
        line = line.strip()
        
        verbose('{}: {}'.format(pc, line))
        
        
        # Make line case-insensitive
        line = line.lower()
        
        # Parse line
        label, op, _ = ISA.get_parts(line)
        if label:
            if label in ISA.SYMBOL_TABLE:
                error(line_count, "label '{}' is defined more than once".format(label))
                no_errors = False
            else:
                ISA.SYMBOL_TABLE[label] = pc
                
        if op:
            try:
                pc += getattr(ISA, ISA.instruction_class(op)).size()
            except:
                error(line_count, "instruction '{}' is not defined in the current ISA".format(op))
                no_errors = False
                
        
    verbose("\nFinished Pass 1.\n")
        
    return no_errors


def pass2(input_file, use_hex):
    verbose("\nBeginning Pass 2...\n")

    pc = 0
    line_count = 0
    success = True
    results = []
    
    # Seek to beginning of file
    input_file.seek(0)
    
        
    for line in input_file:
        line_count += 1
        # Skip blank lines and comments
        if ISA.is_blank(line):
            verbose(line)
            continue
        
        # Trim any leading and trailing whitespace
        line = line.strip()

        verbose('{}: {}'.format(pc, line))
        
        # Make line case-insensitive
        line = line.lower()

        _, op, operands = ISA.get_parts(line)
                
        if op:
            instr = getattr(ISA, ISA.instruction_class(op))
            assembled = None
            try:
                if use_hex:
                    assembled = instr.hex(operands, pc=pc, instruction=op)
                else:
                    assembled = instr.binary(operands, pc=pc, instruction=op)
            except Exception as e:
                error(line_count, str(e))
                success = False
            
            if assembled:
                results.extend(assembled)
                pc += instr.size()
            
    
    verbose("\nFinished Pass 2.\n")
    return (success, results)

def separator(s):
    return s.replace('\s', ' ').encode().decode('unicode_escape')

def parse_params(values):
    if values is None:
        return None
    
    parsed = {}
    values = values.split(',')
    
    for val in values:
        m = RE_PARAMS.match(val)
        if m is None:
            print("Error: '{}' is not a valid custom parameter".format(val))
            exit(1)

        parsed[m.group('key')] = m.group('value')

    return parsed

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser('assembler.py', description='Assembles generic ISA-defined assembly code into hex or binary.')
    parser.add_argument('asmfile', help='the .s file to be assembled')
    parser.add_argument('-i', '--isa', required=False, type=str, default='isa', help='define the Python ISA module to load [default: isa]')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose printing of assembler')
    parser.add_argument('--hex', '--logisim', action='store_true', help='assemble code into hexadecimal (Logisim-compatible)')
    parser.add_argument('-s', '--separator', required=False, type=separator, default='\\n', help='the separator to use between instructions (accepts \s for space and standard escape characters) [default: \\n]')
    parser.add_argument('--sym', '--symbols', action='store_true', help="output an additional file containing the assembled program's symbol table")
    parser.add_argument('--params', required=False, type=str, help='custom parameters to pass to an architecture, formatted as "key1=value1, key2=value2, key3=value3"')
    args = parser.parse_args()
    

    # Try to dynamically load ISA module
    try:
        ISA = importlib.import_module(args.isa)
    except Exception as e:
        print("Error: Failed to load ISA definition module '{}'. {}\n".format(args.isa, str(e)))
        exit(1)
        
    print("Assembling for {} architecture...".format(ISA.__name__))

    # Pass in custom parameters
    try:
        ISA.receive_params(parse_params(args.params))
    except Exception as e:
        print("Error: Failed to parse custom parameters for {}. {}\n".format(ISA.__name__, str(e)))
        exit(1)

    VERBOSE = args.verbose
    FILE_NAME = os.path.basename(args.asmfile)
    
    with open(args.asmfile, 'r') as read_file:
        if not pass1(read_file):
            print("Assemble failed.\n")
            exit(1)
        
        success, results = pass2(read_file, args.hex)
        if not success:
            print("Assemble failed.\n")
            exit(1)
        
    outFileName = os.path.splitext(args.asmfile)[0]
    code_ext = '.hex' if args.hex else '.bin'
    sep = args.separator

    if args.sym:
        sym_ext = '.sym'
        print("Writing symbol table to {}...".format(outFileName + sym_ext), end="")

        sym_sorted = sorted(ISA.SYMBOL_TABLE.items(), key=operator.itemgetter(1))

        with open(outFileName + sym_ext, 'w') as write_file:
            for (symbol, addr) in sym_sorted:
                write_file.write("{}: {}\n".format(symbol, hex(addr)))

        print('done!')


    print("Writing to {}...".format(outFileName + code_ext), end="")
        
    with open(outFileName + code_ext, 'w') as write_file:
        for r in results:
            write_file.write(r + sep)

    print('done!')