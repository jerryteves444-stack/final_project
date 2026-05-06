from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, Comment
from django.db.models import Q


# ==========================================
# 🏠 CORE VIEWS (PROTECTED FEED & PROFILE)
# ==========================================

@login_required(login_url='login')
def home(request):
    """Handles the main feed: displaying posts, creating posts, and comments."""
    # Siguroa nga naay profile ang user
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Mokuha sa tanang posts para sa feed
    posts = Post.objects.all().order_by('-created_at')

    # OPTIONAL: I-calculate ang count sa view para mas sigurado (pero pwede ra sa template)
    # user_post_count = Post.objects.filter(user=request.user).count()

    if request.method == "POST":
        # Handle Profile/Cover Photo Updates
        if 'profile_picture' in request.FILES or 'cover_photo' in request.FILES:
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
            if 'cover_photo' in request.FILES:
                profile.cover_photo = request.FILES['cover_photo']
            profile.save()
            messages.success(request, "Photos updated successfully!")
            return redirect('home')

        # Handle New Post
        elif 'content' in request.POST:
            content = request.POST.get('content')
            if content.strip():
                # Paghimo og post
                Post.objects.create(user=request.user, content=content)
                messages.success(request, "Shared successfully!")
            else:
                messages.error(request, "Cannot share an empty post.")
            return redirect('home')

        # Handle New Comment
        elif 'comment_content' in request.POST:
            post_id = request.POST.get('post_id')
            comment_text = request.POST.get('comment_content')
            if comment_text.strip():
                target_post = get_object_or_404(Post, id=post_id)
                Comment.objects.create(post=target_post, user=request.user, content=comment_text)
                messages.success(request, "Reply added!")
            else:
                messages.error(request, "Cannot add an empty reply.")
            return redirect('home')

    return render(request, "accounts/home.html", {
        "profile": profile,
        "posts": posts,
        # "user_post_count": user_post_count # Pwede nimo i-pass kini kon dili mugana ang template logic
    })

@login_required(login_url='login')
def view_profile(request, pk):
    """
    Public view of a specific member's profile.
    Gipasa ang profile object gamit ang 'profile' nga key.
    """
    # Pangitaon ang profile sa user nga gi-click (target)
    profile_data = get_object_or_404(Profile, pk=pk)

    # I-render ang template uban ang profile data
    return render(request, "accounts/view_profile.html", {"profile": profile_data})

@login_required(login_url='login')
def update_profile(request):
    """Handles updating basic user and profile information via form."""
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')

        new_email = request.POST.get('email')
        if new_email:
            request.user.email = new_email
        request.user.save()

        profile.middle_name = request.POST.get('middle_name')
        profile.gender = request.POST.get('gender')
        profile.user_type = request.POST.get('user_type')
        profile.address = request.POST.get('address')
        profile.dob = request.POST.get('dob')
        profile.save()

        messages.success(request, "Settings updated successfully!")
        return redirect('home')

    return render(request, "accounts/update_profile.html", {"profile": profile})


# ==========================================
# 📝 FEED INTERACTIONS (EDIT/DELETE)
# ==========================================

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == "POST":
        content = request.POST.get('content')
        if content.strip():
            post.content = content
            post.save()
            messages.success(request, "Post updated.")
        else:
            messages.error(request, "Post cannot be empty.")
    return redirect('home')


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user or request.user.is_staff or request.user.is_superuser:
        post.delete()
        messages.success(request, "Post removed successfully.")
    else:
        messages.error(request, "You do not have permission.")
    return redirect('home')


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == "POST":
        content = request.POST.get('content')
        if content.strip():
            comment.content = content
            comment.save()
            messages.success(request, "Reply updated.")
        else:
            messages.error(request, "Reply cannot be empty.")
    return redirect('home')


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user or request.user.is_staff or request.user.is_superuser:
        comment.delete()
        messages.success(request, "Reply removed.")
    else:
        messages.error(request, "Access denied.")
    return redirect('home')



# ==========================================
# 👥 COMMUNITY & MEMBERS VIEWS
# ==========================================

@login_required(login_url='login')
def all_members(request):
    """Handles displaying, searching, and filtering community members."""
    # 1. Get query parameters from the URL
    search_query = request.GET.get('search', '')
    gender_filter = request.GET.get('gender')
    user_type_filter = request.GET.get('user_type')

    # 2. Start with the full list of profiles
    members = Profile.objects.all()

    # 3. Apply Search (First Name, Last Name, or Username)
    if search_query:
        members = members.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )

    # 4. Apply Gender Filter (Exclude if 'All' or empty)
    if gender_filter and gender_filter != 'All':
        members = members.filter(gender=gender_filter)

    # 5. Apply User Type Filter (Exclude if 'All' or empty)
    if user_type_filter and user_type_filter != 'All':
        members = members.filter(user_type=user_type_filter)

    # 6. Pass data back to the template
    return render(request, "accounts/all_members.html", {
        "members": members,
        "search_query": search_query,
        "current_gender": gender_filter,
        "current_user_type": user_type_filter,
    })

def member_list_view(request):
    search_query = request.GET.get('search', '')
    members = Profile.objects.all()
    if search_query:
        members = members.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    return render(request, 'accounts/all_members.html', {'members': members})


# ==========================================
# 🔐 AUTHENTICATION VIEWS
# ==========================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect('/admin/') if user.is_superuser else redirect('home')
        messages.error(request, "Wrong username or password")
    return render(request, "accounts/login.html")


def register_view(request):
    if request.method == "POST":
        data = request.POST
        if User.objects.filter(username=data.get('username')).exists():
            messages.error(request, "Username already taken")
            return redirect('register')

        user = User.objects.create_user(
            username=data.get('username'), email=data.get('email'), password=data.get('password'),
            first_name=data.get('first_name'), last_name=data.get('last_name')
        )

        Profile.objects.filter(user=user).update(
            middle_name=data.get('middle_name'), gender=data.get('gender'),
            user_type=data.get('type'), address=data.get('address'), dob=data.get('birthdate')
        )
        messages.success(request, "Account created! Please log in.")
        return redirect('login')
    return render(request, "accounts/register.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login')


# ==========================================
# 🛠️ ADMIN & USER MANAGEMENT (STAFF ONLY)
# ==========================================

@login_required(login_url='login')
def admin_page(request):
    if not request.user.is_superuser: return redirect('home')
    return render(request, "accounts/admin.html", {"users_count": User.objects.count()})


@login_required(login_url='login')
def user_list(request):
    if not request.user.is_staff: return redirect('home')
    return render(request, "accounts/user_list.html", {
        "sunlight": Profile.objects.filter(user_type="Sunlight"),
        "starlight": Profile.objects.filter(user_type="Starlight"),
        "alpha": Profile.objects.filter(user_type="Alpha"),
        "omega": Profile.objects.filter(user_type="Omega"),
    })


@login_required(login_url='login')
def create_user(request):
    if not request.user.is_staff: return redirect('home')
    if request.method == "POST":
        User.objects.create_user(username=request.POST.get('username'), password=request.POST.get('password'))
        return redirect('user_list')
    return render(request, "accounts/create_user.html")


@login_required(login_url='login')
def update_user(request, id):
    if not request.user.is_staff: return redirect('home')
    user = get_object_or_404(User, id=id)
    if request.method == "POST":
        user.username, user.email = request.POST.get('username'), request.POST.get('email')
        user.save()
        return redirect('user_list')
    return render(request, "accounts/update_user.html", {"user": user})


@login_required(login_url='login')
def delete_user(request, id):
    if not request.user.is_staff or request.user.id == id: return redirect('user_list')
    get_object_or_404(User, id=id).delete()
    return redirect('user_list')


@login_required(login_url='login')
def dashboard(request):
    return render(request, "dashboard.html")