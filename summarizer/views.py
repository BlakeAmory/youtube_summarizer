from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import SingleVideoForm, SearchForm, CustomUserCreationForm, CustomAuthenticationForm
from .utils import get_video_info, generate_summary, summarize_search_results
from .models import VideoSummary, SearchHistory, UserProfile
from .chroma_utils import store_video_data
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'summarizer/home.html')

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'summarizer/register.html', {'form': form})

def login(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                # Ensure UserProfile is created
                if not hasattr(user, 'userprofile'):
                    UserProfile.objects.create(user=user)
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'summarizer/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('home')

@login_required
def single_video_summary(request):
    if request.method == "POST":
        form = SingleVideoForm(request.POST)
        if form.is_valid():
            video_url = form.cleaned_data["video_url"]
            try:
                video_info = get_video_info(video_url)
                logger.debug(f"Video info retrieved: {video_info}")
                text_to_summarize = f"Title: {video_info['title']}\n\nDescription: {video_info['description']}"

                summary = generate_summary(text_to_summarize)
                logger.debug(f"Summary generated: {summary}")

                video_summary = VideoSummary.objects.create(
                    user=request.user,
                    video_url=video_url,
                    video_title=video_info["title"],
                    summary=summary['full_summary'],
                    short_description=summary['short_description'],
                    thumbnail_url=video_info.get("thumbnail"),
                    key_points=summary['key_points']
                )

                store_video_data(video_summary)

                logger.debug(f"Returning JSON response with summary: {summary}")
                return JsonResponse({'success': True, 'summary': summary, 'video': video_info})
            except Exception as e:
                logger.error(f"Error processing video {video_url}: {str(e)}", exc_info=True)
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            logger.error("Invalid form data")
            return JsonResponse({'success': False, 'error': 'Invalid form data'})
    else:
        form = SingleVideoForm()
    return render(request, 'summarizer/single_video_summary.html', {'form': form})

@login_required
def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            logger.info(f"Search query: {query}")
            # Save search query to the database
            search_history = SearchHistory.objects.create(user=request.user, query=query)
            summaries = summarize_search_results(query)
            for summary in summaries[:5]:  # Save only the top 5 summaries
                video_info = summary['video']
                summary_data = summary['summary']
                video_summary = VideoSummary.objects.create(
                    user=request.user,
                    video_url=video_info["url"],
                    video_title=video_info["title"],
                    summary=summary_data['full_summary'],
                    short_description=summary_data['short_description'],
                    thumbnail_url=video_info.get("thumbnail"),
                    key_points=summary_data['key_points']
                )
                search_history.video_summaries.add(video_summary)
            return redirect('search_results', query=query)
        else:
            logger.error(f"Form errors: {form.errors}")
    else:
        form = SearchForm()
    return render(request, 'summarizer/search.html', {'form': form})

@login_required
def search_results(request, query):
    logger.info(f"Processing search results for query: {query}")
    try:
        summaries = summarize_search_results(query)
        logger.info(f"Found {len(summaries)} results")
        for summary in summaries:
            logger.debug(f"Summary: {summary}")
        return render(request, 'summarizer/search_results.html', {'summaries': summaries, 'query': query})
    except Exception as e:
        logger.error(f"Error processing search query {query}: {str(e)}", exc_info=True)
        return render(request, 'summarizer/search_results.html', {'summaries': [], 'query': query, 'error': str(e)})

@login_required
def history(request):
    summaries = VideoSummary.objects.filter(user=request.user).order_by('-created_at')
    search_history = SearchHistory.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'summarizer/history.html', {'summaries': summaries, 'search_history': search_history})

@login_required
def user_profile(request):
    recent_summaries = VideoSummary.objects.filter(user=request.user).order_by('-created_at')[:5]
    recent_searches = SearchHistory.objects.filter(user=request.user).order_by('-created_at')[:5]
    return render(request, 'summarizer/user_profile.html', {'recent_summaries': recent_summaries, 'recent_searches': recent_searches})

@login_required
def view_summary(request, summary_id):
    summary = get_object_or_404(VideoSummary, id=summary_id, user=request.user)
    return render(request, 'summarizer/view_summary.html', {'summary': summary})

@login_required
def view_search(request, search_id):
    search = get_object_or_404(SearchHistory, id=search_id, user=request.user)
    summaries = search.video_summaries.all()
    return render(request, 'summarizer/view_search.html', {'search': search, 'summaries': summaries})
