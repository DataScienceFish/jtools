import pytest
import time
import sys
sys.path.append('F:/projects/jtools')

from jtools.manager import MongoEnhancedManager  # 假设你将整合后的类放在 manager.py 中

# --- 测试配置 ---
TEST_CONFIG = {
    "uri": "localhost:27017",
    "db": "pytest_mock_db",
    "task_table": "test_tasks",
    "result_table": "test_results",
    "result_keys": [("item_id", 1), ("category", 1)]  # 模拟复合索引
}

@pytest.fixture(scope="module")
def manager():
    """初始化 Manager 并确保测试前后数据库环境干净"""
    m = MongoEnhancedManager(TEST_CONFIG)
    # 清理旧数据
    m.db.drop_collection(TEST_CONFIG["task_table"])
    m.db.drop_collection(TEST_CONFIG["result_table"])
    yield m
    # 测试完成后可选清理
    # m.client.drop_database(TEST_CONFIG["db"])

def test_set_tasks_bulk(manager):
    """测试批量加速插入任务"""
    tasks = [
        {"uid": f"user_{i}", "finish": 0, "priority": i} 
        for i in range(10)
    ]
    count = manager.set_tasks(tasks)
    assert count >= 10  # 第一次插入应全部成功
    
    # 测试 insert_ignore (重复插入不应报错，count 应为 0 或保持幂等)
    count_retry = manager.set_tasks(tasks)
    assert count_retry == 0 or count_retry < 10 

def test_get_tasks(manager):
    """测试获取待执行任务"""
    pending = manager.get_tasks(limit=5)
    assert len(pending) == 5
    assert pending[0]['finish'] == 0

def test_bulk_upsert_results(manager):
    """测试结果表的批量 Upsert 功能 (加速逻辑)"""
    results = [
        {"item_id": 101, "category": "A", "data": "old_val"},
        {"item_id": 102, "category": "B", "data": "some_data"}
    ]
    # 第一次写入
    manager.bulk_upsert(
        manager.result_table, 
        results, 
        keys=TEST_CONFIG["result_keys"], 
        insert_ignore=False
    )
    
    # 更新其中一个值
    updated_results = [{"item_id": 101, "category": "A", "data": "new_val"}]
    manager.bulk_upsert(
        manager.result_table, 
        updated_results, 
        keys=TEST_CONFIG["result_keys"], 
        insert_ignore=False
    )
    
    # 验证更新结果
    doc = manager.get_collection(manager.result_table).find_one({"item_id": 101})
    assert doc["data"] == "new_val"

def test_update_finish_bulk(manager):
    """测试批量更新完成状态"""
    uids = ["user_0", "user_1", "user_2"]
    count = manager.update_finish_bulk(uids, finish=1)
    assert count == 3
    
    # 验证数据库状态
    finished_docs = list(manager.get_collection(manager.task_table).find({"finish": 1}))
    assert len(finished_docs) == 3
    assert "finished_timestamp" in finished_docs[0]

def test_auto_switch_logic(manager):
    """测试集合自动切分逻辑 (judge_coll_size 优化版)"""
    # 模拟当前表已有数据，设置极小的阈值触发切换
    manager.get_collection("split_table").insert_one({"test": 1})
    new_table_name = manager.auto_switch_collection("split_table", limit_count=1)
    # 预期切换到 split_table0 或 split_table1
    assert new_table_name != "split_table"
    assert "split_table" in new_table_name