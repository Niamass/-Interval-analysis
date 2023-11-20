import matplotlib.pyplot as plt
import numpy as np
eps = 0.005

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
    return list, stop_position

#Исправление данных - обынтерваливание и вычитание нуля
def correct_data(data, zero_data):
    st, fin = [], []
    for i in range(len(data)):
        st.append(data[i]- zero_data[i]-eps)
        fin.append(data[i]- zero_data[i]+eps)
    return st, fin

#Построение выборки
def get_data(filename):
    data, sp = read_data(filename)
    num_of_file = filename[filename.rfind('_') + 1 : filename.find('.')]
    zero_data, _ = read_data('ZeroLine\\ZeroLine_' + num_of_file +'.txt')
    st, fin = correct_data(data, zero_data)
    return st, fin

#Оценки выборки
def estimations_IJ(st, fin):
    I_down = max(st)
    I_up = min(fin)
    J_down = min(st)
    J_up = max(fin)
    return I_down, I_up, J_down, J_up

#Мера Жаккара
def mera_Jaccard(st, fin):
    JK = (min(fin)-max(st))/(max(fin)-min(st))
    return JK

#Мера Оскорбина
def mera_Oskorbin(st, fin):
    return (max(st)-min(fin))/eps

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
    return nums, intervals_mu, mu, mode

#График моды
def draw_Mu(nums, intervals_mu, name):
    for i in range(len(nums)):
        plt.plot(intervals_mu[i], [nums[i], nums[i]], color='darkslateblue')
    plt.title(name)
    plt.xlabel('intervals')
    plt.ylabel('num')
    plt.show()

#График выборки
def draw(st, fin, name, color):
    I_down, I_up, J_down, J_up = estimations_IJ(st, fin)
    num = len(st)
    for x in range(num):
        plt.plot([x,x], [st[x],fin[x]], color=color)
    plt.plot([0, num-1], [J_up, J_up], color = 'darksalmon', label='J_up')
    plt.plot([0, num-1], [I_up, I_up], color = 'darkslateblue', label='I_up')
    plt.plot([0, num-1], [I_down, I_down], '--', color = 'darkslateblue', label='I_down')
    plt.plot([0, num-1], [J_down, J_down], '--', color = 'darksalmon', label='J_down')
    plt.title(name)
    plt.legend()
    plt.xlabel('n')
    plt.ylabel('intervals')
    plt.show()

#Умножение интервалов
def mult(a, b):
    vec = [a[0]*b[0], a[0]*b[1], a[1]*b[0], a[1]*b[1]]
    return [min(vec), max(vec)]

#Деление интервалов
def div(a,b):
    return mult(a, [1/b[1], 1/b[0]])

#Оценки совместности
def estimations_R(st1, fin1, st2, fin2):
    I_down1, I_up1, J_down1, J_up1 = estimations_IJ(st1, fin1)
    I_down2, I_up2, J_down2, J_up2 = estimations_IJ(st2, fin2)
    R_out = div([J_down2, J_up2], [J_down1, J_up1])
    R_in = div([I_down2, I_up2], [I_down1, I_up1])
    return R_out, R_in

#График зависимости R от JK
def draw_R(R, JK):
    plt.plot(R, JK, color='darkslateblue')
    plt.xlabel('R')
    plt.ylabel('JK')
    plt.show()

#График совмещенных выборок
def draw_connect_data(st, fin):
    I_down, I_up, J_down, J_up = estimations_IJ(st, fin)
    num = len(st)
    plt.subplot()
    for x in range(int(num/2)):
        plt.plot([x,x], [st[x],fin[x]], color='darkseagreen')
    for x in range(int(num/2), num):
        plt.plot([x,x], [st[x],fin[x]], color='cadetblue')
    plt.plot([0, num-1], [J_up, J_up], color = 'darksalmon', label='J_up')
    plt.plot([0, num-1], [I_up, I_up], color = 'darkslateblue', label='I_up')
    plt.plot([0, num-1], [I_down, I_down], '--', color = 'darkslateblue', label='I_down')
    plt.plot([0, num-1], [J_down, J_down], '--', color = 'darksalmon', label='J_down')
    plt.title("X1+R*X2")
    plt.legend()
    plt.xlabel('n')
    plt.ylabel('intervals')
    plt.show()

#Анализ выборки
def data_analysis(st, fin, name, color):
    draw(st, fin, name, color)
    I_down, I_up, J_down, J_up = estimations_IJ(st, fin)
    print("[", round(I_down, 3),",", round(I_up, 3),"] [", round(J_down, 3),",", round(J_up, 3),"]")
    JK = mera_Jaccard(st, fin)
    print("JK = ", round(JK, 3))
    k = mera_Oskorbin(st, fin)
    print("k = ", round(k, 3))
    nums, intervals_mu, mu , mode = mode_mu(st, fin)
    print("mu=", mu, ", Mode = ", mode)
    draw_Mu(nums, intervals_mu, name)

#Анализ совместности выборок
def comp_analysis(st1, fin1, st2, fin2 ):
    R_out, R_in = estimations_R(st1, fin1, st2, fin2)
    print(R_out, R_in)
    JK_list = []
    R_list=[]
    R_max, JK_max= -10, -1
    for R in np.arange(R_in[0], R_in[1], (R_in[1]-R_in[0])/100):
        if R>=0:
            st = st1 + [i * R for i in st2]
            fin = fin1 + [i * R for i in fin2]
        else:
            st = st1 + [i * R for i in fin2]
            fin = fin1 + [i * R for i in st2]
        JK = mera_Jaccard(st, fin)
        if JK > JK_max:
            JK_max = JK
            R_max = R
        R_list.append(R)
        JK_list.append(JK)
    if R_max>=0:
        st = st1 + [i * R_max for i in st2]
        fin = fin1 + [i * R_max for i in fin2]
    else:
        st = st1 + [i * R_max for i in fin2]
        fin = fin1 + [i * R_max for i in st2]
    for i in range(len(JK_list)):
        if JK_list[i]==JK_max:
            print(R_list[i])
    draw_connect_data(st, fin)
    draw_R(R_list, JK_list)
    print("JK = ", round(JK_max, 3))
    return R_list, JK_list


if __name__ == '__main__':
    st1, fin1 = get_data('+0_5V\\+0_5V_1.txt')
    st2, fin2 = get_data('-0_5V\\-0_5V_1.txt')
    data_analysis(st1, fin1, 'X1', 'darkseagreen')
    data_analysis(st2, fin2, 'X2', 'cadetblue')
    comp_analysis(st1, fin1, st2, fin2 )

