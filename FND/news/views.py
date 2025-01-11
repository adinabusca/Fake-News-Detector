from django.shortcuts import render
from .models import SourceStats
from transformers import pipeline
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

#load models
sentiment_analyzer = pipeline("sentiment-analysis", model = "distilbert-base-uncased-finetuned-sst-2-english")

def google_search(query):
    formatted_query = query.replace(" ", "+")
    url = f"https://www.google.com/search?q={formatted_query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
    }

    # Send the request to Google
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Error retrieving search results.")
        return []

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")
    search_results = []

    # Extract search results
    for item in soup.select("div.yuRUbf a"):
        if len(search_results) >= 10:
            break
        link = item["href"]
        if "translate.google.com" in link:
            continue
        
        title = item.select_one("h3")
        if title:
            title_text = title.get_text()  # Extract the text of the title
        else:
            title_text = "No title available"
        domain = urlparse(link).netloc
        search_results.append((title_text,link, domain))

    return search_results


def analyze_news(request):
    result = None
    
    if request.method == 'POST':
        content = request.POST.get('content')
        source = request.POST.get('source')
        
        if not source:
          print("Error: Source is empty")
        
        
        #sentiment analysis
        sentiment_result = sentiment_analyzer(content)[0]['label'].lower()
        confidence = sentiment_analyzer(content)[0]['score']
        
        #update statistics
        source_stats, created = SourceStats.objects.get_or_create(source=source)
        
        if sentiment_result == 'positive':
            source_stats.positive += 1
        elif sentiment_result == 'neutral':
            source_stats.neutral += 1
        elif sentiment_result == 'negative':
            source_stats.negative += 1
        
       
        fake = ""
        if source_stats.positive - source_stats.negative >= 5 or source_stats.positive - source_stats.negative <= -5 :
            fake = "There is a likely chance it is fake"
        elif source_stats.positive - source_stats.negative <= 3 and source_stats.positive - source_stats.negative >= -3 :
            fake = "Inconclusive. We cannot say for sure whether it is real or fake"
        else:
            fake = "There is a likely chance it is real" 
            
            
        source_stats.save() #save updated instance to the database
        
        # Google Search integration
        search_results = google_search(content)
    
        result = {
            "fake": fake,
            "confidence" : confidence,
            "sentiment" : sentiment_result,
            "source_stats":{
                "positive" : source_stats.positive,
                "neutral" : source_stats.neutral,
                "negative" : source_stats.negative,
            },
            "source":source,
            "search_results": search_results,  # Include search results in the result
        }
        
        #generate statistics plot
        generate_plot(source_stats)
        
    
    return render(request,'news/analyze_news.html', {'result': result})




def generate_plot(source_stats):
    categories = ['Positive', 'Neutral', 'Negative']
    values = [
        source_stats.positive,
        source_stats.neutral,
        source_stats.negative,
       
    ]
    
    plt.figure(figsize=(10,6))
    plt.bar(categories,values, color = ['green', 'blue', 'red'])
    plt.title(f'Statistics for {source_stats.source}')
    plt.xlabel('Categories')
    plt.ylabel('Count')
    
    #save plot
    plot_path = f'news/static/images/image{source_stats.source}_stats.png'
    plt.savefig(plot_path)
    plt.close()
        

