"""
验证数据库表结构脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.base import Base
from app.db.session import engine
from app.models import *  # 导入所有模型
from sqlalchemy import inspect


def verify_db():
    """验证数据库表结构"""
    print("开始验证数据库表结构...")
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    expected_tables = [
        "chapters",
        "levels",
        "level_maps",
        "tasks",
        "task_phases",
        "task_steps",
        "task_phase_question_rels",
        "knowledge_cards",
        "skill_cards",
        "skill_nodes",
        "questions",
        "point_malls",
        "point_mall_items",
        "treasure_chests",
        "users",
    ]
    
    print(f"\n数据库中的表数量: {len(tables)}")
    print(f"期望的表数量: {len(expected_tables)}")
    
    print("\n已创建的表:")
    for table in sorted(tables):
        status = "✓" if table in expected_tables else "?"
        print(f"  {status} {table}")
    
    print("\n缺失的表:")
    missing = set(expected_tables) - set(tables)
    if missing:
        for table in sorted(missing):
            print(f"  ✗ {table}")
    else:
        print("  无")
    
    # 检查外键约束
    print("\n检查外键约束:")
    for table_name in expected_tables:
        if table_name in tables:
            fks = inspector.get_foreign_keys(table_name)
            if fks:
                print(f"  {table_name}: {len(fks)} 个外键")
                for fk in fks:
                    print(f"    - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    print("\n验证完成！")


if __name__ == "__main__":
    verify_db()

