import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client

        DATABASE = os.environ.get('DATABASE')
        DATABASE_NAME = os.environ.get('DATABASE_NAME')
        username = os.environ.get('DATABASE_USER')
        password = os.environ.get('DATABASE_PASSWORD')
        url = os.environ.get('DATABASE_HOSTPORT')
        database_URI = "{}://{}:{}@{}/{}".format(
            DATABASE, username, password, url, DATABASE_NAME)

        self.database_path = database_URI
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'How about udaicty FSND project?',
            'answer': 'It\'s really excellent!',
            'difficulty': 3,
            'category': '1'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation
    and for expected errors.
    """
    def test_get_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['categories'])

    def test_search_questions(self):
        response = self.client().post('/questions',
                                      json={'searchTerm': 'boxer'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['questions'][0]['id'], 9)
        self.assertEqual(
            data['questions'][0]['question'],
            'What boxer\'s original name is Cassius Clay?')

    def test_post_new_questions(self):
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['created'])

        question = Question.query.filter_by(id=data['created']).first()
        question.delete()

    def test_delete_question(self):
        # To test 'delete', we insert a question to delete
        question = Question(
            question=self.new_question['question'],
            answer=self.new_question['answer'],
            category=self.new_question['category'],
            difficulty=self.new_question['difficulty'])
        question.insert()

        response = self.client().delete('/questions/{}'.format(question.id))
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question.id)

    def test_category_questions(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['current_category'])

    def test_play_quiz_game(self):
        response = self.client().post('/quizzes',
                                      json={'previous_questions': [2, 6],
                                            'quiz_category': {
                                                'type': 'Entertainment',
                                                'id': '5'}})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 5)
        self.assertNotEqual(data['question']['id'], 2)
        self.assertNotEqual(data['question']['id'], 6)

    def test_play_quiz_fails(self):
        response = self.client().post('/quizzes', json={})

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_404_request(self):
        # send request with bad page data, load response
        response = self.client().get('/questions?page=10000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
