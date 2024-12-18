FROM --platform=linux/amd64 python:3.10.14-alpine3.18

WORKDIR /root/agent-api
USER root
ENV PYTHONPATH /root/agent-api

COPY *.txt /root/agent-api

# 不拷贝，通过挂载的方式加载源码，方便服务器修改
# COPY api /root/agent-api/api
# COPY third /root/agent-api/third
# COPY demo /root/agent-api/demo

RUN pip3 install -r requirements.txt --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD ["python3", "app.py"]