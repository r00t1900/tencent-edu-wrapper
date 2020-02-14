2020-2-14更新：有朋友说不能解码了，实际是因为一个无关紧要的参数官方后来改了，但是治标不治本，依然是能够解码的，会修改的朋友自己就可以修改了，暂时没有更新全功能代码的计划，此项目仅作研究目的，不可作为商业/违法用途。

2019-11-05更新：新增adb模式，双击wrapper_prompt.py，根据提示即可运行。

***
环境配置
>python3.6+

`pip install pycryptodome`

查看帮助

`python wrapper_cli.py -h`

```
usage: wrapper_cli.py [-h] [-f FILE] [-r DIRECTORY] [-o EXPORT_DIR]
                      [-m META_FILE_NAME]

A AES-128 decrypter of Tencent-edu Android app, for offline-downloaded videos.

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  run in file mode and set filename
  -r DIRECTORY, --directory DIRECTORY
                        run directory mode and set directory
  -o EXPORT_DIR, --output EXPORT_DIR
                        dir to export, default is current workspace
  -m META_FILE_NAME, --meta META_FILE_NAME
                        specify the filename of metadata file(.xls)

```
文件模式

`python wrapper_cli.py -f test.m3u8.sqlite`
```
[+]     target on test.m3u8.sqlite
[+]     export to test.ts in 1804.86ms
```
目录模式

`python wrapper_cli.py -r e:\test`
```
[+]     target on 0cf3cdc34fd3303d510c7b30262560b7.m3u8.sqlite
[+]     export to 0cf3cdc34fd3303d510c7b30262560b7.ts in 1681.30ms
[+]     target on 0e78b8a3303b6b86c8c858e593b6c0f4.m3u8.sqlite
[+]     export to 0e78b8a3303b6b86c8c858e593b6c0f4.ts in 7610.95ms
[+]     target on 0ffbd4687bd57cd547fa03d216ec2ae4.m3u8.sqlite
[+]     export to 0ffbd4687bd57cd547fa03d216ec2ae4.ts in 12003.46ms
[+]     target on 1ab245a780c17d32286fb9f3e3acb861.m3u8.sqlite
[+]     export to 1ab245a780c17d32286fb9f3e3acb861.ts in 5210.54ms
[+]     target on 3e8403cb06c7369934455bcfdb543e44.m3u8.sqlite
[+]     export to 3e8403cb06c7369934455bcfdb543e44.ts in 3465.01ms
[+]     target on 5a0bd006b938f5bd36dcdf25b029b7aa.m3u8.sqlite
[+]     export to 5a0bd006b938f5bd36dcdf25b029b7aa.ts in 714.56ms
[+]     metadata saved
```
设置输出目录

`python wrapper_cli.py -f test.sqlite -o export`

or

`python wrapper_cli.py -r e:\test -o export`

待改进

从meta的token中：

获取视频文件名和视频文件自动分类
