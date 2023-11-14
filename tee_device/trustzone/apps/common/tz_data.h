#ifndef TZ_DATA_H_
#define TZ_DATA_H_

struct DMatrix {
    int rows;
    int cols;
    double *data;
};
typedef struct DMatrix DMatrix;


struct SMatrix {
    int rows;
    int cols;
    char **data;
    char **head;
};
typedef struct SMatrix SMatrix;


void matrix_initialize(SMatrix *m, int rows, int cols);

char** get_smatrix_col(SMatrix *m, const char *col_name);

void free_matrix(SMatrix *m);

#endif