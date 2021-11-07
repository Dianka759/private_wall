from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash

class Message:
    def __init__(self,data):
        self.id = data['id']
        self.message = data['message']
        self.user_id = data['user_id']
        self.friend_id = data['friend_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @staticmethod                                   #checks if the message is empty
    def validate_msg(message):
        is_valid = True
        if len(message['message']) < 0:
            flash("message cannot be empty")
            is_valid= False
        return is_valid

    @classmethod                                    #saves messages into the database
    def save_message(cls,data):
        query = "INSERT INTO messages (message, user_id, friend_id, created_at, updated_at) VALUES (%(message)s, %(user_id)s, %(friend_id)s, NOW(), NOW())"
        return connectToMySQL("users_schema").query_db(query,data)

    @classmethod                                    #counts how many messages a specific user sent
    def count_msg(cls,data):
        query = "SELECT COUNT(*) FROM messages WHERE user_id=%(id)s;"
        return connectToMySQL("users_schema").query_db(query,data)

    @classmethod                                    #counts how many messages are currently addressed/sent to this specific user
    def total_messages(cls,data):
        query = "SELECT COUNT(*) FROM users JOIN messages ON users.id = messages.user_id WHERE friend_id = %(id)s;"
        return connectToMySQL("users_schema").query_db(query,data)

    @classmethod                                    #deletes a specific message
    def delete_message(cls,data):
        query = "DELETE FROM messages WHERE id = %(id)s"
        return connectToMySQL("users_schema").query_db(query,data)