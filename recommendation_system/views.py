from django.shortcuts import render
from .forms import SearchForm
from .search import enhanced_search  # Assuming you have a search.py file with enhanced_search function

# Home view to display the search form
def home(request):
    form = SearchForm()
    return render(request, 'recommendation_system/home.html', {'form': form})

# View to handle search query and results
def search_view(request):
    query = request.GET.get('query', '')
    results = []

    if query:
        # Perform the search if there's a query
        results = enhanced_search(query)  # Assuming enhanced_search is a function you defined elsewhere

    return render(request, 'recommendation_system/results.html', {'results': results, 'query': query})
