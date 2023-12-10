import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import linprog
from shapely.geometry import Polygon
eps =  300

#Считывание данных из файла со сдвигом
def read_data(file, stop_position):
    list = []
    f = open('.\\rawData\\rawData\\'+file)
    for line in f:
        strs = line.split(' ')
        if len(strs)> 1:
            list.append(float(strs[1]))
    f.close()
    list = list[len(list) - stop_position:] + list[:len(list) - stop_position]
    return list

#Мода
def mode_mu(st, fin):
    N = len(st)
    intervals_mu = []
    all_int=st + fin
    all_int.sort()
    for i in range(0, 2*N-1):
        if (all_int[i]!=all_int[i+1]):
            intervals_mu.append([all_int[i], all_int[i+1]])
    nums=[]
    for i in range(len(intervals_mu)):
        nums.append(0)
        for j in range(N):
            if intervals_mu[i][0]>=st[j] and intervals_mu[i][1]<=fin[j]:
                nums[i]+=1
    mode=[]
    mu = max(nums)
    for i in range(len(intervals_mu)):
        if(nums[i]==mu):
            mode.append(intervals_mu[i])
    return mode

#Исправление данных
def correct_data(data, zero_data):
    st, fin = [], []
    for i in range(len(data)):
        st.append(data[i] - zero_data[i] -eps)
        fin.append(data[i] - zero_data[i] +eps)
    mode = mode_mu(st, fin)
    return mode[0]

#Построение выборки
def get_data(x):
    st, fin = [], []
    sp = [31, 670, 484, 831, 547,
           321, 9, 320, 300, 176]
    sp_zero = 443
    zero_data = read_data('0.0V_sp'+ str(sp_zero) + '.dat', sp_zero)
    for i in range(len(x)):
        data = read_data(str(x[i]) + 'V_sp' + str(sp[i]) + '.dat', sp[i])
        y = correct_data(data, zero_data)
        st.append(y[0])
        fin.append(y[1])
    return st, fin

#Матрица левой части ограничительных неравенств
def left_part(y_st, y_fin, x):
    n = len(x)
    lp = []
    for i in range(n):
        lp_i = [0] * (n + 2)
        lp_i[i], lp_i[n], lp_i[n + 1] = - abs(y_fin[i] - y_st[i])/2, 1, x[i]
        lp.append(lp_i)
    for i in range(n):
        lp_i = [0] * (n + 2)
        lp_i[i], lp_i[n], lp_i[n + 1] = - abs(y_fin[i] - y_st[i])/2, -1, -x[i]
        lp.append(lp_i)
    return lp

#Вектор правой части ограничительных неравенств
def right_part(y_st, y_fin):
    rp = []
    for i in range(len(y_st)):
        rp.append((y_st[i] + y_fin[i])/2)
    for i in range(len(y_st)):
        rp.append(-(y_st[i] + y_fin[i])/2)
    return rp

#Поиск параметров линейной регрессии
def linear_regression(y_st, y_fin, x):
    target_function = [1]*len(x) + [0, 0]
    lp = left_part(y_st, y_fin, x)
    rp = right_part(y_st, y_fin)
    answer = linprog(c=target_function, A_ub=lp, b_ub=rp, method="highs")
    w = answer.x[:-2] 
    y_st_new, y_fin_new = y_st.copy(), y_fin.copy()
    for i in range(len(w)):
        if(w[i]>1):
            print(i)
            m = mid(y_st[i], y_fin[i])
            r = rad(y_st[i], y_fin[i])
            y_st_new[i] = m - w[i]* r
            y_fin_new[i] = m + w[i]* r
    
    return answer.x, y_st_new, y_fin_new

#График с регрессией
def draw(st, fin, x, b0, b1, show):
    plt.plot([x[0], x[-1]], [x[0]*b1+b0, x[-1]*b1+b0], color='deeppink', label='b0+b1*x', linewidth = 1)
    for i in range(len(st)):
        plt.plot([x[i], x[i]], [st[i],fin[i]], color='darkslateblue')
    plt.grid()
    plt.legend()
    plt.xlabel('x')
    plt.ylabel('y')
    if show:
        plt.show()

#График информационного множества
def draw_information_set(y_st, y_fin, x, b0, b1, edges):
    b=[b1-1000, b1+1000]
    for i in range(len(x)):
        plt.plot(b, [y_fin[i]-x[i]*b[0], y_fin[i]-x[i]*b[1]], color = (i/10,1-i/10, 0.5), label=str(i))
        plt.plot(b, [y_st[i]-x[i]*b[0], y_st[i]-x[i]*b[1]], color = (i/10,1-i/10, 0.5))
    plt.plot(edges.exterior.xy[0], edges.exterior.xy[1], '--', label = 'information set', color = 'midnightblue')
    plt.legend(loc = 2)
    plt.xlabel('beta_1')
    plt.ylabel('beta_0')
    plt.show()

    #Границы информационного множества
def edge_set(y_st, y_fin, x, idx):
    max_beta = 20000
    edge = Polygon((
        (-max_beta, y_st[idx] + max_beta * x[idx] ),
        (-max_beta, y_fin[idx] + max_beta * x[idx]),
        (max_beta, y_fin[idx] - max_beta * x[idx] ),
        (max_beta, y_st[idx] - max_beta * x[idx] )
    ))
    return edge

#Границы информационного множества
def get_edges(y_st, y_fin, x): 
    edges = edge_set(y_st, y_fin, x, 0)
    for i in range(1, len(x)):
        edges = edges.intersection(edge_set(y_st, y_fin, x, i))
    return edges

#Коридор совместных зависимостей
def build_corridor(x, edges):
    y_min, y_max = [], []
    delta = abs(x[1] - x[0])
    x_coridor = x
    for xc in x_coridor:
        y = [edges.exterior.xy[1][i]+ edges.exterior.xy[0][i] * xc for i in range(len(edges.exterior.xy[1]))]
        y_min.append(min(y))
        y_max.append(max(y))
    return y_min, y_max 

#График коридора совместных зависимостей
def draw_corridor(y_st, y_fin, x, b0, b1, edges):
    y_min, y_max = build_corridor(x, edges)
    plt.fill_between(x, y_min, y_max, alpha=0.5, label='corridor', color = 'cyan')
    plt.plot(x, y_min, color = 'cadetblue', linewidth = 0.5)
    plt.plot(x, y_max, color = 'cadetblue',  linewidth = 0.5)
    draw(y_st, y_fin, x, b0, b1, False)
    plt.legend()
    plt.show()
    return y_min, y_max


def mid(a,b):
    return (a+b)/2

def rad(a,b):
    return (max(a,b) - min(a,b))/2

def draw_status_diagram(y_st, y_fin, y_min, y_max):
    r = []
    l = []
    for i in range(len(y_st)):
        r.append((mid(y_st[i], y_fin[i]) - mid(y_min[i], y_max[i]))/rad(y_st[i], y_fin[i]))
        l.append(rad(y_min[i], y_max[i])/rad(y_st[i], y_fin[i]))
    r_edge = np.linspace(-3,3,300)
    plt.plot([1-abs(ri) for ri in r_edge], r_edge, color='deeppink')
    plt.plot([abs(ri)-1 for ri in r_edge], r_edge, color='deeppink')
    plt.plot([1, 1], [-3, 3], '--', color='cadetblue')
    plt.plot(l, r, 'o', color = 'darkslateblue')
    for i in range(len(r)):
        plt.annotate(str(i), (l[i]-0.04, r[i]+0.04))
        if(abs(r[i])>=l[i]+1):
            print('blowout ', i)
        elif(abs(r[i])<1 - l[i]):
            print('inner ', i)
        elif(abs(r[i])==1 - l[i]):
            print('edge ', i)
        elif(abs(r[i])>1 - l[i]):
            print('outer ', i)
    plt.xlim(0, 2)
    plt.ylim(-3, 3)
    plt.xlabel('l')
    plt.ylabel('r')
    plt.show()


#Анализ выборки
def data_analysis(y_st, y_fin, x):
    answer, y_st1, y_fin1 = linear_regression(y_st, y_fin, x)
    b0, b1 = answer[-2], answer[-1]
    edges = get_edges(y_st1, y_fin1, x)
    draw_information_set(y_st1, y_fin1, x, b0, b1, edges)
    y_min, y_max = draw_corridor(y_st, y_fin, x, b0, b1, edges)
    draw_status_diagram(y_st, y_fin, y_min, y_max)


if __name__ == '__main__':
    x = [round(i,2) for i in np.linspace(-0.45, 0.45, 10)]
    y_st, y_fin = get_data(x)
    data_analysis(y_st, y_fin, x)
