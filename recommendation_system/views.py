from django.shortcuts import render
from .forms import SearchForm
from .search import enhanced_search  # Assuming you have a search.py file with enhanced_search function
from .models import UserInput, ResearchPaper
from django.core.paginator import Paginator
from django.db.models.functions import Replace  # Add this import
from django.db.models import Value  # Add this import

# Home view to display the search form
def home(request):
    form = SearchForm()
    return render(request, 'recommendation_system/home.html', {'form': form})

def search_view(request):
    query = request.GET.get('query', '')
    results = []

    if query:
        # Normalize the query: remove ALL whitespace and convert to lowercase
        normalized_query = ''.join(query.split()).lower()
        print(f"Normalized Query: {normalized_query}")

        # Try to find a matching UserInput (compare normalized versions)
        try:
            user_input = UserInput.objects.annotate(
                normalized_text=Replace('query_text', Value(' '), Value(''))
            ).get(normalized_text__iexact=normalized_query)
        except UserInput.DoesNotExist:
            user_input = None

        if user_input:
            # If match found, fetch its recommendations
            results = user_input.recommendations.all()
        else:
            # If no match, perform a new search and save results
            results = enhanced_search(query)
            save_results_to_db(query, results)

    return render(request, 'recommendation_system/results.html', {'results': results, 'query': query})

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
    # Ensure the query always fetches the latest data
    inputs = UserInput.objects.all().order_by('-created_at')  # Order by creation time (newest first)

    # Create a paginator object for the inputs
    paginator = Paginator(inputs, 1)  # Show 1 inputs per page
    page_number = request.GET.get('page')  # Get the current page number from the GET request
    page_obj = paginator.get_page(page_number)  # Get the current page

    # Create an empty list to store inputs and their recommendations
    input_recommendations = []

    # Loop through each user input on the current page and get corresponding recommendations from the database
    for user_input in page_obj:
        # Get the recommendations from the ResearchPaper model that correspond to the current user_input
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

