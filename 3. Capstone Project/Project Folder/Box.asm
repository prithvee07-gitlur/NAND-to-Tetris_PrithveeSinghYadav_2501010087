// Box.asm — Capstone Project
// Prithvee Singh Yadav | Roll No. 2501010087 | K = 87
//
// Draws a black box while any key is pressed, clears it when released.
// Box specs (K = 87):
//   - Starts at row 87
//   - 20 rows tall (rows 87–106)
//   - 64 pixels wide = 4 words from left edge
//   - K mod 4 = 3, so width = 16 * (3+1) = 64 pixels
//
// Screen memory map: base address = 16384
// Each row = 32 words (512 pixels), each word = 16 pixels
// Row r starts at SCREEN + 32*r
// Row 87 starts at SCREEN + 32*87 = SCREEN + 2784 = 16384 + 2784 = 19168

(LOOP)
    // Check keyboard
    @KBD
    D=M

    // If key pressed (D != 0), draw box
    @DRAW
    D;JNE

    // Else clear box
    @CLEAR
    0;JMP

(DRAW)
    // Set fill value to -1 (all 1s = black pixels)
    @fill
    M=-1
    @DOFILL
    0;JMP

(CLEAR)
    // Set fill value to 0 (all 0s = white/clear)
    @fill
    M=0
    @DOFILL
    0;JMP

(DOFILL)
    // Initialize row counter: 20 rows
    @20
    D=A
    @rowcount
    M=D

    // Calculate starting screen address: SCREEN + 32*87 = 16384 + 2784 = 19168
    @19168
    D=A
    @addr
    M=D

(ROWLOOP)
    // Check if all rows done
    @rowcount
    D=M
    @LOOP
    D;JEQ

    // Fill 4 words in this row (64 pixels)
    // Word 0
    @fill
    D=M
    @addr
    A=M
    M=D

    // Word 1
    @addr
    A=M+1
    D=A
    @addr1
    M=D
    @fill
    D=M
    @addr1
    A=M
    M=D

    // Word 2
    @addr
    D=M
    @2
    D=D+A
    @addr2
    M=D
    @fill
    D=M
    @addr2
    A=M
    M=D

    // Word 3
    @addr
    D=M
    @3
    D=D+A
    @addr3
    M=D
    @fill
    D=M
    @addr3
    A=M
    M=D

    // Move to next row: addr = addr + 32
    @32
    D=A
    @addr
    M=D+M

    // Decrement row counter
    @rowcount
    MD=M-1

    // Continue row loop
    @ROWLOOP
    0;JMP
