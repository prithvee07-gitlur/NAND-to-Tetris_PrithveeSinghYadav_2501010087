#!/usr/bin/env python3
"""
Hack Assembler — Capstone Project
Prithvee Singh Yadav | Roll No. 2501010087 | K = 87
K mod 3 = 0 → Extra feature: Save all labels and variables with
              their addresses to symbols.txt

Translates Hack assembly (.asm) files into Hack machine code (.hack).
Two-pass assembler:
  Pass 1: Strip comments/blanks, record label addresses
  Pass 2: Translate A-instructions and C-instructions to 16-bit binary
"""

import sys
import os

# ─── Predefined symbol table ────────────────────────────────────────
PREDEFINED_SYMBOLS = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4,
    "R5": 5, "R6": 6, "R7": 7, "R8": 8, "R9": 9,
    "R10": 10, "R11": 11, "R12": 12, "R13": 13,
    "R14": 14, "R15": 15,
    "SCREEN": 16384, "KBD": 24576,
}

# ─── C-instruction lookup tables ────────────────────────────────────
COMP_TABLE = {
    "0":   "0101010", "1":   "0111111", "-1":  "0111010",
    "D":   "0001100", "A":   "0110000", "!D":  "0001101",
    "!A":  "0110001", "-D":  "0001111", "-A":  "0110011",
    "D+1": "0011111", "A+1": "0110111", "D-1": "0001110",
    "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    # a=1 (M variants)
    "M":   "1110000", "!M":  "1110001", "-M":  "1110011",
    "M+1": "1110111", "M-1": "1110010", "D+M": "1000010",
    "D-M": "1010011", "M-D": "1000111", "D&M": "1000000",
    "D|M": "1010101",
}

DEST_TABLE = {
    None:  "000", "":    "000",
    "M":   "001", "D":   "010", "MD":  "011", "DM":  "011",
    "A":   "100", "AM":  "101", "MA":  "101",
    "AD":  "110", "DA":  "110", "AMD": "111", "ADM": "111",
    "MAD": "111", "MDA": "111", "DAM": "111", "DMA": "111",
}

JUMP_TABLE = {
    None:  "000", "":    "000",
    "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}


def clean_line(line: str) -> str:
    """Remove comments and leading/trailing whitespace."""
    comment_idx = line.find("//")
    if comment_idx != -1:
        line = line[:comment_idx]
    return line.strip()


def first_pass(lines: list[str]) -> tuple[list[str], dict[str, int]]:
    """
    First pass: strip comments/blanks, record label (LABEL) addresses.
    Returns cleaned lines (without label declarations) and symbol table.
    """
    symbol_table = dict(PREDEFINED_SYMBOLS)
    cleaned = []
    rom_address = 0

    for raw_line in lines:
        line = clean_line(raw_line)
        if not line:
            continue
        if line.startswith("(") and line.endswith(")"):
            label = line[1:-1]
            symbol_table[label] = rom_address
        else:
            cleaned.append(line)
            rom_address += 1

    return cleaned, symbol_table


def translate_a_instruction(symbol: str, symbol_table: dict[str, int],
                            next_var_address: list[int]) -> str:
    """Translate @value or @symbol into 16-bit binary."""
    if symbol.isdigit():
        address = int(symbol)
    else:
        if symbol not in symbol_table:
            # Allocate new variable
            symbol_table[symbol] = next_var_address[0]
            next_var_address[0] += 1
        address = symbol_table[symbol]
    return format(address, "016b")


def translate_c_instruction(line: str) -> str:
    """Translate a C-instruction (dest=comp;jump) into 16-bit binary."""
    dest = None
    jump = None
    comp_part = line

    if "=" in comp_part:
        dest, comp_part = comp_part.split("=", 1)
    if ";" in comp_part:
        comp_part, jump = comp_part.split(";", 1)

    comp_bits = COMP_TABLE.get(comp_part)
    dest_bits = DEST_TABLE.get(dest)
    jump_bits = JUMP_TABLE.get(jump)

    if comp_bits is None or dest_bits is None or jump_bits is None:
        return None  # Invalid instruction

    return "111" + comp_bits + dest_bits + jump_bits


def second_pass(cleaned_lines: list[str],
                symbol_table: dict[str, int]) -> list[str]:
    """Second pass: translate every instruction to 16-bit binary."""
    machine_code = []
    next_var_address = [16]  # Variables start at RAM[16]

    for line in cleaned_lines:
        if line.startswith("@"):
            symbol = line[1:]
            binary = translate_a_instruction(symbol, symbol_table,
                                             next_var_address)
        else:
            binary = translate_c_instruction(line)
            if binary is None:
                print(f"Error: could not translate '{line}'")
                sys.exit(1)
        machine_code.append(binary)

    return machine_code


def save_symbols(symbol_table: dict[str, int], output_dir: str,
                 labels: set[str], variables: set[str]):
    """
    Extra feature (K mod 3 = 0):
    Save all labels and variables with their addresses to symbols.txt
    """
    symbols_path = os.path.join(output_dir, "symbols.txt")
    with open(symbols_path, "w") as f:
        f.write("=" * 50 + "\n")
        f.write("  SYMBOL TABLE\n")
        f.write("  Assembler by Prithvee Singh Yadav (2501010087)\n")
        f.write("=" * 50 + "\n\n")

        # Labels section
        f.write("--- Labels (ROM addresses) ---\n")
        sorted_labels = sorted(
            [(name, addr) for name, addr in symbol_table.items()
             if name in labels],
            key=lambda x: x[1]
        )
        for name, addr in sorted_labels:
            f.write(f"  {name:20s}  ->  {addr}\n")

        f.write(f"\nTotal labels: {len(sorted_labels)}\n\n")

        # Variables section
        f.write("--- Variables (RAM addresses) ---\n")
        sorted_vars = sorted(
            [(name, addr) for name, addr in symbol_table.items()
             if name in variables],
            key=lambda x: x[1]
        )
        for name, addr in sorted_vars:
            f.write(f"  {name:20s}  ->  {addr}\n")

        f.write(f"\nTotal variables: {len(sorted_vars)}\n")
    print(f"  -> Symbol table saved to {symbols_path}")


def assemble(input_path: str):
    """Main assembler: read .asm, write .hack, write symbols.txt."""
    # Read source file
    with open(input_path, "r") as f:
        lines = f.readlines()

    # First pass
    cleaned_lines, symbol_table = first_pass(lines)

    # Track which symbols are labels (from first pass)
    labels = set(symbol_table.keys()) - set(PREDEFINED_SYMBOLS.keys())

    # Second pass
    machine_code = second_pass(cleaned_lines, symbol_table)

    # Track variables (symbols added during second pass)
    variables = set(symbol_table.keys()) - set(PREDEFINED_SYMBOLS.keys()) - labels

    # Write .hack output
    output_path = input_path.rsplit(".", 1)[0] + ".hack"
    with open(output_path, "w") as f:
        for code in machine_code:
            f.write(code + "\n")

    print(f"  -> Assembled {len(machine_code)} instructions to {output_path}")

    # Extra feature: save symbols.txt
    output_dir = os.path.dirname(os.path.abspath(output_path))
    save_symbols(symbol_table, output_dir, labels, variables)


def main():
    if len(sys.argv) < 2:
        print("Usage: python assembler.py <file.asm> [file2.asm ...]")
        print("       Assembles Hack assembly files into machine code.")
        sys.exit(1)

    for filepath in sys.argv[1:]:
        if not os.path.exists(filepath):
            print(f"Error: File '{filepath}' not found.")
            continue
        print(f"Assembling: {filepath}")
        assemble(filepath)
        print()


if __name__ == "__main__":
    main()
