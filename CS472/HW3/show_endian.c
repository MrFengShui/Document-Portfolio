#include <stdio.h>

#include "main.h"

void func_swap_endian()
{
	short val, rs;
	char *p_val;
	p_val = (char *) &val;
	p_val[0] = 0x12;
	p_val[1] = 0x34;
	printf("Before: 0x%x\n", val);

	if(__BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__)
	{
		rs = 0;
	    rs = rs | ((val & 0xFF) << 8);
	    rs = rs | ((val & 0xFF00) >> 8);
	    val = rs;
	}

    printf(" After: 0x%x\n", val);
}

void func_shift_endian()
{
	short val, rs;
	char *p_val;
	p_val = (char *) &val;
	p_val[0] = 0x12;
	p_val[1] = 0x34;
	printf("Before: 0x%x\n", val);

	if(*p_val == 0x12)
	{
		rs = 0;
	    rs = rs | ((val & 0xFF) << 8);
	    rs = rs | ((val & 0xFF00) >> 8);
	    val = rs;
	}

    printf(" After: 0x%x\n", val);
}
