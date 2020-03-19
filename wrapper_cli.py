# _*_coding:utf-8 _*_
# @Time    : 2019/11/3 23:01
# @Author  : Shek 
# @FileName: wrapper_cli.py
# @Software: PyCharm
from tencent_edu import wrapper
import argparse

parser = argparse.ArgumentParser(
    description='A AES-128 decrypter of Tencent-edu Android app, for offline-downloaded videos.')
parser.add_argument('-f', '--file', dest='file', help='run in file mode and set filename', default=None)
parser.add_argument('-r', '--directory', dest='directory', help='run directory mode and set directory', default=None)
parser.add_argument('-o', '--output', dest='export_dir', help='dir to export, default is current workspace',
                    default='.')
parser.add_argument('-m', '--meta', dest='meta_file_name', help='specify the filename of metadata file(.xls)',
                    default=None)
parser.add_argument('-l', '--filter', dest='auto_filter', help='set if you need auto_filter',
                    default=False)
args = parser.parse_args()

if (args.file is None) ^ (args.directory is None):
    w = wrapper()
    w.auto_filter = args.auto_filter  # 设置开启自动分类功能的标志位
    if args.meta_file_name is None:  # 设置meta filename
        pass
    else:
        w.meta_export_filename = args.meta_file_name
    w.export_dir = args.export_dir  # 设置输出目录
    if args.file is not None:  # 单文件处理模式
        w.process_db_file(db_filename=args.file)
        pass
    elif args.directory is not None:  # 目录处理模式
        w.process_directory(directory=args.directory)
        pass

else:
    # 两种模式都选中的异常处理
    print('please choose a mode to run, type --help for more details.')
