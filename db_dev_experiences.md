### Teradata 调优

 1. Explain看执行计划
    主要关注执行计划中的关键字：
     - **confidential level**
     - **join**的方式
       例如，A join B，
         - join字段尽量放在PI字段，并在join字段上进行collect stats
           不良的join代码可能会导致 --> **“广播(broadcast)”**或**“重分布(redistribute)”**
         - **广播(broadcast)**
           将A或B的所有数据copy到每个AMP上，再进行join操作。执行计划决定copy哪张表。
         - **重分布(redistribute)**
           将A或B的数据，按照join字段（一般是非PI字段引起的）按照join字段的分布在每个AMP上重分布。

2. collect statistics
   <收集数据的统计信息作为执行计划优化器的参考，一般情况下，保持统计信息是最新的>
   
   例子：`collect statistics on my_table column(col1)`
   
   一般收集统计信息遵循以下原则：
   - 在where条件中常用的字段，在join中使用的字段。
   - 在唯一主索引字段（UPI, unique primary index，UPI应该不存在重复值）。这里另一个概念是NUPI，若字段设置为NUPI，则将会把相同的值分配到同一AMP。
   - 在非唯一索引的第二个索引字段（NUSI, non-unique secondary index）
   - 联合索引（join index）
   - 分区字段（partition columns）
   
3. 字段类型
   - 确保使用恰当的数据类型，避免额外的空间开销
   
4. 数据类型转换
   - 确保join字段类型匹配，避免隐式转换
   
5. 排序
   - 减少不必要的排序
   
6. spool space issue
   - 主要原因是超过了AMP上配置的spool空间限额，例子可以参考[此篇CSDN博客](https://blog.csdn.net/thy822/article/details/49448931/)
   - 查看执行计划，确认那一步使用较多的spool，可以尝试用volatile表分步计算，节省spool的一次性消耗
   
7. primary index
   - PI设置要合理，PI涉及到TD数据的物理存储
8. partition primary index
9. set/multiset表
10. 更新大表
11. 删除临时表
12. 避免使用IN/NOT IN
13. 更新语句
