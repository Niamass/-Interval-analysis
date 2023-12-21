import numpy as np
from math import sqrt

DIFF_RADIUS = 0.15
DIST_PIXELS = 0.01

def intersection_points(r, k, b):
    get_sqrt = pow(r, 2)*(1+pow(k, 2)) - pow(b, 2) 
    if(get_sqrt < 0):
        return 0
    elif(get_sqrt == 0):
        return 1
    else:
        return 2

def init_pixels(n):
    xt, yt = 3, 0
    x_pixels = 4
    if (n == 1):
        k = [0]
        b = [0]
        return k, b
    y, k, b, x = [], [], [], []
    x.append(x_pixels)
    y.append(DIST_PIXELS*(n-1)/2)
    k.append((yt-y[0]) / ( xt - x[0]))
    b.append(y[0] - k[0]*x[0])
    for i in range(1, n):
        x.append(x_pixels)
        y.append(y[i-1]-DIST_PIXELS)
        k.append((yt-y[i]) / ( xt - x[i]))
        b.append(y[i] - k[i]*x[i])
    return k, b

def len_c(a, b, c, d):
    return sqrt(abs(a-b)**2 + abs(c-d)**2)

#Построение матрицы томографии
def matrix(coef_k, coef_b, m):
    prevD = 0
    D = 0
    n = len(coef_k) #count of pixel
    A = [ [0]*m for i in range(n) ]
    for i in range(n):
        radius = 0
        prevD = 0
        for j in range(m):
            radius += DIFF_RADIUS
            ip = intersection_points(radius, coef_k[i], coef_b[i])
            if(ip == 0):
                continue
            elif(ip == 1):
                A[i][j] = 0
                prevD = D = 0
            else:
                x1 = (-coef_k[i]*coef_b[i] + sqrt(pow(radius, 2)*(1+pow(coef_k[i], 2)) - pow(coef_b[i], 2) )) / ((1+pow(coef_k[i], 2)))
                x2 = (-coef_k[i]*coef_b[i] - sqrt(pow(radius, 2)*(1+pow(coef_k[i], 2)) - pow(coef_b[i], 2) )) / ((1+pow(coef_k[i], 2)))
                y1 = coef_k[i]*x1 + coef_b[i]
                y2 = coef_k[i]*x2 + coef_b[i]
                D = len_c(x1,x2,y1,y2)
                if prevD == 0:
                    A[i][j] = D
                    prevD = D
                else:
                    A[i][j] = abs(D - prevD)
                    prevD = D
    return A

def print_matrix(A):
    for i in range(len(A)):
        for j in range(len(A[0])):
            print('{:2.3f}'.format(A[i][j]), end=" ") 
        print()

def write_matrix(file, A):
    np.savetxt(file, np.array(A))


if __name__ == '__main__':
    num_pixel = 10 # число строк
    num_circle = 5 # число столбцов
    k, b = init_pixels(num_pixel)
    A = matrix(k, b, num_circle)
    print_matrix(A)
    write_matrix('matrix.txt', A[:int(len(A)/2)])
