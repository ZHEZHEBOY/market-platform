from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin, get_current_user
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse

router = APIRouter(prefix="/api/categories", tags=["分类"])


def _build_tree(categories: list[Category], parent_id: int | None = None) -> list[dict]:
    result = []
    for cat in categories:
        if cat.parent_id == parent_id:
            node = CategoryResponse(
                id=cat.id,
                name=cat.name,
                parent_id=cat.parent_id,
                sort_order=cat.sort_order,
                is_active=cat.is_active,
                created_at=cat.created_at,
                children=_build_tree(categories, cat.id),
            )
            result.append(node)
    result.sort(key=lambda x: x.sort_order)
    return result


@router.get("", response_model=CategoryListResponse)
def list_categories(
    tree: bool = Query(False),
    db: Session = Depends(get_db),
):
    categories = db.query(Category).filter(Category.is_active == True).all()
    if tree:
        tree_data = _build_tree(categories, None)
        return CategoryListResponse(items=tree_data, total=len(categories))
    flat = [
        CategoryResponse(
            id=c.id, name=c.name, parent_id=c.parent_id,
            sort_order=c.sort_order, is_active=c.is_active,
            created_at=c.created_at, children=[],
        )
        for c in sorted(categories, key=lambda x: (x.parent_id or 0, x.sort_order))
    ]
    return CategoryListResponse(items=flat, total=len(flat))


@router.post("", response_model=CategoryResponse)
def create_category(
    data: CategoryCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if data.parent_id is not None:
        parent = db.query(Category).filter(Category.id == data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="父分类不存在")
    cat = Category(name=data.name, parent_id=data.parent_id, sort_order=data.sort_order)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return CategoryResponse(
        id=cat.id, name=cat.name, parent_id=cat.parent_id,
        sort_order=cat.sort_order, is_active=cat.is_active,
        created_at=cat.created_at, children=[],
    )


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    if data.name is not None:
        cat.name = data.name
    if data.parent_id is not None:
        if data.parent_id == category_id:
            raise HTTPException(status_code=400, detail="不能将分类设为自己的子分类")
        parent = db.query(Category).filter(Category.id == data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="父分类不存在")
        cat.parent_id = data.parent_id
    if data.sort_order is not None:
        cat.sort_order = data.sort_order
    if data.is_active is not None:
        cat.is_active = data.is_active
    db.commit()
    db.refresh(cat)
    return CategoryResponse(
        id=cat.id, name=cat.name, parent_id=cat.parent_id,
        sort_order=cat.sort_order, is_active=cat.is_active,
        created_at=cat.created_at, children=[],
    )


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    db.delete(cat)
    db.commit()
    return {"detail": "已删除"}
