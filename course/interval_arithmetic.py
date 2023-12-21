

class Twin:
    def __init__(self, Xl_l, Xl_r, X_l, X_r):
        self.Xl = Interval(Xl_l, Xl_r)
        self.X = Interval(X_l, X_r)
    
    def inner_width(self):
        return self.Xl.width()

    def outer_width(self):
        return self.X.width()
    
    def pq(self, other): 
        if self.inner_width() < 0 and other.inner_width() < 0:
            return float('nan')
        if self.inner_width() < 0:
            p = other.Xl.l + self.X.r
            q = other.Xl.r + self.X.l
        elif other.inner_width() < 0:
            p = self.Xl.l + other.X.r
            q = self.Xl.r + other.X.l 
        else:
            p = min(other.Xl.l + self.X.r, self.Xl.l + other.X.r)
            q = max(other.Xl.r + self.X.l, self.Xl.r + other.X.l )
        return p, q

    #Сумма твинов
    def add(self, other):
        if self==0 or other==0:
            return self if other==0 else other
        p, q = self.pq(other)
        if self.outer_width() <= other.inner_width() or other.outer_width() <= self.inner_width():
            return Twin(p, q, self.X.l + other.X.l, self.X.r + other.X.r)
        else:
            return Twin(float('nan'), float('nan'), self.X.l + other.X.l, self.X.r + other.X.r)

    #Умножение твина на число
    def mult_num(self, a):
        if a >= 0:
            return Twin(a*self.Xl.l, a*self.Xl.r, a*self.X.l, a*self.X.r)
        else:
            return Twin(a*self.Xl.r, a*self.Xl.l, a*self.X.r, a*self.X.l)
        
    def print(self):
        print('[[{0},{1}], [{2},{3}]]'.format(self.Xl.l,self.Xl.r,self.X.l,self.X.r))


class Interval:
    def __init__(self, l, r):
        self.l = l
        self.r = r

    def width(self):
        return abs(self.r - self.l)

    def mid(self):
        return (self.l + self.r)/2
    
    def rad(self):
        return self.width()/2

    def add(self, other):
        if self==0 or other==0:
            return other if self==0 else self
        return Interval(self.l+ other.l, self.r+ other.r)
    
    def mult_num(self, a):
        if a >= 0:
            return Interval(self.l*a, self.r*a)
        else:
            return Interval(self.r*a, self.l*a)

    def print(self):
        print('[{0},{1}]'.format(self.l,self.r))


#Умножение вектора твинов/интрвалов на численный вектор
def mult_vec(b_vec, a_vec):
    sum = b_vec[0].mult_num(a_vec[0])
    for i in range(1, len(b_vec)):
        m = b_vec[i].mult_num(a_vec[i])
        sum = sum.add(m)
    return sum

