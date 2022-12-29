#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>


// All hexagon cells are in the pointy-top orientation
// One cell has 4 slope edges and 2 vertical edges
//            /\
//            ||
//            \/



int main(int argc, char ** argv)
{
  int NL;      // square mesh length and width, must be positive and even
  int ND;      // mesh depth, must be >=5
  int NT;      // # of trcers, must be psitive

  char filename[20] = "";

  if (argc != 4 ) {
     printf("3 mesh arguments are required: LENGTH DEPTH NTRACERS\n");
     return 1;
  }
  else {
    NL = atoi(argv[1]);
    ND = atoi(argv[2]);
    NT = atoi(argv[3]);
  }

  if (NL <= 0) {
    printf("Mesh length must be positive\n");
    return 1;
  }
  if (NL%2 != 0) {
    printf("Mesh length must be even\n");
    return 1;
  }
  if (ND < 5) {
    printf("Mesh depth must be >= 5\n");
    return 1;
  }
  if (NL <= 0) {
    printf("Number of tracers must be positive\n");
    return 1;
  }

  strcat(filename, argv[1]);
  strcat(filename, "x");
  strcat(filename, argv[1]);
  strcat(filename, "x");
  strcat(filename, argv[2]);
  strcat(filename, "_");
  strcat(filename, argv[3]);
  strcat(filename, ".dat");
  printf("Generating a %d x %d x %d mesh with %d TRACERS\n",NL,NL,ND,NT);
  printf("Writing to file: %s\n",filename);

  // Compute various sizes
  int NH = 2;                       // Halo size
  int N0 = NL;
  int N2 = NL + NH * 2;
  int NSLOPEDGES = 2 * NL + 1;      // Slope edges per row
  int NVERTEDGES = NL + 1;          // Vertical edges per row
  int LSLOPEDGES = NL + 1;          // Number of slope edge rows
  int LVERTEDGES = NL;              // Number of vertical edge rows


  // Numbering non-halo cells first and then halo cells line by line
  int **iCell = (int**)malloc(N2 * sizeof(int*));
  for (int i = 0; i < N2; ++i) iCell[i] = (int*)malloc(N2 * sizeof(int));
  int nCell = 1;
  for (int i=2; i<2+NL; i++) for (int j=2; j<2+NL; j++) iCell[i][j] = nCell++;
  for (int i=0; i<N2; i++) iCell[0][i] = nCell++;
  for (int i=0; i<N2; i++) iCell[1][i] = nCell++;
  for (int i=2; i<2+NL; i++) {
    iCell[i][0] = nCell++;
    iCell[i][1] = nCell++;
    iCell[i][N2-2] = nCell++;
    iCell[i][N2-1] = nCell++;
  }
  for (int i=0; i<N2; i++) iCell[N2-2][i] = nCell++;
  for (int i=0; i<N2; i++) iCell[N2-1][i] = nCell++;


  // Numbering all slope and vertical edges
  int **iSEdge = (int**)malloc(LSLOPEDGES * sizeof(int*));
  for (int i = 0; i < LSLOPEDGES; ++i) iSEdge[i] = (int*)malloc(NSLOPEDGES * sizeof(int));
  int **iVEdge = (int**)malloc(LVERTEDGES * sizeof(int*));
  for (int i = 0; i < LVERTEDGES; ++i) iVEdge[i] = (int*)malloc(NVERTEDGES * sizeof(int));
  int nEdge = 1;
  for (int i=0; i<LVERTEDGES; i++) {
    for (int j=0; j<NSLOPEDGES; j++) iSEdge[i][j] = nEdge++;
    for (int j=0; j<NVERTEDGES; j++) iVEdge[i][j] = nEdge++;
  }
  for (int j=0; j<NSLOPEDGES; j++) iSEdge[LSLOPEDGES-1][j] = nEdge++;


  // Allocate memory for storing various indices
  int nEdgesAll = NSLOPEDGES * LSLOPEDGES + NVERTEDGES * LVERTEDGES;
  int nCellsAll = N0 * N0;
  int nCellsAll2 = N2 * N2;
  int *nAdvCellsForEdge = (int*)malloc(nEdgesAll*sizeof(int));
  for (int i=0;i<nEdgesAll;i++) nAdvCellsForEdge[i] = 10;                                     // Each edge has 10 neighboring cells in regular hexagonal mesh
  int **cellsOnEdge = (int**)malloc((nEdgesAll+1) * sizeof(int*));
  for (int i = 0; i < (nEdgesAll+1); ++i) cellsOnEdge[i] = (int*)malloc(2 * sizeof(int));     // Each edge has 2 cells sharing this edge
  int **edgesOnCell = (int**)malloc((nCellsAll+1) * sizeof(int*)); 
  for (int i = 0; i < (nCellsAll+1); ++i) edgesOnCell[i] = (int*)malloc(6 * sizeof(int));     // Each cell has 6 edges
  int **advCellsForEdge = (int**)malloc((nEdgesAll+1) * sizeof(int*));
  for (int i = 0; i < (nEdgesAll+1); ++i) advCellsForEdge[i] = (int*)malloc(10 * sizeof(int));


  // Generating various indices
  int xCell, xEdge, ptrCell, ptrEdge;
  for (int i=0; i<N0/2; i++) {                           // Iterate every 2 rows
    xCell = i*2 + 2;                                     // Starting cell row number 
    xEdge = i*2;                                         // Starting edge row number
    ptrCell = i*N0*2+1;                                  // Starting cell number
    ptrEdge = i*(NSLOPEDGES+NVERTEDGES)*2+1;           // Starting edge number

    // Odd cell row
    for (int j=0; j<N0; j++) {
      edgesOnCell[ptrCell][0] = iSEdge[xEdge][j*2];
      edgesOnCell[ptrCell][1] = iSEdge[xEdge][j*2+1];
      edgesOnCell[ptrCell][2] = iVEdge[xEdge][j];
      edgesOnCell[ptrCell][3] = iVEdge[xEdge][j+1];
      edgesOnCell[ptrCell][4] = iSEdge[xEdge+1][j*2];
      edgesOnCell[ptrCell][5] = iSEdge[xEdge+1][j*2+1];
      ptrCell++;
    }
    xEdge++;

    // Even cell row
    for (int j=0; j<N0; j++) {
      edgesOnCell[ptrCell][0] = iSEdge[xEdge][j*2+1];
      edgesOnCell[ptrCell][1] = iSEdge[xEdge][j*2+2];
      edgesOnCell[ptrCell][2] = iVEdge[xEdge][j];
      edgesOnCell[ptrCell][3] = iVEdge[xEdge][j+1];
      edgesOnCell[ptrCell][4] = iSEdge[xEdge+1][j*2+1];
      edgesOnCell[ptrCell][5] = iSEdge[xEdge+1][j*2+2];
      ptrCell++;
    }

   
    // Generating neighboring indices for the top slope edges of the odd cell row
    for (int j=2; j<2+N0; j++) {
      advCellsForEdge[ptrEdge][0] = iCell[xCell-2][j-1];
      advCellsForEdge[ptrEdge][1] = iCell[xCell-2][j];
      advCellsForEdge[ptrEdge][2] = iCell[xCell-1][j-2];
      advCellsForEdge[ptrEdge][3] = iCell[xCell-1][j-1];
      advCellsForEdge[ptrEdge][4] = iCell[xCell-1][j];
      advCellsForEdge[ptrEdge][5] = iCell[xCell][j-1];
      advCellsForEdge[ptrEdge][6] = iCell[xCell][j];
      advCellsForEdge[ptrEdge][7] = iCell[xCell][j+1];
      advCellsForEdge[ptrEdge][8] = iCell[xCell+1][j-1];
      advCellsForEdge[ptrEdge][9] = iCell[xCell+1][j];
      cellsOnEdge[ptrEdge][0] = iCell[xCell-1][j-1];
      cellsOnEdge[ptrEdge][1] = iCell[xCell][j];
      ptrEdge++;
      advCellsForEdge[ptrEdge][0] = iCell[xCell-2][j];
      advCellsForEdge[ptrEdge][1] = iCell[xCell-2][j+1];
      advCellsForEdge[ptrEdge][2] = iCell[xCell-1][j-1];
      advCellsForEdge[ptrEdge][3] = iCell[xCell-1][j];
      advCellsForEdge[ptrEdge][4] = iCell[xCell-1][j+1];
      advCellsForEdge[ptrEdge][5] = iCell[xCell][j-1];
      advCellsForEdge[ptrEdge][6] = iCell[xCell][j];
      advCellsForEdge[ptrEdge][7] = iCell[xCell][j+1];
      advCellsForEdge[ptrEdge][8] = iCell[xCell+1][j-1];
      advCellsForEdge[ptrEdge][9] = iCell[xCell+1][j];
      cellsOnEdge[ptrEdge][0] = iCell[xCell-1][j];
      cellsOnEdge[ptrEdge][1] = iCell[xCell][j];
      ptrEdge++;
    }
    advCellsForEdge[ptrEdge][0] = iCell[xCell-2][1+N0];
    advCellsForEdge[ptrEdge][1] = iCell[xCell-2][2+N0];
    advCellsForEdge[ptrEdge][2] = iCell[xCell-1][N0];
    advCellsForEdge[ptrEdge][3] = iCell[xCell-1][1+N0];
    advCellsForEdge[ptrEdge][4] = iCell[xCell-1][2+N0];
    advCellsForEdge[ptrEdge][5] = iCell[xCell][1+N0];
    advCellsForEdge[ptrEdge][6] = iCell[xCell][2+N0];
    advCellsForEdge[ptrEdge][7] = iCell[xCell][3+N0];
    advCellsForEdge[ptrEdge][8] = iCell[xCell+1][1+N0];
    advCellsForEdge[ptrEdge][9] = iCell[xCell+1][2+N0];
    cellsOnEdge[ptrEdge][0] = iCell[xCell-1][1+N0];
    cellsOnEdge[ptrEdge][1] = iCell[xCell][2+N0];
    ptrEdge++;

  
    // Generating neighboring indices for vertical edges of the odd cell row
    for (int j=2; j<3+N0; j++) {
      advCellsForEdge[ptrEdge][0] = iCell[xCell-1][j-2];
      advCellsForEdge[ptrEdge][1] = iCell[xCell-1][j-1];
      advCellsForEdge[ptrEdge][2] = iCell[xCell-1][j];
      advCellsForEdge[ptrEdge][3] = iCell[xCell][j-2];
      advCellsForEdge[ptrEdge][4] = iCell[xCell][j-1];
      advCellsForEdge[ptrEdge][5] = iCell[xCell][j];
      advCellsForEdge[ptrEdge][6] = iCell[xCell][j+1];
      advCellsForEdge[ptrEdge][7] = iCell[xCell+1][j-2];
      advCellsForEdge[ptrEdge][8] = iCell[xCell+1][j-1];
      advCellsForEdge[ptrEdge][9] = iCell[xCell+1][j];
      cellsOnEdge[ptrEdge][0] = iCell[xCell][j-1];
      cellsOnEdge[ptrEdge][1] = iCell[xCell][j];
      ptrEdge++;
    }
    xCell++;
    advCellsForEdge[ptrEdge][0] = iCell[xCell-2][1];
    advCellsForEdge[ptrEdge][1] = iCell[xCell-2][2];
    advCellsForEdge[ptrEdge][2] = iCell[xCell-1][1];
    advCellsForEdge[ptrEdge][3] = iCell[xCell-1][2];
    advCellsForEdge[ptrEdge][4] = iCell[xCell-1][3];
    advCellsForEdge[ptrEdge][5] = iCell[xCell][0];
    advCellsForEdge[ptrEdge][6] = iCell[xCell][1];
    advCellsForEdge[ptrEdge][7] = iCell[xCell][2];
    advCellsForEdge[ptrEdge][8] = iCell[xCell+1][1];
    advCellsForEdge[ptrEdge][9] = iCell[xCell+1][2];
    cellsOnEdge[ptrEdge][0] = iCell[xCell-1][2];
    cellsOnEdge[ptrEdge][1] = iCell[xCell][1];
    ptrEdge++;


    // Generating neighboring indices for top slope edges of the even cell row
    for (int j=2; j<2+N0; j++) {
      advCellsForEdge[ptrEdge][0] = iCell[xCell-2][j-1];
      advCellsForEdge[ptrEdge][1] = iCell[xCell-2][j];
      advCellsForEdge[ptrEdge][2] = iCell[xCell-1][j-1];
      advCellsForEdge[ptrEdge][3] = iCell[xCell-1][j];
      advCellsForEdge[ptrEdge][4] = iCell[xCell-1][j+1];
      advCellsForEdge[ptrEdge][5] = iCell[xCell][j-1];
      advCellsForEdge[ptrEdge][6] = iCell[xCell][j];
      advCellsForEdge[ptrEdge][7] = iCell[xCell][j+1];
      advCellsForEdge[ptrEdge][8] = iCell[xCell+1][j];
      advCellsForEdge[ptrEdge][9] = iCell[xCell+1][j+1];
      cellsOnEdge[ptrEdge][0] = iCell[xCell-1][j];
      cellsOnEdge[ptrEdge][1] = iCell[xCell][j];
      ptrEdge++;
      advCellsForEdge[ptrEdge][0] = iCell[xCell-2][j];
      advCellsForEdge[ptrEdge][1] = iCell[xCell-2][j+1];
      advCellsForEdge[ptrEdge][2] = iCell[xCell-1][j];
      advCellsForEdge[ptrEdge][3] = iCell[xCell-1][j+1];
      advCellsForEdge[ptrEdge][4] = iCell[xCell-1][j+2];
      advCellsForEdge[ptrEdge][5] = iCell[xCell][j-1];
      advCellsForEdge[ptrEdge][6] = iCell[xCell][j];
      advCellsForEdge[ptrEdge][7] = iCell[xCell][j+1];
      advCellsForEdge[ptrEdge][8] = iCell[xCell+1][j];
      advCellsForEdge[ptrEdge][9] = iCell[xCell+1][j+1];
      cellsOnEdge[ptrEdge][0] = iCell[xCell-1][j+1];
      cellsOnEdge[ptrEdge][1] = iCell[xCell][j];
      ptrEdge++;
    }


    // Generating neighboring indices for vertical edges of the even cell row
    for (int j=2; j<3+N0; j++) {
      advCellsForEdge[ptrEdge][0] = iCell[xCell-1][j-1];
      advCellsForEdge[ptrEdge][1] = iCell[xCell-1][j];
      advCellsForEdge[ptrEdge][2] = iCell[xCell-1][j+1];
      advCellsForEdge[ptrEdge][3] = iCell[xCell][j-2];
      advCellsForEdge[ptrEdge][4] = iCell[xCell][j-1];
      advCellsForEdge[ptrEdge][5] = iCell[xCell][j];
      advCellsForEdge[ptrEdge][6] = iCell[xCell][j+1];
      advCellsForEdge[ptrEdge][7] = iCell[xCell+1][j-1];
      advCellsForEdge[ptrEdge][8] = iCell[xCell+1][j];
      advCellsForEdge[ptrEdge][9] = iCell[xCell+1][j+1];
      cellsOnEdge[ptrEdge][0] = iCell[xCell][j-1];
      cellsOnEdge[ptrEdge][1] = iCell[xCell][j];
      ptrEdge++;
    }


  }

  // Generating neighboring indices for bottom slope edges of the last cell row
  xCell = 2 + N0;
  for (int j=2; j<2+N0; j++) {
      advCellsForEdge[ptrEdge][0] = iCell[xCell-2][j-1];
      advCellsForEdge[ptrEdge][1] = iCell[xCell-2][j];
      advCellsForEdge[ptrEdge][2] = iCell[xCell-1][j-2];
      advCellsForEdge[ptrEdge][3] = iCell[xCell-1][j-1];
      advCellsForEdge[ptrEdge][4] = iCell[xCell-1][j];
      advCellsForEdge[ptrEdge][5] = iCell[xCell][j-1];
      advCellsForEdge[ptrEdge][6] = iCell[xCell][j];
      advCellsForEdge[ptrEdge][7] = iCell[xCell][j+1];
      advCellsForEdge[ptrEdge][8] = iCell[xCell+1][j-1];
      advCellsForEdge[ptrEdge][9] = iCell[xCell+1][j];
      cellsOnEdge[ptrEdge][0] = iCell[xCell-1][j-1];
      cellsOnEdge[ptrEdge][1] = iCell[xCell][j];
      ptrEdge++;
      advCellsForEdge[ptrEdge][0] = iCell[xCell-2][j];
      advCellsForEdge[ptrEdge][1] = iCell[xCell-2][j+1];
      advCellsForEdge[ptrEdge][2] = iCell[xCell-1][j-1];
      advCellsForEdge[ptrEdge][3] = iCell[xCell-1][j];
      advCellsForEdge[ptrEdge][4] = iCell[xCell-1][j+1];
      advCellsForEdge[ptrEdge][5] = iCell[xCell][j-1];
      advCellsForEdge[ptrEdge][6] = iCell[xCell][j];
      advCellsForEdge[ptrEdge][7] = iCell[xCell][j+1];
      advCellsForEdge[ptrEdge][8] = iCell[xCell+1][j-1];
      advCellsForEdge[ptrEdge][9] = iCell[xCell+1][j];
      cellsOnEdge[ptrEdge][0] = iCell[xCell-1][j];
      cellsOnEdge[ptrEdge][1] = iCell[xCell][j];
      ptrEdge++;
  }
  advCellsForEdge[ptrEdge][0] = iCell[xCell-2][1+N0];
  advCellsForEdge[ptrEdge][1] = iCell[xCell-2][2+N0];
  advCellsForEdge[ptrEdge][2] = iCell[xCell-1][N0];
  advCellsForEdge[ptrEdge][3] = iCell[xCell-1][1+N0];
  advCellsForEdge[ptrEdge][4] = iCell[xCell-1][2+N0];
  advCellsForEdge[ptrEdge][5] = iCell[xCell][1+N0];
  advCellsForEdge[ptrEdge][6] = iCell[xCell][2+N0];
  advCellsForEdge[ptrEdge][7] = iCell[xCell][3+N0];
  advCellsForEdge[ptrEdge][8] = iCell[xCell+1][1+N0];
  advCellsForEdge[ptrEdge][9] = iCell[xCell+1][2+N0];
  cellsOnEdge[ptrEdge][0] = iCell[xCell-1][1+N0];
  cellsOnEdge[ptrEdge][1] = iCell[xCell][2+N0];
  ptrEdge++;


  // Write size info to file
  FILE *fp;
  fp = fopen(filename, "w+");
  fprintf(fp,"nVertLevels\n");
  fprintf(fp,"%d\n",NL);
  fprintf(fp,"nCellsAll\n");
  fprintf(fp,"%d\n",nCellsAll);
  fprintf(fp,"nCellsAll2\n");
  fprintf(fp,"%d\n",nCellsAll2);
  fprintf(fp,"nEdgesAll\n");
  fprintf(fp,"%d\n",nEdgesAll);
  fprintf(fp,"numTracers\n");
  fprintf(fp,"%d\n",NT);


  // Writing physcis data to file
  fprintf(fp,"tracers\n");fprintf(fp,"%d\n",NT);fprintf(fp,"%d\n",NL);fprintf(fp,"%d\n",nCellsAll2);
  for (int i=0; i<NT; i++) for (int j=0; j<NL; j++) for (int k=0; k<nCellsAll2; k++) fprintf(fp,"%f\n",(float)rand()/(float)(RAND_MAX/30));
  fprintf(fp,"normalThicknessFlux\n");fprintf(fp,"%d\n",NL);fprintf(fp,"%d\n",nEdgesAll);
  for (int i=0; i<NL; i++) for (int j=0; j<nEdgesAll; j++) fprintf(fp,"%f\n",(float)rand()/(float)(RAND_MAX)*((float)rand()/(float)(RAND_MAX/2)<1.0?-1.000:1.000));
  fprintf(fp,"w\n");fprintf(fp,"%d\n",NL);fprintf(fp,"%d\n",nCellsAll);
  for (int i=0; i<NL; i++) for (int j=0; j<nCellsAll; j++) fprintf(fp,"%f\n",0.100000);
  fprintf(fp,"layerThickness\n");fprintf(fp,"%d\n",NL);fprintf(fp,"%d\n",nCellsAll);
  for (int i=0; i<NL; i++) for (int j=0; j<nCellsAll; j++) fprintf(fp,"%f\n",1.509999);
  fprintf(fp,"tend\n");fprintf(fp,"%d\n",NT);fprintf(fp,"%d\n",NL);fprintf(fp,"%d\n",nCellsAll2);
  for (int i=0; i<NT; i++) for (int j=0; j<NL; j++) for (int k=0; k<nCellsAll2; k++) fprintf(fp,"%f\n",0.000);
  fprintf(fp,"advCellsForEdge\n");fprintf(fp,"%d\n",nEdgesAll);fprintf(fp,"%d\n",10);
  for (int i=1; i<1+nEdgesAll; i++) for (int j=0; j<10; j++) fprintf(fp,"%d\n",advCellsForEdge[i][j]);
  fprintf(fp,"advCoefs\n");fprintf(fp,"%d\n",nEdgesAll);fprintf(fp,"%d\n",10);
  for (int i=0; i<nEdgesAll; i++) for (int j=0; j<10; j++) fprintf(fp,"%f\n",(float)rand()/(float)(RAND_MAX/20000)+20000.0);
  fprintf(fp,"advCoefs3rd\n");fprintf(fp,"%d\n",nEdgesAll);fprintf(fp,"%d\n",10);
  for (int i=0; i<nEdgesAll; i++) for (int j=0; j<10; j++) fprintf(fp,"%f\n",(float)rand()/(float)(RAND_MAX/20000)+20000.0);
  fprintf(fp,"advMaskHighOrder\n");fprintf(fp,"%d\n",NL);fprintf(fp,"%d\n",nEdgesAll);
  for (int i=0; i<NL; i++) for (int j=0; j<nEdgesAll; j++) fprintf(fp,"%f\n",((float)rand()/(float)(RAND_MAX/2)<1.0?0.000:1.000));
  fprintf(fp,"cellsOnEdge\n");fprintf(fp,"%d\n",nEdgesAll);fprintf(fp,"%d\n",2);
  for (int i=1; i<1+nEdgesAll; i++) for (int j=0; j<2; j++) fprintf(fp,"%d\n",cellsOnEdge[i][j]);
  fprintf(fp,"areaCell\n");fprintf(fp,"%d\n",nCellsAll2);
  for (int i=0; i<nCellsAll2; i++) fprintf(fp,"%f\n",(float)rand()/(float)(RAND_MAX/80000000)+300000000.0);
  fprintf(fp,"dvEdge\n");fprintf(fp,"%d\n",nEdgesAll);
  for (int i=0; i<nEdgesAll; i++) fprintf(fp,"%f\n",(float)rand()/(float)(RAND_MAX/80000)+100000.0);
  fprintf(fp,"edgeSignOnCell\n");fprintf(fp,"%d\n",nCellsAll);fprintf(fp,"%d\n",6);
  for (int i=0; i<nCellsAll; i++) for (int j=0; j<6; j++) fprintf(fp,"%f\n",((float)rand()/(float)(RAND_MAX/2)<1.0?0.000:1.000));
  fprintf(fp,"edgesOnCell\n");fprintf(fp,"%d\n",nCellsAll);fprintf(fp,"%d\n",6);
  for (int i=1; i<1+nCellsAll; i++) for (int j=0; j<6; j++) {fprintf(fp,"%d\n",edgesOnCell[i][j]);}


  fclose(fp);

  return 0;

}




