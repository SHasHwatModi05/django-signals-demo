import time
import threading
from django.core.management.base import BaseCommand
from django.db import transaction
from signals_demo.models import DemoModel
from signals_demo.signals import (
    sync_async_signal,
    thread_check_signal,
    transaction_check_signal,
    execution_logs,
    log_message
)

class Command(BaseCommand):
    help = "Runs all three Django signals proof demonstrations in the command line."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("\n=== Django Signals Characteristics Demonstration ===\n"))
        
        # --- Experiment 1: Sync vs Async ---
        self.stdout.write("="*80)
        self.stdout.write("EXPERIMENT 1: Are Django signals executed synchronously or asynchronously by default?")
        self.stdout.write("="*80)
        
        execution_logs.clear()
        start_time = time.time()
        log_message(f"[Caller] Starting execution. Time: {time.strftime('%H:%M:%S')}")
        log_message("[Caller] Sending sync_async_signal...")
        
        sync_async_signal.send(sender=None)
        
        end_time = time.time()
        elapsed = end_time - start_time
        log_message(f"[Caller] Returned back to caller. Time: {time.strftime('%H:%M:%S')}")
        log_message(f"[Caller] Total execution time: {elapsed:.4f} seconds.")
        
        if elapsed >= 2.0:
            self.stdout.write(self.style.SUCCESS("\n-> STATUS: PROVEN (Synchronous)"))
            self.stdout.write("Explanation: The signal receiver blocked execution for 2 seconds (using time.sleep).")
            self.stdout.write("The caller was suspended and resumed only after the receiver finished, showing synchronous flow.\n")
        else:
            self.stdout.write(self.style.ERROR("\n-> STATUS: FAILED (Asynchronous execution detected)\n"))

        # --- Experiment 2: Same Thread ---
        self.stdout.write("="*80)
        self.stdout.write("EXPERIMENT 2: Do Django signals run in the same thread as the caller?")
        self.stdout.write("="*80)
        
        execution_logs.clear()
        caller_thread_id = threading.get_ident()
        caller_thread_name = threading.current_thread().name
        log_message(f"[Caller] Caller Thread ID: {caller_thread_id}, Name: '{caller_thread_name}'")
        log_message("[Caller] Sending thread_check_signal...")
        
        responses = thread_check_signal.send(sender=None)
        receiver_info = responses[0][1] if responses else None
        
        if receiver_info:
            rec_id = receiver_info["thread_id"]
            rec_name = receiver_info["thread_name"]
            same_thread = (caller_thread_id == rec_id)
            log_message(f"[Caller] Comparison: Caller Thread ({caller_thread_id}) {'==' if same_thread else '!='} Receiver Thread ({rec_id})")
            
            if same_thread:
                self.stdout.write(self.style.SUCCESS("\n-> STATUS: PROVEN (Same Thread)"))
                self.stdout.write(f"Explanation: Both caller and receiver share Thread ID {caller_thread_id} and name '{caller_thread_name}'.\n")
            else:
                self.stdout.write(self.style.ERROR("\n-> STATUS: FAILED (Different Threads detected)\n"))
        else:
            self.stdout.write(self.style.ERROR("\n-> ERROR: Receiver response could not be verified.\n"))

        # --- Experiment 3: Same Transaction ---
        self.stdout.write("="*80)
        self.stdout.write("EXPERIMENT 3: Do Django signals run in the same database transaction as the caller?")
        self.stdout.write("="*80)
        
        execution_logs.clear()
        DemoModel.objects.all().delete()
        log_message(f"[Caller] Initial DB Record Count: {DemoModel.objects.count()}")
        
        try:
            with transaction.atomic():
                log_message("[Caller] Opened transaction.atomic() block.")
                log_message("[Caller] Creating record 'Caller CLI Record'...")
                DemoModel.objects.create(name="Caller CLI Record")
                
                log_message(f"[Caller] Count in DB (before signal): {DemoModel.objects.count()}")
                log_message("[Caller] Sending transaction_check_signal...")
                transaction_check_signal.send(sender=None)
                
                log_message(f"[Caller] Count in DB (after signal): {DemoModel.objects.count()}")
                log_message("[Caller] Raising ValueError to trigger transaction rollback...")
                raise ValueError("Simulated Rollback Exception")
        except ValueError as e:
            log_message(f"[Caller] Caught expected exception: {e}")
            
        final_count = DemoModel.objects.count()
        log_message(f"[Caller] Post-transaction DB Record Count: {final_count}")
        
        if final_count == 0:
            self.stdout.write(self.style.SUCCESS("\n-> STATUS: PROVEN (Same Transaction)"))
            self.stdout.write("Explanation: Both the record created by the caller and the record created inside the")
            self.stdout.write("signal receiver were rolled back, returning the database count to 0. This confirms transaction sharing.\n")
        else:
            self.stdout.write(self.style.ERROR("\n-> STATUS: FAILED (Signal receiver did not roll back with caller)\n"))
            
        self.stdout.write("="*80)
        self.stdout.write("Django Signals Demonstration Finished.")
        self.stdout.write("="*80)
