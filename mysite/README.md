## 初次安装配置

0. 安装python 

1. clone文件项目，在项目根目录下打开虚拟环境
`source venv/bin/activate`

2. 安装相关依赖
`git config --get http.proxy`

3. 配置mysql(ubuntu环境)
```
sudo apt-get install mysql-server
sudo mysql
```
在mysql中执行命令
```
CREATE DATABASE MealMate;
CREATE USER 'admin'@'%' IDENTIFIED BY 'Admin111!';
GRANT ALL PRIVILEGES ON MealMate.* TO 'admin'@'%';
GRANT PROCESS ON *.* TO 'admin'@'%';
FLUSH PRIVILEGES;
exit
```
使用mysqldeump拷贝数据库备份
```
sudo mysql -u admin -p MealMate < mealmate_backup.sql
```

4. Django数据库迁移
`python manage.py migrate`

5. 安装sementic-ui
   `$ sudo npm install -g gulp@3.9.1`
    > fomentic 官方文档：https://fomantic-ui.com/introduction/getting-started.html 

6. 启动服务器查看效果
`python manage.py runserver`
> 数据库中已有超级用户admin（登录秘钥admin），可登录查看效果x