import time  
import random  
  
class Snowflake:  
    def __init__(self, worker_id, data_center_id):  
        ### 机器标识ID
        self.worker_id = worker_id  
        ### 数据中心ID
        self.data_center_id = data_center_id  
        ### 计数序列号
        self.sequence = 0  
        ### 时间戳
        self.last_timestamp = -1  
  
    def next_id(self):  
        timestamp = int(time.time() * 1000)  
        if timestamp < self.last_timestamp:  
            raise Exception("Clock moved backwards. Refusing to generate id for %d milliseconds" % abs(timestamp - self.last_timestamp))  
        if timestamp == self.last_timestamp:  
            self.sequence = (self.sequence + 1) & 4095  
            if self.sequence == 0:  
                timestamp = self.wait_for_next_millis(self.last_timestamp)  
        else:  
            self.sequence = 0  
        self.last_timestamp = timestamp  
        return ((timestamp - 1288834974657) << 22) | (self.data_center_id << 17) | (self.worker_id << 12) | self.sequence  
  
    def wait_for_next_millis(self, last_timestamp):  
        timestamp = int(time.time() * 1000)  
        while timestamp <= last_timestamp:  
            timestamp = int(time.time() * 1000)  
        return timestamp  
