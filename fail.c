/*
 * This file lists all of our failure functions and related utilities
Failure rate is failures per hour
lambda = 1/SMTBF

Year	Cores	SMTBF(hrs)	System
2002	8192	40	ASCI White
2004	3016	9.7	Lemieux PSC
2007	6656	351	Seaborg NERSC
2002	8192	6.5	ASCI Q
2004	15000	1.2	Google
2006	131072	147.8	BlueGene/L
*/
#include<math.h>
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<omp.h>
#include<sys/time.h>


#define MAX 1000
#define TIMER 0
#define PLOT 0
#ifdef DBL
typedef double size; //fails at 171! use %e
#else
#define DBL 0
typedef long double size; //fails at 1755! use %Le

#endif

int init_machines(void);
double Weibull(double,double, double);
float exponential_dist(float, int);
double wolsten(float, int, int, int);
double poisson(int,float,float);
double get_seconds(void);
double topt(float, float);
int bin_coeff(int, int);
double factorial(int);

/*in:lambda, nodes*/
float failure_rate(float,int);

typedef struct
	{
	int cores;
	float mttf;
	char *name;
	} Stats;

int init_machines(){

/* use existing failure data*/
/* this should be pulled from a file*/
	
Stats machine[6];

machine[0].cores=8192;
machine[0].mttf=40;
machine[0].name="ASCI_White";

machine[1].cores=3016;
machine[1].mttf=9.7;
machine[1].name="Lemiuex";

machine[2].cores=15000;
machine[2].mttf=1.2;
machine[2].name="Google";

machine[3].cores=6656;
machine[3].mttf=351;
machine[3].name="Seaborg";

machine[4].cores=8192;
machine[4].mttf=6.5;
machine[4].name="ASCI_Q";

machine[5].cores=131072;
machine[5].mttf=147.8;
machine[5].name="BlueGene/L";


return 0;
}//end init_machines

/* This is the Exponential CDF, which is OK if want failure over time  and lambda = 1/rate*/
/* Tara Agrees!! 1/23/2017*/ 
float exponential_dist(float rate, int time)
        {
	float lambda=1.0f/rate;
	return (1-expf((-lambda)*time));
        }

/*
The total number of failures within an item population, divided by the total time expended by that population, during a particular measurement interval under stated conditions. (MacDiarmid, et al.)
MacDiarmid, Preston; Morris, Seymour; et al., (no date), Reliability Toolkit: Commercial Practices Edition, pp 35–39, Reliability Analysis Center and Rome Laboratory, Rome, New York.

MTTF for nodes parallel units with equal failure rate
euqation from Wolstenholme pg.112
this just returns the MTTF so if you give it lambda = 1/5 it will tell you 5.
*/
float failure_rate(float lambda,int nodes)
        {
        float sum=0;
        int i;
        for (i=1; i<=nodes; i++)sum+=(1.0/i);
        return (float)(1.0/lambda)*sum;
        }


double factorial(int n)
{
   if(n==0)
      return(1);
   else
      return(n*factorial(n-1));
}

/* Generate a Poisson probability distribution */
//Poisson(x,u) = probability of x occuring given u rate of occurence.
// x = total occurence we would like to know, what is the probability of 3 failures if we know the average is 2(u) a day.
// u = average rate occurences of event, 2 a day (mttf).
double poisson(int x, float mttf, float length) { 
//float u=(1.0/mttf)*length;
float u=(1.0/mttf)*length;
return(exp(-u)*pow(u,x))/(double)factorial(x);
}

/* Include Hazard Function */

/* Quorum, m out of n systems work
 * wolstenholme pg 112 at bottom, eq 6.7*/
//R(t)  =sum_k=m^n (n k)(e^-lambda*t)^k(1-e^-lambda*t)^n-k
double wolsten(float rate, int n, int k, int t){
double reliability_t=0;
float lambda=1/(float)rate;
double bincoeff_res=0;
printf("%d choose %d\n", n,k);

char mystr[MAX];
	for (k=1; k<=n; k++)
	{
	//strcpy(mystr,bin_coeff(n,k)); //used when using gmp
	bincoeff_res=bin_coeff(n,k);
	reliability_t+=bincoeff_res*pow(expf(-lambda*t),k)*pow(1-expf(-lambda*t),(n-k));
	}
return reliability_t;
}//end wolsten

/* simple failure over time for parallel system with different failure rates.
* wolstenholme 
* ***/


double get_seconds(void) { /* to read time */
struct timeval tval;
gettimeofday(&tval,NULL);
return ((double)tval.tv_sec+(double)tval.tv_usec/1000000.0);
}


/* Daly 2006
in: m = mtti
in:  delta = time to write a checkpoint file
out: "topt" is the optimum compute time between writing checkpoint files.
*/ 
double topt(float m, float delta)
	{
	double result; 

	if (delta < (0.5*m))result = sqrt(2*delta*m)-delta;
	if (delta >= (0.5*m))result = m;

	return result;
	}

/* old  reliable, n choose k function */
int bin_coeff(int n, int m)
{
  size nfac;
  size mfac;
  size nmfac;
  size result;

    nfac = factorial(n);
    mfac = factorial(m);
    nmfac = factorial(n-m);
    result = nfac / (nmfac * mfac);
return result;
}
//here  alpha can be our mttf, beta is 2 per Wolstenholme pg. 26
double Weibull(double value,double alpha, double beta){
  /*input: scale paramter alpha, shape parameter beta, time value t (note: t>= 0) 
 *  *  output: Weibull probability at time value given input shape and scale values */
  double res;
  double pow(double x, double y);
  double exp(double x);
  res = (beta/alpha)*pow((value/alpha),(beta-1))*exp(-pow((value/alpha),beta));
  return res;
}

double Weibull_reliability(double value, double alpha, double beta){
  double res;
  double pow(double x, double y);
  double exp(double x);
  res = exp(-pow((value/alpha),beta));
  return res;

}

double Weibull_hazard(double value, double alpha, double beta){
  double res, c;
  double pow(double x, double y);
  c = pow(alpha,beta);
  res = (beta/c) * pow(value,(beta-1));
  return res;

}





