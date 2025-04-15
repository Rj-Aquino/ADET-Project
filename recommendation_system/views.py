from django.shortcuts import render
from .forms import SearchForm
#from .search import enhanced_search  # Assuming you have a search.py file with enhanced_search function
from .models import UserInput, ResearchPaper
from django.core.paginator import Paginator
from django.db.models.functions import Replace  # Add this import
from django.db.models import Value  # Add this import
from django.db.models.functions import Replace
import requests
from django.shortcuts import render
from dotenv import load_dotenv
import os
import time
import json
import ast

# Home view to display the search form
def home(request):
    return render(request, 'home.html', {'active_page': 'home'})

def history(request):
    return render(request, 'history.html')

def pinecone(request):
    return render(request, 'pinecone.html', {'active_page': 'history'})

def exa(request):
    return render(request, 'exa.html', {'active_page': 'history'})

def search_view(request):
    query = request.GET.get('query', '')
    results = []

    if query:
        # Normalize the query: remove ALL whitespace and convert to lowercase
        normalized_query = ''.join(query.split()).lower()

        # Try to find a matching UserInput (compare normalized versions)
        try:
            user_input = UserInput.objects.annotate(
                normalized_text=Replace('query_text', Value(' '), Value(''))
            ).get(normalized_text__iexact=normalized_query)
        except UserInput.DoesNotExist:
            user_input = None

        if user_input:
            results = user_input.recommendations.all()
        else:

            load_dotenv(dotenv_path=".env")

            # ✅ Check if variables are loaded
            API_TOKEN = os.getenv("API_TOKEN")

            results = call_gradio_api(query, API_TOKEN)
            save_results_to_db(query, results)

    return render(request, 'recommendation_system/results.html', {
        'results': results,
        'query': query
    })

def save_results_to_db(query_text, results):
    user_input = UserInput.objects.create(query_text=query_text)

    for result in results:
        ResearchPaper.objects.create(
            input=user_input,
            title=result.get('title'),
            abstract=result.get('abstract'),
            authors=result.get('authors'),
            year=result.get('year'),
            url=result.get('url'),
            score=result.get('score'),
            source=result.get('source')
        )
    return user_input

def input_recommendations_view(request):
    # Get the current page number from the GET request
    page_number = request.GET.get('page')
    
    # Get a paginated queryset of UserInput (instead of fetching all data first)
    inputs = UserInput.objects.all().order_by('-created_at')
    
    # Create a paginator object for the inputs
    paginator = Paginator(inputs, 1)  # 1 input per page
    page_obj = paginator.get_page(page_number)  # Get the current page
    
    # Create an empty list to store inputs and their recommendations
    input_recommendations = []

    # Loop through each user input on the current page and get corresponding recommendations
    for user_input in page_obj:
        # Instead of fetching all recommendations, fetch only the ones needed for the current user_input
        recommendations = ResearchPaper.objects.filter(input=user_input)
        
        # Add the input and its corresponding recommendations to the list
        input_recommendations.append({
            'user_input': user_input,
            'recommendations': recommendations
        })

    # Render the template with input_recommendations context and pagination info
    return render(request, 'recommendation_system/inputs_recommendations.html', {
        'input_recommendations': input_recommendations,
        'page_obj': page_obj  # Pass the pagination object to the template
    })

def call_gradio_api(query_text, api_token):
    post_url = "https://nalzero-adet.hf.space/gradio_api/call/predict"
    headers = {
        "Authorization": api_token,
        "Content-Type": "application/json"
    }

    try:
        # POST request
        response = requests.post(
            post_url,
            json={"data": [query_text]},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        event_id = response.json().get('event_id')
        if not event_id:
            return {"error": "No event_id in response"}

        # GET request
        get_url = f"{post_url}/{event_id}"
        with requests.get(
            get_url,
            headers=headers,
            stream=True,
            timeout=30
        ) as get_response:
            get_response.raise_for_status()
            
            for line in get_response.iter_lines():
                if line:
                    try:
                        decoded = line.decode('utf-8').strip()
                        if decoded.startswith('data:'):
                            json_str = decoded[5:].strip()
                            if json_str:
                                data = json.loads(json_str)
                                # Extract the inner list of results
                                if isinstance(data, list) and len(data) > 0:
                                    return data[0]  # Return first (and only) list of results
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue

        return {"error": "No valid data received in SSE stream"}

    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}