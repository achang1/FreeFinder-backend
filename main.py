from flask import Flask
from flask_restful import Api, current_app
from flask_jwt_simple import (
    JWTManager
)

from datetime import datetime

app = Flask(__name__)
api = Api(app)

app = Flask(__name__)
api = Api(app)

app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_KEY_LOCATION'] = ['headers']

jwt = JWTManager(app)

import Models.data
from Models import users, posts, comments

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

api.add_resource(users.Users, '/users')
api.add_resource(users.User, '/users/<string:user_id>')
api.add_resource(users.Login, '/login')
api.add_resource(posts.Posts, '/posts')
api.add_resource(posts.Post, '/posts/<string:post_id>')
api.add_resource(comments.Comments, '/comments/')
api.add_resource(comments.Comment, '/comments/<string:comment_id>')


if __name__ == '__main__':
    app.run(debug=True)