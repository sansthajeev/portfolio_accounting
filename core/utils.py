from .models import JournalType

def determine_journal_for_entry(entry_type=None, is_cash=False, is_investment=False):
    if is_investment:
        journal, _ = JournalType.objects.get_or_create(name="Investment Journal", defaults={"prefix": "INV"})
    elif is_cash:
        journal, _ = JournalType.objects.get_or_create(name="Cash Journal", defaults={"prefix": "CASH"})
    else:
        journal, _ = JournalType.objects.get_or_create(name="General Journal", defaults={"prefix": "GEN"})
    return journal
