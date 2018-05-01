from flask_restful import Resource, reqparse
from sqlalchemy import select, DateTime
import json
from Models import data
import decimal, datetime

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
            stmt = select([data.posts.c.id, data.posts.c.user_id, data.posts.c.title, data.posts.c.time, data.posts.c.expiry, data.posts.c.last_modified,
                           data.posts.c.description, data.posts.c.location, data.posts.c.lat, data.posts.c.lon]) \
                .select_from(data.posts).where(data.posts.c.id == post_id)
            res = data.conn.execute(stmt)
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
            stmt = select([data.posts.c.id, data.posts.c.user_id, data.posts.c.title, data.posts.c.time, data.posts.c.expiry, data.posts.c.last_modified,
                           data.posts.c.description, data.posts.c.location, data.posts.c.lat, data.posts.c.lon]) \
                .select_from(data.posts)
            res = data.conn.execute(stmt)
            res_dict = [dict(r) for r in res]
            serialize_dict = json.dumps(res_dict[0], default=alchemyencoder)
            deserialize_dict = json.loads(serialize_dict)
            return deserialize_dict

        except Exception as e:
            return {'error': str(e)}

    def post(self):     #create post
        # Parse the arguments
        parser = reqparse.RequestParser()
        self.make_parser_args(parser)
        args = parser.parse_args()

        _postUserId = args['user_id']
        _postTitle = args['title']
        _postTime = args['time']
        _postExpiry = args['expiry']
        _postLastModified = args['last_modified']
        _postDescription = args['description']
        _postLocation = args['location']
        _postLat = args['lat']
        _postLon = args['lon']

        #TODO: validate inputs

        stmt = data.posts.insert().values(user_id=_postUserId, title=_postTitle, time=_postTime, expiry=_postExpiry, last_modified=_postLastModified,
                                         description=_postDescription, location=_postLocation, lat=_postLat, lon=_postLon)
        res = data.conn.execute(stmt)
        return