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

DREGISTERS = {
    0: "$zero", 1: "$at", 2: "$v0", 3: "$v1",
    4: "$a0", 5: "$a1", 6: "$a2", 7: "$a3",
    8: "$t0", 9: "$t1", 10: "$t2", 11: "$t3",
    12: "$t4", 13: "$t5", 14: "$t6", 15: "$t7",
    16: "$s0", 17: "$s1", 18: "$s2", 19: "$s3",
    20: "$s4", 21: "$s5", 22: "$s6", 23: "$s7",
    24: "$t8", 25: "$t9", 26: "$k0", 27: "$k1",
    28: "$gp", 29: "$sp", 30: "$fp", 31: "$ra"
}

R = {
    "add": 0x20, "addu": 0x21, "sub": 0x22, "subu": 0x23,
    "and": 0x24, "or": 0x25, "xor": 0x26, "nor": 0x27,
    "slt": 0x2A, "sltu": 0x2B,
}
DR = {v: k for k, v in R.items()}

I = {
    "addi": 0x08, "addiu": 0x09, "andi": 0x0C, "ori": 0x0D,
    "xori": 0x0E, "lui": 0x0F, "lw": 0x23, "sw": 0x2B,
    "lb": 0x20, "sb": 0x28, "beq": 0x04, "bne": 0x05,
}
DI = {v: k for k, v in I.items()}

J = {
    "j": 0x02, "jal": 0x03,
}
DJ = {v: k for k, v in J.items()}


def se16(value):
    if value & 0x8000:
        return value - 0x10000
    return value


def disassemble(i):
    labels = {}
    di = []

    pc = 0
    for instr in i:
        opcode = (instr >> 26) & 0x3F
        
        if opcode in DI and DI[opcode] in ["beq", "bne"]:
            imm = se16(instr & 0xFFFF)
            target = pc + 4 + (imm * 4)
            labels[target] = f"label{target:x}"
        elif opcode in DJ:
            addr = (instr & 0x3FFFFFF) << 2
            labels[addr] = f"label{addr:x}"
            
        pc += 4

    pc = 0
    for instr in i:
        if pc in labels:
            di.append((pc, f"{labels[pc]}:"))

        opcode = (instr >> 26) & 0x3F
        rs = (instr >> 21) & 0x1F
        rt = (instr >> 16) & 0x1F
        rd = (instr >> 11) & 0x1F
        shamt = (instr >> 6) & 0x1F
        funct = instr & 0x3F

        line = ""
        if opcode == 0:
            op = DR.get(funct, "unknown r")
            line = f"    {op} {DREGISTERS.get(rd, f'${rd}')}, {DREGISTERS.get(rs, f'${rs}')}, {DREGISTERS.get(rt, f'${rt}')}"
        
        elif opcode in DI:
            op = DI[opcode]
            imm = instr & 0xFFFF
            
            if op in ["lw", "sw", "lb", "sb"]:
                si = se16(imm)
                line = f"    {op} {DREGISTERS.get(rt, f'${rt}')}, {si}({DREGISTERS.get(rs, f'${rs}')})"
            elif op == "lui":
                line = f"    {op} {DREGISTERS.get(rt, f'${rt}')}, {imm}"
            elif op in ["beq", "bne"]:
                si = se16(imm)
                target = pc + 4 + (si * 4)
                targetl = labels.get(target, f"0x{target:x}")
                line = f"    {op} {DREGISTERS.get(rs, f'${rs}')}, {DREGISTERS.get(rt, f'${rt}')}, {targetl}"
            else:
                si = se16(imm)
                line = f"    {op} {DREGISTERS.get(rt, f'${rt}')}, {DREGISTERS.get(rs, f'${rs}')}, {si}"
                
        elif opcode in DJ:
            op = DJ[opcode]
            addr = (instr & 0x3FFFFFF) << 2
            targetl = labels.get(addr, f"0x{addr:x}")
            line = f"{op} {targetl}"
        else:
            line = f"# Unknown{instr:08x}"

        di.append((pc, line))
        pc += 4

    return di


def main():
    try:
        with open("fizzbuzz.mhc-bin", "rb") as f:
            bd = f.read()
            
        instructions = []
        for i in range(0, len(bd), 4):
            if i + 4 <= len(bd):
                instr = struct.unpack(">I", bd[i:i+4])[0]
                instructions.append(instr)
                
        decoded = disassemble(instructions)
        
        of = "diss.asm"
        with open(of, "w") as out:
            for pc, line in decoded:
                out.write(line + "\n")
                
        print(f"done")

    except FileNotFoundError:
        print("not found")

main()