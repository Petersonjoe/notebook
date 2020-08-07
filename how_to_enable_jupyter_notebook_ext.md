Guidance Link: https://ndres.me/post/best-jupyter-notebook-extensions/

#### Install steps:

*Use pip*
```shell
pip install jupyter_nbextensions_configurator jupyter_contrib_nbextensions
```

*Use Conda*
```shell
conda install -c conda-forge jupyter_contrib_nbextensions
conda install -c conda-forge jupyter_nbextensions_configurator
```

*Enable Ext*
```shell
jupyter contrib nbextension install --user
jupyter nbextensions_configurator enable --user
```

#### Create domestic PYPI Mirrors:

##### Domestic sources:

For Ubuntu, it requires https source, only http protocol cannot work.

|Source Name|Source Link|
|:---|:---|
|清华|https://pypi.tuna.tsinghua.edu.cn/simple|
|阿里云|http://mirrors.aliyun.com/pypi/simple/|
|中国科技大学|https://pypi.mirrors.ustc.edu.cn/simple/|
|华中理工大学|http://pypi.hustunique.com/|
|山东理工大学|http://pypi.sdutlinux.org/|
|豆瓣|http://pypi.douban.com/simple/|

##### Temporary settings

Use `-i` parameter

`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyspider`

##### Permenate change:

In Linux system, add below info into ~/.pip/pip.conf (if not exists, please create a new one)

```shell
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host=mirrors.aliyun.com
```

Windows下，直接在user目录中创建一个pip目录，如：C:\Users\xx\pip，新建文件pip.ini。内容同上。

