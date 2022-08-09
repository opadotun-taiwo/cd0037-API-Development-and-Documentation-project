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
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['total_categories'], 6)
        self.assertTrue(data['categories'])

    def test_404_beyond_valid_categories(self):
        res = self.client().get('/categoriess')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions(self):
        res = self.client().get("/questions", json={'page': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], 20)
        self.assertEqual(data['current_category'], 'Sports')
        self.assertTrue(data['categories'])

    def test_404_sent_a_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        res = self.client().delete("/questions/10")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_404_if_question_does_not_exist(self):
        res = self.client().delete("/questions/10")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_search_questions(self):
        res = self.client().post("/questions/search", json={"search":"title"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 2)
        self.assertTrue(data['total_questions'])

    def test_add_question(self):
        res = self.client().post("/questions", json={"question":"Next Nigeria president?", "answer":"Peter Obi", "difficulty":"3","category":"5"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)

    def test_failed_to_add_question(self):
        res = self.client().post("/questions", json={ "answer":"Peter Obi", "difficulty":"3","category":"5"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'],False)

    def test_search_questions_with_no_results(self):
        res = self.client().post("/questions/search", json={"search":"xxxxxxxxxxxxxx"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200) 
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)

    def test_get_questions_by_category(self):
        res = self.client().get("/categories/3/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 4)
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['current_category'])

    def test_questions_by_category_not_found(self):
        res = self.client().get("/categories/22/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_random_question_by_category(self):
        res = self.client().post("/quizzes", json={"previous_questions": [], "quiz_category":{"type":"Art", "id":"2"}})
        data = json.loads(res.data)

        print(data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question']['answer'], "Escher")
        self.assertEqual(data['question']['id'], 16)
        self.assertTrue(data['question'])

    def test_get_random_question_from_any_category(self):
        res = self.client().post("/quizzes", json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()