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
    - **spool**消耗的大小
    - **redistribution**重分布

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
   - PI设置要合理，PI涉及到TD数据的物理存储。PI一般设置在分布较均匀且经常用到的字段上。
   - TD PI相关介绍
     - [teradata PI-- 数据分布](https://blog.csdn.net/wali_wang/article/details/50493077)
     - [teradata 预先探查数据分布](https://blog.csdn.net/wali_wang/article/details/50463107)
   
8. partition primary index
   - 存在PII字段就尽量在where条件中使用，会极大加快查询速度。（例如，DW_OMS_ORDER表上，order_cre_dt为PII字段，如果不在where条件中使用，查询速度会非常慢）
   
9. set/multiset表
   - 尽量减少使用set表，每次都会查重，插入效率会非常低
   - multiset表会有效地整合可能重复的数据，同时不会将完全重复的记录重复加载到表中
   - 涉及的两种case处理
     - TD中的去重操作
       - 确定逻辑字段和数据记录的key（可唯一标识一条记录）
       - 按照key筛选重复数据，并插入临时表（表中不含以key为标识的重复数据）
       - 将重复数据在原表中删除
       - 将临时表数据插入到原表
       - Teradata支持语法`qualify row_number() over(parition by col1 order by col2 desc) = 1`
       
     - 如何处理null数据
       - 更改字符集、字段约束、字段长度等
       - 将不符合逻辑的原始数据存入一张dirty数据表中，以便业务部门检查
       
 10. 更新大表
     - 将 update 转为 delete-insert    
 
 11. 删除临时表
     - 及时删除临时表将节省更多空间和spool 

 12. 避免使用IN/NOT IN
     - IN, NOT IN会触发全字段排序、扫描
     - 如果IN的条件包含多个值，可以插入到一张临时表中，然后Inner join
     
 13. 更新语句
     - update中尽量避免使用只有set的语句，尽量包含where条件
       即便更新的表只有一条记录，最好也在where条件中带上PI字段
       
 14. 实例
     Scenario: 有一个业务逻辑SQL跑的非常慢，如何调优？
     
     - 观察SQL内容
       - select的字段
       - join的字段
         有无PI和非PI字段join，有无复杂转换/隐式转换？
       - where条件
         IN/NOT IN，子查询
         
     - 将 关联表 改为 子查询 来缩小join的数据量
     - 将 关联表 改为 临时表 再join
     - 对where条件的各条件进行逐一排查，观察是否哪一具体条件影响查询速度
     - IN/NOT IN是否可用join条件替代
     - 以上条件无发现情况下：
       - 查询表的数据倾斜（skew）情况
         - 数据表实际分布不存在skew --> collect statistics
         - 数据表实际存在skew --> 查看执行计划：join条件是否有问题，join字段存在null值<将数据表按照join字段是否为null横向切分，分别join，再union all>
         - join方式是否合适，broadcast大表小表分配是否存在错误等
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
