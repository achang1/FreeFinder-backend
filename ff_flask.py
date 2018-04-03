from flask import Flask
from flask_restful import Resource, Api, reqparse
from sqlalchemy import create_engine, select, insert, MetaData, Table, Column, Integer, String, ForeignKey, Sequence
import decimal, datetime
import json
import bcrypt

engine = create_engine('mysql://freefinder_admin:test123@70.79.100.163/ff_db')
conn = engine.connect()

app = Flask(__name__)
api = Api(app)

metadata = MetaData()



users = Table('users', metadata,
    Column('id', Integer, Sequence('user_id_seq'), primary_key=True),
    Column('email', String(50), nullable=False, unique=True),
    Column('name', String(50), nullable=False),
    Column('password', String(255), nullable=False),
    Column('phone', String(50)),
    Column('location', String(50)),
)

# metadata.create_all(engine)
#Usage: json.dumps([dict(r) for r in res], default=alchemyencoder)
def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

class User(Resource):
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

class Users(Resource):
    def post(self):
        # Parse the arguments
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help='Email address to create user')
        parser.add_argument('name', type=str, help='Name to create user')
        parser.add_argument('password', type=str, help='Password to create user')
        parser.add_argument('phone', type=str, help='Phone to create user')
        parser.add_argument('location', type=str, help='Location to create user')
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



api.add_resource(Users, '/users')
api.add_resource(User, '/users/<string:user_id>')

if __name__ == '__main__':
    app.run(debug=True)
    # app.run()
