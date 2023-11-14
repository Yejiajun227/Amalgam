CC=gcc

# KML库 下载地址 
# https://www.hikunpeng.com/document/detail/zh/kunpengaccel/math-lib/devg-kml/kunpengaccel_kml_16_0011.html


# 单线程不加锁版本: -L /usr/local/kml/lib/kblas/nolocking -lkblas
# 单线程加锁版本: -L /usr/local/kml/lib/kblas/locking -lkblas
# pthread实现多线程版本: -L /usr/local/kml/lib/kblas/pthread -lkblas
# OpenMP实现多线程版本: -L /usr/local/kml/lib/kblas/omp -lkblas
kml: 
	$(CC) -o kml kml.c -I /usr/local/kml/include/  -L /usr/local/kml/lib/kblas/omp -lkblas
