# xhspin

实现对xhs列表用户的监听
1. 获取用户信息 xhs_client.get_user_info("用户ID")
2. 获取用户笔记 xhs_client.get_user_notes("用户ID")
3. 使用数据库记录 用户信息, 一个用户一个表
4. 监听变化,如果某个用户的信息有差异,比如信息或者笔记增删改,发出通知

## 更新逻辑:
### 对于用户信息
1. 数据库中查找ID, 不存在则创建
2. 如果存在同ID内容,则比较信息,如果信息有差异,则添加一条新的记录,并通知
3. 如果信息一致,则跳过

### 对于笔记
1. 先遍历当前用户的笔记ID, 如果笔记ID不存在,则创建,并通知
2. 如果存在同ID内容,则比较信息,如果信息有差异,则添加一条新的记录,并通知
3. 如果信息一致,则跳过

## 通知
1. 记录变更日志文件
2. 略


# 感谢
- https://reajason.github.io/xhs/index.html