from django.shortcuts import render
from .forms import SearchForm
from .search import enhanced_search  # Assuming you have a search.py file with enhanced_search function
from .models import UserInput, ResearchPaper

# Home view to display the search form
def home(request):
    form = SearchForm()
    return render(request, 'recommendation_system/home.html', {'form': form})

def search_view(request):
    query = request.GET.get('query', '')
    results = []

    if query:
        # Perform the search if there's a query
        results = enhanced_search(query)

        # ✅ Save results to the database
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
