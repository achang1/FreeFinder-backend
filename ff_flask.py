from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse, current_app
from sqlalchemy import create_engine, Float, DateTime, select, insert, MetaData, Table, Column, Integer, String, ForeignKey, Sequence
import decimal, datetime
import json
import bcrypt
from flask_jwt import jwt_required
from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt
)
from datetime import datetime

# from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt

engine = create_engine('mysql://freefinder_admin:test123@70.79.100.163/ff_db')
conn = engine.connect()

app = Flask(__name__)
api = Api(app)

app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_KEY_LOCATION'] = ['headers']

jwt = JWTManager(app)


metadata = MetaData()

users = Table('users', metadata,
    Column('id', Integer, Sequence('user_id_seq'), primary_key=True),
    Column('email', String(50), nullable=False, unique=True),
    Column('name', String(50), nullable=False),
    Column('password', String(255), nullable=False),
    Column('phone', String(50)),
    Column('location', String(50)),
)

posts = Table('posts', metadata,
    Column('id', Integer, Sequence('post_id_seq'), primary_key=True),
    Column('user_id', Integer, ForeignKey("users.id"), nullable=False),
    Column('title', String(50), nullable=False),
    Column('time', DateTime, nullable=False),
    Column('expiry', DateTime),
    Column('last_modified', DateTime, onupdate=datetime.now(), nullable=False),
    Column('description', String(5000), nullable=False),
    Column('location', String(50), nullable=False),
    Column('lat', Float),
    Column('lon', Float),
)


@jwt.jwt_data_loader
def add_claims_to_access_token(body):
    now = datetime.utcnow()
    return {
        'exp': now + current_app.config['JWT_EXPIRES'],
        'iat': now,
        'nbf': now,
        'sub': body['email'],
        'id': body['id'],
        # 'roles': roles
    }

# metadata.create_all(engine)
#Usage: json.dumps([dict(r) for r in res], default=alchemyencoder)
def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, (datetime, DateTime)):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

class Post(Resource):
    def get(self, post_id): #HTTP verb to retrieve something
        try:
            stmt = select([posts.c.id, posts.c.user_id, posts.c.title, posts.c.time, posts.c.expiry, posts.c.last_modified,
                           posts.c.description, posts.c.location, posts.c.lat, posts.c.lon]) \
                .select_from(posts).where(posts.c.id == post_id)
            res = conn.execute(stmt)
            res_dict = [dict(r) for r in res]
            if len(res_dict) == 0:
                return {}, 404
            serialize_dict = json.dumps(res_dict[0], default=alchemyencoder)
            deserialize_dict = json.loads(serialize_dict)
            # print(deserialize_dict)
            return deserialize_dict

        except Exception as e:
            return {'error': str(e)}

class Posts(Resource):
    def make_parser_args(self, parser):
        parser.add_argument('user_id', type=int, help='User of post')
        parser.add_argument('title', type=str, help='Title of post')
        parser.add_argument('time', type=str, help='Time of post')
        parser.add_argument('expiry', type=str, help='Expiry time of post')
        parser.add_argument('last_modified', type=str, help='Last modified time of post')
        parser.add_argument('description', type=str, help='Description of post')
        parser.add_argument('location', type=str, help='Location to create user')
        parser.add_argument('lat', type=float, help='Latitude of post')
        parser.add_argument('lon', type=float, help='Longitude time of post')

    def get(self):
        try:
            stmt = select([posts.c.id, posts.c.user_id, posts.c.title, posts.c.time, posts.c.expiry, posts.c.last_modified,
                 posts.c.description, posts.c.location, posts.c.lat, posts.c.lon]) \
                .select_from(posts)
            res = conn.execute(stmt)
            res_dict = [dict(r) for r in res]
            serialize_dict = json.dumps(res_dict[0], default=alchemyencoder)
            deserialize_dict = json.loads(serialize_dict)
            return deserialize_dict

        except Exception as e:
            return {'error': str(e)}


class User(Resource):
    def make_parser_args(self, parser):
        parser.add_argument('email', type=str, help='Email address to create user')
        parser.add_argument('name', type=str, help='Name to create user')
        parser.add_argument('password', type=str, help='Password to create user')
        parser.add_argument('phone', type=str, help='Phone to create user')
        parser.add_argument('location', type=str, help='Location to create user')

    def get(self, user_id):
        try:
            stmt = select([users.c.id, users.c.name, users.c.email, users.c.phone, users.c.location])\
                .select_from(users).where(users.c.id == user_id)
            res = conn.execute(stmt)
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
        print('PUT /users/' + user_id)
        print(get_jwt())

class Users(Resource):
    def make_parser_args(self, parser):
        parser.add_argument('email', type=str, help='Email address to create user')
        parser.add_argument('name', type=str, help='Name to create user')
        parser.add_argument('password', type=str, help='Password to create user')
        parser.add_argument('phone', type=str, help='Phone to create user')
        parser.add_argument('location', type=str, help='Location to create user')

    def get(self):
        try:
            stmt = select([users.c.id, users.c.name, users.c.email, users.c.phone, users.c.location])\
                .select_from(users)
            res = conn.execute(stmt)
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

        stmt = select([users.c.id, users.c.name, users.c.email, users.c.phone, users.c.location]) \
            .select_from(users).where(users.c.email == _userEmail)
        res = conn.execute(stmt)
        res_dict = [dict(r) for r in res]

        #TODO: validate inputs

        password_bytes = _userPassword.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

        if len(res_dict) > 0: # user already exists
            return {'message': 'User already exists in database'}, 400
        else:
            stmt = users.insert().values(email=_userEmail, name=_userName, phone=_userPhone, location=_userLocation, password=hashed)
            res = conn.execute(stmt)
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

        stmt = select([users.c.id, users.c.name, users.c.email, users.c.phone, users.c.location, users.c.password]) \
            .select_from(users).where(users.c.email == _userEmail)
        res = conn.execute(stmt)
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




api.add_resource(Users, '/users')
api.add_resource(User, '/users/<string:user_id>')
api.add_resource(Login, '/login')
api.add_resource(Posts, '/posts/')
api.add_resource(Post, '/posts/<string:post_id>')

if __name__ == '__main__':
    app.run(debug=True)
    # app.run()
