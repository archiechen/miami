miami
=====

～ miami是什么？
miami是迈阿密
～ 为什么叫迈阿密？
是为了让团队工作更高效，节约下来的时间，程序猿们可以去迈阿密洗海澡、晒太阳、看小皇帝打篮球：）
～ 为什么能高效呢？
    每项任务都有价值，让程序猿更有成就感。
    安全约束，避免粗心的程序猿忘记遵守规约。
    每日重新领取任务，让程序猿做好每日工作规划。
    每次只关注一个任务，让程序猿更专注。
    对比评估与实际，让程序猿更了解自己。
    回顾历史战绩，让程序猿看到自己的进步。
    价值导向，鼓励高效工作，不鼓励加班。
    轻项目重团队，让程序猿关注当前sprint，不必在不同项目间切换。

～ 怎么做呢？
    在planning game中安排sprint计划，计划中的任务状态为ready。
    进入ready状态的任务，必须评估价值。比如，编写一个斐波那契数列的实现，价值10$。
    进入progress状态的任务之前，必须评估耗时，这个由程序猿根据自己的能力来评估。
    进入progress状态之后，开始计算实际耗时时间，实际耗时时间截止到进入done状态为止，迁回ready状态时，中断耗时计算。
    每个程序猿只能有一个任务处于progress状态，要想做其他的，先把当前的任务放回ready状态中。
    每日23:00，自动将所有progress状态的任务迁回ready状态中，并按8小时统计实际耗时。
    程序猿可以手动释放progress状态的任务，耗时按照当前时间减去签入时间计算。
    

    