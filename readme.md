# ServerManagerGui

ServerManagerGui用于管理本机的各种第三方服务。
在本地开发时，可能需要用到mysql,redis,zookeeper等服务，每个服务的启动关闭命令又都不一样，通过键入命令的方式，使用界面进行统一管理。

<img src="https://github.com/wuworker/pictures/blob/master/my/servergui2.png?raw=true" width = 30% height = 30% /><img src="https://github.com/wuworker/pictures/blob/master/my/servergui3.png?raw=true" width = 30% height = 30% /><img src="https://github.com/wuworker/pictures/blob/master/my/servergui1.png?raw=true" width = 40% height = 40% />


# 启动

1. [安装python3](https://www.python.org/downloads/)
2. 安装第三方依赖
```
pip install pillow
pip install pexpect
```
3. 运行
```
./startup.sh
```
