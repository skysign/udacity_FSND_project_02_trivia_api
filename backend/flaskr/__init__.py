import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO:
    Set up CORS. Allow '*' for origins. Delete the sample route
    after completing the TODOs
    '''
    CORS(app, resources={'/': {'origins': '*'}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests for all available categories.
    '''

    @app.route('/categories', methods=['GET'])
    def get_categories():
        # get all categories and add to dict
        categories = Category.query.all()
        dict = {}
        for category in categories:
            dict[category.id] = category.type

        # abort 404 if no categories found
        if (len(dict) == 0):
            abort(404)

        # return data to view
        return jsonify({
            'success': True,
            'categories': dict
        })

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen
    for three pages.
    Clicking on the page numbers should update the questions.
    '''

    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)

        pagination = Question.query.order_by(Question.id.desc()).paginate(
            page=page, per_page=QUESTIONS_PER_PAGE)
        questions = [q.format() for q in pagination.items]
        categories = Category.query.all()
        dictCategories = {}

        for category in categories:
            dictCategories[category.id] = category.type

        if (len(questions) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': pagination.total,
            'categories': dictCategories
        })

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed. This removal will persist in the database
    and when you refresh the page.
    '''

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter_by(id=id).first()

            if question is None:
                abort(404)

            question.delete()

        except Exception as e:
            print(e)
            abort(422)

        # return success response
        return jsonify({
            'success': True,
            'deleted': question.id
        })

    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of
    the last page of the questions list in the "List" tab.
    '''

    @app.route('/questions', methods=['POST'])
    def post_question():
        jsonQuestion = request.get_json()

        if (jsonQuestion.get('searchTerm')):
            try:
                search = jsonQuestion.get('searchTerm')
                questions = Question.query.filter(
                    Question.question.ilike(f'%{search}%')).all()
            except Exception as e:
                print(e)
                abort(422)

            questions = [q.format() for q in questions]
            cntQuestions = len(questions)

            if (cntQuestions == 0):
                abort(404)

            page = request.args.get('page', 1, type=int)
            begin = (page - 1) * QUESTIONS_PER_PAGE
            end = min(begin + QUESTIONS_PER_PAGE, cntQuestions)
            questionsInPage = questions[begin:end]

            return jsonify({
                'success': True,
                'questions': questionsInPage,
                'total_questions': len(questions)
            })

        new_question = jsonQuestion.get('question')
        new_answer = jsonQuestion.get('answer')
        new_difficulty = jsonQuestion.get('difficulty')
        new_category = jsonQuestion.get('category')

        if ((new_question is None) or
                (new_answer is None) or
                (new_difficulty is None) or
                (new_category is None)):
            abort(422)

        try:
            newQuestion = Question(
              question=new_question, answer=new_answer,
              difficulty=new_difficulty, category=new_category)
            newQuestion.insert()

            questions = Question.query.order_by(Question.id).all()
            questionsInPage = [q.format() for q in questions]
            cntQuestions = len(questions)

        except Exception as e:
            print(e)
            abort(422)

        return jsonify({
            'success': True,
            'created': newQuestion.id,
            'question_created': newQuestion.question,
            'questions': questionsInPage,
            'total_questions': cntQuestions
        })

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''

    @app.route('/categories/<int:id>/questions')
    def get_questions_in_category(id):
        try:
            category = Category.query.filter_by(id=id).first()

            if (category is None):
                abort(400)

            questions = Question.query.filter_by(category=category.id).all()
        except Exception as e:
            print(e)
            abort(400)

        questions = [q.format() for q in questions]

        cntQuestions = len(questions)
        page = request.args.get('page', 1, type=int)
        begin = (page - 1) * QUESTIONS_PER_PAGE
        end = min(begin + QUESTIONS_PER_PAGE, cntQuestions)
        questionsInPage = questions[begin:end]

        return jsonify({
            'success': True,
            'questions': questionsInPage,
            'total_questions': cntQuestions,
            'current_category': category.type
        })

    def check_params_quizzes(json):
        if (json.get('previous_questions') is None):
            return False

        if (json.get('quiz_category') is None):
            return False

        if (json.get('quiz_category')['id'] is None):
            return False

        return True

    def check_previous(pre_question_ids, id):
        for p_id in pre_question_ids:
            if p_id == id:
                return True

        return False

    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''

    @app.route('/quizzes', methods=['POST'])
    def post_quizzes():
        json = request.get_json()
        category = json.get('quiz_category')
        pre_question_ids = json.get('previous_questions')

        if False is check_params_quizzes(json):
            abort(422)

        try:
            category = int(category['id'])
            all_questions = Question.query.all() if (category == 0) \
                else Question.query.filter_by(category=category).all()
        except Exception as e:
            print(e)
            abort(422)

        no_previous_questions = []

        for question in all_questions:
            if check_previous(pre_question_ids, question.id) is False:
                no_previous_questions.append(question)

        if len(no_previous_questions) <= 0:
            return jsonify({'success': False})

        random.shuffle(no_previous_questions)
        new_question = no_previous_questions[0].format()

        print(new_question)

        return jsonify({
            'success': True,
            'question': new_question
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not Found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    return app
