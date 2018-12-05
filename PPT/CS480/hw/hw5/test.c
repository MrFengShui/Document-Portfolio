
#include <stdio.h>
int main()
{
int a = (0);
while(a < (10))
{
a += (1);
printf("%d\n", a);
}

a = (0);
int b = (1);
while(a < (10))
{
a += (1);
while(b < (11))
{
b += (2);
printf("%d\n", b);
}
printf("%d\n", a);
}

return 0;
}
