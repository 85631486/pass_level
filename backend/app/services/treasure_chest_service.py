"""
宝箱服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from ..models.treasure_chest import TreasureChest
from ..core.exceptions import NotFoundError, ValidationError


class TreasureChestService:
    """宝箱服务类"""

    @staticmethod
    def get_treasure_chest(db: Session, chest_id: int) -> Optional[TreasureChest]:
        """获取宝箱"""
        return db.query(TreasureChest).filter(TreasureChest.id == chest_id).first()

    @staticmethod
    def get_chests_by_level(db: Session, level_id: int) -> List[TreasureChest]:
        """获取关卡下的宝箱列表"""
        return db.query(TreasureChest).filter(TreasureChest.level_id == level_id).all()

    @staticmethod
    def create_chest(
        db: Session,
        level_id: int,
        name: str,
        position_x: Optional[float] = None,
        position_y: Optional[float] = None,
        reward_config: Optional[dict] = None
    ) -> TreasureChest:
        """创建宝箱"""
        if not name:
            raise ValidationError("宝箱名称不能为空")
        
        chest = TreasureChest(
            level_id=level_id,
            name=name,
            position_x=position_x,
            position_y=position_y,
            reward_config=reward_config
        )
        db.add(chest)
        db.commit()
        db.refresh(chest)
        return chest

    @staticmethod
    def update_chest(
        db: Session,
        chest_id: int,
        name: Optional[str] = None,
        position_x: Optional[float] = None,
        position_y: Optional[float] = None,
        reward_config: Optional[dict] = None
    ) -> TreasureChest:
        """更新宝箱"""
        chest = TreasureChestService.get_treasure_chest(db, chest_id)
        if not chest:
            raise NotFoundError("宝箱不存在")
        
        if name is not None:
            chest.name = name
        if position_x is not None:
            chest.position_x = position_x
        if position_y is not None:
            chest.position_y = position_y
        if reward_config is not None:
            chest.reward_config = reward_config
        
        db.commit()
        db.refresh(chest)
        return chest

    @staticmethod
    def delete_chest(db: Session, chest_id: int) -> bool:
        """删除宝箱"""
        chest = TreasureChestService.get_treasure_chest(db, chest_id)
        if not chest:
            raise NotFoundError("宝箱不存在")
        
        db.delete(chest)
        db.commit()
        return True

