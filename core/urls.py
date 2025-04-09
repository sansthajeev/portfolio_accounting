from django.urls import path
from . import views

urlpatterns = [
    path('accounts/', views.account_list, name='accounts'),
    # path('add/', views.add_transaction, name='add_transaction'),
    path('journal/', views.journal, name='journal'),
    path('', views.dashboard, name='dashboard'),
    path('portfolio/add/', views.add_portfolio, name='add_portfolio'),
    path('portfolios/', views.portfolio_list, name='portfolio_list'),  
    path('portfolio/<int:portfolio_id>/', views.view_portfolio, name='view_portfolio'),
    path('portfolio/<int:portfolio_id>/add-investment/', views.add_investment, name='add_investment'),
    path('investment/<int:investment_id>/delete/', views.delete_investment, name='delete_investment'),
    path('accounts/add/', views.add_account, name='add_account'),
    path('reports/trial-balance/', views.trial_balance, name='trial_balance'),
    path('reports/profit-loss/', views.profit_loss, name='profit_loss'),
    path('reports/balance-sheet/', views.balance_sheet, name='balance_sheet'),
    path('shareholders/add/', views.add_shareholder, name='add_shareholder'),
    path('shareholders/', views.list_shareholders, name='list_shareholders'),
    path('shareholders/<int:shareholder_id>/add-capital/', views.add_capital_contribution, name='add_capital_contribution'),
    path('accounts/<int:account_id>/edit/', views.edit_account, name='edit_account'),
    path('accounts/<int:account_id>/delete/', views.delete_account, name='delete_account'),
    path('accounts/<int:account_id>/ledger/', views.account_ledger, name='account_ledger'),
    path('reports/day-journal/', views.day_journal, name='day_journal'),
    path('journals/', views.journal_list, name='journal_list'),
    path('journals/<int:pk>/edit/', views.edit_transaction, name='edit_transaction'),
    path('journals/<int:pk>/delete/', views.delete_transaction, name='delete_transaction'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),




    








]
