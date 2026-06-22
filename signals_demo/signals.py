import time
import threading
from django.dispatch import Signal, receiver
from django.db import transaction
from .models import DemoModel

# 1. Custom Signal for Synchronous vs Asynchronous test
sync_async_signal = Signal()

# 2. Custom Signal for Thread identity test
thread_check_signal = Signal()

# 3. Custom Signal for Database Transaction test
transaction_check_signal = Signal()

# Define list to accumulate logs during execution for view display
execution_logs = []

def log_message(msg):
    execution_logs.append(msg)
    print(msg)

@receiver(sync_async_signal)
def handle_sync_async(sender, **kwargs):
    log_message("[Receiver] Signal handler started (simulating heavy 2s task).")
    time.sleep(2)
    log_message("[Receiver] Signal handler finished.")

@receiver(thread_check_signal)
def handle_thread_check(sender, **kwargs):
    thread_id = threading.get_ident()
    thread_name = threading.current_thread().name
    log_message(f"[Receiver] Current Thread ID: {thread_id}, Thread Name: '{thread_name}'")
    return {"thread_id": thread_id, "thread_name": thread_name}

@receiver(transaction_check_signal)
def handle_transaction_check(sender, **kwargs):
    log_message("[Receiver] Signal receiver triggered.")
    
    # Check if the record created by caller inside transaction is visible to receiver
    visible_records = list(DemoModel.objects.all())
    log_message(f"[Receiver] Querying DB: Found {len(visible_records)} records.")
    for rec in visible_records:
        log_message(f"  - Record in DB: '{rec.name}'")
        
    log_message("[Receiver] Creating new record inside signal receiver...")
    DemoModel.objects.create(name="Record created by Receiver")
    
    total_count = DemoModel.objects.count()
    log_message(f"[Receiver] Count after receiver insert: {total_count}")
