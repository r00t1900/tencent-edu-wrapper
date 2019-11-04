# _*_coding:utf-8 _*_
# @Time    : 2019/11/4 12:54
# @Author  : Shek 
# @FileName: wrapper_prompt.py
# @Software: PyCharm
from tencent_edu import wrapper
import os

run_mode = input('run mode(0 for file, 1 for directory and 2 for adb)>')
export_dir = input('export directory>')
w = wrapper()
w.export_dir = str(export_dir)
if int(run_mode) == 1:
    directory = input('read directory>')
    w.process_directory(directory=directory)
elif int(run_mode) == 2:
    directory = 'txdownload'
    input('[+] please enable debug mode on your phone, and press any key to continue..')
    os.system('adb devices')
    try:
        os.system('adb pull {}'.format('/sdcard/Android/data/com.tencent.edu/files/tencentedu/video/txdownload'))
    except KeyboardInterrupt:
        print('[-] stop pulling from phone, some files may be damaged')
    print('[+] Pulling finished, starting job...')
    w.process_directory(directory=directory)
    os.system('del {}'.format(directory))
    # print('[+] please delete temp folder:{} manually'.format(os.path.abspath(directory)))
elif int(run_mode) == 0:
    filename = input('filename>')
    w.process_db_file(db_filename=filename)

ex = input('done, press any key to quit :)')
