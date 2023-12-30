import numpy as np
from scipy.optimize import linprog
from interval_arithmetic import mult_vec, Twin

#Чтение матрицы из файла
def get_A(file):
    return np.loadtxt(file, delimiter=' ')

#Правая часть ИСЛАУ
def get_b(n, A):
    b = []
    d = 0.000001
    rnd = 1
    for i in range(n):
        rnd = sum(A[i]*100)
        #b.append(Twin(rnd-d, rnd+d, rnd-2*d, rnd+2*d))
        if i == 1:
             b.append(Twin(rnd-30*d, rnd + 30*d, rnd-31*d, rnd+31*d))
        else:
            b.append(Twin(rnd-d, rnd+d, rnd-2*d, rnd+2*d))
    return b

#Матрица левой части ограничительных неравенств
def left_part(b, A):
    n = len(A)
    lp = []
    for i in range(n):
        lp_i = [0] * n
        lp_i[i] = - b[i].rad()
        lp.append(lp_i + list(A[i]))
    for i in range(n):
        lp_i = [0] * n
        lp_i[i] = - b[i].rad()
        lp.append(lp_i + list(-1*A[i]))
    return lp

#Вектор правой части ограничительных неравенств
def right_part(b):
    rp = []
    for i in range(len(b)):
        rp.append(b[i].mid())
    for i in range(len(b)):
        rp.append(- b[i].mid())
    return rp

#Решение оптимизационной задачи
def regression(b, A):
    target_function = [1]*len(b) + [0]*len(A[0])
    lp = left_part(b, A)
    rp = right_part(b)
    n, m = len(A), len(A[0])
    bounds = [(0,None) for i in range(n)] + [(None,None) for i in range(m)]
    answer = linprog(c=target_function, A_ub=lp, b_ub=rp, bounds=bounds, method="highs")
    w = answer.x[:n]
    x = answer.x[n:]
    return w, x

#Разделение вектора твинов на два вектора интервалов
def get_st_fin(b):
    b0, b1=[], []
    for bi in b:
        b0.append(bi.Xl)
        b1.append(bi.X)
    return b0, b1

#Точечное решение системы с твином в правой части
def points_solution(A, b):
    b0, b1 = get_st_fin(b)
    w0, x0 = regression(b0, A)
    w1, x1  = regression(b1, A)
    #print('w0 = ',w0)
    #print('w1 = ',w1)
    return x0, x1

#Решение системы с твином/интервал в правой части 
def solution(A, b):
    x = [0]*len(A)
    invA = list(np.linalg.inv(np.array(A)))
    for i in range(len(A)):
        x[i] = mult_vec(b, invA[i])
    return x

def print_vec(vec):
    for v in vec:
        v.print()
    print('')

#Исследование собственных значений матрицы
def eigenvalues_analysis(A):
    e_val, _ = np.linalg.eig(np.array(A))
    print([round(e, 5) for e in e_val])
    max_val = abs(max(e_val))
    sum_val = 0
    for v in e_val:
        if v!=max_val:
            sum_val+=abs(v)
    print(max_val, sum_val)


if __name__ == '__main__':
    A = get_A("matrix.txt")
    b = get_b(len(A), A)

    #Точечное решение
    x_in, x_out = points_solution(A, b)
    print(x_in)
    print(x_out)
    
    #Решение отдельно для внутренних и внешних оценок
    b0, b1 = get_st_fin(b) 
    x_in = solution(A, b0)
    print_vec(x_in)
    x_out = solution(A, b1)
    print_vec(x_out)

    #Решение с использованием твинной арифметрики
    x = solution(A, b)
    print_vec(x)
    
    #Анализ собственных чисел
    eigenvalues_analysis(A)
    
 
    

