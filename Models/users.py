from flask import jsonify
from flask_restful import Resource, reqparse, current_app
from sqlalchemy import select, update
import bcrypt
from flask_jwt_simple import (
    jwt_required, create_jwt, get_jwt
)
from Models import data

class User(Resource):
    def make_parser_args(self, parser):
        parser.add_argument('email', type=str, help='Email address to create user')
        parser.add_argument('name', type=str, help='Name to create user')
        parser.add_argument('password', type=str, help='Password to create user')
        parser.add_argument('phone', type=str, help='Phone to create user')
        parser.add_argument('location', type=str, help='Location to create user')

    def get(self, user_id):
        try:
            stmt = select([data.users.c.id, data.users.c.name, data.users.c.email, data.users.c.phone, data.users.c.location])\
                .select_from(data.users).where(data.users.c.id == user_id)
            res = data.conn.execute(stmt)
            res_dict = [dict(r) for r in res]
            if len(res_dict) == 0:
                return {}, 404
            else:
                return res_dict[0]
            # return {'good': 'good'}

        except Exception as e:
            return {'error': str(e)}


    @jwt_required
    def put(self, user_id):
        parser = reqparse.RequestParser()
        self.make_parser_args(parser)
        args = parser.parse_args()

        _userEmail = args['email']
        _userName = args['name']
        # _userPassword = args['password']
        _userPhone = args['phone']
        _userLocation = args['location']

        user_jwt = get_jwt()
        if (user_jwt['id'] != int(user_id)):
            return {}, 404

        try:
            stmt = select([data.users.c.id, data.users.c.name, data.users.c.email, data.users.c.phone, data.users.c.location])\
                .select_from(data.users).where((data.users.c.id != user_id) & (data.users.c.email == _userEmail))    #checks if email has been used by another user
            res = data.conn.execute(stmt)
            res_dict = [dict(r) for r in res]
            if len(res_dict) > 0:
                return {}, 400

            stmt = update(data.users).where(data.users.c.id == user_jwt['id']).\
                values(email=_userEmail, name=_userName, phone=_userPhone, location=_userLocation)
            res = data.conn.execute(stmt)
            return {}, 200

        except Exception as e:
            return {'error': str(e)}

class Users(Resource):
    def make_parser_args(self, parser):
        parser.add_argument('email', type=str, help='Email address to create user')
        parser.add_argument('name', type=str, help='Name to create user')
        parser.add_argument('password', type=str, help='Password to create user')
        parser.add_argument('phone', type=str, help='Phone to create user')
        parser.add_argument('location', type=str, help='Location to create user')

    def get(self):
        try:
            stmt = select([data.users.c.id, data.users.c.name, data.users.c.email, data.users.c.phone, data.users.c.location])\
                .select_from(data.users)
            res = data.conn.execute(stmt)
            res_dict = [dict(r) for r in res]
            return res_dict

        except Exception as e:
            return {'error': str(e)}


    def post(self):     #create user
        # Parse the arguments
        parser = reqparse.RequestParser()
        self.make_parser_args(parser)
        args = parser.parse_args()

        _userEmail = args['email']
        _userName = args['name']
        _userPassword = args['password']
        _userPhone = args['phone']
        _userLocation = args['location']

        stmt = select([data.users.c.id, data.users.c.name, data.users.c.email, data.users.c.phone, data.users.c.location]) \
            .select_from(data.users).where(data.users.c.email == _userEmail)
        res = data.conn.execute(stmt)
        res_dict = [dict(r) for r in res]

        password_bytes = _userPassword.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

        if len(res_dict) > 0: # user already exists
            return {'message': 'User already exists in database'}, 400
        else:
            stmt = data.users.insert().values(email=_userEmail, name=_userName, phone=_userPhone, location=_userLocation, password=hashed)
            res = data.conn.execute(stmt)
            return

        # print(_userEmail, _userName, _userPassword, _userPhone, _userLocation)

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help='Email address to create user')
        parser.add_argument('password', type=str, help='Password to create user')
        args = parser.parse_args()

        _userEmail = args['email']
        _userPassword = args['password']

        stmt = select([data.users.c.id, data.users.c.name, data.users.c.email, data.users.c.phone, data.users.c.location, data.users.c.password]) \
            .select_from(data.users).where(data.users.c.email == _userEmail)
        res = data.conn.execute(stmt)
        res_dict = [dict(r) for r in res]
        if not len(res_dict):
            return {'message': 'Invalid Credentials'}, 401
        encrypted_pass = res_dict[0]['password']
        if bcrypt.checkpw(_userPassword.encode('utf-8'), hashed_password=encrypted_pass.encode('utf-8')):
            ret = {'token': create_jwt({
                'email': res_dict[0]['email'],
                'id': res_dict[0]['id']
            })}
            res = jsonify(ret)
            res.status_code = 200
            return res

        else:
            return {'message': 'Invalid Credentials'}, 401
