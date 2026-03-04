import time
import subprocess
import re
from typing import List, Dict, Any, Union
from pymongo import MongoClient, UpdateOne, IndexModel, ASCENDING
from pymongo.errors import BulkWriteError

from loguru import logger


class MongoEnhancedManager:
    def __init__(self, config: Dict):
        """
        融合管理工具：集成基础操作、批量加速及运维导出功能
        config 需包含: uri, db, task_table, result_table, result_keys
        """
        self.uri = config.get("uri", f'mongodb://localhost:27017')
        self.db_name = config.get('db')
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        
        self.task_table = config.get('task_table')
        self.result_table = config.get('result_table')
        self.result_keys = config.get('result_keys', [('uid', 1)])
        
        self.logger = logger

    # --- 基础工具函数 ---
    
    def get_collection(self, name: str):
        return self.db[name]

    def ensure_index(self, coll_name: str, keys: List[tuple]):
        """确保索引存在，避免在循环中重复查询"""
        coll = self.db[coll_name]
        if keys:
            # 格式化索引名：[('uid', 1)] -> 'uid_1'
            coll.create_index(keys, unique=True)

    # --- 批量加速插入/更新 (Bulk Operations) ---

    def bulk_upsert(self, coll_name: str, datas: List[Dict], keys: List[tuple], insert_ignore=True):
        """
        使用 Bulk Write 实现高性能插入/更新
        :param insert_ignore: 若为True，则冲突时忽略；若为False，则执行覆盖更新
        """
        if not datas:
            return 0
        
        self.ensure_index(coll_name, keys)
        coll = self.db[coll_name]
        key_names = [k[0] for k in keys]
        
        operations = []
        for data in datas:
            # 构建查询条件
            filter_dict = {k: data.get(k) for k in key_names}
            
            if insert_ignore:
                # 仅在不存在时插入 (SetOnInsert)
                operations.append(UpdateOne(filter_dict, {'$setOnInsert': data}, upsert=True))
            else:
                # 存在则全量更新 (除_id外)
                update_data = {k: v for k, v in data.items() if k != '_id'}
                operations.append(UpdateOne(filter_dict, {'$set': update_data}, upsert=True))

        try:
            result = coll.bulk_write(operations, ordered=False)
            return (result.upserted_count + result.modified_count)
        except BulkWriteError as bwe:
            self.logger.error(f"Bulk write error: {bwe.details}")
            return 0

    # --- 业务逻辑：任务管理 ---

    def set_tasks(self, datas: List[Dict], task_coll=None):
        coll = task_coll or self.task_table
        # 任务表通常以 uid 作为主键
        return self.bulk_upsert(coll, datas, keys=[('uid', 1)], insert_ignore=True)

    def get_tasks(self, filter_dict=None, limit=1000):
        coll = self.db[self.task_table]
        query = {'finish': 0}
        if filter_dict:
            query.update(filter_dict)
        return list(coll.find(query).limit(limit))

    def update_finish_bulk(self, uids: List[Any], task_coll=None, finish=1):
        """批量更新完成状态"""
        coll_name = task_coll or self.task_table
        coll = self.db[coll_name]
        
        now = time.time()
        filter_query = {'uid': {'$in': uids}}
        update_query = {
            '$set': {
                'finish': finish,
                'finished_timestamp': now
            }
        }
        res = coll.update_many(filter_query, update_query)
        return res.modified_count

    # --- 运维与导出函数 (Shell Wrappers) ---

    def run_mongo_cmd(self, cmd: str):
        try:
            subprocess.check_call(cmd, shell=True)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {cmd}, error: {e}")
            return False

    def dump(self, out_dir: str, collection=None, gzip=True):
        """导出数据库或集合"""
        host = self.uri.split(':')[0]
        cmd = f'mongodump -h {host} --db {self.db_name} -o {out_dir}'
        if collection:
            cmd += f' --collection {collection}'
        if gzip:
            cmd += ' --gzip'
        return self.run_mongo_cmd(cmd)

    def export_json(self, collection: str, out_path: str, limit=None):
        """导出为JSON文件"""
        host = self.uri.split(':')[0]
        cmd = f'mongoexport -h {host} -d {self.db_name} -c {collection} -o {out_path} --type=json'
        if limit:
            cmd += f' --limit {limit}'
        return self.run_mongo_cmd(cmd)

    # --- 状态与动态调整 ---

    def get_coll_stats(self, collection: str):
        return self.db.command('collstats', collection)

    def auto_switch_collection(self, base_name: str, limit_count=1000000):
        """
        根据数据量动态切换集合名 (对应原 judge_coll_size)
        """
        i = 0
        current_name = base_name
        while True:
            count = self.get_coll_stats(current_name).get('count', 0)
            if count < limit_count:
                return current_name
            i += 1
            current_name = f"{base_name}{i}"

    def refresh_db(self, force=False):
        """清空数据表"""
        if not force:
            confirm = input(f"Confirm drop all collections in {self.db_name}? [Y/N]: ")
            if confirm != 'Y': return
        
        for name in self.db.list_collection_names():
            self.db.drop_collection(name)
            self.logger.info(f"Dropped: {name}")
