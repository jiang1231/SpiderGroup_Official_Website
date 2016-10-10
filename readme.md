# SpiderGroup Official Website

目前地址： [征信大数据]( http://120.76.229.178:7000/)

阿里云项目文件夹路径： /home/tdz/SpiderGroup_Official_Website

数据库路径： mysql://pbb:pbb@123___@rm-wz9z97an1up0y6h7b.mysql.rds.aliyuncs.com:3306/spider

部署方案： gunicorn +　supervisor + nginx     [详情部署方案点这里](https://github.com/bigzhao/Ubuntu_gunicorn_nginx_supervisor)

supervisor 可视化管理地址： http://120.76.229.178:9001/ 

* 帐号 user 密码 123
* 当修改了check_spider.py 也就是主函数的时候记得去http://120.76.229.178:9001/ 重启一遍
* 若只单单修改其他东西则不需要重启服务

### 具体视图函数意义：

名称 | 含义 | 方法 | 参数意义 | 返回结果|
---| ---| ---| ---| ---
index | 主页 | GET | 无参数 | 渲染后的index.html
check | 运营商查询页面 | GET | 无参数 | 渲染后的operators.html
get_data_union | 返回用户运营商数据 测试用 数据来源result是外部导入 | GET | number:手机号码 password：密码 | 渲染后的operator_output.html
get_data_mobile | 获取移动运营商数据 暂时不用 | GET | number, password, vcode（验证码） | None
check_phone_number | 查询号码归属及类型api | GET | number（号码） | json格式数据
institution | 政府机构查询页面 | GET | 无参数 | 渲染后的government.html
get_area | 根据前端传过来的参数查询相对应子地区并返回的api | POST | 参数来源是request的form字典province： type：类型 in（province city sub_city） name：地区的名字 | 查库后渲染成json
get_mess | 在数据库里查询政府机构的api | POST | 参数来源是request的form字典province：省份 city：城市 sub_city：县城 town_street：街道 | 渲染后的government_output.html 
dishonest_check | 被执行人视图 | GET POST | POST参数： company_name（公司名或人名） card_num（号码） flag（标识 个人或公司） province（省份） | GET:dishonest_check.html POST:找到的话dishonest_executor_output.html 否则not_found_message.html（是一张图：恭喜无记录）
dishonest_person | 执行人视图 | GET POST | POST参数： company_name（名字） card_num（号码）  court（省份） | GET:dishonest_person.html POST:找到的话 dishonest_person_output.html 否则not_found_message.html（是一张图：恭喜无记录）

### 截图
主页
![image](http://o6gcipdzi.bkt.clouddn.com/%E4%B8%BB%E9%A1%B5.png)
运营商
![image](http://o6gcipdzi.bkt.clouddn.com/%E8%BF%90%E8%90%A5%E5%95%86.png)
执行被执行人
![image](http://o6gcipdzi.bkt.clouddn.com/%E8%A2%AB%E6%89%A7%E8%A1%8C%E4%BA%BA.png)
被执行人
![image](http://o6gcipdzi.bkt.clouddn.com/%E5%A4%B1%E4%BF%A1%E8%A2%AB%E6%89%A7%E8%A1%8C%E4%BA%BA.png)
政府机构
![image](http://o6gcipdzi.bkt.clouddn.com/%E6%94%BF%E5%BA%9C%E6%9C%BA%E6%9E%84.png)