#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2021年09月17日
# @Author  : zzz (kkzzhizhou@gmail.com)
# @Desc    : 上传并获取Nextcloud内部链接

import os
import sys
import json
import logging
import argparse
import tkinter.messagebox

import pyperclip
from nextcloud import NextCloud
from plyer import notification
import winreg

def add_rcm(rcm_path):
    prog_name = '上传至Nextcloud'
    prog_path = os.path.realpath(sys.argv[0])
    key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,r'*\\shell')
    winreg.SetValue(key, rcm_path, winreg.REG_SZ, prog_name + '(&U)')
    prog_key = winreg.OpenKey(key,rcm_path)
    winreg.SetValue(prog_key, 'command', winreg.REG_SZ, prog_path + ' -f "%1"')
    winreg.CloseKey(prog_key)
    winreg.CloseKey(key)
    notification.notify(title = "",message = "注册右键成功",timeout  = 3)

def del_rcm(root,sub):
    try:
        open_key = winreg.OpenKey(root, sub, 0, winreg.KEY_ALL_ACCESS)
        num, _, _ = winreg.QueryInfoKey(open_key)
        for i in range(num):
            child = winreg.EnumKey(open_key, 0)
            del_rcm(open_key, child)
        try:
           winreg.DeleteKey(open_key, '')
        except Exception:
            logging.error("deletion failure")
        finally:
           winreg.CloseKey(open_key)
    except Exception:
        logging.error("opening/closure failure")
    notification.notify(title = "",message = "删除右键成功",timeout  = 3)

def upload_file(file):
    local_filepath = file
    with open('%s\\data\\config.json' % exe_path, 'r') as f:
        config = json.loads(f.read())
        NEXTCLOUD_URL = config['nextcloud_url']
        NEXTCLOUD_USERNAME = config['username']
        NEXTCLOUD_PASSWORD = config['password']
        PATH = config['upload_path']
        to_js = True
    if NEXTCLOUD_URL and NEXTCLOUD_USERNAME and NEXTCLOUD_PASSWORD and PATH:
        if not os.path.isdir(local_filepath) and os.path.isfile(local_filepath) and os.path.exists(local_filepath):
            logging.info('参数校验通过')
            nxc = NextCloud(endpoint=NEXTCLOUD_URL, user=NEXTCLOUD_USERNAME, password=NEXTCLOUD_PASSWORD, json_output=to_js)
            filepath,filename = os.path.split(local_filepath)
            upload_filepath = '%s/%s' % (PATH,filename)
            notification.notify(title = "",message = "上传中，请稍等...",timeout  = 8)
            try:
                logging.info('上传中：%s' % local_filepath)
                nxc.upload_file(local_filepath,upload_filepath)
                file_id = nxc.get_file('%s/%s' % (PATH,filename)).file_id
                internal_link = "%s/f/%s" % (NEXTCLOUD_URL,file_id)
                notification.notify(title = "",message = "上传成功",timeout  = 3)
                logging.info('上传成功：%s  内部链接：%s' % (local_filepath,internal_link))
                pyperclip.copy(internal_link)
            except:
                notification.notify(title = "",message = "上传失败，请检查日志。",timeout  = 3)
                sys.exit(1)
    else:
        logging.info('参数填写不完整，请检查配置文件。')
        notification.notify(title = "",message = "参数填写不完整，请检查配置文件。",timeout  = 3)
        sys.exit(1)

def generate_config(exe_path):
    if not os.path.exists('%s\\data\\config.json' % exe_path):
        config = {
            "nextcloud_url": "",
            "username": "",
            "password": "",
            "upload_path": ""
        }
        json_config = json.dumps(config)
        with open('%s\\data\\config.json' % exe_path, 'w') as json_file:
            json_file.write(json_config)

if __name__ == "__main__":
    exe_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
    if not os.path.exists("%s\\data" % exe_path):
        os.mkdir("%s\\data" % exe_path)
    logging.basicConfig(level=logging.INFO,filename='%s\\data\\nextcloud_uploader.log' % exe_path, format='%(asctime)s %(levelname)s %(message)s')
    os.chdir(exe_path)
    rcm_path = 'NextcloudUploader'
    app_name = os.path.split(sys.argv[0])[1]
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--init', help="生成配置文件", action="store_true")
    parser.add_argument('-a', '--assoc', help="安装右键菜单", action="store_true")
    parser.add_argument('-u', '--unassoc', help="删除右键菜单", action="store_true")
    parser.add_argument('-f', '--file', help="上传文件路径")
    args = parser.parse_args()
    if args.init or hasattr(args,'help') or args.assoc or args.unassoc or args.file:
        if args.init:
            logging.info("生成配置文件")
            generate_config(exe_path)
        if args.assoc:
            logging.info("添加右键菜单")
            add_rcm(rcm_path)
        if args.unassoc:
            logging.info("删除右键菜单")
            del_rcm(winreg.HKEY_CLASSES_ROOT,"*\\shell\\%s" % rcm_path)
        if args.file:
            logging.info("上传文件")
            upload_file(args.file)
    else:
        root = tkinter.Tk()
        root.withdraw()
        tkinter.messagebox.showinfo('使用帮助', 
            '该程序仅支持命令行\n%s -i 生成配置文件\n%s -a 安装右键菜单\n%s -a 删除右键菜单\n%s -f FILE 上传文件'
            %(app_name,app_name,app_name,app_name))