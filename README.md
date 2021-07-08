一个轻量级的游戏服务器引擎


# python version

python 3.8.8


# 要点

- 业务层基于ECS框架来做开发, 继承实体基类与组件基类即可
- 基于`etcd`的 服务注册 / TTL / 服务发现 / 负载均衡 / 上报负载 / Watch机制 一体化
- 基于`msgpack`的RPC框架, 支持 ip地址直接call以及配合ECS的remote虚拟实体/组件直接call
- 基于asyncio异步IO的协程业务层支持, 可实现类似 `result = await rpc_call()` 的效果
    - 实现了协程池, 封装成简洁的装饰器便于业务层调用
- 基于sanic开发的异步HTTP微服务框架供方便开发各类公共服务
    - 基于jwt的auth模块
    - 基于redis的数据落地模块
    - 基于umongo的ODM模块
- 热更新reload模块
    - 全量式, 安全保障
    - 增量式, 速度更快, 方便平时开发
- 支持异步的TimedRotating日志模块
    - 根据日期时间自动滚动切换日志文件
    - 支持协程对象的callback
    - 根据日志level改变颜色, 方便查询
    - 报trace可打印堆栈与`locals`
    - 对于 warning 以上的日志级别直接对Pycharm提供文件跳转支持
- 支持1:N模型的定时器模块, 避免覆盖同一个key的易错点 
    - 可以重复使用一个key, 并不会冲掉之前key的timer, 但是当调用`cancel_timer`的时候, 会一次性全部cancel掉所有
- 制作了增强型json解析器, 支持注释/自动去除逗号/变量宏
- 基于MongoDB的数据落地模块
- client端的模拟与自动化测试配套
- 大厅服务器的前置网关gate服务器, 负责压缩/解压, 加密/解密数据以及鉴权


# 架构图


```puml
actor game_player_client as cl
database MongoDB
database Redis
database etcd

rectangle hs [
    <b>HTTP微服务集群
    ....
    基于sanic开发的异步HTTP微服务类集群
    ----
    可基于此扩展实现登陆微服务、排队微服务、排行榜微服务等等
]

rectangle lg [
    <b>lobby_gate0, lobby_gate1, ...
    ----
    负责客户端到 lobby 服 之间的数据转发
]

rectangle lb [
    <b>lobby_0, lobby_1, ....
    ----
    负责游戏大厅逻辑的集群
]

rectangle bs [
    <b>battle_0, battle_1, ...
    ----
    承载战斗服逻辑的集群
]

rectangle ds[
    <b>调度逻辑类集群
    ....
    基于etcd的 服务注册 / TTL / 服务发现 / 负载均衡 / 上报负载 / Watch机制 的调度逻辑类集群
    ----
    可基于此扩展实现匹配类逻辑、全局广播类逻辑
]

cl <--> lg: TCP
lb <--> bs: TCP
lg <--> lb: TCP
cl <--> bs: TCP/RUDP
lb <--> ds: TCP
lg <--> ds: TCP
bs <--> ds: TCP

cl <--> hs: HTTPS
lb <--> hs: HTTP/HTTPS
bs <--> hs: HTTP/HTTPS

ds <--> Redis
hs <--> Redis
hs <--> MongoDB
lb <--> MongoDB

lb <--> etcd: HTTP/HTTPS
lg <--> etcd: HTTP/HTTPS
bs <--> etcd: HTTP/HTTPS
ds <--> etcd: HTTP/HTTPS


```


# Q&A

常见问题解答, 就不要去群里刷屏问了哈:  
* 为何选用python? 不选cpp
    * 原来是cpp的, 但本服务器引擎的愿景是面向大众开发者, 能够快速开发, 且希望更多的开发者能够参与贡献, python受众广, 易上手, 好维护
* lobby_gate的意义? 为何客户端不直连lobby?
    * 一般的，在延迟不敏感的情况下，客户端通过连接 gate 来访问 lobby, gate负责代理转发客户端与 game 之间的网络通信数据。由 gate 负责完成对通信数据加密解析、压缩解压操作, 减轻lobby性能压力。
    * lobby 处理消息的逻辑可以更加简洁，不用处理 I/O 复用，因为所有的消息来自单个 TCP 连接（单网关）或者固定数量的几个 TCP 连接（多网关的情况）。
    * 客户端启动后连接的是网关，网关再去连接场景服务器并转发所有消息包。切换场景时客户端与网关的连接是不断的，由网关负责去连接新的场景，因为网关和游戏服务器通常在同一局域网内，所以掉线的问题大大改善了。
    * 在多进程的网络游戏架构中，game 除了要处理客户端的消息，同时还会处理其他进程的消息，比如账号、GM 工具等。出于安全原因，一定需要把客户端的消息隔离开来加以限制。
    * 游戏服务器经常需要开服、合服，还有硬件故障等原因导致不得不做服务器迁移。如果 game 直接对客户端提供服务，服务发生变更时往往需要客户端退出重新走登录流程。如果使用网关，在服务器内部发生地址变更时只需要保证网关得到更新并发起重连，客户端甚至根本觉察不到。
* RUDP是什么?
    * 全称是 reliable UDP
    * 目前本服务器引擎基于标准KCP算法使用py实现
    * 后续有计划要改造kcp, 性能将更上一层楼敬请期待:
        * 加入基于srtt监测的动态冗余包机制
        * 精简包头(如包头的一些字段并不需要32位, 可改为16位)
        * 引入dupack机制, 不只是发`IKCP_CMD_ACK`包
            * 充分利用包头的字段, 比如当acklist数组里需要发送的ack小于等于3时, 用包头中的len/rdc_len/sn来表示收到了的包的序号
            * 冗余ack机制: 当acklist数组里需要发送的ack大于3时, body里会包含合并acklist的所有ack以及之前发过的ack, 直到包大小到达mss
        * ...


# 关于引入etcd

* 通过其ttl以及watch机制来实现 服务注册 / 服务发现 / 负载均衡 / 上报负载
* 方便做严谨的分布式锁
* 与etcd的交互使用的是其V2版本的HTTP API, 与其交互是延迟不敏感的所以不使用grpc, 保持简单
* 为啥选etcd不选zookeeper?
    * 两个应用实现的目的不同。etcd的目的是一个高可用的 Key/Value 存储系统，主要用于分享配置和服务发现；zookeeper的目的是高有效和可靠的协同工作系统。
    * 接口调用方式不同。etcd是基于HTTP+JSON的API，直接使用curl就可以轻松使用，方便集群中每一个主机访问；zookeeper基于TCP，需要专门的客户端支持。
    * 功能就比较相似了。etcd和zookeeper都是提供了key，value存储服务，集群队列同步服务，观察一个key的数值变化。
    * 部署方式也是差不多：采用集群的方式，可以达到上千节点。只是etcd是go写的，直接编译好二进制文件部署安装即可；zookeeper是java写的，需要依赖于jdk，需要先部署jdk。
    * 实现语言： go 拥有几乎不输于C的效率，特别是go语言本身就是面向多线程，进程通信的语言。在小规模集群中性能非常突出；java，实现代码量要多于go，在小规模集群中性能一般，但是在大规模情况下，使用对多线程的优化后，也和go相差不大。


# ToDo List

- Unity基于pythonnet来引入python做热更或业务编写, 实现前后端代码统一
- 火焰图的配套工具制作
- 配表导表工具
- ...


