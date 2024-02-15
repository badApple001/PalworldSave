import json,zipfile,os,time,sys

argv = sys.argv
jsoncof_path = ''
if len(argv)>0:
    jsoncof_path, full_file_name = os.path.split(argv[0])
    
# 读取配置
conf = json.load(open(os.path.join(jsoncof_path,'conf.json'),'r',encoding='utf-8'))
save_rate_minutes = conf['save_rate']

isInttype = type(save_rate_minutes) == int
if not isInttype:
    raise RuntimeError('conf.json save_rate 必须为整形')

#保存配置为zip
def save2zip():
    dir_name, full_file_name = os.path.split(os.getcwd())
    zip_from = os.path.join(dir_name,"SaveGames")
    
    # 归档带上日期和时间 
    datestr = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
    savedir = os.path.join(os.getcwd(),"backups")
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    save_to = savedir + f'\\SaveGames_{datestr}.zip'
    
    #压缩至本地
    try:
        zipDir( zip_from, save_to )
    except Exception as e:
        print(f'存档失败: {datestr}')
        print(e)
    finally:
        print(f'存档完成: {datestr}')
        
# 压缩文件夹
def zipDir(dirpath, outFullName):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath, '')
 
        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
 
# 运行 就备份一次
save2zip()

# 每分钟去对整个存档文件夹去打一个zip归档
def tickSave():
    save2zip()

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
# 输出时间
def job():
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
# BlockingScheduler
sched = BlockingScheduler()
sched.add_job(tickSave, 'interval', minutes=save_rate_minutes, id='my_job_id')
sched.start()

print('结束运行')
input("")


