# coding:utf-8
import os
import re
import csv
import time
import argparse
import itertools


API_KEY = '' # API-KEY FROM https://www.zoomeye.org/profile


class ArgParse:
    def parse(self):
        parser = argparse.ArgumentParser(description='By zongdeiqianxing; Email: jshahjk@163.com')
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-d', action="store", dest="domain",)
        group.add_argument('-f', action="store", dest="file",)
        parser.add_argument('-o', action="store", dest="output", type=str, help='txt file', default='')
        args = parser.parse_args()
        return args


class DownTools:
    def __init__(self):
        self.tools = {'oneforall': 'https://github.com/shmilylty/OneForAll/archive/v0.4.3.zip',
                      'zoomeye': 'https://github.com/knownsec/ZoomEye-python/releases/tag/v2.0.4.6.1'}

        self.tool_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tools')
        if not os.path.exists(self.tool_dir):
            os.mkdir(self.tool_dir)
        self.down()

    def down(self):
        os.chdir(self.tool_dir)
        files = os.listdir(self.tool_dir)
        for key, value in self.tools.items():
            if key not in files:
                print('{} is not found, ready to download'.format(key))
                time.sleep(3)
                os.system('wget --no-check-certificate {url} -O {name}.zip'.format(name=key, url=value))
                os.system('unzip {}.zip'.format(key))
                os.system('mv {}.zip /tmp'.format(key))

        for file in os.listdir(self.tool_dir):
            for key in self.tools.keys():
                if file.lower().startswith(key) and file != key:
                    os.system('mv {} {}'.format(file, key))
        os.chdir('../')

# oneforall  Zoonmeye  cduan
class Zoomeye:
    def __init__(self, target):
        self.domains = []
        self.target = target

    def run(self):
        for i in itertools.count(1, 1):
            r = os.popen('python3 tools/zoomeye/zoomeye/cli.py domain -page {p} {d} 1'.format(p=i, d=self.target)).read()
            # print(r)
            if r"please run 'zoomeye init -apikey <api key>'" in r:
                os.system('pip3 install zoomeye')
                os.system('zoomeye init -apikey "{}"'.format(API_KEY))

            for line in r.splitlines():
                line = re.sub('\x1b.*?m', '', line)
                line = [_ for _ in line.split(' ') if _]
                # print(line)

                if line and 'name' in line and 'timestamp' in line:
                    continue

                if line:
                    if line[0].startswith('total'):
                        if line[1] and int(int(line[1].split('/')[1])/int(line[1].split('/')[0]))+1 == i:
                            print('zoomeye scan over')
                            return
                    else:
                        print(line[0])
                        self.domains.append(line[0])


class Oneforall:
    def __init__(self, target):
        self.target = target
        self.domains = []

    def run(self):
        comm = "python3 tools/oneforall/oneforall.py --target {domain} run".format(domain=self.target)
        logfile = 'tools/oneforall/results/{domain}.csv'.format(domain=self.target)
        os.system(comm)
        if os.path.exists(logfile):
            try:
                with open(logfile, 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    column5 = [row[5] for row in reader]
                    del column5[0]
                    self.domains += column5
            except Exception as e:
                print(e)


def ipscan(domain):
    # IBM 阿里云 中国互联网络信息中心
    dns = ['9.9.9.9', '223.5.5.5', '1.2.4.8']
    _ = []
    for _dns in dns:
        r = os.popen('nslookup {t} {d}'.format(t=domain, d=_dns)).read()
        r = r.split('\n')[4:]
        _.append(r)

    # print(_)
    if _[0] == _[1] == _[2]:
        ip = re.search(r'(([01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5])\.){3}([01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5])',''.join(_[0]))
        print(ip)
        if ip:
            return ip.group()
    else:
        print('{}存在cdn或多ip'.format(domain))
        return None


class Controller:
    def __init__(self):
        self.args = ArgParse().parse()
        self.data = []
        self.domainsDict = {}

        if self.args.domain:
            self.run(self.args.domain)
        if self.args.file:
            with open(self.args.file, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    self.run(line.strip())

    def run(self, domain):
        oneforall = Oneforall(domain)
        zoomeye = Zoomeye(domain)
        zoomeye.run()
        oneforall.run()

        # 保持zoomeye独有的doamins在上面
        D = []
        for d in zoomeye.domains:
            if d not in oneforall.domains:
                D.append(d)
        D += oneforall.domains

        for d in D:
            self.domainsDict[d] = ipscan(d)

        self.output(domain, self.domainsDict)

    def output(self, file, domainsDict):
        file = self.args.output if self.args.output else '{}.txt'.format(file.strip())
        with open(file, 'w', encoding='utf-8') as f:
            for k, v in domainsDict.items():
                f.write('{}\t{}'.format(k, v))
                f.write('\n')


if __name__ == '__main__':
    if not API_KEY :
        exit('需要输入zoomeye的api_key')
    DownTools()
    Controller()
