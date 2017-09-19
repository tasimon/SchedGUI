all: SchedSim fail.o


fail.o: fail.c
	cc -c fail.c 

SchedSim: SchedSim.c fail.o
	 cc -DIO=1 -DDEBUG=1 -o SchedSim SchedSim.c fail.o -lm

clean: 
	rm -f SchedSim fail.o


