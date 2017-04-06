#ifndef _EXTRACT_H_
#define _EXTRACT_H_

typedef struct
{
	long int integer;
	double floating;
	char string[8];
	int sign, exponent;
	unsigned long int mantissa;
} bit_pattern_t;

void func_pattern(bit_pattern_t *);

#endif