#------------------------------------------
# Usage: pulses.py [ outfile [ debug ] ]
#------------------------------------------

from collections import defaultdict, namedtuple
import re
import math
import sys

TEMPLATE_FILE = 'pulses_template.asm'
DEFAULT_OUTFILE = 'codegen/pulses.asm'

VOLUME_STEPS = 1
MIN_VOLUME = 0.125

VARIANTS = 119

PULSE1MIN = 4        # pulse 1 variant part minimal length
PULSE1MBAL = 3       # pulse 1 minimal balance
INTERVAL1MAX = 131   # interval 1 variant part maximal length
INTERVAL1MBAL = 3    # interval 1 minimal balance


PULSE2MIN = 4        # pulse 2 variant part minimal length
PULSE2MBAL = 4       # pulse 2 minimal balance
INTERVAL2MAX = 122   # interval 2 variant part maximal length
INTERVAL2MBAL = 4    # interval 2 minimal balance

def parse_template(path):
    sections = None
    t_section_header = re.compile(r'^\s*\[\s*(\w+)\s*\]\s*$')
    section = None
    lines = None
    with open(path) as f:
        for line in f:
            line = line.rstrip()
            if line.strip() == '':
                continue
            if ( m := t_section_header.match(line) ) is not None:
                if sections is not None:
                    sections[section] = lines
                else:
                    sections = {}
                section = m[1]
                lines = []
            else:
                if lines is None:
                    raise RuntimeError('Wrong pulse template file format. Section name required first')
                lines.append(line)
    
    if section is not None:
        sections[section] = lines
    
    return sections

inf = float('inf')

def comb_iter(n, variants):
    if len(variants) < 1:
        if n==0:
            yield []
        return
    s = 0
    cnt = 0
    variant, limit = variants[0]
    if variant < 1:
        raise ValueError(f'Inacceptable variant: {variant!r}')
    while s <= n and cnt <= limit:
        for suffix in comb_iter(n-s, variants[1:]):
            yield [(variant, cnt)] + suffix
        s += variant
        cnt += 1

def comb(n, variants):
    all_comb = [defaultdict(int, c) for c in comb_iter(n, list(variants.items()))]
    if len(all_comb) < 1:
        return None
    minlen = min(sum(c.values()) for c in all_comb)
    return next(filter(lambda c: sum(c.values())==minlen, all_comb))

tacts_template = re.compile(r';=\s*(\d+)')
bset_include_template = re.compile(r'=balance_set_include_(\S+)')
bset_exclude_template = re.compile(r'=balance_set_exclude_(\S+)')

CommonLine = namedtuple('CommonLine', [])
Instruction = namedtuple('InstructionLine', ['tacts'])
BalanceOnce = namedtuple('BalanceOnce', ['tacts'])
BalanceMany = namedtuple('BalanceMany', ['tacts'])
BalanceSetItem = namedtuple('BalanceSetItem', ['tacts', 'bset_id'])

def inspect_line(line):
    m = tacts_template.search(line)
    if m is None:
        return CommonLine()
    tacts = int(m[1])
    if '=balance_once' in line:
        return BalanceOnce(tacts)
    if '=balance_many' in line:
        return BalanceMany(tacts)
    if ( m := bset_include_template.search(line) ) is not None:
        return BalanceSetItem(tacts, m[1])
    if ( m := bset_exclude_template.search(line) ) is not None:
        return BalanceSetItem(-tacts, m[1])
    if '=b' in line:
        raise ValueError(f'Invalid balance mark in line: {line!r}')
    return Instruction(tacts)

class PulseBuilder:
    def __init__(self, lines, debug = False):
        self.src_lines = list(lines)
        self.unspent_lineno = 0
        self.finished = False
        self.debug = debug
    
    def build_part(self, required_tacts, min_balance, prolog_lines, epilog_lines, greedy):
        if self.debug:
            print(f'        Internal length: {required_tacts}')
        
        available_balances = defaultdict(int)
        balance_sets = defaultdict(int)
        
        def register_balances(line, allow_sets):
            line_info = inspect_line(line)
            if isinstance(line_info, BalanceOnce):
                available_balances[line_info.tacts] += 1
            elif isinstance(line_info, BalanceMany):
                available_balances[line_info.tacts] += float('inf')
            elif isinstance(line_info, BalanceSetItem):
                if not allow_sets:
                    raise ValueError(f'Balance sets not allowed here: {line!r}')
                balance_sets[line_info.bset_id] += line_info.tacts
            elif not isinstance(line_info, (Instruction, CommonLine)):
                raise ValueError(f'Unknown line info type {line_info!r} for line {line!r}')
            
        tacts_sum = 0
        end_lineno = self.unspent_lineno
        for i, line in enumerate(self.src_lines[self.unspent_lineno:], self.unspent_lineno):
            line_info = inspect_line(line)
            if isinstance(line_info, Instruction):
                if tacts_sum + line_info.tacts + min_balance > required_tacts:
                    break
                tacts_sum += line_info.tacts
                end_lineno = i + 1
            elif greedy:
                end_lineno = i + 1
        
        spent_lines = self.src_lines[self.unspent_lineno : end_lineno]
        
        for line in prolog_lines:
            register_balances(line, True)
        
        for line in spent_lines:
            register_balances(line, False)
        
        for line in epilog_lines:
            register_balances(line, True)
        
        for t in balance_sets.values():
            available_balances[t] += 1
        
        if self.debug:
            print(f'        Available balances: {dict(available_balances)}')
        
        balance = required_tacts - tacts_sum
        balance_combination = comb(balance, available_balances)
        if balance_combination is None:
            raise RuntimeError(f"Can not combine balance {balance} from {dict(available_balances)}")
        
        if self.debug:
            print(f'        Spent lines: [{self.unspent_lineno} : {end_lineno}]')
            print(f'        Instructions tacts: {tacts_sum}')
            print(f'        Balance: {balance} / {dict(balance_combination)}')
        
        used_balance_sets = set()
        for bset_id, t in balance_sets.items():
            if balance_combination[t] > 0:
                balance_combination[t] -= 1
                used_balance_sets.add(bset_id)
        
        result_lines = []
        
        def make_output(line):
            line_info = inspect_line(line)
            if isinstance(line_info, BalanceMany):
                while balance_combination[line_info.tacts] > 0:
                    result_lines.append(line)
                    balance_combination[line_info.tacts] -= 1
            elif isinstance(line_info, BalanceOnce):
                if balance_combination[line_info.tacts] > 0:
                    result_lines.append(line)
                    balance_combination[line_info.tacts] -= 1
            elif isinstance(line_info, BalanceSetItem):
                if (
                    line_info.bset_id in used_balance_sets and line_info.tacts > 0
                    or line_info.bset_id not in used_balance_sets and line_info.tacts < 0
                ):
                    result_lines.append(line)
            else:
                result_lines.append(line)
        
        for line in prolog_lines:
            make_output(line)
        
        for line in spent_lines:
            make_output(line)
        
        for line in epilog_lines:
            make_output(line)
        
        self.unspent_lineno = end_lineno
        if self.unspent_lineno == len(self.src_lines):
            self.finished = True
        
        #if self.debug:
        #    print('=== Spent lines ==')
        #    for line in spent_lines:
        #        print(line)
        #    print('==================')
        
        return result_lines

def build_variant(f, n, template, debug):
    print(f'Building variant {n}')
    
    pb = PulseBuilder(template['part1'], debug)
    if debug:
        print(f'    Building pulse 1')
    pulse1_lines = pb.build_part(PULSE1MIN + n, PULSE1MBAL, template['pulse1prolog'], template['pulse1epilog'], False)
    if debug:
        print(f'    Building interval 1')
    interval1_lines = pb.build_part(INTERVAL1MAX - n, INTERVAL1MBAL, template['interval1prolog'], template['interval1epilog'], True)
    if not pb.finished:
        raise RuntimeError(f'Redundant lines remained after pulse 1')
    
    pb = PulseBuilder(template['part2'], debug)
    if debug:
        print(f'    Building pulse 2')
    pulse2_lines = pb.build_part(PULSE2MIN + n, PULSE2MBAL, template['pulse2prolog'], template['pulse2epilog'], True)
    if debug:
        print(f'    Building interval 2')
    interval2_lines = pb.build_part(INTERVAL2MAX - n, INTERVAL2MBAL, template['interval2prolog'], template['interval2epilog'], True)
    if not pb.finished:
        raise RuntimeError(f'Redundant lines remained after pulse 2')
    
    if debug:
        print()
    
    f.write(f'\nplsvariant{n}:\n')
    f.write('\n'.join(pulse1_lines) + '\n')
    f.write('\n'.join(interval1_lines) + '\n')
    f.write('\n'.join(pulse2_lines) + '\n')
    f.write('\n'.join(interval2_lines) + '\n')
    


def build_pulses_code(f, debug = False):
    template = parse_template(TEMPLATE_FILE)
    
    for n in range(VARIANTS):
        build_variant(f, n, template, debug)
    
    middle_point = VARIANTS / 2
    att = math.exp(math.log(MIN_VOLUME) / max(1, VOLUME_STEPS - 1))
    
    f.write('\n\n;====================================================\n')
    f.write('\talign   512\n')
    k = 1
    for i in range(VOLUME_STEPS):
        tblname = f'plstbl{i}'
        print(tblname)
        f.write(f'\n{tblname}:\n')
        for t in range(256):
            sigt = (t + 128) % 256 - 128
            val = sigt * k
            intval = int(math.floor(val + middle_point))
            bounded = max(min(intval, VARIANTS - 1), 0)
            f.write( '\tdw  plsvariant{}\t; {}, {}\n'.format(bounded, sigt, val) )
            
        k *= att
    
    f.write('\n')

if __name__ == '__main__':
    # Usage: pulses.py [ outfile [ debug ] ]
    outfile = DEFAULT_OUTFILE
    if len(sys.argv) > 1:
        outfile = sys.argv[1]
    
    debug = False
    if len(sys.argv) > 2:
        debug = True

    with open(outfile, 'w') as fw:
        build_pulses_code(fw, debug)
