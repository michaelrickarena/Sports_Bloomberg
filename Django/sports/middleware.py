# from datetime import timedelta
# from django.utils.timezone import now
# from django.shortcuts import redirect
# from django.urls import reverse
# from sports.models import UserSubscription

# class SubscriptionCheckMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Allow public pages to be accessed without authentication or subscription checks
#         public_pages = ['/home', '/login', '/checkout', '/register']
#         if any(request.path.startswith(page) for page in public_pages):
#             return self.get_response(request)

#         if not request.user.is_authenticated:
#             # Redirect to login page if the user is not authenticated
#             return redirect(reverse('login'))  # Adjust this if needed to your login page URL

#         try:
#             subscription = UserSubscription.objects.get(user=request.user)
            
#             # Calculate trial end date by adding 7 days to trial_start_date
#             trial_end_date = subscription.start_date + timedelta(days=7)
            
#             # If the user hasn't paid and the trial period has expired, redirect to checkout
#             if subscription.status == 'inactive' and now() > trial_end_date:
#                 return redirect('/checkout')
            
#             # Check if subscription is active and the expiration date has passed
#             if subscription.status == 'active' and subscription.expiration_date and now() < subscription.expiration_date:
#                 return self.get_response(request)
            
#             # If subscription has been canceled, redirect to checkout
#             if subscription.status == 'canceled' or (subscription.status == 'inactive' and now() > subscription.expiration_date):
#                 return redirect('/checkout')

#         except UserSubscription.DoesNotExist:
#             pass

#         # If no issues, continue with the request
#         return self.get_response(request)
