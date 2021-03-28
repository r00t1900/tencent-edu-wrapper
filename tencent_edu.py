# _*_coding:utf-8 _*_
# @Time    : 2019/11/3 23:00
# @Author  : Shek 
# @FileName: tencent_edu.py
# @Software: PyCharm

import sqlite3 as db, base64, re, os, time, binascii, argparse
from Crypto.Cipher import AES
from urllib import parse
from pyexcel_xls import save_data


class wrapper:
    metadata_debug = False
    cache_debug = False
    auto_filter = True
    export_dir = '.'
    meta_export_filename = 'meta.xls'

    def __init__(self):
        pass

    def __aes_decrypt(self, raw: bytes, key: bytes, mode: int = AES.MODE_CBC, iv=b'0' * 16):
        """
        二进制数据AES128解密
        :param raw:二进制数据
        :param key:AES128 KEY
        :param mode:AES DECRYPT MODE
        :param iv:AES IV
        :return:解密后的二进制数据
        """
        cipher = AES.new(key=key, mode=mode, IV=iv)
        plain = cipher.decrypt(raw)
        return plain

    def __base64_url_decode(self, text):
        """
        通过url传输时去掉了=号，所以需要补上=号，补齐字符串长度为4的整数倍
        :param text:待urlsafe_base64解码字符串
        :return:解码结果（bytes）
        """
        return base64.urlsafe_b64decode(str(text + '=' * (4 - len(text) % 4)))

    def __extract_from_url(self, url: str):
        """
        提取url中的参数、主机地址、访问路径等信息
        :param url:URL
        :return:rich class
        """
        result = parse.urlparse(url=url)
        # token in path(if exists)
        # path
        o_path = result.path
        o_token_raw = re.findall(r'token\.([\S]+)\%', o_path)
        if len(o_token_raw):
            # tokens = parse.parse_qs(base64_url_decode(token_raw[0]))  # 二进制形式
            o_tokens = parse.parse_qs(self.__base64_url_decode(o_token_raw[0]).decode('utf-8', 'ignore'))  # 字符串形式
        else:
            o_tokens = None

        class tc:
            # addr
            netloc = result.netloc
            # path
            path = o_path
            # token in path(if exists)
            token_raw = o_token_raw
            # params in path(if exists)
            tokens = o_tokens
            params = result.params
            # fragment in path(uf exists)
            fragment = result.fragment
            # arguments in url(if exists)
            queries = parse.parse_qs(result.query)
            # all data in dict format
            get_all = {
                'netloc': netloc,
                'path': path,
                'tokens': tokens,
                'params': params,
                'fragment': fragment,
                'queries': queries
            }

        return tc

    def __fetch_one_metadata(self, filename: str):
        metadata_table_name = 'metadata'
        con = db.connect(filename)
        cu = con.cursor()
        ex1 = cu.execute('SELECT * FROM {}'.format(metadata_table_name))
        result = ex1.fetchall()
        if len(result):
            metadata = result[0][1]
        else:
            print('[-]\tmetadata does not exists in {}'.format(os.path.split(filename)[1]))
            return None
        ex = self.__extract_from_url(url=metadata)
        result = [os.path.split(filename)[1], ex.tokens['uin'][0], ex.tokens['term_id'][0], ex.tokens['ext'][0]]

        if self.metadata_debug:
            print('[+]\tMetadata of {}:'.format(os.path.split(filename)[1]))
            print('[+]\tuin:{}\tterm_id:{}\text:{}'.format(ex.tokens['uin'][0], ex.tokens['term_id'][0],
                                                           ex.tokens['ext'][0]))
            print('[+]\targs:{}'.format(ex.queries))
            # print(result)
        return result

    def __fetch_one_ts(self, filename: str, uin: str, term_id: str):
        start_time = time.time()
        # 文件存在，读取sqlite3数据库
        caches_table_name = 'caches'
        con = db.connect(filename)
        cu = con.cursor()
        ex1 = cu.execute('SELECT * FROM {}'.format(caches_table_name))
        row_index = -1

        aes_keys = []  # 有时候会有多个KEY(16bytes)，基本上是相同的
        ts_index = []
        # if debug:
        print('[+]\ttarget on {}'.format(os.path.split(filename)[1]))
        if self.cache_debug:
            print('[+]\tParsing ...', end='')
        while True:
            data = ex1.fetchone()
            if data is None:
                break
            else:
                row_index += 1
            key = data[0]  # column:key
            value = data[1]  # column:value
            key_extracted = self.__extract_from_url(key)  # 判断行数据类型（M3U8（可选）、AES_KEY和TS_BLOB）
            if '#EXTM3U' in str(value):
                pass

            elif 'edk' in key_extracted.queries.keys():  # AES-128密钥行
                aes_keys.append(value)
                key_in_hex = binascii.b2a_hex(value)
                if self.cache_debug:
                    print('[KEY]\t{},length:{}'.format(key_in_hex, format(len(value))))
            else:  # TS BLOB片段
                start = key_extracted.queries['start'][0]
                end = key_extracted.queries['end'][0]
                ts_index.append([row_index, start, end])
                if self.cache_debug:
                    print('[TS{:03d}] {}-{}'.format(row_index, start, end))
        match_time = -1
        ordered_ts_index = []
        # 重排序ts片段
        for i in range(len(ts_index)):
            for j in range(len(ts_index)):
                if int(ts_index[j][1]) == match_time + 1:
                    ordered_ts_index.append(ts_index[j])
                    match_time = int(ts_index[j][2])
                    break
        # 合并片段
        ex2 = cu.execute('SELECT * FROM {}'.format(caches_table_name))
        data_all = ex2.fetchall()
        if self.cache_debug:
            print('Decrypting data...', end='')
        order_index = 0
        plain = b''
        for ts_one in ordered_ts_index:
            if self.cache_debug:
                print('[TS{:03d}]\t{}-{} writing'.format(ts_one[0], ts_one[1], ts_one[2]))
            raw = data_all[ts_one[0]][1]
            chip = self.__aes_decrypt(raw=raw, key=aes_keys[0])
            plain += chip
            order_index += 1
        if self.cache_debug:
            print('Combining {} clips...'.format(len(ordered_ts_index)), end='')

        # 保存文件
        save_filename = os.path.split(filename)[1].lower().replace('.m3u8.sqlite', '.ts')
        export_dir = os.path.abspath(self.export_dir)
        term_id = str(term_id)  # 视频集共用一个term_id，以此对多个视频进行分类
        save_dir = os.path.join(export_dir, term_id)  # 视频保存的文件夹完整路径
        save_path = os.path.join(save_dir, save_filename)  # 视频文件保存的完整路径
        if os.path.exists(save_dir):
            pass
        else:
            os.makedirs(save_dir)

        with open(save_path, 'wb') as fp1:
            fp1.write(plain)
        fp1.close()

        # 用时计算
        end_time = time.time()
        delta = end_time - start_time
        if self.cache_debug:
            pass
        else:
            print('[+]\t', end='')
        print('export to {} in {:.2f}ms'.format(save_filename, delta * 1e3))

    def process_db_file(self, db_filename: str):
        # 判断文件是否存在
        if os.path.exists(os.path.abspath(db_filename)):
            db_filename = os.path.abspath(db_filename)
            pass
        else:
            print('[-]\tfile \"{}\" does not exist, skipped.'.format(db_filename))
            return None
        try:
            meta_this = self.__fetch_one_metadata(filename=db_filename)
            uin = meta_this[1]
            term_id = meta_this[2]
            self.__fetch_one_ts(filename=db_filename, uin=uin, term_id=term_id)
            return meta_this
        except db.DatabaseError as e:
            print('[-]\tdamage at {}'.format(os.path.split(db_filename)[1]))
            return None

    def process_directory(self, directory: str):
        meta_all = []
        dir_path = os.path.abspath(directory)
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            for file in files:
                if os.path.isfile(os.path.join(dir_path, file)):
                    pass
                else:
                    continue

                ext = os.path.splitext(file)[1]
                if ext.lower() == '.sqlite':
                    meta_one = self.process_db_file(db_filename=os.path.join(dir_path, file))
                    if meta_one is None:
                        pass
                    else:
                        meta_all.append(meta_one)
            # 保存meta文件到excel文档
            save_root = os.path.abspath(self.export_dir)
            save_path = os.path.join(save_root, self.meta_export_filename)
            if os.path.exists(save_root):
                pass
            else:
                os.makedirs(save_root)
            save_data(save_path, {'Sheet1': meta_all})
            print('[+]\tmetadata saved')

        else:
            print('[-]\tdirectory \"{}\" not found, please check again.'.format(dir_path))
            pass
