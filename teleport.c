#include <stdio.h>
#include <inttypes.h>

#define ARRAYSIZE 32768
int16_t memo[ARRAYSIZE][ARRAYSIZE];
int hits = 0, calls = 0, h = 0;

int main()
{
  int a, b, i, j, res;
  //FILE *fp;
  //fp = fopen("results.txt", "w+");
  a = 4;
  b = 1;
  for ( h = 0; h < ARRAYSIZE; h++) {
    for ( i = 0; i < ARRAYSIZE; i++) {
      for ( j = 0; j < ARRAYSIZE; j++) {
	memo[i][j] = -1;
      }
    }
    if ( h % 512 == 0) {
      printf("iteration #%6d\n", h);
      fflush(stdout);
    }
    calls = 0;
    hits = 0;
    res = fn2(a, b);
    if ( res == 6 ) {
      printf("***********************\n");
      //fprintf(fp, "%d, %d, calls=%d, hits=%d\n", h, res, calls, hits);
      printf("%d, %d\n", h, res);
      fflush(stdout);
    }
  }
}

/*
 * basic function
int fn1(int a, int b) {
  if ( a == 0 ) {
    return (b + 1) % ARRAYSIZE;
  }

  if ( b == 0 ) {
    return (h + 1) % ARRAYSIZE;
  }
  return fn1(a - 1, fn1(a, b - 1));
}
*/

/* optimised in various ways */
int fn2(int a, int b) {
  calls++;
  if ( memo[a][b] != -1 ) {
    hits++;
    return memo[a][b];
  }
  if ( a == 0 ) {
    memo[a][b] = (b + 1) % ARRAYSIZE;
    return memo[a][b];
  }
  if ( b == 0 ) {
    memo[a][b] = fn2(a - 1, h);
    return memo[a][b];
  }
  if ( a == 1 ) {
    memo[a][b] = (h + 1 + b) % ARRAYSIZE;
    return memo[a][b];
  }
  if ( a == 2 ) {
    memo[a][b] = (h * (b + 2) + b + 1) % ARRAYSIZE;
    return memo[a][b];
  }
  memo[a][b] = fn2(a - 1, fn2(a, b - 1));
  return memo[a][b];
}
