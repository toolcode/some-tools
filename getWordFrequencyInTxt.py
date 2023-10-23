from jieba import lcut
from tkinter import *
from tkinter.filedialog import *
from importlib.resources import path
def wordtxtfrequency(txtpath,ranks):
    displaytxt.insert(END, "开始运行\n")
    txt=open(txtpath,'r',encoding="utf-8").read()
    words=lcut(txt)   #jieba库函数
    count={}    #创建字典
    for word in words:
            count[word]=count.get(word,0)+1
    items=list(count.items())   #转换成列表
    items.sort(key=lambda x:x[-1],reverse=True)
    index=0
    for i in range(ranks):
        index+=1
        word,count=items[i]
        displaytxt.insert(END, str(word)+"出现了"+str(count)+"次"+ "是第"+str(index)+"多"+"\n")

def guiwordtxtfrequecy():
    
    if inputrank.get()=="":
        displaytxt.insert(END, "你没有输入你想要几个词语的排行\n")
    rank=int(inputrank.get())
    txtpath=selectPath("打开txt")
    wordtxtfrequency(txtpath,rank)

def selectPath(atitle):
    path =  askopenfilename(title=atitle)#获取地址的文本
    return path
def saverecordtotxt():
        newtxtpath=selectPath("打开txt")
        with open(newtxtpath,"a",encoding="utf-8") as j:
            j.write(displaytxt.get('1.0', END))
            displaytxt.insert(END, "已经保存了，去你设置的txt文件里面查收\n")
root = Tk()#建一个根窗体
root.title('计算txt文件中的中文词语频率，并且从大到小排序')
lb0=Label(root, text="计算txt文件中的中文词语出现的频率，并且从大到小排序")
lb = Label(root, text='请先输入你想要几个词语的排行（一个整数）,一般最前面的都是标点符号，所以你可以输入大一点，比如100')
lb0.pack()
lb.pack()


inputrank=Entry(root)
inputrank.pack()

beginrunbtn = Button(root, text='直接打开你要统计的一个txt文件,然后直接运行', command=guiwordtxtfrequecy)
beginrunbtn.pack()


displaytxt = Text(root)
displaytxt.pack()

saveresultbtn = Button(root, text='把结果保存到一个txt文件，如果你没有，可以自己创一个.txt文件', command=saverecordtotxt)
saveresultbtn.pack()
######################################################################################################

root.mainloop()
