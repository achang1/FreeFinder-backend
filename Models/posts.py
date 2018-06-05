from flask_restful import Resource, reqparse
from sqlalchemy import select, DateTime, update, func
import json
from flask_jwt_simple import (
    jwt_required, create_jwt, get_jwt
)
from Models import data, helperFns
import traceback

class Post(Resource):
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

    def get(self, post_id): #HTTP verb to retrieve something
        try:
            stmt = select([data.posts.c.id, data.posts.c.user_id, data.posts.c.title, data.posts.c.time, data.posts.c.expiry, data.posts.c.last_modified,
                           data.posts.c.description, data.posts.c.location, data.posts.c.lat, data.posts.c.lon]) \
                .select_from(data.posts).where(data.posts.c.id == post_id)
            res = data.conn.execute(stmt)
            res_dict = [dict(r) for r in res]
            if len(res_dict) == 0:
                return {}, 404
            serialize_dict = json.dumps(res_dict[0], default=helperFns.alchemyencoder)
            deserialize_dict = json.loads(serialize_dict)
            return deserialize_dict

        except Exception as e:
            return {'error': str(e)}

    @jwt_required
    def put(self, post_id):
        parser = reqparse.RequestParser()
        self.make_parser_args(parser)
        args = parser.parse_args()

        _postTitle = args['title']
        _postLastModified = args['last_modified']
        _postDescription = args['description']
        _postLocation = args['location']
        _postLat = args['lat']
        _postLon = args['lon']

        user_jwt = get_jwt()
        jwt_user_id = user_jwt['id']

        try:
            stmt = select([data.posts.c.id, data.posts.c.user_id, data.posts.c.title, data.posts.c.time, data.posts.c.expiry,
                 data.posts.c.last_modified, data.posts.c.description, data.posts.c.location, data.posts.c.lat, data.posts.c.lon]) \
                .select_from(data.posts).where(data.posts.c.id == post_id)
            res = data.conn.execute(stmt)
            res_dict = [dict(r) for r in res]

            if jwt_user_id != res_dict[0]['user_id']:
                return {'message': 'Unauthorized'}, 403

            if len(res_dict) == 0:
                return {'message': 'Post does not exist'}, 404

            #TODO: check if fields are modified

            stmt = update(data.posts).where(data.posts.c.id == post_id). \
                values(title=_postTitle, last_modified=_postLastModified, description=_postDescription,
                       location=_postLocation, lat=_postLat, lon=_postLon)
            res = data.conn.execute(stmt)
            return {}, 200

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
            serialize_dict = json.dumps(res_dict, default=helperFns.alchemyencoder)
            deserialize_dict = json.loads(serialize_dict)
            return deserialize_dict

        except Exception as e:
            return {'error': str(e)}

    @jwt_required
    def post(self):     #create post
        # Parse the arguments
        parser = reqparse.RequestParser()
        self.make_parser_args(parser)
        args = parser.parse_args()

        user_jwt = get_jwt()
        jwt_user_id = user_jwt['id']
        # print("user jwt id:", jwt_user_id)

        _postTitle = args['title']
        _postTime = args['time']
        _postExpiry = args['expiry']
        _postDescription = args['description']
        _postLocation = args['location']
        _postLat = args['lat']
        _postLon = args['lon']

        #TODO: check validity of user

        #checking validity of lat and lon
        if (_postLat >= 90) or (_postLat <= -90):
            return {'message': 'Invalid Request'}, 400
        elif (_postLon >= 180) or (_postLon <= -180):
            return {'message': 'Invalid Request'}, 400
        else:
            stmt = data.posts.insert().values(user_id=jwt_user_id, title=_postTitle, time=_postTime, expiry=_postExpiry,
                                              description=_postDescription, location=_postLocation, lat=_postLat, lon=_postLon)
            res = data.conn.execute(stmt)
        return


def calc_distance(p1, p2):
    return func.sqrt(func.pow(69.1 * (p1[0] - p2[0], 2) + func.pow(53.0 * (p1[1] - p2[1]), 2)))


class NearbyPosts(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('lat', type=float, help='current latitude', location='args')
        parser.add_argument('lon', type=float, help='current longitude', location='args')
        args = parser.parse_args()

        _lat = args['lat']
        _lon = args['lon']

        lat_float = float(_lat)
        lon_float = float(_lon)

        try:
            # stmt = select([data.posts.c.id, data.posts.c.user_id, data.posts.c.title, data.posts.c.time, data.posts.c.expiry, data.posts.c.last_modified,
            #                data.posts.c.description, data.posts.c.location, data.posts.c.lat, data.posts.c.lon]) \
            #     .select_from(data.posts).order_by(calc_distance(data.posts.get_lat_lon(), (lat_float, lon_float)))
            # res = data.conn.execute(stmt)

            query = "SELECT `id`, `user_id`, `title`, `time`, `expiry`, `last_modified`, `description`, `location`, `lat`, `lon`," \
                    "ACOS(SIN(PI()*`lat`/180.0)*SIN(PI()*"+str(lat_float)+"/180.0)+COS(PI()*`lat`/180.0)*COS(PI()*"+str(lat_float)+"/180.0)*COS(PI()*`lon`/180.0-PI()*"+str(lon_float)+"/180.0))*6371 as `distance`" \
                    "FROM `posts` WHERE `lat` IS NOT NULL ORDER BY `distance` ASC"
            print(query)
            res = data.conn.execute(query)
            res_dict = [dict(r) for r in res]
            serialize_dict = json.dumps(res_dict, default=helperFns.alchemyencoder)
            deserialize_dict = json.loads(serialize_dict)
            return deserialize_dict

        except Exception as e:
            traceback.print_exc()
            return {'error': str(e)}
