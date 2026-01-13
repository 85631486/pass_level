"""
学生服务
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from ..models.student_profile import StudentProfile
from ..models.student_skill import StudentSkill
from ..models.skill_node import SkillNode
from ..core.exceptions import NotFoundError


class StudentService:
    """学生服务类"""

    @staticmethod
    def get_or_create_profile(db: Session, user_id: int) -> StudentProfile:
        """获取或创建学生档案"""
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        if not profile:
            profile = StudentProfile(user_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile

    @staticmethod
    def get_profile(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
        """获取学生档案和技能树"""
        profile = StudentService.get_or_create_profile(db, user_id)
        
        # 获取学生技能
        student_skills = db.query(StudentSkill).filter(StudentSkill.user_id == user_id).all()
        
        # 获取技能树节点
        skill_nodes = db.query(SkillNode).all()
        
        # 构建技能树数据
        skills_data = []
        for skill_node in skill_nodes:
            student_skill = next((s for s in student_skills if s.skill_node_id == skill_node.id), None)
            skills_data.append({
                "skill_node_id": skill_node.id,
                "skill_name": skill_node.name,
                "skill_description": skill_node.description,
                "level": student_skill.level if student_skill else 0,
                "experience": student_skill.experience if student_skill else 0.0,
                "parent_id": skill_node.parent_id
            })
        
        return {
            "user_id": user_id,
            "level": profile.level,
            "experience": profile.experience,
            "total_score": profile.total_score,
            "skills": skills_data
        }

