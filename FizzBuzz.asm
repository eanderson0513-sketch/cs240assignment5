.data
	fizz: .asciiz "Fizz"
	buzz: .asciiz "Buzz"
	line: .asciiz "\n"
.text
.globl main
main:
	li $t0, 0
	li $t1, 0
	li $9, 0
	loop:
		beq $t0, 100, exit
		li $t9, 0
		la $a0, line
		li $v0, 4
		syscall
		addi $t0, $t0, 1
		move $t1, $t0
		rem $t2, $t1, 3
		beq $t2, 0, F
		j L
		F:
			la $a0, fizz
			li $v0, 4
			syscall
			li $t9, 1
		L:
		move $t1, $t0
		rem $t2, $t1, 5
		beq $t2, 0, B
		j cont
		B:
			la $a0, buzz
			li $v0, 4
			syscall
			li $t9, 1
		cont:
		beq $t9, 1, loop
		move $a0, $t0
		li $v0, 1
		syscall
		j loop
exit:
	li $v0, 10
	syscall