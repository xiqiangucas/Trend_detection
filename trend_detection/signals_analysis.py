#coding=utf8
import matplotlib.pyplot as plt
from trend_detection.generate_blogs_to_signals import GenerateTopicSignals, load_json

"""
#给一个信号列表将其可视化
"""
def plot_lst(lst,para_dict):
    pass
    num=len(lst)
    #x,y轴
    x_axis=range(num)
    y_axis=lst
    #创建绘图对象,figsize参数可以指定绘图对象的宽度和高度，单位为英寸，一英寸=80px
    plt.figure(figsize=(8,4))
    #在当前绘图对象进行绘图（x轴,y轴,给所绘制的曲线的名字(可在图例中显示)，画线颜色，画线宽度）
    # plt.plot(x_axis,y_axis,label='signal',color="r",linewidth=2,marker='o',mec='r',mfc='w',linestyle='-')
    plt.plot(x_axis, y_axis,
             label=para_dict['label'],
             color=para_dict['color'],
             linewidth=para_dict['linewidth'],
             marker=para_dict['marker'],
             linestyle=para_dict['linestyle'])
    #给图上加上标签和标题
    plt.xlabel("time")
    plt.ylabel("sigals")
    plt.title("sigals of topic")
    #y轴的范围
    # plt.ylim(0,60)
    #显示图例
    plt.legend()
    #保存图像
    plt.savefig(para_dict['pic_save_file'])
    # 显示图
    plt.show()

color_dict={
    '蓝色':'b',
    '绿色':'g',
    '红色':'r',
    '黄色':'y',
    '青色':'c',
    '黑色':'k',
    '白色':'w',

}
maker_dict={
    '圆圈':'o',
    '点':'.',
    '菱形':'D',
    '正方形':'s',
    '星号':'*',
    '加号':'+',
    '一角朝下三角形':'v',
}
linestyle_dict={
    '实线':'-',
    '虚线':':',
    '破折线':'--',
    '点画线':'-.',
}
para_dict={
    'label':'signal',
    'color':"red",
    'marker':'o',
    'linestyle':'-',
    'linewidth':2,
    'pic_save_file':'hot_predict_test.png',
}

#测试代码1
def test1():
    gts = GenerateTopicSignals()
    original_signal = [2, 4, 3, 2, 1, 3, 2, 1, 7, 8, 10, 15, 20, 50, 10, 0, 2, 4, 1, 2, 3]
    signals_b, signals_b_s, signals_b_s_c, signals_b_s_c_l = gts.process_signals(original_signal=original_signal,
                                                                                 beta=1, alpha=1, N_smooth=3,
                                                                                 b_flag=True)

    # signals=load_json(r'hot_predict_test\topic_signals\topic_1.json')
    para_dict1 = {
        'label': 'original_signal',
        'color': color_dict['红色'],
        'marker': maker_dict['圆圈'],
        'linestyle': linestyle_dict['实线'],
        'linewidth': 2,
        'pic_save_file': 'test1.png',
    }
    plot_lst(original_signal, para_dict1)
    # plot_lst(signals['original_signals'], para_dict1)
    para_dict2 = {
        'label': 'signals_b',
        'color': color_dict['绿色'],
        'marker': maker_dict['菱形'],
        'linestyle': linestyle_dict['破折线'],
        'linewidth': 2,
        'pic_save_file': 'test2.png',
    }
    plot_lst(signals_b, para_dict2)
    # plot_lst(signals['signals_b'], para_dict2)
    para_dict3 = {
        'label': 'signals_b_s',
        'color': color_dict['黄色'],
        'marker': maker_dict['星号'],
        'linestyle': linestyle_dict['点画线'],
        'linewidth': 2,
        'pic_save_file': 'test3.png',
    }
    plot_lst(signals_b_s, para_dict3)
    # plot_lst(signals['signals_b_s'], para_dict3)
    para_dict4 = {
        'label': 'signals_b_s_c',
        'color': color_dict['蓝色'],
        'marker': maker_dict['点'],
        'linestyle': linestyle_dict['虚线'],
        'linewidth': 2,
        'pic_save_file': 'test4.png',
    }
    plot_lst(signals_b_s_c, para_dict4)
    # plot_lst(signals['signals_b_s_c'], para_dict4)
    para_dict5 = {
        'label': 'signals_b_s_c_l',
        'color': color_dict['青色'],
        'marker': maker_dict['正方形'],
        'linestyle': linestyle_dict['虚线'],
        'linewidth': 2,
        'pic_save_file': 'test5.png',
    }
    plot_lst(signals_b_s_c_l, para_dict5)
    # plot_lst(signals['signals_b_s_c_l'], para_dict5)

#测试代码2
def test2():
    pass
    # signals=load_json(r'hot_predict_test\topic_signals\topic_2.json')
    # signals = load_json(r'hot_predict_test\pos_topic_signals\topic_48.json')
    signals = load_json(r'obs_topic_signals\topic_78.json')
    para_dict1 = {
        'label': 'original_signal',
        'color': color_dict['红色'],
        'marker': maker_dict['圆圈'],
        'linestyle': linestyle_dict['实线'],
        'linewidth': 2,
        'pic_save_file': 'test1.png',
    }
    plot_lst(signals['original_signals'], para_dict1)

    para_dict2 = {
        'label': 'signals_b',
        'color': color_dict['绿色'],
        'marker': maker_dict['菱形'],
        'linestyle': linestyle_dict['破折线'],
        'linewidth': 2,
        'pic_save_file': 'test2.png',
    }
    plot_lst(signals['signals_b'], para_dict2)

    para_dict3 = {
        'label': 'signals_b_s',
        'color': color_dict['黄色'],
        'marker': maker_dict['星号'],
        'linestyle': linestyle_dict['点画线'],
        'linewidth': 2,
        'pic_save_file': 'test3.png',
    }
    plot_lst(signals['signals_b_s'], para_dict3)

    para_dict4 = {
        'label': 'signals_b_s_c',
        'color': color_dict['蓝色'],
        'marker': maker_dict['点'],
        'linestyle': linestyle_dict['虚线'],
        'linewidth': 2,
        'pic_save_file': 'test4.png',
    }
    plot_lst(signals['signals_b_s_c'], para_dict4)

    para_dict5 = {
        'label': 'signals_b_s_c_l',
        'color': color_dict['青色'],
        'marker': maker_dict['正方形'],
        'linestyle': linestyle_dict['虚线'],
        'linewidth': 2,
        'pic_save_file': 'test5.png',
    }
    plot_lst(signals['signals_b_s_c_l'], para_dict5)

if __name__=="__main__":
    pass
    test2()

    # import time
    # print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(1227628280.0))

#信号处理
import math
def Normalize_away_the_baseline(original_signals,beta=1):
    signals_b=[]
    signals_len=len(original_signals)
    for i in range(signals_len):
        b = sum(original_signals[:i+1])
        print b
        if b == 0:
            signals_b.append(original_signals[i])
        else:
            print float(original_signals[i])/float(b)
            signals_b.append((float(original_signals[i])/float(b))**beta)
    return signals_b
def Emphasize_spikes(signals,alpha=1):

    signals_len=len(signals)
    signals_b_s=[]
    for i in range(1,signals_len):

        s = (abs(signals[i]-signals[i-1]))**alpha
        signals_b_s.append(s)
    return signals_b_s
def Convolve_the_result(signals,N_smooth=10):

    signals_b_s_c=[]
    signals_b_s_c_l=[]
    for i in range(1, len(signals)):
        sum_smooth = 0
        for j in range(i - N_smooth, i):
            if j < 0:
                continue
            sum_smooth += signals[j]
        signals_b_s_c.append(sum_smooth)
        signals_b_s_c_l.append(math.log(sum_smooth + 0.00001))
    return signals_b_s_c,signals_b_s_c_l


if __name__=='__main__':
    pass
    # signals = load_json(r'test\pos_topic_signals\topic_3.json')
    # para_dict1 = {
    #     'label': 'original_signal',
    #     'color': color_dict['红色'],
    #     'marker': maker_dict['圆圈'],
    #     'linestyle': linestyle_dict['实线'],
    #     'linewidth': 2,
    #     'pic_save_file': 'test1.png',
    # }
    # plot_lst(signals['original_signals'], para_dict1)
    # signals_b=Normalize_away_the_baseline(signals['original_signals'])
    # para_dict1 = {
    #     'label': 'signal_b',
    #     'color': color_dict['红色'],
    #     'marker': maker_dict['圆圈'],
    #     'linestyle': linestyle_dict['实线'],
    #     'linewidth': 2,
    #     'pic_save_file': 'test2.png',
    # }
    # plot_lst(signals_b, para_dict1)
    # signals_b_s=Emphasize_spikes(signals_b)
    # para_dict1 = {
    #     'label': 'signal_b_s',
    #     'color': color_dict['红色'],
    #     'marker': maker_dict['圆圈'],
    #     'linestyle': linestyle_dict['实线'],
    #     'linewidth': 2,
    #     'pic_save_file': 'test3.png',
    # }
    # plot_lst(signals_b_s, para_dict1)
    # signals_b_s_c, signals_b_s_c_l=Convolve_the_result(signals_b_s)
    # para_dict1 = {
    #     'label': 'signal_b_s_c',
    #     'color': color_dict['红色'],
    #     'marker': maker_dict['圆圈'],
    #     'linestyle': linestyle_dict['实线'],
    #     'linewidth': 2,
    #     'pic_save_file': 'test4.png',
    # }
    # plot_lst(signals_b_s_c, para_dict1)
    # para_dict1 = {
    #     'label': 'signal_b_s_c_l',
    #     'color': color_dict['红色'],
    #     'marker': maker_dict['圆圈'],
    #     'linestyle': linestyle_dict['实线'],
    #     'linewidth': 2,
    #     'pic_save_file': 'test5.png',
    # }
    # plot_lst(signals_b_s_c_l, para_dict1)

