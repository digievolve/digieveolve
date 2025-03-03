from django.shortcuts import render, get_object_or_404
from .models import BlogPost, Category
from django.core.paginator import Paginator

def blog_list(request, category_slug=None):
    """View for listing all blog posts, optionally filtered by category"""
    # Start with all posts
    post_list = BlogPost.objects.all().order_by('-published_date')

    # Filter by category if provided
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        post_list = post_list.filter(category=category)

    # Get featured post (most recent or marked as featured)
    featured_post = BlogPost.objects.all().order_by('-published_date').first()

    # Get all categories
    categories = Category.objects.all()

    # Pagination
    paginator = Paginator(post_list, 6)  # Show 6 posts per page
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    context = {
        'posts': posts,
        'featured_post': featured_post,
        'categories': categories,
        'category': category,
        'title': f'Blog - {category.name}' if category else 'Blog'
    }

    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, slug):
    """View for displaying a single blog post"""
    post = get_object_or_404(BlogPost, slug=slug)

    # Optional: Get related posts
    related_posts = BlogPost.objects.filter(category=post.category).exclude(id=post.id)[:2]

    context = {
        'post': post,
        'related_posts': related_posts,
        'title': post.title
    }

    return render(request, 'blog/blog_detail.html', context)