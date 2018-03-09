#coding=utf8
import math
import decimal
from decimal import Decimal
from trend_detection.generate_blogs_to_signals import load_json

"""
#根据已生成的参考信号，对观测信号进行预测，看其是否会成为热点
"""
class detectTrend():
    def __init__(self):
        pass

    #compute the distance between two signals s and t of the same length
    def dist(self,s,t):
        distance=0
        for i in range(len(s)):
            distance += (s[i]-t[i])**2
        # print distance
        return distance

    #compute the minimum distance between s and all pieces of r of the same length as s
    #s：为观测序列
    #r：为参考序列
    #观测序列的长度小于等于参考序列
    def distToRefrence(self,s,r):
        N_obs=len(s)
        N_ref=len(r)
        mindist=100000000
        for i in range(N_ref-N_obs+1):
            mindist=min(mindist,self.dist(r[i:i+N_obs],s))
        return mindist

    #uing the distances of an observation to the refrence signals of a certain class, compute a number proportional
    #to the probability that the observation belongs to that class
    def probClass(self,dists,gama):
        prob=0
        for i in range(len(dists)):
            # p =
            prob += math.exp(-gama*dists[i])
        return prob

    def detect(self, ref_pos_lst, ref_neg_lst, observation, gama, theta):

        pos_dists=[]
        neg_dists=[]

        for ref in ref_pos_lst:
            pos_dists.append(self.distToRefrence(observation,ref))
        for ref in ref_neg_lst:
            neg_dists.append(self.distToRefrence(observation,ref))

        print "观测信号与正样本之间的距离：",pos_dists
        print "观测信号与负样本之间的距离：",neg_dists

        pos_prob=self.probClass(pos_dists,gama)
        neg_prob=self.probClass(neg_dists,gama)
        #设置精度
        decimal.getcontext().prec=100
        pos_prob=Decimal(str(pos_prob))
        neg_prob=Decimal(str(neg_prob))
        print "观测信号属于正样本的概率：",pos_prob
        print "观测信号属于负样本的概率：",neg_prob

        if neg_prob == 0.0 and pos_prob != 0.0:
            R = 2
        else:
            R = pos_prob/neg_prob
        print "概率比为：",R

        if R > theta:
            return 1
        else:
            return 0

    def detect_stream(self, observation_stream, N_obs, ref_pos_lst, ref_neg_lst, gama, theta, d_ref):

        consecutivedetections=0
        lst=[]
        steam_length=len(observation_stream)
        for i in range(steam_length-N_obs+1):
        # for i in range(1):
            s=observation_stream[i:N_obs+i]
            result = self.detect(ref_pos_lst=ref_pos_lst,
                                                 ref_neg_lst=ref_neg_lst,
                                                 observation=s,
                                                 gama=gama,
                                                 theta=theta)
            consecutivedetections += result
            lst.append(result)
            print "第", i, "段观测结果：",consecutivedetections
            # if consecutivedetections > d_ref:
            #     return i            #返回时间节点，即该话题即将成为热点
        if d_ref == 1:
            if 1 in lst:
                return lst.index(1)
            else:
                return -1
        else:
            p_l=[1]*d_ref
            flag=0
            for i in range(len(lst)):
                if p_l == lst[i:i+d_ref]:
                    flag=1
                    return i
            if flag==0:
                return -1

#读取观测流信号
def read_obs_stream(filename=r'test/obs_topic_signals/topic_2.json'):
    signal=load_json(filename=filename)
    s=signal['signals_b_s_c_l']
    # print s
    return s
# 遍历文件夹下的所有文件
import os
def visitDir(filepath):
    file_lst = []
    parents = os.listdir(filepath)
    #对其进行排序
    parents.sort()
    for parent in parents:
        # print parent
        child = os.path.join(filepath, parent)
        file_lst.append(child)
        # print child
    print filepath,'中文件数为：',len(file_lst)
    return file_lst
#读取正样本参考信号
def read_pos_ref_signals(filepath=r'hot_predict_test/pos_topic_signals'):
    #遍历文件夹
    file_list=visitDir(filepath)
    pos_lst=[]
    for filename in file_list:
        s=load_json(filename=filename)['signals_b_s_c_l']
        pos_lst.append(s)
        # print s
    return pos_lst
#读取负样本参考信号
def read_neg_ref_signals(filepath=r'hot_predict_test/neg_topic_signals'):
    #遍历文件夹
    file_list=visitDir(filepath)
    neg_lst=[]
    for filename in file_list[0:4]:
        s=load_json(filename=filename)['signals_b_s_c_l']
        neg_lst.append(s)
        # print s
    return neg_lst

#测试decimal模块
def test_decimal():
    pass
    print(1.1 + 2.2)
    print (Decimal('1.1') + Decimal('2.2'))  # 3.3

    print (0.1 + 0.1 + 0.1 - 0.3)
    print (Decimal('0.1') + Decimal('0.1') + Decimal('0.1') - Decimal('0.3'))

    print (1.20 + 1.30)  # 2.5
    print (Decimal('1.20') + Decimal('1.30'))  # 2.50

    a=Decimal('1.20') + Decimal('1.30')
    print a, type(a)
    # print 2.01*a

    # Set up a context with limited precision
    c = decimal.getcontext().copy()
    c.prec = 3


    # Create our constant
    pi = c.create_decimal('3.1415')

    # The constant value is rounded off
    print 'PI    :', pi

    # The result of using the constant uses the global context
    print 'RESULT:', decimal.Decimal('2.01') * pi


#读取信号
def read_signals(dir,topic_id_lst,signal_type='signals_b_s_c_l'):

    signal_lst=[]
    for id in topic_id_lst:
        filename = os.path.join(dir,"topic_"+str(id)+'.json')
        signal_lst.append(load_json(filename=filename)[signal_type])
    return signal_lst

#测试热点预测
def test():

    neg_samples=[10,12,14,15,17,19,23,24,29,46,47,48]
    pos_samples=[1,2,3,4,5,6,7,8,9,11,13,16,18,20,21,22,25,26,27,28,30]
    obs_samples=[31,32,33,34,35,36,37,38,39,40,41]
    obs_pos_lst=[49-53,60-65,72-76,83-92]
    obs_neg_lst=[54-59,66-71,77-81,93-114]

    print len(neg_samples)
    print len(pos_samples)
    print len(obs_samples)

    neg_lst=read_signals(dir=r'test/pos_topic_signals',topic_id_lst=neg_samples[:10],signal_type='signals_b_s_c')
    pos_lst=read_signals(dir=r'test/pos_topic_signals',topic_id_lst=pos_samples[:10],signal_type='signals_b_s_c')

    # obs_stream=load_json(filename=r'test/obs_topic_signals/topic_31.json')['signals_b_s_c']
    obs_stream = load_json(filename=r'test/pos_topic_signals/topic_12.json')['signals_b_s_c']

    dt = detectTrend()
    i = dt.detect_stream(
                     observation_stream=obs_stream,
                     N_obs=20,
                     ref_pos_lst=pos_lst,
                     ref_neg_lst=neg_lst,
                     gama=1,
                     theta=1.09,
                     d_ref=2)
    print i


if __name__=='__main__':
    pass
    # test()


    # dt=detectTrend()
    # # dt.distToRefrence(s=[1,2,3,4,5],r=[3,5,6,7,8,9,1,0,4,6,3,2,1])
    # obs_stream=read_obs_stream(filename=r'hot_predict_test/obs_topic_signals/topic_31.json')
    # pos_lst=read_pos_ref_signals(filepath=r'hot_predict_test/pos_topic_signals')
    # neg_lst=read_neg_ref_signals(filepath=r'hot_predict_test/neg_topic_signals')
    #
    # dt.detect_stream(
    #                  observation_stream=obs_stream,
    #                  N_obs=20,
    #                  ref_pos_lst=pos_lst,
    #                  ref_neg_lst=neg_lst,
    #                  gama=1,
    #                  theta=1,
    #                  d_ref=2)

    # test_decimal()


#构建样本信号
def construt_signal_sample():
    pass
    #负样本（长度为60）
    neg_samples1 = [10, 12, 14, 15, 17, 19, 23, 24, 29, 46, 47, 48] #12
    neg_lst1 = read_signals(dir=r'pos_topic_signals', topic_id_lst=neg_samples1, signal_type='signals_b_s_c')
    # obs_neg_lst = [54 - 59, 66 - 71, 77 - 81, 93 - 114]
    neg_samples2= range(54,60)+range(66,72)+range(77,83)+range(93,115)  #40
    neg_lst2 = read_signals(dir=r'obs_topic_signals', topic_id_lst=neg_samples2, signal_type='signals_b_s_c')
    #用于预测的信号
    neg_lst3 = [s[19:78] for s in neg_lst2[0:18]]
    neg_lst=neg_lst1+neg_lst3   #30
    #用于测试的信号
    obs_neg_lst=[s for s in neg_lst2[18:]]  #22


    #正样本
    pos_samples1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13, 16, 18, 20, 21, 22, 25, 26, 27, 28, 30,42,43,44,45] #25
    pos_lst1 = read_signals(dir=r'pos_topic_signals', topic_id_lst=pos_samples1, signal_type='signals_b_s_c')
    # obs_pos_lst = [49 - 53, 60 - 65, 72 - 76, 83 - 92]
    pos_samples2=range(49,54)+range(60,66)+range(72,77)+range(83,93)+[31,32, 33, 34, 35, 36, 37, 38, 39, 40, 41]   #37
    pos_lst2 = read_signals(dir=r'obs_topic_signals', topic_id_lst=pos_samples2, signal_type='signals_b_s_c')

    #用于预测的信号
    pos_lst=pos_lst1+[s[19:78] for s in pos_lst2[0:10]] #35
    #用于测试的信号
    obs_pos_lst=[s for s in pos_lst2[10:]]  #27

    return neg_lst,pos_lst,obs_neg_lst,obs_pos_lst




if __name__=='__main__':
    pass
    neg_lst, pos_lst, obs_neg_lst, obs_pos_lst = construt_signal_sample()
    A,B,C,D=0,0,0,0
    detect_time=[]
    dt = detectTrend()
    for pos in obs_pos_lst:
        flag = dt.detect_stream(
            observation_stream=pos,
            N_obs=20,
            ref_pos_lst=pos_lst,
            ref_neg_lst=neg_lst,
            gama=1,
            theta=1.4,
            d_ref=3)
        #如果预测为-1则说明不是热点，其他值表示将要爆发的时间段
        print flag
        if flag == -1:
            B += 1
        else:
            A += 1
            detect_time.append(flag)

    for neg in obs_neg_lst:
        flag = dt.detect_stream(
            observation_stream=neg,
            N_obs=20,
            ref_pos_lst=pos_lst,
            ref_neg_lst=neg_lst,
            gama=1,
            theta=1.4,
            d_ref=2)
        #如果预测为-1则说明不是热点，其他值表示将要爆发的时间段
        print flag
        if flag == -1:
            D += 1
        else:
            C += 1

    print "A:",A
    print "B:", B
    print "C:", C
    print "D:",D
    print "正确率：",(A+D)/(A+B+C+D+1.0)
    r=A/(A+C+1.0)
    print "召回率：",r
    p=A/(A+B+1.0)
    print "精准率：",p
    print "F1值：",2*p*r/(p+r)

    if len(detect_time)!=0:
        t=[60-t for t in detect_time]
        averge_t=sum(t)*10.0/len(t)
        print "平均预测提前时间为",averge_t,"(分钟)"




