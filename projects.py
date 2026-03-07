from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.utils.auth import get_current_admin_user
from app.database import get_collection
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/projects", tags=["Projects"])


# =====================================================
# GET ALL PROJECTS (PUBLIC)
# =====================================================
@router.get("", response_model=List[ProjectResponse])
async def get_all_projects(
    skip: int = 0,
    limit: int = 50,
    featured: Optional[bool] = None,
):
    projects_collection = get_collection("projects")

    query = {}
    if featured is not None:
        query["featured"] = featured

    cursor = (
        projects_collection.find(query)
        .sort("order", 1)
        .skip(skip)
        .limit(limit)
    )

    projects = await cursor.to_list(length=limit)

    return [
        ProjectResponse(
            id=str(project["_id"]),
            title=project["title"],
            description=project["description"],
            image=project["image"],
            tags=project.get("tags", []),
            github_url=project.get("github_url"),
            demo_url=project.get("demo_url"),
            featured=project.get("featured", False),
            order=project.get("order", 0),
            created_at=project["created_at"],
            updated_at=project["updated_at"],
        )
        for project in projects
    ]


# =====================================================
# GET SINGLE PROJECT (PUBLIC)
# =====================================================
@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    projects_collection = get_collection("projects")

    try:
        project = await projects_collection.find_one(
            {"_id": ObjectId(project_id)}
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID",
        )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return ProjectResponse(
        id=str(project["_id"]),
        title=project["title"],
        description=project["description"],
        image=project["image"],
        tags=project.get("tags", []),
        github_url=project.get("github_url"),
        demo_url=project.get("demo_url"),
        featured=project.get("featured", False),
        order=project.get("order", 0),
        created_at=project["created_at"],
        updated_at=project["updated_at"],
    )


# =====================================================
# CREATE PROJECT (ADMIN)
# =====================================================
@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: dict = Depends(get_current_admin_user),
):
    projects_collection = get_collection("projects")

    # Use model_dump with mode='json' to convert HttpUrl to str
    project_dict = project.model_dump(mode='json')
    project_dict["created_at"] = datetime.utcnow()
    project_dict["updated_at"] = datetime.utcnow()

    result = await projects_collection.insert_one(project_dict)

    created_project = await projects_collection.find_one(
        {"_id": result.inserted_id}
    )

    # ✅ FIX: Ensure not None
    if not created_project:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project",
        )

    return ProjectResponse(
        id=str(created_project["_id"]),
        title=created_project["title"],
        description=created_project["description"],
        image=created_project["image"],
        tags=created_project.get("tags", []),
        github_url=created_project.get("github_url"),
        demo_url=created_project.get("demo_url"),
        featured=created_project.get("featured", False),
        order=created_project.get("order", 0),
        created_at=created_project["created_at"],
        updated_at=created_project["updated_at"],
    )


# =====================================================
# UPDATE PROJECT (ADMIN)
# =====================================================
@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: dict = Depends(get_current_admin_user),
):
    projects_collection = get_collection("projects")

    try:
        project = await projects_collection.find_one(
            {"_id": ObjectId(project_id)}
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID",
        )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    update_data = project_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    await projects_collection.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": update_data},
    )

    updated_project = await projects_collection.find_one(
        {"_id": ObjectId(project_id)}
    )

    # ✅ FIX: Ensure not None
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project",
        )

    return ProjectResponse(
        id=str(updated_project["_id"]),
        title=updated_project["title"],
        description=updated_project["description"],
        image=updated_project["image"],
        tags=updated_project.get("tags", []),
        github_url=updated_project.get("github_url"),
        demo_url=updated_project.get("demo_url"),
        featured=updated_project.get("featured", False),
        order=updated_project.get("order", 0),
        created_at=updated_project["created_at"],
        updated_at=updated_project["updated_at"],
    )


# =====================================================
# DELETE PROJECT (ADMIN)
# =====================================================
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_admin_user),
):
    projects_collection = get_collection("projects")

    try:
        result = await projects_collection.delete_one(
            {"_id": ObjectId(project_id)}
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID",
        )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return None
