from flask import Blueprint, request, jsonify
from app.cmd.http import user_usecase
from app.infrastructure.http.base import json
from app.domain.model.user import User

user_controller = Blueprint('user_controller', __name__)


@user_controller.route('/users', methods=['POST'])
@json
def sign_up():
    pass


@user_controller.route('/users', methods=['POST'])
def login():
    pass


@user_controller.route('/admin/users', methods=['POST'])
@json
def create_new_user_by_admin():
    content: dict = request.get_json(silent=True)
    email = content.get('email', '')
    password = content.get('password', '')
    user = user_usecase.create_new_user(email, password, '')
    return user.to_json()


@user_controller.route('/admin/users', methods=['GET'])
@json
def find_all():
    search_word = request.args.get('email', '')
    users = user_usecase.search(search_word)
    res = []
    for u in users:
        res.append(u.to_json())
    return res


@user_controller.route('/admin/users/<id>') 
@json
def find_one(id):
    user = user_usecase.find_by_id(id)
    return user.to_json()


@user_controller.route('/users/<id>/password', methods=['PUT'])
@json
def update_password(id):
    content: dict = request.get_json(silent=True)
    old_password = content.get('old_password', '')
    new_password = content.get('new_password', '')
    retype_password = content.get('retype_password', '')
    return user_usecase.update_password(id, old_password, new_password, retype_password)

@user_controller.route('/users/<id>/confirm', methods=['PUT'])
@json
def update_is_confirmed(id):
    content: dict = request.get_json(silent=True)
    old_password = content.get('is_confirmed', False)
    return user_usecase.update_password(id, old_password, new_password, retype_password)



@user_controller.route('/users/<id>', methods=['DELETE'])
def delete(id):
    pass
