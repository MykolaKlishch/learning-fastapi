from fastapi import Depends, HTTPException, status, APIRouter, Request, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

import models
from database import get_db, engine
from routers.auth import get_current_user, LoginForm, login_for_access_token, get_password_hash

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory='./templates')


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={401: {"user": "Not authorized"}}
)


class NewPassword(BaseModel):
    password: str


@router.get('/')
async def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.Users).all()


@router.get('/user/')
@router.get('/user/{user_id}')
async def get_user_by_id(
        user_id: int,
        db: Session = Depends(get_db)
):
    user_model = db.query(models.Users) \
        .filter(models.Users.id == user_id) \
        .first()

    if user_model is not None:
        return user_model
    raise HTTPException(status_code=404, detail='User not found')


@router.delete('/')
async def delete_user(
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if user is None:
        raise HTTPException(status_code=404, detail='Not Found')

    user_model = db.query(models.Users) \
        .filter(models.Users.id == user.get('id')) \
        .first()

    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found')

    db.query(models.Users) \
        .filter(models.Users.id == user.get('id')) \
        .delete()

    db.commit()

    return "Successful"


# # todo it may be better to ask for a username and old password
# #  instead of asking for token
# #  but this implementation works as well and has the same security implications
# @router.patch('/password')
# async def change_password(
#         new_password: NewPassword,
#         user: dict = Depends(get_current_user),
#         db: Session = Depends(get_db)
# ):
#     if user is None:
#         raise HTTPException(status_code=404, detail='Not Found')
#
#     user_model = db.query(models.Users) \
#         .filter(models.Users.id == user.get('id')) \
#         .first()
#
#     if user_model is None:
#         raise HTTPException(status_code=404, detail='User not found')
#
#     hash_password = get_password_hash(new_password.password)
#     user_model.hashed_password = hash_password
#
#     db.commit()
#
#     return user_model


@router.get('/reset-password', response_class=HTMLResponse)
async def reset_password_page(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse('reset-password.html', {'request': request, 'user': user})


@router.post('/reset-password', response_class=HTMLResponse)
async def reset_password(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        new_password: str = Form(...),
        db: Session = Depends(get_db),
):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)
        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)
        if not validate_user_cookie:
            msg = 'Incorrect Username or Password'
            return templates.TemplateResponse('reset-password.html', {'request': request, 'msg': msg})
        if password == new_password:
            msg = 'New password is identical to old password'
            return templates.TemplateResponse('reset-password.html', {'request': request, 'msg': msg})

        user_model = db.query(models.Users).filter(models.Users.username == email).first()

        hash_password = get_password_hash(new_password)
        user_model.hashed_password = hash_password

        db.commit()

        msg = 'Reset Successful'
        response = templates.TemplateResponse('login.html', {'request': request, 'msg': msg})
        response.delete_cookie(key='access_token')
        return response

    except HTTPException:
        msg = 'Unknown Error'
        return templates.TemplateResponse('reset-password.html', {'request': request, 'msg': msg})

