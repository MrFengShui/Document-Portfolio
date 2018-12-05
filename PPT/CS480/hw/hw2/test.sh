#!/bin/sh
echo '--------------------------------------------------'
echo '--------------------------------------------------'
echo '**************** READING TEST FILS ***************'
for((i = 1; i < 17; i ++));
do
	cat './TEST/case'$i'.in' | python &> './source'$i'.out'
done
echo '--------------------------------------------------'
echo '--------------------------------------------------'
echo '*********** GENERATING PYTHON RESULT *************'
echo '--------------------------------------------------'
echo '--------------------------------------------------'
for((i = 1; i < 17; i ++));
do
	cat './TEST/case'$i'.in' | python hw2.py &> './case'$i'.c'
done
echo '--------------------------------------------------'
echo '--------------------------------------------------'

echo '--------------------------------------------------'
echo '--------------------------------------------------'
echo '************* COMPILE & RUNNING C ****************'
for((i = 1; i < 17; i ++));
do
	gcc -o './case'$i './case'$i'.c'
	./'case'$i &> './result'$i'.out' 
done
echo '--------------------------------------------------'
echo '--------------------------------------------------'

echo '--------------------------------------------------'
echo '--------------------------------------------------'
echo '***************** COMPARING RESULT ***************'
echo '--------------------------------------------------'
echo '--------------------------------------------------'
for((i = 1; i < 17; i ++));
do
	diff './source'$i'.out' './result'$i'.out'
	if [ $? -ne 0 ];
	then
		echo './source'$i'.out fail...'
	else
		echo './source'$i'.out pass...'
	fi
done
echo '--------------------------------------------------'
echo '--------------------------------------------------'
echo '****************** REMOVE FILES ******************'
echo '--------------------------------------------------'
echo '--------------------------------------------------'
for((i = 1; i < 17; i ++));
do
	rm -f './source'$i'.out' './result'$i'.out' './case'$i'.c' ./'case'$i
done
echo '--------------------------------------------------'
echo '--------------------------------------------------'