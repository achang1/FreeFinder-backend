from flask_restful import Resource, reqparse
from sqlalchemy import select
import json
from Models import data, helperFns

class Comment(Resource):
    def get(self, comment_id): #HTTP verb to retrieve something
        try:
            stmt = select([data.comments.c.id, data.comments.c.post_id, data.comments.c.user_id,
                           data.comments.c.text_body, data.comments.c.date]) \
                .select_from(data.comments).where(data.comments.c.id == comment_id)
            res = data.conn.execute(stmt)
            res_dict = [dict(r) for r in res]
            if len(res_dict) == 0:
                return {}, 404
            serialize_dict = json.dumps(res_dict[0], default=helperFns.alchemyencoder)
            deserialize_dict = json.loads(serialize_dict)
            # print(deserialize_dict)
            return deserialize_dict

        except Exception as e:
            return {'error': str(e)}

class Comments(Resource):
    def make_parser_args(self, parser):
        parser.add_argument('post_id', type=int, help='Post id of thread')
        parser.add_argument('user_id', type=int, help='Poster of comment')
        parser.add_argument('text_body', type=str, help='Content of comment')
        parser.add_argument('date', type=str, help='Time of comment posting')

    def get(self):
        try:
            stmt = select([data.comments.c.id, data.comments.c.post_id, data.comments.c.user_id, data.posts.c.text_body,
                           data.posts.c.date]) \
                .select_from(data.comments)
            res = data.conn.execute(stmt)
            res_dict = [dict(r) for r in res]
            serialize_dict = json.dumps(res_dict[0], default=helperFns.alchemyencoder)
            deserialize_dict = json.loads(serialize_dict)
            return deserialize_dict

        except Exception as e:
            return {'error': str(e)}

    def post(self):     #create comment
        # Parse the arguments
        parser = reqparse.RequestParser()
        self.make_parser_args(parser)
        args = parser.parse_args()

        _commentPostId = args['post_id']
        _commentUserId = args['user_id']
        _commentTextBody = args['text_body']
        _commentDate = args['date']

        #TODO: validate inputs

        stmt = data.comments.insert().values(post_id=_commentPostId, user_id=_commentUserId, text_body=_commentTextBody, date=_commentDate)
        res = data.conn.execute(stmt)
        return