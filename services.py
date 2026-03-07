from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.service import ServiceCreate, ServiceResponse, ServiceUpdate
from app.utils.auth import get_current_admin_user
from app.database import get_collection
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/services", tags=["Services"])


# =====================================================
# GET ALL SERVICES (PUBLIC)
# =====================================================
@router.get("", response_model=List[ServiceResponse])
async def get_all_services(skip: int = 0, limit: int = 50):
    """Get all services"""
    services_collection = get_collection("services")

    cursor = services_collection.find().sort("order", 1).skip(skip).limit(limit)
    services = await cursor.to_list(length=limit)

    return [
        ServiceResponse(
            id=str(service["_id"]),
            title=service.get("title"),
            description=service.get("description"),
            icon=service.get("icon"),
            color=service.get("color", "from-blue-500 to-cyan-500"),
            features=service.get("features", []),
            order=service.get("order", 0),
            created_at=service.get("created_at"),
            updated_at=service.get("updated_at"),
        )
        for service in services
    ]


# =====================================================
# GET SINGLE SERVICE (PUBLIC)
# =====================================================
@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: str):
    """Get service by ID"""
    services_collection = get_collection("services")

    if not ObjectId.is_valid(service_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid service ID"
        )

    service = await services_collection.find_one({"_id": ObjectId(service_id)})

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    return ServiceResponse(
        id=str(service["_id"]),
        title=service.get("title"),
        description=service.get("description"),
        icon=service.get("icon"),
        color=service.get("color", "from-blue-500 to-cyan-500"),
        features=service.get("features", []),
        order=service.get("order", 0),
        created_at=service.get("created_at"),
        updated_at=service.get("updated_at"),
    )


# =====================================================
# CREATE SERVICE (ADMIN)
# =====================================================
@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(service: ServiceCreate, current_user: dict = Depends(get_current_admin_user)):
    """Create new service (admin only)"""
    services_collection = get_collection("services")

    service_dict = service.model_dump()  # Pydantic v2
    service_dict["created_at"] = datetime.utcnow()
    service_dict["updated_at"] = datetime.utcnow()

    result = await services_collection.insert_one(service_dict)
    created_service = await services_collection.find_one({"_id": result.inserted_id})

    if not created_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create service"
        )

    return ServiceResponse(
        id=str(created_service["_id"]),
        title=created_service.get("title"),
        description=created_service.get("description"),
        icon=created_service.get("icon"),
        color=created_service.get("color", "from-blue-500 to-cyan-500"),
        features=created_service.get("features", []),
        order=created_service.get("order", 0),
        created_at=created_service.get("created_at"),
        updated_at=created_service.get("updated_at"),
    )


# =====================================================
# UPDATE SERVICE (ADMIN)
# =====================================================
@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(service_id: str, service_update: ServiceUpdate, current_user: dict = Depends(get_current_admin_user)):
    """Update service (admin only)"""
    services_collection = get_collection("services")

    if not ObjectId.is_valid(service_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid service ID"
        )

    existing_service = await services_collection.find_one({"_id": ObjectId(service_id)})
    if not existing_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    update_data = service_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    await services_collection.update_one({"_id": ObjectId(service_id)}, {"$set": update_data})

    updated_service = await services_collection.find_one({"_id": ObjectId(service_id)})

    if not updated_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update service"
        )

    return ServiceResponse(
        id=str(updated_service["_id"]),
        title=updated_service.get("title"),
        description=updated_service.get("description"),
        icon=updated_service.get("icon"),
        color=updated_service.get("color", "from-blue-500 to-cyan-500"),
        features=updated_service.get("features", []),
        order=updated_service.get("order", 0),
        created_at=updated_service.get("created_at"),
        updated_at=updated_service.get("updated_at"),
    )


# =====================================================
# DELETE SERVICE (ADMIN)
# =====================================================
@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(service_id: str, current_user: dict = Depends(get_current_admin_user)):
    """Delete service (admin only)"""
    services_collection = get_collection("services")

    if not ObjectId.is_valid(service_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid service ID"
        )

    result = await services_collection.delete_one({"_id": ObjectId(service_id)})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    return None
