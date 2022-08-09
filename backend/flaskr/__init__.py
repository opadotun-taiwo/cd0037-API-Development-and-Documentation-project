import os
from flask import Flask, request, abort, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import sys

from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    #cors = CORS(app, resources={r"*/*": {"origins": "*"}})
    CORS(app)


    """
    TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-type,Authorization,true')
        response.headers.add('Access-Control_Allow-Methods', 'GET, POST, PATCH, PUT, DELETE, OPTIONS')
        return response


    """
    TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    @cross_origin()
    def get_categories():
        categories = Category.query.all()

        if len(categories) == 0:
            abort(404)

        category_format = {cat.id:cat.type for cat in categories}

        return jsonify({
            'success':True,
            'category':category_format
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        items_limit = request.args.get('limit', 10, type=int)
        selected_page = request.args.get('page', 1, type=int)
        current_index = selected_page - 1

        select_questions = Question.query.order_by(Question.id).limit(items_limit).offset(current_index * items_limit)
        questions = [q.format() for q in select_questions]

        select_categories = Category.query.order_by(Category.id).all()
        categories = {cat.id:cat.type for cat in select_categories}

        if len(questions) == 0:
            abort(404)

        response = jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(Question.query.all()),
            'current_category': 'Sports',
            'categories': categories
        })

        return response
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:delete_id>', methods=['DELETE'])
    def delete_question(delete_id):
        try:
            question = Question.query.filter(Question.id == delete_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()


            return jsonify({
                'success':True,
                'deleted':delete_id,
                'total_question':len(Question.query.all())
            })

        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    
    @app.route('/questions/', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        if new_question is None or new_answer is None or new_difficulty is None or new_category is None:
            abort(422)

        try:
            question = Question(
                question=new_question, 
                answer=new_answer, 
                category=new_category,
                difficulty=new_difficulty)

            question.insert()

            return jsonify({
            'success':True,
            })

        except:
            abort(422)

    """
    
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()
        search = body.get("search", None)

        select_questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search))).all()

        return jsonify({
            'success': True,
            'total_questions': len(select_questions),
            'current_category': 'Sports',
        })



    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def questions_by_category(category_id):
        items_limit = request.args.get('limit', 10, type=int)
        selected_page = request.args.get('page', 1, type=int)
        current_index = selected_page - 1

        current_category = Category.query.filter(Category.id == category_id).one_or_none()

        if current_category is None:
            abort(404)
        else:
            try:
                select_questions = Question.query.order_by(Question.id).filter(Question.category==category_id).limit(items_limit).offset(current_index * items_limit).all()
                
                questions = [q.format() for q in select_questions]

                if len(questions) == 0:
                    abort(404)

                select_categories = Category.query.order_by(Category.id).all()
                categories = [cat.format() for cat in select_categories]

                return jsonify({
                    'success': True,
                    'questions': questions,
                    'total_questions': len(questions),
                    'current_category': current_category.format(),
                    'categories': categories
                })
            except:
                print(sys.exc_info())
                abort(404)


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def quizzes ():
        try:
            body = request.get_json()
            previous_questions = body.get("previous_questions", [])
            quiz_category = body.get("quiz_category", 0)

            print(previous_questions, quiz_category)

            if quiz_category == 0 or quiz_category['id'] == 0:
                questions = Question.query.all()
                questions = [q.format() for q in questions]

                return jsonify({
                        'success': True,
                        'question': questions[random.randint(0, len(questions) - 1)]
                    })
            else:
                questions = Question.query.filter(Question.category == quiz_category['id']).all()

                questions = [q.format() for q in questions]

                for quest in questions:
                    while quest['id'] not in previous_questions:
                        print({
                            'success': True,
                            'question': quest
                        })
                        return jsonify({
                            'success': True,
                            'question': quest
                        })
                    
            return jsonify({
                        'success': True,
                        'question': None
                    })
        except:
            abort(404)
    
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success':False,
            'error':404,
            'message': "resourse not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success':False,
            'error':422,
            'message': "request cannot be processed"
        }), 422

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success':False,
            'error':405,
            'message': "method not allowed"
        }), 405


    @app.errorhandler(500)
    def internal_server(error):
        return jsonify({
            'success':False,
            'error':500,
            'message': "An internl server error occured"
        }), 500

    return app

