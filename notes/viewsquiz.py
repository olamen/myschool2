import json
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from notes.models import Quiz
from django.views.generic import ListView
from .models import NoteComposition, Exam, NoteDevoir, Quiz, Question, Answer, Result, Student
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import logging
from django.contrib import messages


class QuiZListView(ListView):
    model = Quiz
    template_name = 'quiz/quiz_main.html'
    #context_object_name = 'quizzes'

    def get_queryset(self):
        return Quiz.objects.filter(is_active=True)  # Filter active quizzes
    
@login_required   
def quiz_view(request, pk):
    quiz =  get_object_or_404(Quiz,pk=pk)
    #questions = quiz.get_questions()
    
    print("olame")
    return render(request, 'quiz/quiz_view.html', {'obj': quiz,})

@login_required
def quiz_data_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = []
    for q in quiz.get_questions():
        answers =[]
        for a in q.get_answers():
            answers.append({
                'text': a.text,            })
        questions.append({
            'id': q.id,  # Include the question ID
            'text': str(q),  # Include the question text
            'answers': answers
        })
    return JsonResponse({'data': questions, 'time': quiz.time})

logger = logging.getLogger(__name__)  # Django logging setup


@csrf_exempt
@login_required
def save_quiz_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)  # Retrieve the Quiz object using the pk
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            
            # Extract quiz answers (excluding CSRF token)
            quiz_answers = {k: v for k, v in data.items() if k != "csrfmiddlewaretoken"}
            print(f"Final extracted answers: {quiz_answers}")

            correct_count = 0  # Initialize a counter for correct answers
            total_questions = 0 # Initialize a counter for total questions

            for key, submitted_answer in quiz_answers.items():
                # Skip the csrfmiddlewaretoken
                if key == 'csrfmiddlewaretoken':
                    continue

                # Extract the question ID from the key
                try:
                    question_id = int(key.replace("question-", ""))  # Remove "question-" and convert to int
                except ValueError:
                    print(f"Invalid key format: {key}")
                    continue
                print(f"Extracted Question ID: {question_id}")

                try:
                    # Get the Question object
                    question = Question.objects.get(pk=question_id)
                    total_questions += 1

                    # Get the correct Answer for the Question
                    correct_answer = Answer.objects.get(question=question, correct=True)

                    print(f"Question: {question}, Correct Answer: {correct_answer.text}, Submitted Answer: {submitted_answer}")

                    # Compare the submitted answer with the correct answer
                    if submitted_answer == correct_answer.text:
                        correct_count += 1
                        print("Correct Answer!")
                    else:
                        print("Incorrect Answer!")

                except Question.DoesNotExist:
                    print(f"Question with ID {question_id} does not exist.")
                    continue  # Skip to the next question
                except Answer.DoesNotExist:
                    print(f"No correct answer found for question with ID {question_id}.")
                    continue  # Skip to the next question
                except Exception as e:
                    print(f"An error occurred: {e}")
                    continue  # Skip to the next question

            # Calculate the score (percentage of correct answers)
            if total_questions > 0:
                score = (correct_count / total_questions) * 100
            else:
                score = 0

            print(f"Final Score: {score}")

            # Get the Student object associated with the logged-in user
            try:
                student = Student.objects.get(user=request.user)
            except Student.DoesNotExist:
                print(f"No Student object found for user {request.user}")
                return JsonResponse({"error": "No Student object found for this user"}, status=400)

            # Save the score to the Result model
            result = Result.objects.create(quiz=quiz, student=student, score=score)
            result.save()

            # Determine the redirect URL based on the score
            if score >= quiz.required_score_to_pass:
                redirect_url = f"/notes/quiz/?message=congrats"  # Success URL
            else:
                redirect_url = f"/notes/quiz/?message=failed"  # Failure URL

            return JsonResponse({"redirect_url": redirect_url})

        except json.JSONDecodeError:
            print("Failed to decode JSON.")
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            print(f"An error occurred: {e}")
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)



