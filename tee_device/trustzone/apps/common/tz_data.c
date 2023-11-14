#include "tz_data.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


void matrix_initialize(SMatrix *m, int rows, int cols)
{
    m->rows = rows;
    m->cols = cols;
    // 单个id占用256B
    m->data = malloc(rows * cols * sizeof(char*));
    m->head = malloc(cols * sizeof(char*));
}


char** get_smatrix_col(SMatrix *m, const char *col_name)
{
    int col = 0;
    for (int i=0;i<m->cols;i++)
    {
        // printf("%s ",m->head[i]);
        if(strcmp(m->head[i], col_name)==0)
        {
            col=i;
            break;
        }
    }
    // get col data
    char **res = malloc(sizeof(char*)*m->rows);
    // printf("current col is :%d\n",col);
    for (int i=0; i<m->rows; i++)
    {
        int len = strlen(m->data[i*m->cols]) + 1;
        char *data = (char *)malloc(sizeof(char)*len);
        memcpy(data, m->data[i*m->cols], len -1);
        data[len -1] = '\0';
        // printf("%s ", m->data[i*col]);
        res[i] = data;
        // printf("%s ",res[i-1]);
    }
    return res;
}


void free_matrix(SMatrix *m)
{
    if (m != NULL)
    {
        if (m->data != NULL)
        {
            for(int i=0 ;i< m->rows*m->cols;i++)free(m->data[i]);
        }
        free(m);
    }
}
