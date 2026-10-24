import re
import struct

REGISTERS = {
    "$zero": 0, "$0": 0,
    "$at": 1,
    "$v0": 2, "$v1": 3,
    "$a0": 4, "$a1": 5, "$a2": 6, "$a3": 7,
    "$t0": 8, "$t1": 9, "$t2": 10, "$t3": 11,
    "$t4": 12, "$t5": 13, "$t6": 14, "$t7": 15,
    "$s0": 16, "$s1": 17, "$s2": 18, "$s3": 19,
    "$s4": 20, "$s5": 21, "$s6": 22, "$s7": 23,
    "$t8": 24, "$t9": 25,
    "$k0": 26, "$k1": 27,
    "$gp": 28, "$sp": 29, "$fp": 30, "$s8": 30,
    "$ra": 31,
}

R = {
    "add": 0x20,
    "addu": 0x21,
    "sub": 0x22,
    "subu": 0x23,
    "and": 0x24,
    "or": 0x25,
    "xor": 0x26,
    "nor": 0x27,
    "slt": 0x2A,
    "sltu": 0x2B,
}

I = {
    "addi": 0x08,
    "addiu": 0x09,
    "andi": 0x0C,
    "ori": 0x0D,
    "xori": 0x0E,
    "lui": 0x0F,
    "lw": 0x23,
    "sw": 0x2B,
    "lb": 0x20,
    "sb": 0x28,
    "beq": 0x04,
    "bne": 0x05,
}

J = {
    "j": 0x02,
    "jal": 0x03,
}

def main():
    with open("FizzBuzz.asm", "r") as file:
        content = file.read()
        
        bits = convert(content)
        
        with open("fizzbuzz.mhc-ascii", "w") as asciif:
            asciif.write(bits)

        with open("fizzbuzz.mhc-bin", "wb") as binf:
            lines = bits.strip().splitlines()
            for line in lines:
                if line:
                    a = int(line, 2)
                    binf.write(struct.pack(">I", a))

def pr(reg):
    reg = reg.strip(",()")
    if reg in REGISTERS:
        return REGISTERS[reg]
    try:
        return int(reg)
    except ValueError:
        raise ValueError(f"bad register: {reg}")

def convert(f):
    lines = f.splitlines()
    clines = []
    labels = {}
    pc = 0
    
    for line in lines:
        if '#' in line:
            line = line[:line.index('#')]
        line = line.strip()
        if not line:
            continue
        
        if ':' in line:
            parts = line.split(':', 1)
            label = parts[0].strip()
            labels[label] = pc
            line = parts[1].strip()
            if not line:
                continue
                
        clines.append((pc, line))
        pc += 4

    mcode = []
    for pc, line in clines:
        t = re.findall(r'[\w\$]+', line)
        if not t:
            continue
        
        op = t[0].lower()
        
        if op in R:
            rd = pr(t[1])
            rs = pr(t[2])
            rt = pr(t[3])
            shamt = 0
            funct = R[op]
            
            minstr = (0 << 26) | (rs << 21) | (rt << 16) | (rd << 11) | (shamt << 6) | funct
            mcode.append(minstr)
            
        elif op in I:

            opcode = I[op]
            if op in ["lw", "sw", "lb", "sb"]:
                rt = pr(t[1])
                imm = int(t[2], 0)
                rs = pr(t[3])

            elif op == "lui":
                rt = pr(t[1])
                rs = 0
                imm = int(t[2], 0)

            elif op in ["beq", "bne"]:
                rs = pr(t[1])
                rt = pr(t[2])
                target = t[3]
                if target in labels:
                    imm = (labels[target] - (pc + 4)) // 4
                else:
                    imm = int(target, 0)
            else:

                rt = pr(t[1])
                rs = pr(t[2])
                imm = int(t[3], 0)
                
            imm = imm & 0xFFFF
            minstr = (opcode << 26) | (rs << 21) | (rt << 16) | imm
            mcode.append(minstr)
            
        elif op in J:
            opcode = J[op]
            target = t[1]
            if target in labels:
                addr = (labels[target] // 4) & 0x3FFFFFF
            else:
                addr = int(target, 0) & 0x3FFFFFF
            
            minstr = (opcode << 26) | addr
            mcode.append(minstr)
            
    return "".join(f"{instr:032b}\n" for instr in mcode)

if __name__ == "__main__":
    main()
