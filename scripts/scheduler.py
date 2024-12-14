from apscheduler.schedulers.blocking import BlockingScheduler

def schedule_tasks(retry_interval, auto_buy_time):
    scheduler = BlockingScheduler()
    
    # 定时执行抢票任务
    scheduler.add_job(func=buy_ticket, trigger='cron', hour=auto_buy_time.split(':')[0], minute=auto_buy_time.split(':')[1])
    
    # 设置重试间隔
    scheduler.add_job(func=retry_buy, trigger='interval', seconds=retry_interval)
    
    scheduler.start()

def buy_ticket():
    # 进行抢票操作
    print("执行抢票任务...")

def retry_buy():
    # 进行重试抢票操作
    print("重试抢票任务...")
