import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import linprog
from shapely.geometry import Polygon
eps = 0.05
max_beta = 10

#Считывание данных из файла со сдвигом
def read_data(file):
    list = []
    f = open('.\\adc18ch_experiments\\Bazenov\\'+file)
    line = f.readline()
    strs = line.split(' ')
    stop_position = int(strs[-1])
    for line in f:
        strs = line.split('    ')
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
        st.append(((data[i]- zero_data[i]-eps)))
        fin.append(((data[i]- zero_data[i]+eps)))
    mode = mode_mu(st, fin)
    return mode[0]

'''#Исправление данных другим образом
def correct_data(data, zero_data):
    new_data = []
    for i in range(len(data)):
        new_data.append(round(data[i]- zero_data[i], 5))
    m = np.mean(new_data)
    return [m-eps, m+eps]'''

#Построение выборки
def get_data(num):
    st, fin = [], []
    foldernums =['-0_5V','-0_25V','+0_25V','+0_5V']
    zero_data = read_data('ZeroLine\\ZeroLine_' + str(num) +'.txt')
    for name in foldernums:
        filename = name +'\\'+ name +'_'+str(num) + '.txt'
        data = read_data(filename)
        #zero_data=[0]*len(data)
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
    return answer.x

#График с регрессией
def draw(st, fin, x, b0, b1, show):
    plt.plot([x[0], x[-1]], [x[0]*b1+b0, x[-1]*b1+b0], color='deeppink', label='b0+b1*x', linewidth = 1)
    for i in range(len(st)):
        plt.plot([x[i], x[i]], [st[i],fin[i]], color='darkslateblue')
        #plt.scatter(x[i], (fin[i]+st[i])/2, color='darkslateblue')
    plt.grid()
    plt.legend()
    plt.xlabel('x')
    plt.ylabel('y')
    if show:
        plt.show()

#График информационного множества
def draw_information_set(y_st, y_fin, x, b0, b1):
    b=[b1-0.2, b1+0.2]
    line=['--',':','-.','-']
    for i in range(len(x)):
        plt.plot(b, [y_fin[i]-x[i]*b[0], y_fin[i]-x[i]*b[1]], line[i], color='darksalmon', label='up_'+str(i+1))
        plt.plot(b, [y_st[i]-x[i]*b[0], y_st[i]-x[i]*b[1]], line[i], color = 'darkseagreen', label='down_'+str(i+1))
    plt.scatter(b1, b0, color='darkslateblue', label = '(b1, b0)')
    plt.legend()
    plt.xlabel('beta_1')
    plt.ylabel('beta_0')
    plt.show()

#Границы информационного множества
def edge_set(y_st, y_fin, x, idx):
    edge = Polygon((
        (-max_beta, y_st[idx] + max_beta * x[idx] ),
        (-max_beta, y_fin[idx] + max_beta * x[idx]),
        (max_beta, y_fin[idx] - max_beta * x[idx] ),
        (max_beta, y_st[idx] - max_beta * x[idx] )
    ))
    return edge

#Границы информационного множества и внешние оценки параметров
def get_min_max_beta(y_st, y_fin, x): 
    edges = edge_set(y_st, y_fin, x, 0)
    for i in range(1, len(x)):
        edges = edges.intersection(edge_set(y_st, y_fin, x, i))
    angles_coord = edges.exterior.xy
    beta_0 =[min(angles_coord[1]), max(angles_coord[1])]    
    beta_1 =[min(angles_coord[0]), max(angles_coord[0])]    
    return beta_0, beta_1, edges

#График коридора совместных зависимостей
def draw_corridor(y_st, y_fin, x, b0, b1, edges):
    y_min, y_max = [], []
    delta = abs(x[1] - x[0])
    x_coridor = [x[0] - 2*delta, x[0] - delta] + x + [x[-1] + delta, x[-1] + 2*delta]
    for xc in x_coridor:
        y = [edges.exterior.xy[1][i]+ edges.exterior.xy[0][i] * xc for i in range(len(edges.exterior.xy[1]))]
        y_min.append(min(y))
        y_max.append(max(y))
    plt.fill_between(x_coridor, y_min, y_max, alpha=0.5, label='corridor', color = 'cyan')
    plt.plot(x_coridor, y_min, color = 'cadetblue', linewidth = 0.5)
    plt.plot(x_coridor, y_max, color = 'cadetblue',  linewidth = 0.5)
    draw(y_st, y_fin, x, b0, b1, False)
    plt.legend()
    plt.show()


#Анализ выборки
def data_analysis(y_st, y_fin, x):
    answer = linear_regression(y_st, y_fin, x)
    b0, b1 = answer[-2], answer[-1]
    print(b0, b1)
    draw(y_st, y_fin, x, b0, b1, True)
    draw_information_set(y_st, y_fin, x, b0, b1)
    beta_0, beta_1, edges = get_min_max_beta(y_st, y_fin, x)
    print(beta_0, beta_1)
    draw_corridor(y_st, y_fin, x, b0, b1, edges)


if __name__ == '__main__':
    x = [-0.5, -0.25, 0.25, 0.5]
    y_st, y_fin = get_data(1)
    data_analysis(y_st, y_fin, x)
