#coding=utf8
import time
import re
import jieba.analyse
import os
import math
import json
import datetime

"""
功能:
    给定话题产生其信号
参数：
    topic：           话题
    based_point:      基准时间点（对热点话题参考信号为其成为热点的时间点，对于非热点话题随机选择一个时间点）
    start_point:      信号起始时间点
    end_point:        信号结束时间点
    
    signal_length:    信号长度
    signal_span:      每个信号的时间跨度  
    
    blog_filepath:    存放微博的文件路径
"""
class GenerateTopicSignals():

    def __init__(self,topic=None):
        pass

    #对原始信号进行处理
    #1、baseline normalization 参数：beta
    #2、spike normalization 参数： alpha
    #3、smothing 参数：N_smooth
    def process_signals(self,original_signal,beta,alpha,N_smooth,b_flag=True):

        #step1:baseline normalization
        if b_flag:
            b=sum(original_signal)
            signals_b =[(s/(float(b)+0.0001))**beta for s in original_signal]
        else:
            signals_b=original_signal

        #step2:spike normalization
        signals_b_s=[float(abs(signals_b[i]-signals_b[i-1]))**alpha for i in range(1,len(original_signal))]
        # signals_b_s的长度较原始信号长度减1
        signals_b_s.insert(0,signals_b[0])  #补齐？？？（可能有问题）

        #step3:smothing
        signals_b_s_c=[]
        signals_b_s_c_l=[]
        for i in range(1, len(signals_b_s)):
            sum_smooth = 0
            for j in range(i - N_smooth, i):
                if j < 0:
                    continue
                sum_smooth += signals_b_s[j]
            signals_b_s_c.append(sum_smooth)
            signals_b_s_c_l.append(math.log(sum_smooth+0.00001))
        #signals_b_s_c和signals_b_s_c_l信号长度较signals_b_s长度减1
        signals_b_s_c.insert(0,signals_b_s[0])  #补齐？？？（可能有问题）
        signals_b_s_c_l.insert(0,math.log(signals_b_s[0]+0.00001)) #补齐？？？（可能有问题）

        print len(original_signal),':',original_signal
        print len(signals_b),':',signals_b
        print len(signals_b_s),':',signals_b_s
        print len(signals_b_s_c),':',signals_b_s_c
        print len(signals_b_s_c_l),':',signals_b_s_c_l

        return signals_b,signals_b_s,signals_b_s_c,signals_b_s_c_l

    #根据话题关联的微博的发布时间形成话题信号，返回
    #start_point：以秒为单位的浮点类型，话题信号起始时间点
    #signal_span：以秒为单位，每个信号的时间跨度
    def generate_signals(self,blog_lst,start_point,signal_length,signal_span):

        #初始化参考信号
        signal = [0] * signal_length
        if len(blog_lst)==0:
            return signal
        #对于话题相关的每条微博
        for blog_dict in blog_lst:
            blog_create_time=blog_dict['blog_create_time']
            #计算微博落在第几个信号内
            i = int(float(blog_create_time - start_point) / signal_span)    #表示微博落在第i个信号内，
            #如果微博落在信号长度之外，跳出循环
            if i >= signal_length or i < 0:
                continue
            #如果微博落在信号长度之内，则对应的信号加1
            signal[i]+=1
        return signal

    #给定话题，在一个微博文件中收集其相关的微博,返回微博列表[{'blog_create_time':float,'blog_text':str}……],可能为空
    #blog_filename形式为：'/data0/shaojie5/source_mblog/data/mblog/20171228/25239839'
    def collect_blogs_for_one_topic_from_file(self,topic,blog_filename,start_point,end_point):

        print "下载文件为：",blog_filename
        blogs_lst=[]
        for line in open(blog_filename).readlines():

            line = line.decode('utf8')
            items = line.strip().strip('\n').split('\t')

            content_dic = eval(items[7])            # 将字符串转化为字典类型
            timestr = content_dic['created_at']     # 提取出微博发布的时间，字符串形式如“Sun Dec 17 23:58:49 +0800 2017”
            # 对微博发布时间进行处理,将“Sun Dec 17 23:58:49 +0800 2017”转化为#转化为时间对象，用秒数来表示时间的浮点数
            time1 = timestr[4:7]    # 提取出月份，形式如：‘Dec’
            time_dic = {
                'Jan': '1',
                'Feb': '2',
                'Mar': '3',
                'Apr ': '4',
                'May': '5',
                'Jun': '6',
                'Jul': '7',
                'Aug': '8',
                'Sep': '9',
                'Oct': '10',
                'Nov': '11',
                'Dec': '12'
            }        #月份词典
            time2 = timestr[8:16]   # 提取出天，小时，分钟，形式如：‘17 23:58’
            year=timestr[26:]
            # time_last = '2017-' + time_dic[time1] + '-' + time2  # 得到微博发布时间，字符串类型形式如“2017-12-17 23:58”
            time_last=year+'-'+time_dic[time1] + '-' + time2
            blog_create_time = time.mktime(time.strptime(time_last, '%Y-%m-%d %H:%M'))  # 转化为时间对象，用秒数来表示时间的浮点数
            # print "微博创建时间为：",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(blog_create_time)),'==',blog_create_time
            # print "起始和终止时间为：",start_point , end_point
            #判断微博发布时间是否在所需信号时间段内
            if blog_create_time>=start_point and blog_create_time<=end_point:
                text = content_dic['text']  # 提取出微博的文本内容,unicode格式
                #对微博文本进行清洗
                blog_text = self.filter_symbol(text)
                # print blog_text
                # 获取微博正文中的关键词，前10个
                # key_words_list = jieba.analyse.extract_tags(blog_text, topK=20, withWeight=False,
                #                                             allowPOS=(("nr", "nr1", "nr2", "ns", "n", "nsf", "nt", "nrf")))
                key_words_list = jieba.analyse.extract_tags(blog_text, topK=10, withWeight=False)
                #设置计数器
                count = 0
                if len(key_words_list)<=3:
                    continue
                # 遍历微博关键词列表
                for keyword in key_words_list:
                    # 如果话题中包含微博中的关键词，计算加1
                    if topic.__contains__(keyword.encode('utf-8')):
                        count += 1
                    # 如果微博中2个以上的关键词在话题中，则微博属于该话题
                    if count >= 2:
                        dict={}
                        dict['blog_create_time']=blog_create_time                   #浮点型
                        dict['blog_text']=blog_text.encode('utf-8')                 #字符串，转化为utf-8格式
                        print "信号开始时间点:", start_point, '==', time.strftime("%Y-%m-%d %H:%M:%S",
                                                                           time.localtime(start_point))
                        # print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(blog_create_time)), ':', blog_text
                        # print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(blog_create_time)), ':', ' '.join(
                        #     key_words_list)
                        print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(blog_create_time)), ':', blog_text.encode('utf-8')

                        print "信号结束时间点:", end_point, '==', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_point))
                        #print blog_create_time,':',blog_text
                        print count
                        blogs_lst.append(dict)
                        break
        return blogs_lst

    def collect_blogs_for_one_topic_from_file_v1(self,topic,blog_filename,start_point,end_point):

        print "下载文件为：",blog_filename
        blogs_lst=[]
        for line in open(blog_filename).readlines():

            line = line.decode('utf8')
            items = line.strip().strip('\n').split('\t')

            content_dic = eval(items[7])            # 将字符串转化为字典类型
            timestr = content_dic['created_at']     # 提取出微博发布的时间，字符串形式如“Sun Dec 17 23:58:49 +0800 2017”
            # 对微博发布时间进行处理,将“Sun Dec 17 23:58:49 +0800 2017”转化为#转化为时间对象，用秒数来表示时间的浮点数
            time1 = timestr[4:7]    # 提取出月份，形式如：‘Dec’
            time_dic = {
                'Jan': '1',
                'Feb': '2',
                'Mar': '3',
                'Apr ': '4',
                'May': '5',
                'Jun': '6',
                'Jul': '7',
                'Aug': '8',
                'Sep': '9',
                'Oct': '10',
                'Nov': '11',
                'Dec': '12'
            }        #月份词典
            time2 = timestr[8:16]   # 提取出天，小时，分钟，形式如：‘17 23:58’
            year=timestr[26:]
            # time_last = '2017-' + time_dic[time1] + '-' + time2  # 得到微博发布时间，字符串类型形式如“2017-12-17 23:58”
            time_last=year+'-'+time_dic[time1] + '-' + time2
            blog_create_time = time.mktime(time.strptime(time_last, '%Y-%m-%d %H:%M'))  # 转化为时间对象，用秒数来表示时间的浮点数
            # print "微博创建时间为：",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(blog_create_time)),'==',blog_create_time
            # print "起始和终止时间为：",start_point , end_point
            #判断微博发布时间是否在所需信号时间段内
            if blog_create_time>=start_point and blog_create_time<=end_point:
                text = content_dic['text']  # 提取出微博的文本内容,unicode格式
                #对微博文本进行清洗
                blog_text = self.filter_symbol(text)
                # print blog_text
                # 获取微博正文中的关键词，前10个
                # key_words_list = jieba.analyse.extract_tags(blog_text, topK=20, withWeight=False,
                #                                             allowPOS=(("nr", "nr1", "nr2", "ns", "n", "nsf", "nt", "nrf")))
                key_words_list = jieba.analyse.extract_tags(blog_text, topK=10, withWeight=False)
                #设置计数器
                count = 0
                if len(key_words_list)<=3:
                    continue

                # 遍历微博关键词列表,只要话题中包含微博中的一个关键词就行
                for keyword in key_words_list:
                    # 如果话题中包含微博中的关键词，计算加1
                    if topic.__contains__(keyword.encode('utf-8')):
                    #     count += 1
                    # # 如果微博中2个以上的关键词在话题中，则微博属于该话题
                    # if count >= 2:
                        dict={}
                        dict['blog_create_time']=blog_create_time                   #浮点型
                        dict['blog_text']=blog_text.encode('utf-8')                 #字符串，转化为utf-8格式
                        print "信号开始时间点:", start_point, '==', time.strftime("%Y-%m-%d %H:%M:%S",
                                                                           time.localtime(start_point))
                        # print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(blog_create_time)), ':', blog_text
                        # print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(blog_create_time)), ':', ' '.join(
                        #     key_words_list)
                        print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(blog_create_time)), ':', blog_text.encode(
                            'utf-8')

                        print "信号结束时间点:", end_point, '==', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_point))
                        #print blog_create_time,':',blog_text
                        print count
                        blogs_lst.append(dict)
                        break
        return blogs_lst
    #根据微博发布时间对微博进行过滤
    #给定话题在一个微博文件夹中收集其相关的微博，返回微博列表[{'blog_create_time':float,'blog_text':str}……]
    #blog_filepath形式为：'/data0/shaojie5/source_mblog/data/mblog/20171228
    def collect_blogs_for_one_topic_from_fold(self,topic,blog_filepath,start_point,end_point):
        blog_lst=[]
        blog_file_lst=self.visitDir(blog_filepath=blog_filepath)
        for file in blog_file_lst:
            # # 获取该文件最后修改时间（类型为浮点型），并减去180秒
            # t = os.path.getmtime(file) - 3 * 60  # ？？？？
            # # 如果文件的最后修改时间在话题成为热点期间，则使用其生成参考信号
            # if t < start_point and t > end_point:
            #     continue
            lst=self.collect_blogs_for_one_topic_from_file(topic=topic,
                                                           blog_filename=file,
                                                           start_point=start_point,
                                                           end_point=end_point)
            # lst = self.collect_blogs_for_one_topic_from_file_v1(topic=topic,
            #                                                  blog_filename=file,
            #                                                  start_point=start_point,
            #                                                  end_point=end_point)
            if len(lst)!=0:
                blog_lst.extend(lst)
        return blog_lst

    def collect_blogs_for_one_topic_from_fold_v1(self,topic,blog_filepath,start_point,end_point):
        blog_lst=[]
        blog_file_lst=self.visitDir(blog_filepath=blog_filepath)
        for file in blog_file_lst:
            # # 获取该文件最后修改时间（类型为浮点型），并减去180秒
            # t = os.path.getmtime(file) - 3 * 60  # ？？？？
            # # 如果文件的最后修改时间在话题成为热点期间，则使用其生成参考信号
            # if t < start_point and t > end_point:
            #     continue
            lst=self.collect_blogs_for_one_topic_from_file_v1(topic=topic,
                                                           blog_filename=file,
                                                           start_point=start_point,
                                                           end_point=end_point)
            # lst = self.collect_blogs_for_one_topic_from_file_v1(topic=topic,
            #                                                  blog_filename=file,
            #                                                  start_point=start_point,
            #                                                  end_point=end_point)
            if len(lst)!=0:
                blog_lst.extend(lst)
        return blog_lst
    #根据文件修改时间对文件过滤

    # 遍历文件夹下的所有文件
    def visitDir(self, blog_filepath):
        file_lst = []
        parents = os.listdir(blog_filepath)
        #对其进行排序
        parents.sort()
        for parent in parents:
            # print parent
            child = os.path.join(blog_filepath, parent)
            file_lst.append(child)
            # print child
        print blog_filepath,'中文件数为：',len(file_lst)
        return file_lst
    # 使用正则表达式对微博内容清洗
    def filter_symbol(self,context):
        re_http = re.compile(r'[a-zA-z]+://[^\s]*')
        re_punc = re.compile('[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*🙄“”《》【】：（）]+'.decode('utf8'))
        context = context.decode('utf-8')
        context = context.strip().strip('\n')
        context = re_http.sub('', context)
        context = re_punc.sub('', context)
        return context

"""
中间结果数据保存与导入
"""
#保存
def store_json(data,filename):
    with open(filename, 'w') as json_file:
        # json_file.write(json.dumps(data))
        json.dump(data, json_file, indent=4, encoding='utf-8', ensure_ascii=False)
#导入
def load_json(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
    return data
#创建文件目录
def mkdir(path):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)

        print path + ' 创建成功'
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print path + ' 目录已存在'
        return False

"""
#为热点话题产生参考信号
#blog_basepath的形式为：'/data0/shaojie5/source_mblog/data/mblog’
#blog_savepath为：‘pos_topic_related_blogs’
#signal_savepath为：'pos_topic_signals'
#topic_trended_time为话题成为热点时间（为已知数据，每个历史热点会提供）的形式：‘2017-12-28 13:43’
"""
def generate_refrence_signals_for_trended_topic(blog_basepath,
                                                blog_savepath,
                                                signal_savepath,
                                                trended_topic,
                                                topic_trended_time,
                                                topic_id,
                                                signal_span):

    N_ref1 = 7 * 3600  # 话题成为热点之前的时间跨度：7小时(可修改)
    N_ref2 = 3 * 3600  # 话题成为热点之后的时间跨度：3小时（可修改）
    ref_signal_length = (N_ref1 + N_ref2) / signal_span  # 参考信号的长度
    print "参考信号的长度为：",ref_signal_length

    trendTime = time.mktime(time.strptime(topic_trended_time, '%Y-%m-%d %H:%M'))  # 获取话题成为热点的时间戳浮点数表示
    start_point = trendTime - N_ref1    # 参考信号开始时间点
    end_point = trendTime + N_ref2      # 参考信号结束时间点

    #根据话题话题成为热点时间，生成微博存放路径
    timeStruct = time.strptime(topic_trended_time, '%Y-%m-%d %H:%M')  # 将成为热点时间点转化为时间元组类型
    date_path = time.strftime("%Y%m%d", timeStruct)  # 将时间转化为字符串格式，如“201712220”
    blog_filepath=os.path.join(blog_basepath,date_path)
    print "需读取的微博存放路径:",blog_filepath
    #从微博存放路径中获取话题相关的微博
    gts = GenerateTopicSignals()
    blog_lst=gts.collect_blogs_for_one_topic_from_fold(topic=trended_topic,
                                                       blog_filepath=blog_filepath,
                                                       start_point=start_point,
                                                       end_point=end_point)

    #将话题相关微博以json的形式保存
    filepath=os.path.join(blog_basepath,blog_savepath)
    mkdir(filepath)
    filename=os.path.join(filepath,topic_id+'.json')
    print "话题相关微博保存路径：",filename
    store_json(data=blog_lst,filename=filename)

    #根据收集到的微博，得到热点话题的参考信号
    #得到原始信号
    original_signals=gts.generate_signals(blog_lst=blog_lst,
                                          start_point=start_point,
                                          signal_length=ref_signal_length,
                                          signal_span=signal_span)
    #对原始信号进行处理
    signals_b, signals_b_s, signals_b_s_c, signals_b_s_c_l=gts.process_signals(original_signal=original_signals,
                                                                               beta=1,
                                                                               alpha=1,
                                                                               N_smooth=10,
                                                                               b_flag=True)
    signal_dict={}
    signal_dict['original_signals']=original_signals
    signal_dict['signals_b'] = signals_b
    signal_dict['signals_b_s'] = signals_b_s
    signal_dict['signals_b_s_c'] = signals_b_s_c
    signal_dict['signals_b_s_c_l'] = signals_b_s_c_l
    #将话题信号保存起来
    filepath = os.path.join(blog_basepath, signal_savepath)
    mkdir(filepath)
    filename = os.path.join(filepath, topic_id + '.json')
    print "话题信号保存路径：",filename
    store_json(data=signal_dict, filename=filename)
"""
#为话题产生观测信号,观测信号长度要长于参考信号
#此时topic_trended_time为基准点时间,形式：‘2017-12-28 13:43’
#blog_basepath的形式为：'/data0/shaojie5/source_mblog/data/mblog’
#blog_savepath为：‘obs_topic_related_blogs’
#signal_savepath为：'obs_topic_signals'
"""
def generate_observation_signals_for_topic(signal_span,
                                           topic_trended_time,
                                           blog_basepath,
                                           trended_topic,
                                           blog_savepath,
                                           topic_id,
                                           signal_savepath,
                                           topic_type=1):

    print "开始收集***",trended_topic,"***的信号"
    N_ref1 = 10 * 3600      # 话题微博收集基准点之前：10小时(可修改)
    N_ref2 = 5 * 3600       # 话题微博收集基准点之后：3小时（可修改）
    obs_signal_length = (N_ref1 + N_ref2) / signal_span  #观测信号的长度
    print "参考信号的长度为：", obs_signal_length

    trendTime = time.mktime(time.strptime(topic_trended_time, '%Y-%m-%d %H:%M'))  # 获取话题成为热点的时间戳浮点数表示
    start_point = trendTime - N_ref1  # 参考信号开始时间点
    end_point = trendTime + N_ref2  # 参考信号结束时间点
    print "基准时间为：",trendTime ,'==',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(trendTime))
    print "信号开始时间点:",start_point,'==',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_point))
    print "信号结束时间点:",end_point,'==',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_point))

    # 根据基准点时间，生成微博存放路径
    timeStruct = time.strptime(topic_trended_time, '%Y-%m-%d %H:%M')  # 将成为热点时间点转化为时间元组类型
    date_path = time.strftime("%Y%m%d", timeStruct)  # 将时间转化为字符串格式，如“201712220”
    blog_filepath = os.path.join(blog_basepath, date_path)
    print "需读取的微博存放路径:", blog_filepath

    # 从微博存放路径中获取话题相关的微博
    gts = GenerateTopicSignals()
    if topic_type:
        blog_lst = gts.collect_blogs_for_one_topic_from_fold(topic=trended_topic,
                                                             blog_filepath=blog_filepath,
                                                             start_point=start_point,
                                                             end_point=end_point)
    else:
        blog_lst = gts.collect_blogs_for_one_topic_from_fold_v1(topic=trended_topic,
                                                             blog_filepath=blog_filepath,
                                                             start_point=start_point,
                                                             end_point=end_point)
    #
    # 将话题相关微博以json的形式保存
    filepath = os.path.join(blog_basepath, blog_savepath)
    mkdir(filepath)
    filename = os.path.join(filepath, topic_id + '.json')
    print "话题相关微博保存路径：", filename
    store_json(data=blog_lst, filename=filename)

    # 根据收集到的微博，得到热点话题的参考信号
    # 得到原始信号
    original_signals = gts.generate_signals(blog_lst=blog_lst,
                                            start_point=start_point,
                                            signal_length=obs_signal_length,
                                            signal_span=signal_span)
    # 对原始信号进行处理
    signals_b, signals_b_s, signals_b_s_c, signals_b_s_c_l = gts.process_signals(original_signal=original_signals,
                                                                                 beta=1,
                                                                                 alpha=1,
                                                                                 N_smooth=10,
                                                                                 b_flag=True)
    signal_dict = {}
    signal_dict['original_signals'] = original_signals
    signal_dict['signals_b'] = signals_b
    signal_dict['signals_b_s'] = signals_b_s
    signal_dict['signals_b_s_c'] = signals_b_s_c
    signal_dict['signals_b_s_c_l'] = signals_b_s_c_l
    # 将话题信号保存起来
    filepath = os.path.join(blog_basepath, signal_savepath)
    mkdir(filepath)
    filename = os.path.join(filepath, topic_id + '.json')
    print "话题信号保存路径：", filename
    store_json(data=signal_dict, filename=filename)

"""
#读取参考信号对应的话题
#三种话题
#1、正样本话题即热点话题'pos_topic.txt'
#2、负样本话题即非热点话题'neg_topic.txt'
#3、观测话题即待预测话题'obs_topic.txt'
"""
def read_topics(blog_basepath,filename):
    filename=os.path.join(blog_basepath,filename)
    topic_lst=[]
    for line in open(filename).readlines():
        line = line.decode('utf8')
        items = line.strip().strip('\n').split(',')
        if len(items)!=3:
            continue
        dict={}
        dict['topic_id']=items[0].encode('utf-8')
        dict['trended_topic'] = items[1].encode('utf-8')
        dict['topic_trended_time'] = items[2].encode('utf-8')
        trendTime = time.mktime(time.strptime(dict['topic_trended_time'], '%Y-%m-%d %H:%M'))  # 获取话题成为热点的时间戳浮点数表示
        print trendTime
        topic_lst.append(dict)
        for key,value in dict.items():
            print key,":",value,type(value)           #类型为unicode
    return topic_lst

#处理程序1:产生参考信号
def process1(topic_dict):

    print "======================================================================="
    print "\n"
    start_time=datetime.datetime.now()
    print "程序开始时间：",start_time
    generate_refrence_signals_for_trended_topic(blog_basepath='/data0/shaojie5/source_mblog/data/mblog',
                                                blog_savepath='pos_topic_related_blogs',
                                                signal_savepath='pos_topic_signals',
                                                trended_topic=topic_dict['trended_topic'],
                                                topic_trended_time=topic_dict['topic_trended_time'],
                                                topic_id=topic_dict['topic_id'],
                                                signal_span=600)
    end_time=datetime.datetime.now()
    print "程序结束时间：", end_time
    print "代码运行时间为：",(end_time - start_time).seconds

# 处理程序2:产生观测信号
def process2(topic_dict,topic_type):
    print "======================================================================="
    print "\n"
    start_time = datetime.datetime.now()
    print "程序开始时间：", start_time
    generate_observation_signals_for_topic(signal_span=600,
                                              topic_trended_time=topic_dict['topic_trended_time'],
                                              blog_basepath='/data0/shaojie5/source_mblog/data/mblog',
                                              trended_topic=topic_dict['trended_topic'],
                                              blog_savepath='obs_topic_related_blogs',
                                              topic_id=topic_dict['topic_id'],
                                              signal_savepath='obs_topic_signals',
                                              topic_type=topic_type)
    end_time = datetime.datetime.now()
    print "程序结束时间：", end_time
    print "代码运行时间为：", (end_time - start_time).seconds

#单线程处理
if __name__=='__main__':
    pass
    topic_lst = read_topics(blog_basepath='/data0/shaojie5/source_mblog/data/mblog', filename='obs_topic_2018_03_02.txt')
    # # 产生参考信号
    # for topic_dict in topic_lst[41:48]:
    #    process1(topic_dict)

    # 产生观测信号(热搜话题)
    # topic_lst1=topic_lst[82:92]
    # for topic_dict in topic_lst1:
    #     print "开始收集话题：",topic_dict['trended_topic']
    #     process2(topic_dict,topic_type=1)

    #产生观测信号(自选话题)
    topic_lst2=topic_lst[110:114]
    for topic_dict in topic_lst2:
        print "开始收集话题：", topic_dict['trended_topic']
        process2(topic_dict, topic_type=0)






