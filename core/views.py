from django.shortcuts import render, redirect
from .models import Account, Transaction, Entry
from django.db import transaction as db_transaction
from .models import Portfolio, Investment
from django.contrib.auth.decorators import login_required

def account_list(request):
    accounts = Account.objects.all().order_by('code')
    return render(request, 'accounts.html', {'accounts': accounts})

from .models import Account, Transaction, Entry, JournalType

@login_required
def add_transaction(request):
    accounts = Account.objects.all()
    journals = JournalType.objects.all()

    if request.method == 'POST':
        description = request.POST['description']
        journal_id = request.POST['journal_id']
        debit_account = request.POST['debit_account']
        credit_account = request.POST['credit_account']
        amount = float(request.POST['amount'])

        journal = JournalType.objects.get(id=journal_id)

        # Create transaction
        tx = Transaction.objects.create(description=description, journal=journal)

        # Create debit and credit entries
        Entry.objects.create(transaction=tx, account_id=debit_account, amount=amount, entry_type='debit')
        Entry.objects.create(transaction=tx, account_id=credit_account, amount=amount, entry_type='credit')

        return redirect('journal_list')  # or wherever your success URL goes

    return render(request, 'transactions/add_transaction.html', {
        'accounts': accounts,
        'journals': journals,
    })

def journal(request):
    transactions = Transaction.objects.prefetch_related('entries__account').order_by('-date')
    return render(request, 'journal.html', {'transactions': transactions})



@login_required
def dashboard(request):
    portfolios = Portfolio.objects.filter(owner=request.user)
    return render(request, 'dashboard.html', {'portfolios': portfolios})

@login_required
def add_portfolio(request):
    if request.method == 'POST':
        Portfolio.objects.create(name=request.POST['name'], owner=request.user)
        return redirect('dashboard')
    return render(request, 'add_portfolio.html')

@login_required
def view_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
    investments = portfolio.investments.all()

    total_invested = sum(inv.amount_invested for inv in investments)
    total_current = sum(inv.current_value for inv in investments)
    gain_loss = total_current - total_invested
    return_pct = (gain_loss / total_invested * 100) if total_invested > 0 else 0

    return render(request, 'portfolio_detail.html', {
        'portfolio': portfolio,
        'total_invested': total_invested,
        'total_current': total_current,
        'gain_loss': gain_loss,
        'return_pct': return_pct,
    })

from django.shortcuts import get_object_or_404
from .utils import determine_journal_for_entry

@login_required
def add_investment(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
    accounts = Account.objects.all()

    if request.method == 'POST':
        asset_name = request.POST['asset_name']
        asset_type = request.POST['asset_type']
        purchase_date = request.POST['purchase_date']
        units = int(request.POST['units'])
        face_value = request.POST.get('face_value') or None
        cost_per_unit = float(request.POST['cost_per_unit'])
        amount_invested = units * cost_per_unit
        current_value = float(request.POST.get('current_value') or amount_invested)
        debit_account_id = request.POST['debit_account']
        credit_account_id = request.POST['credit_account']
        symbol = request.POST['symbol']

        with db_transaction.atomic():
            journal = determine_journal_for_entry(entry_type='investment', is_investment=True)
            tx = Transaction.objects.create(
                description=f"Purchase of {units} {asset_name} for portfolio '{portfolio.name}'",
                journal=journal
            )

            Entry.objects.create(transaction=tx, account_id=debit_account_id, amount=amount_invested, entry_type='debit')
            Entry.objects.create(transaction=tx, account_id=credit_account_id, amount=amount_invested, entry_type='credit')

            Investment.objects.create(
                portfolio=portfolio,
                asset_name=asset_name,
                asset_type=asset_type,
                purchase_date=purchase_date,
                units=units,
                face_value=face_value,
                cost_per_unit=cost_per_unit,
                amount_invested=amount_invested,
                current_value=current_value,
                transaction=tx,
                symbol=symbol,
            )

        return redirect('view_portfolio', portfolio_id=portfolio.id)

    return render(request, 'add_investment.html', {
        'portfolio': portfolio,
        'accounts': accounts,
    })

@login_required
def delete_investment(request, investment_id):
    investment = get_object_or_404(Investment, id=investment_id, portfolio__owner=request.user)
    portfolio_id = investment.portfolio.id
    investment.delete()
    return redirect('view_portfolio', portfolio_id=portfolio_id)


@login_required
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(owner=request.user)
    return render(request, 'portfolio_list.html', {'portfolios': portfolios})

from django.contrib import messages
from .models import Account, ACCOUNT_TYPES
@login_required
def add_account(request):
    accounts = Account.objects.all()

    if request.method == 'POST':
        name = request.POST['name']
        code = request.POST['code']
        type = request.POST['type']
        parent_id = request.POST.get('parent') or None

        Account.objects.create(
            name=name,
            code=code,
            type=type,
            parent_id=parent_id
        )
        messages.success(request, "Account created successfully.")
        return redirect('accounts')

    return render(request, 'add_account.html', {'accounts': accounts, 'account_types': ACCOUNT_TYPES})

@login_required
def edit_account(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    accounts = Account.objects.exclude(id=account_id)

    if request.method == 'POST':
        account.name = request.POST['name']
        account.code = request.POST['code']
        account.type = request.POST['type']
        parent_id = request.POST.get('parent')
        account.parent_id = parent_id if parent_id else None
        account.save()
        messages.success(request, "Account updated.")
        return redirect('accounts')

    return render(request, 'edit_account.html', {
        'account': account,
        'accounts': accounts,
        'account_types': ACCOUNT_TYPES
    })

@login_required
def delete_account(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    account.delete()
    messages.success(request, "Account deleted.")
    return redirect('accounts')



from datetime import date
from collections import defaultdict
from django.db.models import Sum, Q

@login_required
def trial_balance(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date:
        start_date = date.min
    else:
        start_date = date.fromisoformat(start_date)

    if not end_date:
        end_date = date.max
    else:
        end_date = date.fromisoformat(end_date)

    accounts = Account.objects.all().order_by('code')
    grouped_accounts = defaultdict(list)

    # Group accounts by type (string)
    for acc in accounts:
        group_name = acc.type.capitalize()
        grouped_accounts[group_name].append(acc)

    report_data = {}

    for group_name, group_accounts in grouped_accounts.items():
        group_rows = []
        totals = {
            'opening_debit': 0,
            'opening_credit': 0,
            'period_debit': 0,
            'period_credit': 0,
            'closing_debit': 0,
            'closing_credit': 0,
        }

        for acc in group_accounts:
            opening_debit = acc.entry_set.filter(entry_type='debit', transaction__date__lt=start_date).aggregate(s=Sum('amount'))['s'] or 0
            opening_credit = acc.entry_set.filter(entry_type='credit', transaction__date__lt=start_date).aggregate(s=Sum('amount'))['s'] or 0
            opening = opening_debit - opening_credit

            period_debit = acc.entry_set.filter(entry_type='debit', transaction__date__range=(start_date, end_date)).aggregate(s=Sum('amount'))['s'] or 0
            period_credit = acc.entry_set.filter(entry_type='credit', transaction__date__range=(start_date, end_date)).aggregate(s=Sum('amount'))['s'] or 0
            period = period_debit - period_credit

            closing = opening + period

            group_rows.append({
                'account': acc,
                'opening': opening,
                'period_debit': period_debit,
                'period_credit': period_credit,
                'closing': closing,
            })

            # Totals
            totals['opening_debit'] += opening if opening > 0 else 0
            totals['opening_credit'] += abs(opening) if opening < 0 else 0
            totals['period_debit'] += period_debit
            totals['period_credit'] += period_credit
            totals['closing_debit'] += closing if closing > 0 else 0
            totals['closing_credit'] += abs(closing) if closing < 0 else 0

        report_data[group_name] = {
            'rows': group_rows,
            'totals': totals,
        }
    # Calculate grand totals
    grand_totals = {
        'opening_debit': 0,
        'opening_credit': 0,
        'period_debit': 0,
        'period_credit': 0,
        'closing_debit': 0,
        'closing_credit': 0,
    }

    for data in report_data.values():
        for key in grand_totals:
            grand_totals[key] += data['totals'][key]

    return render(request, 'trial_balance.html', {
        'report_data': report_data,
        'start_date': None if start_date == date.min else start_date,
        'end_date': None if end_date == date.max else end_date,
        'grand_totals': grand_totals,
    })

@login_required
def profit_loss(request):
    income_accounts = Account.objects.filter(type='income')
    expense_accounts = Account.objects.filter(type='expense')

    income = []
    total_income = 0

    for acc in income_accounts:
        total = acc.entry_set.filter(entry_type='credit').aggregate(sum=Sum('amount'))['sum'] or 0
        if total > 0:
            income.append({'account': acc, 'amount': total})
            total_income += total

    expenses = []
    total_expense = 0

    for acc in expense_accounts:
        total = acc.entry_set.filter(entry_type='debit').aggregate(sum=Sum('amount'))['sum'] or 0
        if total > 0:
            expenses.append({'account': acc, 'amount': total})
            total_expense += total

    net_profit = total_income - total_expense

    return render(request, 'profit_loss.html', {
        'income': income,
        'expenses': expenses,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_profit': net_profit,
    })


@login_required
def balance_sheet(request):
    # Assets
    asset_accounts = Account.objects.filter(type='asset')
    assets = []
    total_assets = 0

    for acc in asset_accounts:
        debit = acc.entry_set.filter(entry_type='debit').aggregate(sum=Sum('amount'))['sum'] or 0
        credit = acc.entry_set.filter(entry_type='credit').aggregate(sum=Sum('amount'))['sum'] or 0
        balance = debit - credit
        if balance != 0:
            assets.append({'account': acc, 'balance': balance})
            total_assets += balance

    # Liabilities and Equity
    liabilities_equity = []
    total_liabilities_equity = 0

    for acc in Account.objects.filter(type__in=['liability', 'equity']):
        debit = acc.entry_set.filter(entry_type='debit').aggregate(sum=Sum('amount'))['sum'] or 0
        credit = acc.entry_set.filter(entry_type='credit').aggregate(sum=Sum('amount'))['sum'] or 0
        balance = credit - debit
        if balance != 0:
            liabilities_equity.append({'account': acc, 'balance': balance})
            total_liabilities_equity += balance

    return render(request, 'balance_sheet.html', {
        'assets': assets,
        'liabilities_equity': liabilities_equity,
        'total_assets': total_assets,
        'total_liabilities_equity': total_liabilities_equity,
    })


from .models import Shareholder

@login_required
def add_shareholder(request):
    equity_accounts = Account.objects.filter(type='equity').exclude(shareholder__isnull=False)

    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        account_id = request.POST['account']
        Shareholder.objects.create(
            name=name,
            email=email,
            account_id=account_id
        )
        messages.success(request, "Shareholder added successfully.")
        return redirect('list_shareholders')

    return render(request, 'add_shareholder.html', {
        'accounts': equity_accounts
    })

@login_required
def list_shareholders(request):
    shareholders = Shareholder.objects.select_related('account')
    return render(request, 'shareholder_list.html', {'shareholders': shareholders})


@login_required
def add_capital_contribution(request, shareholder_id):
    shareholder = get_object_or_404(Shareholder, id=shareholder_id)
    cash_accounts = Account.objects.filter(type__in=['asset']).order_by('code')  # e.g., Bank or Cash accounts

    if request.method == 'POST':
        amount = float(request.POST['amount'])
        cash_account_id = request.POST['cash_account']
        cash_account = Account.objects.get(id=cash_account_id)

        # Create Transaction
        journal = determine_journal_for_entry(entry_type="equity", is_investment=False)
        tx = Transaction.objects.create(description=f"Capital contribution by {shareholder.name}", journal=journal)

      

        # Debit Cash/Bank
        Entry.objects.create(
            transaction=tx,
            account=cash_account,
            amount=amount,
            entry_type='debit'
        )

        # Credit Shareholder's Capital Account
        Entry.objects.create(
            transaction=tx,
            account=shareholder.account,
            amount=amount,
            entry_type='credit'
        )

        messages.success(request, "Capital contribution recorded.")
        return redirect('list_shareholders')

    return render(request, 'add_capital_contribution.html', {
        'shareholder': shareholder,
        'cash_accounts': cash_accounts
    })


from django.db.models import Q

@login_required
def account_ledger(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    entries = account.entry_set.select_related('transaction').order_by('transaction__date', 'id')

    # Filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        entries = entries.filter(transaction__date__gte=start_date)
    if end_date:
        entries = entries.filter(transaction__date__lte=end_date)

    ledger = []
    balance = 0

    for entry in entries:
        if entry.entry_type == 'debit':
            balance += entry.amount
        else:
            balance -= entry.amount

        ledger.append({
            'date': entry.transaction.date,
            'description': entry.transaction.description,
            'debit': entry.amount if entry.entry_type == 'debit' else 0,
            'credit': entry.amount if entry.entry_type == 'credit' else 0,
            'balance': balance
        })

    return render(request, 'account_ledger.html', {
        'account': account,
        'ledger': ledger,
        'start_date': start_date,
        'end_date': end_date
    })


from django.db.models import Sum
from django.utils.dateparse import parse_date
from .models import Transaction, Entry

@login_required
def day_journal(request):
    selected_date = request.GET.get('date')
    transactions = []
    total_debit = total_credit = 0

    if selected_date:
        transactions = Transaction.objects.filter(date=parse_date(selected_date)).prefetch_related('entries', 'journal')

        total_debit = Entry.objects.filter(
            transaction__in=transactions,
            entry_type='debit'
        ).aggregate(s=Sum('amount'))['s'] or 0

        total_credit = Entry.objects.filter(
            transaction__in=transactions,
            entry_type='credit'
        ).aggregate(s=Sum('amount'))['s'] or 0

    return render(request, 'reports/day_journal.html', {
        'transactions': transactions,
        'selected_date': selected_date,
        'total_debit': total_debit,
        'total_credit': total_credit,
    })



from django.shortcuts import render, get_object_or_404, redirect
from .models import Transaction, Entry, JournalType
from .forms import TransactionForm  # We'll make this next

@login_required
def journal_list(request):
    transactions = Transaction.objects.select_related('journal').prefetch_related('entries').order_by('-date')
    return render(request, 'journals/list.html', {'transactions': transactions})


@login_required
def edit_transaction(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=tx)
        if form.is_valid():
            form.save()
            return redirect('journal_list')
    else:
        form = TransactionForm(instance=tx)

    return render(request, 'journals/edit.html', {'form': form, 'transaction': tx})


@login_required
def delete_transaction(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)

    if request.method == 'POST':
        tx.delete()
        return redirect('journal_list')

    return render(request, 'journals/delete_confirm.html', {'transaction': tx})