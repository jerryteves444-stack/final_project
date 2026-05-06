import time
import xendit
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Sum
from xendit.apis import InvoiceApi
from .models import Payment
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json



# 1. Helper function to get Xendit Instance
def get_xendit_instance():
    # FIXED: Replaced dictionary with a direct string to avoid 'dict' + 'str' error
    configuration = xendit.Configuration(
        api_key='xnd_development_ZtSng94l33FdcGgjoaLYAGV4qMaw0ESCiWyr8kgdcfOG9ZkQL38TNLEnThwW'
    )
    api_client = xendit.ApiClient(configuration)
    return InvoiceApi(api_client)


# 2. Admin Dashboard
def admin_dashboard(request):
    payments = Payment.objects.all().order_by('-created_at')
    # Summing up revenue for the Mortic platform
    total_revenue = payments.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'payments/admin_dashboard.html', {
        'payments': payments,
        'total_revenue': total_revenue
    })


# 3. Main Registration Page (Plan Selection)
def payment_page(request):
    return render(request, 'payments/register.html')


# 4. Processing Logic for Solo and Family Plans
def process_payment(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')

        plan = request.POST.get('plan_choice', 'Solo')

        # --- MUTUALLY EXCLUSIVE FILTER START ---
        # Define the list of plans that belong to the "Mortic Platform"
        platform_plans = ['Solo', 'Family']

        # Check if the user has ANY of these plans with a 'paid' or 'pending' status
        already_has_plan = Payment.objects.filter(
            user=request.user,
            plan_requested__in=platform_plans,
            status__in=['paid', 'pending']
        ).exists()

        if already_has_plan:
            return render(request, 'payments/failure.html', {
                'error': 'You already have an active or pending subscription. '
                         'Users with a Solo plan cannot register for Family, and vice versa.'
            })
        # --- MUTUALLY EXCLUSIVE FILTER END ---

        # ... (Rest of your existing name retrieval and price logic)
        user_profile = getattr(request.user, 'profile', None)
        fname = user_profile.first_name if user_profile and user_profile.first_name else (
                    request.user.first_name or request.user.username)
        lname = user_profile.last_name if user_profile and user_profile.last_name else (
                    request.user.last_name or "User")
        price = 2000 if plan == "Family" else 500

        api_instance = get_xendit_instance()
        ext_id = f"mortic-{request.user.username}-{plan.lower()}-{int(time.time())}"

        try:
            # Create local record and redirect to Xendit
            Payment.objects.create(
                user=request.user,
                first_name=fname,
                last_name=lname,
                amount=price,
                external_id=ext_id,
                plan_requested=plan,
                status='pending'
            )

            create_invoice_request = {
                "external_id": ext_id,
                "amount": price,
                "payer_email": request.user.email,
                "description": f"Mortic {plan} Plan Subscription",
                "success_redirect_url": request.build_absolute_uri(reverse('payments:success')),
                "failure_redirect_url": request.build_absolute_uri(reverse('payments:failure')),
                "payment_methods": ["GCASH"],
            }

            api_response = api_instance.create_invoice(create_invoice_request=create_invoice_request)
            return redirect(api_response.invoice_url)

        except Exception as e:
            return render(request, 'payments/failure.html', {'error': str(e)})

    return redirect('payments:payments')


def process_mortuary_payment(request):
    """
    Handles Mortuary logic:
    - Solo platform members -> Can only pay Mortuary Solo (₱125).
    - Family platform members -> Can only pay Mortuary Family (₱300).
    - Unregistered users -> Can ONLY Donate.
    - Multiple payments allowed for the same tier (e.g., consecutive deaths),
      but only if no invoice is currently 'pending'.
    """
    if request.method != "POST":
        return redirect('payments:mortuary')

    if not request.user.is_authenticated:
        return redirect('login')

    # Get the requested plan from the form (Solo, Family, or Donation)
    plan = request.POST.get('plan_choice', 'Solo')

    # --- 1. TIER-BASED VALIDATION ---
    if plan != "Donation":
        # Check which platform plan the user has PAID for
        user_subscription = Payment.objects.filter(
            user=request.user,
            plan_requested__in=['Solo', 'Family'],
            status='paid'
        ).first()

        # If they haven't paid for a platform plan, they can't access fixed tiers
        if not user_subscription:
            return render(request, 'payments/failure.html', {
                'error': 'Access Denied. You must have an active subscription to use Mortuary services. '
                         'However, you are still welcome to donate.'
            })

        # STRICT MATCH: Block Solo users from paying Family Mortuary and vice versa
        if plan != user_subscription.plan_requested:
            return render(request, 'payments/failure.html', {
                'error': f'Tier Mismatch. As a {user_subscription.plan_requested} member, '
                         f'you can only pay for the Mortuary {user_subscription.plan_requested} plan.'
            })

    # --- 2. PENDING INVOICE FILTER ---
    # Prevents creating a new invoice if one is already awaiting payment
    if plan != "Donation":
        target_plan = f"Mortuary {plan}"

        # We check both to be safe, though the tier match above makes the "alternate" check secondary
        has_pending = Payment.objects.filter(
            user=request.user,
            plan_requested__icontains="Mortuary",
            status='pending'
        ).exists()

        if has_pending:
            return render(request, 'payments/failure.html', {
                'error': 'You already have a pending Mortuary invoice. '
                         'Please finish that payment or wait for it to expire before starting a new one.'
            })

    # --- 3. PRICE LOGIC ---
    if plan == "Solo":
        price = 125
    elif plan == "Family":
        price = 300
    elif plan == "Donation":
        try:
            price = float(request.POST.get('donation_amount', 0))
            if price <= 0: raise ValueError
        except (ValueError, TypeError):
            return render(request, 'payments/failure.html', {'error': 'Invalid donation amount.'})
    else:
        # Fallback security
        return redirect('payments:mortuary')

    # --- 4. XENDIT GENERATION & LOCAL RECORD ---
    user_profile = getattr(request.user, 'profile', None)
    fname = user_profile.first_name if user_profile and user_profile.first_name else (
            request.user.first_name or request.user.username)
    lname = user_profile.last_name if user_profile and user_profile.last_name else (
            request.user.last_name or "User")

    api_instance = get_xendit_instance()
    ext_id = f"mortuary-{request.user.username}-{plan.lower()}-{int(time.time())}"

    try:
        Payment.objects.create(
            user=request.user,
            first_name=fname,
            last_name=lname,
            amount=price,
            external_id=ext_id,
            plan_requested=f"Mortuary {plan}",
            status='pending'
        )

        create_invoice_request = {
            "external_id": ext_id,
            "amount": price,
            "payer_email": request.user.email,
            "description": f"Mortic Mortuary {plan} - {fname} {lname}",
            "success_redirect_url": request.build_absolute_uri(reverse('payments:success')),
            "failure_redirect_url": request.build_absolute_uri(reverse('payments:failure')),
            "payment_methods": ["GCASH"],
        }

        api_response = api_instance.create_invoice(create_invoice_request=create_invoice_request)
        return redirect(api_response.invoice_url)

    except Exception as e:
        return render(request, 'payments/failure.html', {'error': str(e)})
# 5. Helper Views for Template Rendering
def success(request):
    return render(request, 'payments/success.html')


def failure(request):
    return render(request, 'payments/failure.html')


def solo_registration(request):
    return render(request, 'payments/solo.html')


def family_registration(request):
    return render(request, 'payments/family.html')

def solo_payment(request):
    return render(request, 'payments/solo_pay.html')

def family_payment(request):
    return render(request, 'payments/family_pay.html')

def mortuary_registration(request):
    """Renders the main Mortuary service and plan selection page."""
    return render(request, 'payments/mortuary.html')

def donation_page(request):
    """Renders the custom donation amount page."""
    return render(request, 'payments/donation.html')


@csrf_exempt
def xendit_webhook(request):
    """
    Receives notification from Xendit and updates Payment status to 'paid'.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # This matches the external_id you generated during payment creation
            external_id = data.get('external_id')
            status = data.get('status')

            if status == 'PAID':
                # Locate the record and update it
                payment = Payment.objects.filter(external_id=external_id).first()
                if payment:
                    payment.status = 'paid'
                    payment.save()

            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(status=400)
    return HttpResponse(status=405)
