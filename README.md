# 介绍

使用Python开发的Windows下右键菜单上传至NextCloud并获取内部链接复制到剪贴板,可用于管理obsidian非图片附件。

# 安装

``` powershell
# windows scoop
scoop bucket add zapps https://github.com/kkzhizhou/scoop-zapps
scoop install nextcloud-uploader
```

# 配置

修改config.json文件, 放在程序的/data目录下，格式如下：

``` json
{
    "nextcloud_url": "",
    "username": "",
    "password": "",
    "upload_path": ""
}
```