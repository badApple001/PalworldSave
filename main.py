import json,zipfile,os,time,sys
from apscheduler.schedulers.blocking import BlockingScheduler

# 程序工作目录
work_path = os.path.dirname(os.path.realpath(sys.argv[0]))
print(f'work path: {work_path}')

# 存档目录
savegames_path = os.path.join(work_path,"../SaveGames")
print(f'SaveGames path: {savegames_path}');
 
# 备份目录
backups_path = os.path.join(work_path,"backups")
backups_dirs = []
backups_count = 0
print(f'backups path: {backups_path}')
if not os.path.exists(backups_path):
    os.makedirs(backups_path)
    print(f'makedir success: {backups_path}')
else:
    #获取本地备份存档目录并按照时间排序
    backups_dirs = os.listdir(backups_path)
    backups_count = len(backups_dirs)
    def dir_sort_fun( dirname:str ):
        ts = dirname.split('_')[2].split('.')[0]
        its = int(ts)
        return its
    if backups_count > 1:
        backups_dirs.sort(key=dir_sort_fun)
        print('---存档备份列表---')   
        for _dir in backups_dirs:
            print(f'---{_dir.removesuffix(".zip")}\t{os.path.join(backups_path,_dir)}')
        print('---存档备份列表---')
    
    
# 读取配置
conf = json.load(open(os.path.join(work_path,'conf.json'),'r',encoding='utf-8'))
save_rate_minutes = conf['save_rate']
max_backups_count = conf['max_backups_count']

isInttype = type(save_rate_minutes) == int
if not isInttype:
    raise RuntimeError('conf.json save_rate 必须为整形')
print(f'存档间隔: {save_rate_minutes}分')

#保存配置为zip
def save2zip():
    global backups_count
    
    # 归档带上日期和时间 
    datestr = time.strftime("%Y-%m-%d %H.%M.%S", time.localtime())
    sortflag = int(time.time())
    save_name = f'SaveGames_{datestr}_{sortflag}.zip'
    backups_count+=1
    backups_dirs.append(save_name)
    
    #压缩至本地
    try:
        zipDir( savegames_path, f'{backups_path}\\{save_name}' )
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

#定时清理
def stripFront():
    global backups_count
    
    if backups_count > max_backups_count:
        _dirname = backups_dirs.pop(0)
        dirpath = os.path.join(backups_path,_dirname)
        if os.path.exists(dirpath):
            os.remove(dirpath)
            backups_count -= 1
            print(f'del {dirpath}')
 
# 运行 主动备份一次
save2zip()

# 间隔一段时间存档一次
def tick_event():
    save2zip()
    stripFront()

# BlockingScheduler
sched = BlockingScheduler()
sched.add_job(tick_event, 'interval', minutes=save_rate_minutes, id='my_job_id')
sched.start()

print('结束运行')
input("")


