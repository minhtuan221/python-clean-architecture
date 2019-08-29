from flask import Blueprint, request, jsonify
from app.cmd.http import user_usecase, middleware
from app.domain.model.user import User
from app.domain.model.errors import Error

user_controller = Blueprint('user_controller', __name__)


@user_controller.route('/users', methods=['POST'])
@middleware.json
def sign_up():
    pass


@user_controller.route('/login', methods=['POST'])
@middleware.json
def login():
    content: dict = request.get_json(silent=True)
    email = content.get('email', '')
    password = content.get('password', '')
    token = user_usecase.login(email, password)
    return {'token': token}


@user_controller.route('/admin/users', methods=['POST'])
@middleware.json
def create_new_user_by_admin():
    content: dict = request.get_json(silent=True)
    email = content.get('email', '')
    password = content.get('password', '')
    user = user_usecase.create_new_user(email, password, '')
    return user.to_json()


@user_controller.route('/admin/users', methods=['GET'])
@middleware.json
@middleware.verify_auth_token
def find_all():
    search_word = request.args.get('email', '')
    users = user_usecase.search(search_word)
    res = []
    for u in users:
        res.append(u.to_json())
    return res


@user_controller.route('/admin/users/<id>')
@middleware.json
@middleware.verify_auth_token
def find_one(id):
    user = user_usecase.find_by_id(id)
    if user:
        return user.to_json()
    return None


@user_controller.route('/users/<id>/password', methods=['PUT'])
@middleware.json
def update_password(id):
    content: dict = request.get_json(silent=True)
    old_password = content.get('old_password', '')
    new_password = content.get('new_password', '')
    retype_password = content.get('retype_password', '')
    return user_usecase.update_password(id, old_password, new_password, retype_password)


@user_controller.route('/users/<id>/confirm', methods=['PUT'])
@middleware.json
def update_is_confirmed(id):
    content: dict = request.get_json(silent=True)
    old_password = content.get('is_confirmed', False)
    new_password = content.get('new_password', '')
    retype_password = content.get('retype_password', '')
    return user_usecase.update_password(id, old_password, new_password, retype_password)


@user_controller.route('/users/<id>', methods=['DELETE'])
@middleware.json
def delete(id):
    pass
