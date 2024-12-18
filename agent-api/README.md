# README

## 代码更新

1. 代码部署在服务器agent-api目录，代码修改后更新到此目录
2. 代码的启动是通过k8s的pod拉起，代码更新后，要重新程序按以下操作
   1. 找到当前运行的pod：kubectl get pod -A | grep agent
   2. 删除当前运行的pod：kubectl delete pod agent-api-xxxx (以上查出的名称)
   3. 查看新pod运行情况：kubectl get pod -A | grep agent

## 日志查看

1. 写入文件的日志到，/agent-api/log 中查看
2. 标准控制台的输出 kubectl logs -f agent-api-xxxx -c api (xxxx换为实际pod名称)
