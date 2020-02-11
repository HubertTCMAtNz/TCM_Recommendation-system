from sklearn.model_selection import train_test_split
f1=open('bing.txt','r')
f2=open('fang.txt','r')

line1=f1.readlines()
line2=f2.readlines()
bi=[]
for line in line1:
    line=line.replace('\n','')
    x=line.split(' ')
    bi.append(x)


fa=[]
for line in line2:
    line=line.replace('\n','')
    x=line.split(' ')
    fa.append(x)


import numpy as np

bi_a=np.array(bi)

fa_a=np.array(fa)


label1=bi_a[:,0]


fe1=bi_a[:,1:]
fe1= fe1.astype(np.float64)
label1= label1.astype(np.int)


label2=fa_a[:,0]
fe2=fa_a[:,1:]
fe2= fe2.astype(np.float64)
label2= label2.astype(np.int)




train_X,test_X, train_y, test_y = train_test_split(fe1,label1,test_size=0.2)

from math import sqrt

def knn(x,k):
    dis=[sqrt(np.sum((g-x)**2))for g in fe2]
    nearest=np.argsort(dis)
    topK_k=[label2[i] for i in nearest[:k]]
    #print(topK_k)
    p=0
    ans =[]
    print('匹配的药方如下：')
    for h in nearest[:k]:
        print(topK_k[p],'欧式距离是：',dis[h])
        ans.append(topK_k[p])
        p = p + 1
    return ans

err=0
predicted =[]
j=0
ll=list(fe2)
te=list(test_X)
ty=list(test_y)
f4=open('graph_edges_bing-fang-relation.txt','r')

dic={}
all1=[]
set1=set()
set2=set()
lines=f4.readlines()
for line in lines:
    line=line.replace('\n','')
    x=line.split(' ')
    set1.add(x[0])
    set2.add(x[1])
    all1.append(x)
print(len(set1))
print(len(set2))

for k in set2:
    v=[]
    for i in all1:
        if k in i:
            v.append(i[0])
    dic[k]=v
j=0
test_X=list(test_X)
ri=0
for x in test_X:
    print('*************',j,'*************')
    print(test_y[j])
    ans=knn(x,15)
    # fang=[]
    fang=dic.get(str(test_y[j]))
    fang=list(map(int,fang))
    print('该病对应的全部药方是：',fang)
    print('推荐的全部药方是：',ans)
    ins=list(set(fang).intersection(set(ans)))

    if(len(ins)!=0):
        ri=ri+1
    j=j+1
print("test 个数为：",len(test_X))
print("hit 个数为：",ri)
print("命中率为：",ri/len(test_X))

