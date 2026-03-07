from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.skill import SkillCreate, SkillResponse, SkillUpdate
from app.utils.auth import get_current_admin_user
from app.database import get_collection
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/skills", tags=["Skills"])

# =====================================================
# GET ALL SKILLS (PUBLIC)
# =====================================================
@router.get("", response_model=List[SkillResponse])
async def get_all_skills(skip: int = 0, limit: int = 50):
    skills_collection = get_collection("skills")
    cursor = skills_collection.find().sort("order", 1).skip(skip).limit(limit)
    skills = await cursor.to_list(length=limit)

    # Use **skill to unpack the dictionary. 
    # The Schema will handle the _id to id mapping and optional dates.
    return [SkillResponse(**skill) for skill in skills]

# =====================================================
# GET SINGLE SKILL (PUBLIC)
# =====================================================
@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: str):
    skills_collection = get_collection("skills")

    if not ObjectId.is_valid(skill_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid skill ID"
        )

    skill = await skills_collection.find_one({"_id": ObjectId(skill_id)})

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )

    return SkillResponse(**skill)

# =====================================================
# CREATE SKILL (ADMIN)
# =====================================================
@router.post("", response_model=SkillResponse, status_code=201)
async def create_skill_category(
    category_in: SkillCreate,
    current_user: dict = Depends(get_current_admin_user)
):
    skills_collection = get_collection("skills")
    
    # 1. Convert to dict and add timestamps
    data = category_in.model_dump()
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = datetime.utcnow()
    
    # 2. Insert into DB
    result = await skills_collection.insert_one(data)
    
    # 3. Retrieve the newly created document to return it
    created_skill = await skills_collection.find_one({"_id": result.inserted_id})
    
    if not created_skill:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create skill"
        )

    return SkillResponse(**created_skill)

# =====================================================
# UPDATE SKILL (ADMIN)
# =====================================================
@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: str, 
    skill_update: SkillUpdate, 
    current_user: dict = Depends(get_current_admin_user)
):
    skills_collection = get_collection("skills")

    if not ObjectId.is_valid(skill_id):
        raise HTTPException(status_code=400, detail="Invalid skill ID")

    # 1. Prepare update data
    update_data = skill_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    # 2. Update in DB
    result = await skills_collection.update_one(
        {"_id": ObjectId(skill_id)}, 
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Skill not found")

    # 3. Get updated doc
    updated_doc = await skills_collection.find_one({"_id": ObjectId(skill_id)})
    
    if not updated_doc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated skill"
        )
    
    return SkillResponse(**updated_doc)

# =====================================================
# DELETE SKILL (ADMIN)
# =====================================================
@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(skill_id: str, current_user: dict = Depends(get_current_admin_user)):
    skills_collection = get_collection("skills")

    if not ObjectId.is_valid(skill_id):
        raise HTTPException(status_code=400, detail="Invalid skill ID")

    result = await skills_collection.delete_one({"_id": ObjectId(skill_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Skill not found")

    return None